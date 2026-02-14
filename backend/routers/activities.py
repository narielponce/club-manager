from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List

from .. import models, schemas
from ..database import get_db
from ..security import require_roles, get_current_user

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

@router.post("/", response_model=schemas.Activity, status_code=201, dependencies=[Depends(require_roles(['admin']))])
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

@router.put("/{activity_id}", response_model=schemas.Activity, dependencies=[Depends(require_roles(['admin']))])
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

@router.delete("/{activity_id}", status_code=204, dependencies=[Depends(require_roles(['admin']))])
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
