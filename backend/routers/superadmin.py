from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from .. import models, schemas, security
from ..database import get_db

from sqlalchemy import func

router = APIRouter(
    prefix="/superadmin",
    tags=["superadmin"],
    dependencies=[Depends(security.get_current_superadmin_user)],
)

@router.get("/clubs/", response_model=List[schemas.ClubWithMemberCount])
def get_all_clubs(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all clubs with their active member count.
    By default, only active clubs are returned.
    """
    query = db.query(
        models.Club,
        func.count(models.Member.id).label("member_count")
    ).outerjoin(models.Member, (models.Member.club_id == models.Club.id) & (models.Member.is_active == True))
    
    if not include_inactive:
        query = query.filter(models.Club.is_active == True)
    
    query = query.group_by(models.Club.id).order_by(models.Club.name)
    
    results = query.all()

    # Manually construct the response to match the Pydantic model
    clubs_with_counts = []
    for club, member_count in results:
        club_data = schemas.Club.from_orm(club).model_dump()
        club_data['member_count'] = member_count
        clubs_with_counts.append(schemas.ClubWithMemberCount(**club_data))

    return clubs_with_counts

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


@router.delete("/clubs/{club_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_superadmin_user)
):
    """
    Permanently delete a club and all of its associated data. This is an
    irreversible action.
    """
    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not club:
        return

    # Subqueries for efficiency
    member_ids_subquery = db.query(models.Member.id).filter(models.Member.club_id == club_id).subquery()
    debt_ids_subquery = db.query(models.Debt.id).filter(models.Debt.member_id.in_(member_ids_subquery)).subquery()

    # Delete related entities in order of dependency
    db.query(models.ClubTransaction).filter(models.ClubTransaction.club_id == club_id).delete(synchronize_session=False)
    db.query(models.Payment).filter(models.Payment.debt_id.in_(debt_ids_subquery)).delete(synchronize_session=False)
    db.query(models.DebtItem).filter(models.DebtItem.debt_id.in_(debt_ids_subquery)).delete(synchronize_session=False)
    db.query(models.Debt).filter(models.Debt.member_id.in_(member_ids_subquery)).delete(synchronize_session=False)

    members_to_clear = db.query(models.Member).filter(models.Member.id.in_(member_ids_subquery)).all()
    for member in members_to_clear:
        member.activities.clear()
    
    db.commit() # Commit association changes before deleting members

    db.query(models.Member).filter(models.Member.id.in_(member_ids_subquery)).delete(synchronize_session=False)
    db.query(models.Activity).filter(models.Activity.club_id == club_id).delete(synchronize_session=False)
    db.query(models.Category).filter(models.Category.club_id == club_id).delete(synchronize_session=False)
    db.query(models.User).filter(models.User.club_id == club_id).delete(synchronize_session=False)

    db.delete(club)
    db.commit()

    return


@router.post("/clubs/{club_id}/logo", response_model=schemas.Club)
async def upload_club_logo(
    club_id: int,
    logo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_superadmin_user)
):
    """
    Upload or update a club's logo.
    """
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="Club not found")

    # If there's an old logo, delete it from the filesystem
    if db_club.logo_url and os.path.exists(db_club.logo_url):
        try:
            os.remove(db_club.logo_url)
        except OSError:
            # Log this error if a logging system is in place
            pass

    UPLOAD_DIR = "uploads/logos"
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create upload directory: {e}")

    file_extension = os.path.splitext(logo.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await logo.read())
        logo_url = file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {e}")

    db_club.logo_url = logo_url
    db.add(db_club)
    db.commit()
    db.refresh(db_club)

    return db_club


@router.get("/clubs/{club_id}/users", response_model=List[schemas.User])
def get_users_for_club_by_superadmin(
    club_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all users for a specific club by ID.
    """
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    return db.query(models.User).filter(models.User.club_id == club_id).all()


@router.get("/clubs/{club_id}/admins", response_model=List[schemas.User])
def get_admin_users_for_club(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_superadmin_user)
):
    """
    Get all users with the 'admin' role for a specific club.
    """
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    admins = db.query(models.User).filter(
        models.User.club_id == club_id,
        models.User.role == 'admin'
    ).all()
    
    return admins


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user_by_superadmin(
    user_id: int,
    user_in: schemas.SuperadminUserUpdate,
    db: Session = Depends(get_db)
):
    """
    Allows a superadmin to update any user's details.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
