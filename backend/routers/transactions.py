from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
import os
import uuid

from .. import models, schemas
from ..database import get_db
from ..security import require_roles, get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(require_roles(['admin', 'tesorero']))],
)

@router.post("/", response_model=schemas.ClubTransaction, status_code=status.HTTP_201_CREATED)
async def create_club_transaction(
    transaction_date: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    type: schemas.CategoryType = Form(...),
    payment_method: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    receipt: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new club transaction (income or expense).
    """
    try:
        parsed_date = date.fromisoformat(transaction_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if category_id:
        db_category = db.query(models.Category).filter(
            models.Category.id == category_id,
            models.Category.club_id == current_user.club_id,
            models.Category.type == type # Ensure category type matches transaction type
        ).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found or does not match transaction type")

    receipt_url = None
    if receipt:
        upload_dir = "uploads/transactions"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(receipt.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_location = os.path.join(upload_dir, unique_filename)
        
        with open(file_location, "wb+") as file_object:
            file_object.write(await receipt.read())
        receipt_url = file_location

    db_transaction = models.ClubTransaction(
        transaction_date=parsed_date,
        description=description,
        amount=amount,
        type=type,
        payment_method=payment_method,
        category_id=category_id,
        receipt_url=receipt_url,
        user_id=current_user.id,
        club_id=current_user.club_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/", response_model=schemas.ClubTransactionPage)
def read_club_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    type: Optional[schemas.CategoryType] = None,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 10
):
    """
    Retrieve club transactions for the current user's club, with optional filters and pagination.
    """
    query = db.query(models.ClubTransaction).filter(
        models.ClubTransaction.club_id == current_user.club_id
    )

    if type:
        query = query.filter(models.ClubTransaction.type == type)
    if category_id:
        query = query.filter(models.ClubTransaction.category_id == category_id)
    if start_date:
        query = query.filter(models.ClubTransaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.ClubTransaction.transaction_date <= end_date)
    
    total = query.count()
    items = query.order_by(models.ClubTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}

@router.get("/balance", response_model=schemas.Balance)
def get_club_balance(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Calculate and return the total balance for the current user's club,
    including a breakdown by payment method.
    """
    # Query to get sum of amounts grouped by type and payment_method
    results = db.query(
        models.ClubTransaction.type,
        models.ClubTransaction.payment_method,
        func.sum(models.ClubTransaction.amount)
    ).filter(
        models.ClubTransaction.club_id == current_user.club_id
    ).group_by(
        models.ClubTransaction.type,
        models.ClubTransaction.payment_method
    ).all()

    breakdown = {}
    
    for type, payment_method, total_amount in results:
        # Use a default name if payment_method is None
        method_name = payment_method or "No Especificado"
        
        if method_name not in breakdown:
            breakdown[method_name] = 0.0
        
        amount = float(total_amount)
        if type == models.CategoryType.INCOME:
            breakdown[method_name] += amount
        else: # expense
            breakdown[method_name] -= amount
            
    # Calculate the grand total from the breakdown
    total_balance = sum(breakdown.values())
    
    return {"total": total_balance, "breakdown": breakdown}
