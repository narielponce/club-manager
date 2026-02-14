from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os

from .. import models, schemas, security
from ..database import get_db
from ..security import get_current_user, get_password_hash, create_random_string, require_roles
from ..email_service import email_service

router = APIRouter()

@router.get("/users/test")
def test_users_endpoint():
    return {"message": "Users endpoint test successful"}

@router.post("/users/", response_model=schemas.ClubCreationResponse)
async def create_user(
    club_name: str = Form(...),
    email: str = Form(...),
    recovery_email: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_superadmin_user),
    background_tasks: BackgroundTasks = None
):
    if '@' not in email or len(email.split('@')[1]) == 0:
        raise HTTPException(status_code=400, detail="Invalid email format for primary email")
    if '@' not in recovery_email or len(recovery_email.split('@')[1]) == 0:
        raise HTTPException(status_code=400, detail="Invalid email format for recovery email")

    existing_user_by_email = db.query(models.User).join(models.Club).filter(
        models.User.email == email,
        models.Club.is_active == True
    ).first()
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail="Primary email already registered with an active club")

    email_domain = email.split('@')[1]
    db_club = db.query(models.Club).filter(models.Club.name == club_name, models.Club.is_active == True).first()
    if db_club:
        raise HTTPException(status_code=400, detail="An active club with this name already exists.")

    logo_url = None
    if logo:
        UPLOAD_DIR = "uploads/logos"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_extension = os.path.splitext(logo.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await logo.read())
        logo_url = file_path

    new_club = models.Club(name=club_name, email_domain=email_domain, logo_url=logo_url)
    db.add(new_club)
    db.commit()
    db.refresh(new_club)

    temporary_password = create_random_string()
    hashed_password = get_password_hash(temporary_password)
    
    new_user = models.User(
        email=email,
        hashed_password=hashed_password,
        club_id=new_club.id,
        role="admin",
        recovery_email=recovery_email,
        force_password_change=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return schemas.ClubCreationResponse(
        club=new_club,
        admin_user=new_user,
        temporary_password=temporary_password
    )

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.get("/club/users/", response_model=List[schemas.User], dependencies=[Depends(require_roles(['admin']))])
def get_club_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return db.query(models.User).filter(models.User.club_id == current_user.club_id).all()

@router.post("/club/users/", response_model=schemas.User, status_code=201, dependencies=[Depends(require_roles(['admin']))])
def create_user_by_admin(user_in: schemas.UserCreateByAdmin, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_club = db.query(models.Club).filter(models.Club.id == current_user.club_id).first()
    if not db_club or not db_club.email_domain:
        raise HTTPException(status_code=400, detail="El dominio del email no está configurado para este club.")

    full_email = f"{user_in.email_local_part}@{db_club.email_domain}"

    user_exists = db.query(models.User).filter(
        models.User.club_id == current_user.club_id,
        models.User.email == full_email
    ).first()
    if user_exists:
        raise HTTPException(status_code=400, detail=f"El email '{full_email}' ya está registrado en este club.")

    hashed_password = get_password_hash(user_in.password)
    new_user = models.User(
        email=full_email,
        hashed_password=hashed_password,
        role=user_in.role,
        club_id=current_user.club_id,
        recovery_email=user_in.recovery_email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/club/users/{user_id}", response_model=schemas.User, dependencies=[Depends(require_roles(['admin']))])
def update_user_by_admin(user_id: int, user_in: schemas.UserUpdateByAdmin, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.club_id == current_user.club_id
    ).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found in this club")

    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/club/users/{user_id}", status_code=204, dependencies=[Depends(require_roles(['admin']))])
def delete_user_by_admin(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Admin users cannot delete themselves")

    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.club_id == current_user.club_id
    ).first()

    if db_user:
        db_user.is_active = False
        db.commit()
    
    return

@router.post("/club/users/{user_id}/change-password", status_code=204, dependencies=[Depends(require_roles(['admin']))])
def change_user_password_by_admin(
    user_id: int, 
    password_in: schemas.AdminPasswordChange,
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.club_id == current_user.club_id
    ).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found in this club")

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Admins cannot change their own password via this endpoint. Please use the 'Account' section.")

    db_user.hashed_password = get_password_hash(password_in.new_password)
    db_user.force_password_change = True
    
    db.add(db_user)
    db.commit()
    
    return
