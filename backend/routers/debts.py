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
    Create a payment for a specific debt, correctly allocating the payment across
    debt items and creating corresponding, correctly categorized club transactions.
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

    # --- Calculate amounts paid before this new payment ---
    total_previously_paid = sum(p.amount for p in db_debt.payments)

    # --- Handle Receipt Upload ---
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

    # --- Create and Save the Payment ---
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

    # --- Update Debt Paid Status ---
    db.refresh(db_debt)
    total_paid_after_current = sum(p.amount for p in db_debt.payments)
    db_debt.is_paid = total_paid_after_current >= db_debt.total_amount
    db.add(db_debt)

    # --- Payment Allocation and Club Transaction Creation ---
    db_member = db.query(models.Member).filter(models.Member.id == db_debt.member_id).first()
    sorted_items = sorted(db_debt.items, key=lambda x: x.activity_id is not None)
    
    remaining_current_payment = payment_amount
    outstanding_debt_tracker = total_previously_paid

    # Get or create categories
    social_fee_category, activity_income_category = get_or_create_payment_categories(db, current_user.club_id)

    for item in sorted_items:
        if remaining_current_payment <= 0:
            break

        already_covered = max(Decimal(0), outstanding_debt_tracker)
        item_outstanding = item.amount - already_covered
        
        if item_outstanding <= 0:
            outstanding_debt_tracker -= item.amount
            continue

        amount_to_allocate = min(remaining_current_payment, item_outstanding)

        if amount_to_allocate > 0:
            member_name = f"{db_member.first_name} {db_member.last_name}" if db_member else ""
            transaction_description = f"Pago {item.description} - {member_name}".strip()
            
            # Determine correct category
            category_id_to_use = social_fee_category.id if item.activity_id is None else activity_income_category.id

            new_club_transaction = models.ClubTransaction(
                transaction_date=parsed_payment_date,
                description=transaction_description,
                amount=amount_to_allocate,
                type=models.CategoryType.INCOME,
                payment_method=payment_method,
                category_id=category_id_to_use,
                activity_id=item.activity_id,
                receipt_url=receipt_url,
                user_id=current_user.id,
                club_id=current_user.club_id
            )
            db.add(new_club_transaction)
            remaining_current_payment -= amount_to_allocate
        
        outstanding_debt_tracker -= item.amount

    db.commit()
    return db_payment

def get_or_create_payment_categories(db: Session, club_id: int):
    """Gets or creates the default categories for social fees and activity income."""
    # For Social Fee
    social_fee_category = db.query(models.Category).filter(
        models.Category.club_id == club_id,
        models.Category.name == "Cuota de Socio",
        models.Category.type == models.CategoryType.INCOME
    ).first()
    if not social_fee_category:
        social_fee_category = models.Category(name="Cuota de Socio", type=models.CategoryType.INCOME, club_id=club_id)
        db.add(social_fee_category)
        db.commit()
        db.refresh(social_fee_category)

    # For Activity Income
    activity_income_category = db.query(models.Category).filter(
        models.Category.club_id == club_id,
        models.Category.name == "Ingreso por Actividades",
        models.Category.type == models.CategoryType.INCOME
    ).first()
    if not activity_income_category:
        activity_income_category = models.Category(name="Ingreso por Actividades", type=models.CategoryType.INCOME, club_id=club_id)
        db.add(activity_income_category)
        db.commit()
        db.refresh(activity_income_category)
        
    return social_fee_category, activity_income_category

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

@router.post("/debts/manual", response_model=schemas.Debt)
def create_manual_charge(
    charge_data: schemas.ManualChargeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Creates a manual charge for a member.
    - Admins/Tesoreros can create a charge for any member.
    - Profesors can only create a charge for a member enrolled in one of their activities.
    """
    member = db.query(models.Member).filter(
        models.Member.id == charge_data.member_id,
        models.Member.club_id == current_user.club_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Authorization check
    if current_user.role not in ['admin', 'tesorero']:
        if current_user.role == 'profesor':
            # Check if the member is a student of the professor
            professor_activities = db.query(models.Activity.id).filter(
                models.Activity.profesor_id == current_user.id
            ).all()
            professor_activity_ids = {activity_id for activity_id, in professor_activities}

            member_activities = {activity.id for activity in member.activities}
            
            if not professor_activity_ids.intersection(member_activities):
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to create a charge for this member. The member is not in any of your activities."
                )
        else:
            # Other roles are not permitted
            raise HTTPException(status_code=403, detail="Not authorized to perform this action.")

    month_date = charge_data.date.replace(day=1)
    charge_amount = Decimal(str(charge_data.amount))

    if charge_amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive.")

    # Find existing debt for the month
    db_debt = db.query(models.Debt).filter(
        models.Debt.member_id == charge_data.member_id,
        models.Debt.month == month_date
    ).first()

    if db_debt:
        # Debt exists, add new item
        new_debt_item = models.DebtItem(
            description=charge_data.description,
            amount=charge_amount,
            debt_id=db_debt.id,
            activity_id=None
        )
        db.add(new_debt_item)
        db_debt.total_amount += charge_amount
        db.add(db_debt)
    else:
        # Debt does not exist, create a new one
        new_debt = models.Debt(
            month=month_date,
            total_amount=charge_amount,
            is_paid=False,
            member_id=charge_data.member_id,
            items=[
                models.DebtItem(
                    description=charge_data.description,
                    amount=charge_amount,
                    activity_id=None
                )
            ]
        )
        db.add(new_debt)
        db_debt = new_debt
    
    db.commit()
    db.refresh(db_debt)
    
    return db_debt
