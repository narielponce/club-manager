from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os

from .. import models, schemas, security
from ..database import get_db
from ..security import get_current_user, get_current_admin_user, get_password_hash

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
async def create_user(
    club_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_superadmin_user)
):
    # --- DEBUG PRINTS ---
    print(f"--- DEBUG: Received request to create club '{club_name}'.")
    print(f"--- DEBUG: Logo object received: {logo}")
    if logo:
        print(f"--- DEBUG: Logo filename: {logo.filename}, Content-Type: {logo.content_type}")
    # --- END DEBUG PRINTS ---

    # Basic email validation
    if '@' not in email or len(email.split('@')[1]) == 0:
        raise HTTPException(status_code=400, detail="Invalid email format")

    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Extract domain and check if a club with a similar name exists
    email_domain = email.split('@')[1]
    db_club = db.query(models.Club).filter(models.Club.name == club_name).first()
    if db_club:
        raise HTTPException(status_code=400, detail="Club name already registered")

    logo_url = None
    if logo:
        print("--- DEBUG: Entering 'if logo:' block to process file.") # DEBUG
        UPLOAD_DIR = "uploads/logos"
        print(f"--- DEBUG: UPLOAD_DIR resolved to: {UPLOAD_DIR}") # DEBUG
        
        try:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            print(f"--- DEBUG: Directory '{UPLOAD_DIR}' ensured.") # DEBUG
        except Exception as e:
            print(f"--- DEBUG: Error creating directory: {e}") # DEBUG
            raise HTTPException(status_code=500, detail=f"Failed to create upload directory: {e}")

        file_extension = os.path.splitext(logo.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        print(f"--- DEBUG: Full file_path: {file_path}") # DEBUG
        
        try:
            # Save the file
            with open(file_path, "wb") as buffer:
                buffer.write(await logo.read())
            print(f"--- DEBUG: File '{unique_filename}' written successfully.") # DEBUG
            logo_url = file_path
        except Exception as e:
            print(f"--- DEBUG: Error writing file: {e}") # DEBUG
            raise HTTPException(status_code=500, detail=f"Failed to write file: {e}")
    else:
        print("--- DEBUG: 'if logo:' block was skipped. Logo is None or False.") # DEBUG

    # Create the new club with the extracted domain and logo URL
    new_club = models.Club(name=club_name, email_domain=email_domain, logo_url=logo_url)
    db.add(new_club)
    db.commit()
    db.refresh(new_club)

    # Create the admin user for the new club
    hashed_password = get_password_hash(password)
    new_user = models.User(
        email=email,
        hashed_password=hashed_password,
        club_id=new_club.id,
        role="admin"  # Assign 'admin' role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    """
    Get current logged in user.
    """
    return current_user

@router.get("/club/users/", response_model=List[schemas.User])
def get_club_users(db: Session = Depends(get_db), current_admin: schemas.User = Depends(get_current_admin_user)):
    """
    Get all users for the admin's club.
    """
    return db.query(models.User).filter(models.User.club_id == current_admin.club_id).all()

@router.post("/club/users/", response_model=schemas.User, status_code=201)
def create_user_by_admin(user_in: schemas.UserCreateByAdmin, db: Session = Depends(get_db), current_admin: schemas.User = Depends(get_current_admin_user)):
    """
    Create a new user for the admin's club.
    The email is constructed from the local part and the club's domain.
    """
    # 1. Get the club's domain
    db_club = db.query(models.Club).filter(models.Club.id == current_admin.club_id).first()
    if not db_club or not db_club.email_domain:
        raise HTTPException(status_code=400, detail="El dominio del email no está configurado para este club.")

    # 2. Construct the full email
    full_email = f"{user_in.email_local_part}@{db_club.email_domain}"

    # 3. Check if the constructed email already exists
    user_exists = db.query(models.User).filter(
        models.User.club_id == current_admin.club_id,
        models.User.email == full_email
    ).first()
    if user_exists:
        raise HTTPException(status_code=400, detail=f"El email '{full_email}' ya está registrado en este club.")

    # 4. Create the new user
    hashed_password = get_password_hash(user_in.password)
    new_user = models.User(
        email=full_email,
        hashed_password=hashed_password,
        role=user_in.role,
        club_id=current_admin.club_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/club/users/{user_id}", response_model=schemas.User)
def update_user_by_admin(user_id: int, user_in: schemas.UserUpdateByAdmin, db: Session = Depends(get_db), current_admin: schemas.User = Depends(get_current_admin_user)):
    """
    Update a user's role or status in the admin's club.
    """
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.club_id == current_admin.club_id
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

@router.delete("/club/users/{user_id}", status_code=204)
def delete_user_by_admin(user_id: int, db: Session = Depends(get_db), current_admin: schemas.User = Depends(get_current_admin_user)):
    """
    Soft delete a user in the admin's club.
    """
    # Prevent an admin from deleting themselves
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Admin users cannot delete themselves")

    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.club_id == current_admin.club_id
    ).first()

    if db_user:
        db_user.is_active = False
        db.commit()
    
    return
