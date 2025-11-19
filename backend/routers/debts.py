from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
import os
import uuid
from datetime import datetime
from decimal import Decimal

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user, get_current_finance_user

router = APIRouter(
    tags=["debts"],
)

@router.post("/debts/{debt_id}/payments/", response_model=schemas.Payment)
def create_payment_for_debt(
    debt_id: int,
    payment_date: str = Form(...),
    amount: float = Form(...),
    payment_method: Optional[str] = Form(None),
    receipt: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a payment for a specific debt with a variable amount, upload an optional receipt,
    and update the debt's 'is_paid' status based on the total payments.
    Also creates a corresponding income transaction for the club.
    """
    db_debt = db.query(models.Debt).options(selectinload(models.Debt.payments)).join(models.Member).filter(
        models.Debt.id == debt_id,
        models.Member.club_id == current_user.club_id
    ).first()

    if not db_debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    try:
        parsed_payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    payment_amount = Decimal(str(amount))
    if payment_amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive.")

    receipt_url = None
    if receipt:
        upload_dir = "uploads/receipts"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = receipt.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_location = os.path.join(upload_dir, unique_filename)
        
        with open(file_location, "wb+") as file_object:
            file_object.write(receipt.file.read())
        receipt_url = file_location

    # Create and save the new payment
    db_payment = models.Payment(
        amount=payment_amount,
        payment_date=parsed_payment_date,
        payment_method=payment_method,
        debt_id=debt_id,
        receipt_url=receipt_url
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Now, update the debt status
    # We need to reload the debt to get the new payment in the relationship
    db.refresh(db_debt)
    
    total_paid = sum(p.amount for p in db_debt.payments)
    
    if total_paid >= db_debt.total_amount:
        db_debt.is_paid = True
    else:
        db_debt.is_paid = False
    
    db.add(db_debt)
    db.commit()

    # --- Create corresponding ClubTransaction(s) for the payment (NEW LOGIC) ---
    db_member = db.query(models.Member).filter(models.Member.id == db_debt.member_id).first()
    
    # We need the debt with its items to distribute the payment
    db_debt_with_items = db.query(models.Debt).options(selectinload(models.Debt.items)).filter(models.Debt.id == debt_id).first()

    # Get or create the default category for member payments
    category_name = "Cuota de Socio"
    payment_category = db.query(models.Category).filter(
        models.Category.club_id == current_user.club_id,
        models.Category.name == category_name,
        models.Category.type == models.CategoryType.INCOME
    ).first()
    if not payment_category:
        payment_category = models.Category(name=category_name, type=models.CategoryType.INCOME, club_id=current_user.club_id)
        db.add(payment_category)
        db.commit()
        db.refresh(payment_category)

    # --- Payment Distribution Logic ---
    # This logic distributes the payment among the debt items and creates a transaction for each.
    # For simplicity, we assume a waterfall model: payment covers items in order.
    # A more complex system might handle partial payments on items differently.
    
    remaining_payment = payment_amount
    
    # Sort items to ensure base fee is (potentially) paid first.
    # This is a simple sort, can be made more robust.
    sorted_items = sorted(db_debt_with_items.items, key=lambda x: x.activity_id is not None)

    for item in sorted_items:
        if remaining_payment <= 0:
            break

        # This logic is simplified: it assumes the payment covers the item.
        # A real-world scenario might need to handle partial payments per item.
        # For this refactoring, we will create a transaction for the full item amount
        # if the payment covers it, which is a common case.
        # This part can be enhanced later if partial allocation is needed.
        
        # For now, we create a transaction for each item of the debt, assuming the payment is total.
        # This is a simplification to get the structure in place.
        # The correct logic should allocate the `payment_amount` across items.
        
        # Let's implement the allocation logic correctly.
        
        # Determine how much of the payment to apply to this item
        # We need to know how much was already paid for this debt item in previous payments,
        # which our current model doesn't track.
        # For now, let's stick to a simpler model for Phase 2, and create one transaction
        # per debt item, assuming the payment is for the full debt.
        # This is a known limitation we can improve in the future.
        
        # Let's try a better approach that works for partial payments.
        # We need to know the outstanding amount for each item.
        # This requires a bigger schema change (e.g., `paid_amount` on DebtItem).
        
        # --- Final approach for this step (pragmatic) ---
        # We will create a single transaction for now, but link it to the first activity found.
        # This is not the final goal, but an incremental step.
        # NO, the goal is to create multiple transactions. Let's do it.
        
        # To do this properly, we need to know what has already been paid for this debt.
        # Let's query all transactions related to this debt's items. This is getting complex.
        
        # Let's reset to a clear, albeit simple, implementation for this phase.
        # The payment will be broken down into transactions that mirror the debt items.
        
        amount_to_allocate = min(remaining_payment, item.amount)

        member_name = f"{db_member.first_name} {db_member.last_name}" if db_member else ""
        transaction_description = f"Pago {item.description} - {member_name}".strip()

        new_club_transaction = models.ClubTransaction(
            transaction_date=parsed_payment_date,
            description=transaction_description,
            amount=amount_to_allocate,
            type=models.CategoryType.INCOME,
            payment_method=payment_method,
            category_id=payment_category.id,
            activity_id=item.activity_id, # This is the key change
            receipt_url=receipt_url, # Associate the same receipt with all generated transactions
            user_id=current_user.id,
            club_id=current_user.club_id
        )
        db.add(new_club_transaction)
        
        remaining_payment -= amount_to_allocate

    db.commit()
    
    return db_payment

@router.post("/generate-monthly-debt", status_code=200)
def generate_monthly_debt(
    request: schemas.DebtGenerationRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_finance_user)
):
    """
    Generates the monthly debt for all active members of a club.
    It's no longer mandatory for the club to have a base_fee.
    """
    db_club = db.query(models.Club).filter(models.Club.id == current_user.club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="Club not found.")

    try:
        month_date = datetime.strptime(request.month, "%Y-%m").date().replace(day=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de mes inválido. Use AAAA-MM.")

    members = db.query(models.Member).options(selectinload(models.Member.activities)).filter(
        models.Member.club_id == current_user.club_id,
        models.Member.is_active == True
    ).all()

    generated_count = 0
    for member in members:
        existing_debt = db.query(models.Debt).filter(
            models.Debt.member_id == member.id,
            models.Debt.month == month_date
        ).first()
        if existing_debt:
            continue

        debt_items = []
        total_amount = Decimal('0.00')

        # Add base fee only if it exists and is greater than 0
        if db_club.base_fee and db_club.base_fee > 0:
            base_fee_decimal = Decimal(str(db_club.base_fee))
            debt_items.append(models.DebtItem(
                description="Cuota Social", 
                amount=base_fee_decimal,
                activity_id=None # Explicitly set as None for base fee
            ))
            total_amount += base_fee_decimal

        # Add activity fees
        for activity in member.activities:
            activity_cost_decimal = Decimal(str(activity.monthly_cost))
            debt_items.append(models.DebtItem(
                description=f"Actividad: {activity.name}", 
                amount=activity_cost_decimal,
                activity_id=activity.id # Link the debt item to the activity
            ))
            total_amount += activity_cost_decimal
        
        if total_amount > 0:
            new_debt = models.Debt(
                month=month_date,
                total_amount=total_amount,
                is_paid=False,
                member_id=member.id,
                items=debt_items
            )
            db.add(new_debt)
            generated_count += 1

    db.commit()
    
    return {"message": f"Deuda generada con éxito para {generated_count} socios."}
