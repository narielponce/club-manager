from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload, joinedload
from typing import List

from .. import models, schemas
from ..database import get_db
from ..security import get_current_admin_user, require_roles, get_current_user

router = APIRouter(
    prefix="/activities",
    tags=["activities"],
)

@router.get("/", response_model=List[schemas.Activity], dependencies=[Depends(require_roles(['admin', 'profesor']))])
def get_activities(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    """
    Get all activities for the current user's club.
    Accessible by admin and profesor.
    """
    return db.query(models.Activity).options(selectinload(models.Activity.profesor)).filter(models.Activity.club_id == current_user.club_id).all()

@router.post("/", response_model=schemas.Activity, status_code=201, dependencies=[Depends(get_current_admin_user)])
def create_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    """
    Create a new activity for the current user's club (Admin only).
    """
    if activity.profesor_id:
        profesor = db.query(models.User).filter(
            models.User.id == activity.profesor_id,
            models.User.club_id == current_user.club_id,
            models.User.role == 'profesor'
        ).first()
        if not profesor:
            raise HTTPException(status_code=400, detail=f"Profesor with id {activity.profesor_id} not found or invalid role.")

    db_activity = models.Activity(**activity.model_dump(), club_id=current_user.club_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.put("/{activity_id}", response_model=schemas.Activity, dependencies=[Depends(get_current_admin_user)])
def update_activity(activity_id: int, activity_in: schemas.ActivityCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    """
    Update an activity's details (Admin only).
    """
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.club_id == current_user.club_id
    ).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found in this club")
    
    update_data = activity_in.model_dump(exclude_unset=True)

    if 'profesor_id' in update_data and update_data['profesor_id'] is not None:
        profesor = db.query(models.User).filter(
            models.User.id == update_data['profesor_id'],
            models.User.club_id == current_user.club_id,
            models.User.role == 'profesor'
        ).first()
        if not profesor:
            raise HTTPException(status_code=400, detail=f"Profesor with id {update_data['profesor_id']} not found or invalid role.")

    for key, value in update_data.items():
        setattr(db_activity, key, value)
    
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.delete("/{activity_id}", status_code=204, dependencies=[Depends(get_current_admin_user)])
def delete_activity(activity_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    """
    Delete an activity (Admin only).
    """
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.club_id == current_user.club_id
    ).first()
    if db_activity:
        db.delete(db_activity)
        db.commit()
    return

@router.get("/{activity_id}/records", response_model=List[schemas.ClassRecord], dependencies=[Depends(require_roles(['admin', 'profesor']))])
def get_activity_class_records(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all class records for a specific activity in the current club.
    """
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.club_id == current_user.club_id
    ).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    # Check if professor is assigned to this activity
    if current_user.role == 'profesor' and db_activity.profesor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this activity's records")

    return db.query(models.ClassRecord).options(joinedload(models.ClassRecord.member)).filter(models.ClassRecord.activity_id == activity_id).all()

@router.post("/{activity_id}/records", response_model=schemas.ClassRecord, status_code=201, dependencies=[Depends(require_roles(['admin', 'profesor']))])
def create_activity_class_record(
    activity_id: int,
    record: schemas.ClassRecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Log a class session/attendance for a student.
    """
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.club_id == current_user.club_id
    ).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if current_user.role == 'profesor' and db_activity.profesor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to log attendance for this activity")

    # Verify student exists in current club and is enrolled in this activity
    db_member = db.query(models.Member).filter(
        models.Member.id == record.member_id,
        models.Member.club_id == current_user.club_id
    ).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Verify registration in activity
    if db_activity not in db_member.activities:
        raise HTTPException(status_code=400, detail="Member is not enrolled in this activity")

    from decimal import Decimal
    hours_val = record.hours if record.hours is not None else 1.0
    calc_amount = Decimal(str(hours_val)) * db_activity.monthly_cost

    db_record = models.ClassRecord(
        member_id=record.member_id,
        activity_id=activity_id,
        date=record.date,
        notes=record.notes,
        hours=hours_val,
        amount=calc_amount
    )
    db.add(db_record)

    # Generate real-time debt if it's billed per class/session
    if db_activity.billing_type == 'per_class':
        debt_item = models.DebtItem(
            description=f"{db_activity.name} ({hours_val} Horas)",
            amount=calc_amount,
            activity_id=activity_id
        )
        new_debt = models.Debt(
            month=record.date,
            total_amount=calc_amount,
            is_paid=False,
            member_id=record.member_id,
            items=[debt_item]
        )
        db.add(new_debt)

    db.commit()
    db.refresh(db_record)
    
    # Reload with member details loaded
    db_record = db.query(models.ClassRecord).options(joinedload(models.ClassRecord.member)).filter(models.ClassRecord.id == db_record.id).first()
    return db_record

@router.delete("/records/{record_id}", status_code=204, dependencies=[Depends(require_roles(['admin', 'profesor']))])
def delete_class_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Remove a class session record.
    """
    db_record = db.query(models.ClassRecord).join(models.Activity).filter(
        models.ClassRecord.id == record_id,
        models.Activity.club_id == current_user.club_id
    ).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Class record not found")

    if current_user.role == 'profesor' and db_record.activity.profesor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this record")

    db.delete(db_record)
    db.commit()
    return
