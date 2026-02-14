from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import require_roles, get_current_user

router = APIRouter(
    prefix="/club",
    tags=["club"],
    dependencies=[Depends(require_roles(['admin']))],
)

@router.get("/settings", response_model=schemas.Club)
def get_club_settings(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get the current admin's club settings.
    """
    return db.query(models.Club).filter(models.Club.id == current_user.club_id).first()

@router.put("/settings", response_model=schemas.Club)
def update_club_settings(
    club_in: schemas.ClubUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Update the current admin's club settings (e.g., base_fee).
    """
    db_club = db.query(models.Club).filter(models.Club.id == current_user.club_id).first()
    
    db_club.base_fee = club_in.base_fee
    
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club
