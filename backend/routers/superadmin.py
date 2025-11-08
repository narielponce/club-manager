from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, security
from ..database import get_db

router = APIRouter(
    prefix="/superadmin",
    tags=["superadmin"],
    dependencies=[Depends(security.get_current_superadmin_user)],
)

@router.get("/clubs/", response_model=List[schemas.Club])
def get_all_clubs(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all clubs. By default, only active clubs are returned.
    """
    query = db.query(models.Club)
    if not include_inactive:
        query = query.filter(models.Club.is_active == True)
    return query.order_by(models.Club.name).all()

@router.put("/clubs/{club_id}", response_model=schemas.Club)
def update_club_by_superadmin(
    club_id: int,
    club_in: schemas.SuperadminClubUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a club's details (name, base_fee, is_active).
    """
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="Club not found")

    update_data = club_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_club, key, value)
    
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club

@router.delete("/clubs/{club_id}", status_code=204)
def deactivate_club_by_superadmin(
    club_id: int,
    db: Session = Depends(get_db)
):
    """
    Deactivate a club (soft delete).
    """
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not db_club:
        # Even if not found, return success to be idempotent
        return

    db_club.is_active = False
    db.add(db_club)
    db.commit()
    return
