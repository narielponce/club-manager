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

    # --- Create corresponding ClubTransaction (Income) ---
    db_member = db.query(models.Member).filter(models.Member.id == db_debt.member_id).first()
    if db_member:
        description = f"Pago de cuota de {db_member.first_name} {db_member.last_name} ({db_member.email})"
    else:
        description = f"Pago de cuota (Deuda ID: {debt_id})"
    
    # Get or create the default category for member payments
    category_name = "Cuota de Socio"
    payment_category = db.query(models.Category).filter(
        models.Category.club_id == current_user.club_id,
        models.Category.name == category_name,
        models.Category.type == models.CategoryType.INCOME
    ).first()
    
    if not payment_category:
        payment_category = models.Category(
            name=category_name,
            type=models.CategoryType.INCOME,
            club_id=current_user.club_id
        )
        db.add(payment_category)
        db.commit()
        db.refresh(payment_category)
    
    new_club_transaction = models.ClubTransaction(
        transaction_date=parsed_payment_date,
        description=description,
        amount=payment_amount,
        type=models.CategoryType.INCOME,
        category_id=payment_category.id,
        receipt_url=receipt_url,
        user_id=current_user.id,
        club_id=current_user.club_id
    )
    db.add(new_club_transaction)
    db.commit()
    db.refresh(new_club_transaction)
    
    return db_payment

@router.post("/generate-monthly-debt", status_code=200)
def generate_monthly_debt(
    request: schemas.DebtGenerationRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_finance_user)
):
    """
    Generates the monthly debt for all active members of a club.
    """
    db_club = db.query(models.Club).filter(models.Club.id == current_user.club_id).first()
    if not db_club or db_club.base_fee is None:
        raise HTTPException(status_code=400, detail="La cuota social base no está configurada para el club. Por favor, configúrela primero.")

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
        total_amount = Decimal('0.00') # Initialize as Decimal

        # Add base fee
        if db_club.base_fee is not None:
            base_fee_decimal = Decimal(str(db_club.base_fee)) # Convert to Decimal
            debt_items.append(models.DebtItem(description="Cuota Social", amount=base_fee_decimal))
            total_amount += base_fee_decimal

        # Add activity fees
        for activity in member.activities:
            activity_cost_decimal = Decimal(str(activity.monthly_cost)) # Convert to Decimal
            debt_items.append(models.DebtItem(description=f"Actividad: {activity.name}", amount=activity_cost_decimal))
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
