from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from typing import List, Optional

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user, get_current_admin_user, require_roles

router = APIRouter(
    prefix="/members",
    tags=["members"],
)

@router.get("", response_model=schemas.MemberPage)
def get_all_members(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None
):
    """
    Get a paginated list of active members for the current user's club.
    Can be filtered by a search term matching DNI or last name.
    """
    query = db.query(models.Member).filter(
        models.Member.club_id == current_user.club_id,
        models.Member.is_active == True
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Member.first_name.ilike(search_term),
                models.Member.last_name.ilike(search_term),
                models.Member.dni == search
            )
        )

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return {"items": items, "total": total}

@router.post("", response_model=schemas.Member, status_code=201, dependencies=[Depends(require_roles(['admin']))])
def create_new_member(member_in: schemas.MemberCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_member_exists = db.query(models.Member).filter(
        models.Member.club_id == current_user.club_id,
        models.Member.email == member_in.email
    ).first()
    if db_member_exists:
        raise HTTPException(status_code=400, detail="Email already registered for this club")
    db_member = models.Member(**member_in.model_dump(), club_id=current_user.club_id)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.put("/{member_id}", response_model=schemas.Member, dependencies=[Depends(require_roles(['admin', 'tesorero']))])
def update_member(member_id: int, member_update: schemas.MemberUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.club_id == current_user.club_id
    ).first()
    if not db_member or not db_member.is_active:
        raise HTTPException(status_code=404, detail="Active member not found")
    update_data = member_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_member, key, value)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.delete("/{member_id}", status_code=204, dependencies=[Depends(get_current_admin_user)])
def delete_member(member_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    """Soft delete a member, ensuring the member belongs to the current user's club."""
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.club_id == current_user.club_id
    ).first()
    if not db_member:
        return
    db_member.is_active = False
    db.commit()
    return

@router.post("/{member_id}/activities/{activity_id}", response_model=schemas.Member, dependencies=[Depends(require_roles(['admin', 'profesor']))])
def add_activity_to_member(
    member_id: int,
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Enroll a member in an activity.
    """
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.club_id == current_user.club_id
    ).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found in this club")

    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if db_activity in db_member.activities:
        raise HTTPException(status_code=400, detail="Member is already enrolled in this activity")

    db_member.activities.append(db_activity)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.delete("/{member_id}/activities/{activity_id}", response_model=schemas.Member, dependencies=[Depends(require_roles(['admin', 'profesor']))])
def remove_activity_from_member(
    member_id: int,
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Un-enroll a member from an activity.
    """
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.club_id == current_user.club_id
    ).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found in this club")

    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if db_activity not in db_member.activities:
        raise HTTPException(status_code=400, detail="Member is not enrolled in this activity")

    db_member.activities.remove(db_activity)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.get("/{member_id}/debts/", response_model=List[schemas.Debt])
def get_debts_for_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get all debts for a specific member, ensuring the member belongs to the current user's club.
    """
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.club_id == current_user.club_id
    ).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found in this club")

    debts = db.query(models.Debt).options(
        selectinload(models.Debt.items),
        selectinload(models.Debt.payments)
    ).filter(models.Debt.member_id == member_id).order_by(models.Debt.month.desc()).all()
    
    return debts

@router.get("/{member_id}/statement/", response_model=schemas.MemberStatement)
def get_member_statement(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get a chronological account statement for a member, including debts and payments.
    """
    # 1. Verify member exists and belongs to the user's club
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.club_id == current_user.club_id
    ).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found in this club")

    # 2. Fetch all debts and associated payments for the member
    debts = db.query(models.Debt).options(
        selectinload(models.Debt.payments)
    ).filter(models.Debt.member_id == member_id).all()

    # 3. Create a unified list of transactions
    transactions = []
    for debt in debts:
        # Add the debt itself as a transaction
        concept = f"Deuda de {debt.month.strftime('%B %Y')}"
        transactions.append({
            "date": debt.month,
            "type": schemas.TransactionType.DEBT,
            "concept": concept,
            "amount": float(debt.total_amount),
            "debt_id": debt.id
        })
        # Add all payments for this debt as transactions
        for payment in debt.payments:
            transactions.append({
                "date": payment.payment_date,
                "type": schemas.TransactionType.PAYMENT,
                "concept": f"Pago (Recibo: {payment.id})",
                "amount": -float(payment.amount),
                "debt_id": debt.id
            })

    # 4. Sort transactions chronologically
    transactions.sort(key=lambda x: x["date"])

    # 5. Calculate running balance and create final statement items
    running_balance = 0.0
    statement_items = []
    for t in transactions:
        running_balance += t["amount"]
        statement_items.append(schemas.StatementItem(
            transaction_date=t["date"],
            transaction_type=t["type"],
            concept=t["concept"],
            amount=t["amount"],
            balance=running_balance,
            debt_id=t["debt_id"]
        ))

    return schemas.MemberStatement(items=statement_items, final_balance=running_balance)
