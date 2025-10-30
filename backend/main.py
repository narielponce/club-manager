from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
import os
import uuid
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
import enum
from sqlalchemy.orm import Session, selectinload
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone, date

from jose import JWTError, jwt
from passlib.context import CryptContext

from . import models, database

# This line creates the database tables if they don't exist
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- Security Utils (Inlined) ---
SECRET_KEY = "a_very_secret_key_that_should_be_in_env_vars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- CORS Middleware ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"], # Explicitly allow Authorization
)

# --- DB Dependency ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Schemas ---
class UserRole(str, enum.Enum):
    admin = "admin"
    tesorero = "tesorero"
    comision = "comision"
    profesor = "profesor"
    socio = "socio"

class MemberBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    dni: Optional[str] = None
    birth_date: Optional[date] = None

class MemberCreate(MemberBase):
    pass

class MemberUpdate(MemberBase):
    is_active: Optional[bool] = None

class ActivityBase(BaseModel):
    name: str
    monthly_cost: float

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    class Config:
        from_attributes = True

class Member(MemberBase):
    id: int
    is_active: bool
    activities: List[Activity] = []
    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    amount: float
    payment_date: date

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    debt_id: int
    receipt_url: Optional[str] = None

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    club_name: str


class UserCreateByAdmin(UserBase):
    password: str
    role: UserRole


class UserUpdateByAdmin(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class ClubUpdate(BaseModel):
    base_fee: float

class Club(BaseModel):
    id: int
    name: str
    base_fee: Optional[float] = None
    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole
    club: Club
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class DebtGenerationRequest(BaseModel):
    month: str # Expected format: YYYY-MM


# Schemas for Debt
class DebtItemBase(BaseModel):
    description: str
    amount: float

class DebtItem(DebtItemBase):
    id: int
    class Config:
        from_attributes = True

class DebtBase(BaseModel):
    month: date
    total_amount: float
    is_paid: bool

class Debt(DebtBase):
    id: int
    member_id: int
    items: List[DebtItem] = []
    payments: List[Payment] = []
    class Config:
        from_attributes = True


# --- Auth Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="The user does not have enough privileges")
    return current_user

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Club Manager API"}

@app.post("/users/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_club = db.query(models.Club).filter(models.Club.name == user_in.club_name).first()
    if db_club:
        raise HTTPException(status_code=400, detail="Club name already registered")
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_club = models.Club(name=user_in.club_name)
    db.add(new_club)
    db.commit()
    db.refresh(new_club)
    hashed_password = get_password_hash(user_in.password)
    new_user = models.User(
        email=user_in.email,
        hashed_password=hashed_password,
        club_id=new_club.id,
        role="admin"  # Assign 'admin' role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged in user.
    """
    return current_user

@app.get("/members", response_model=List[Member])
def get_all_members(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    members = db.query(models.Member).filter(
        models.Member.club_id == current_user.club_id,
        models.Member.is_active == True
    ).all()
    return members

@app.post("/members", response_model=Member, status_code=201)
def create_new_member(member_in: MemberCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

@app.put("/members/{member_id}", response_model=Member)
def update_member(member_id: int, member_update: MemberUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

@app.delete("/members/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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


# --- User Management Endpoints (Admin Only) ---

@app.get("/club/users/", response_model=List[User])
def get_club_users(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    Get all users for the admin's club.
    """
    return db.query(models.User).filter(models.User.club_id == current_admin.club_id).all()

@app.post("/club/users/", response_model=User, status_code=201)
def create_user_by_admin(user_in: UserCreateByAdmin, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    Create a new user for the admin's club.
    """
    user_exists = db.query(models.User).filter(
        models.User.club_id == current_admin.club_id,
        models.User.email == user_in.email
    ).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered for this club")

    hashed_password = get_password_hash(user_in.password)
    new_user = models.User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role,
        club_id=current_admin.club_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.put("/club/users/{user_id}", response_model=User)
def update_user_by_admin(user_id: int, user_in: UserUpdateByAdmin, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
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

@app.delete("/club/users/{user_id}", status_code=204)
def delete_user_by_admin(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
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


# --- Club Settings Endpoints (Admin Only) ---

@app.put("/club/settings", response_model=Club)
def update_club_settings(
    club_in: ClubUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Update the current admin's club settings (e.g., base_fee).
    """
    # The admin's user object has the club loaded, but we fetch it again
    # to ensure we are working with a fresh session-managed object.
    db_club = db.query(models.Club).filter(models.Club.id == current_admin.club_id).first()
    
    db_club.base_fee = club_in.base_fee
    
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club


# --- Debt & Payment Endpoints ---

@app.get("/members/{member_id}/debts/", response_model=List[Debt])
def get_debts_for_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    # Eager load items and payments for efficiency
    debts = db.query(models.Debt).options(
        selectinload(models.Debt.items),
        selectinload(models.Debt.payments)
    ).filter(models.Debt.member_id == member_id).order_by(models.Debt.month.desc()).all()
    
    return debts

@app.post("/debts/{debt_id}/payments/", response_model=Payment)
def create_payment_for_debt(
    debt_id: int,
    payment_date: str = Form(...),
    receipt: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a payment for a specific debt, upload a receipt, and mark the debt as paid.
    """
    # Verify the debt exists and belongs to the user's club
    db_debt = db.query(models.Debt).join(models.Member).filter(
        models.Debt.id == debt_id,
        models.Member.club_id == current_user.club_id
    ).first()

    if not db_debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    if db_debt.is_paid:
        raise HTTPException(status_code=400, detail="Debt is already paid")

    # Manually parse the date to avoid validation errors
    try:
        parsed_payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    receipt_url = None
    if receipt:
        # Ensure the uploads directory exists
        upload_dir = "uploads/receipts"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create a unique filename and save the file
        file_extension = receipt.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_location = os.path.join(upload_dir, unique_filename)
        
        with open(file_location, "wb+") as file_object:
            file_object.write(receipt.file.read())
        receipt_url = file_location

    # Create the payment record
    db_payment = models.Payment(
        amount=db_debt.total_amount,
        payment_date=parsed_payment_date,
        debt_id=debt_id,
        receipt_url=receipt_url
    )
    
    # Mark debt as paid
    db_debt.is_paid = True
    
    db.add(db_payment)
    db.add(db_debt)
    db.commit()
    db.refresh(db_payment)
    
    return db_payment




# --- Activity Endpoints (Admin Only) ---

@app.get("/activities/", response_model=List[Activity])
def get_activities(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    Get all activities.
    NOTE: For now, activities are global across all clubs.
    """
    return db.query(models.Activity).all()

@app.post("/activities/", response_model=Activity, status_code=201)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    Create a new activity.
    """
    db_activity = models.Activity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.put("/activities/{activity_id}", response_model=Activity)
def update_activity(activity_id: int, activity_in: ActivityCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    Update an activity's details.
    """
    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    update_data = activity_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_activity, key, value)
    
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.delete("/activities/{activity_id}", status_code=204)
def delete_activity(activity_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """
    Delete an activity.
    """
    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if db_activity:
        db.delete(db_activity)
        db.commit()
    return


# --- Member-Activity Association Endpoints (Admin Only) ---

@app.post("/members/{member_id}/activities/{activity_id}", response_model=Member)
def add_activity_to_member(
    member_id: int,
    activity_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Enroll a member in an activity.
    """
    # Verify the member exists and belongs to the admin's club
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.club_id == current_admin.club_id
    ).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found in this club")

    # Verify the activity exists
    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if already enrolled
    if db_activity in db_member.activities:
        raise HTTPException(status_code=400, detail="Member is already enrolled in this activity")

    db_member.activities.append(db_activity)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.delete("/members/{member_id}/activities/{activity_id}", response_model=Member)
def remove_activity_from_member(
    member_id: int,
    activity_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Un-enroll a member from an activity.
    """
    # Verify the member exists and belongs to the admin's club
    db_member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.club_id == current_admin.club_id
    ).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found in this club")

    # Verify the activity exists
    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if member is enrolled before trying to remove
    if db_activity not in db_member.activities:
        raise HTTPException(status_code=400, detail="Member is not enrolled in this activity")

    db_member.activities.remove(db_activity)
    db.commit()
    db.refresh(db_member)
    return db_member


# --- Debt Generation Endpoint (Admin Only) ---

@app.post("/generate-monthly-debt", status_code=200)
def generate_monthly_debt(
    request: DebtGenerationRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Generates the monthly debt for all active members of a club.
    This includes the base club fee and any activities the member is enrolled in.
    """
    # 1. Get the club and its base_fee
    db_club = db.query(models.Club).filter(models.Club.id == current_admin.club_id).first()
    if not db_club or db_club.base_fee is None:
        raise HTTPException(status_code=400, detail="La cuota social base no está configurada para el club. Por favor, configúrela primero.")

    # 2. Parse the month string
    try:
        month_date = datetime.strptime(request.month, "%Y-%m").date().replace(day=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de mes inválido. Use AAAA-MM.")

    # 3. Get all active members of the club, pre-loading their activities
    members = db.query(models.Member).options(selectinload(models.Member.activities)).filter(
        models.Member.club_id == current_admin.club_id,
        models.Member.is_active == True
    ).all()

    generated_count = 0
    for member in members:
        # 4. Check if debt for this month already exists for this member
        existing_debt = db.query(models.Debt).filter(
            models.Debt.member_id == member.id,
            models.Debt.month == month_date
        ).first()
        if existing_debt:
            continue # Skip if already generated

        # 5. Create DebtItems and calculate total
        debt_items = []
        total_amount = 0

        # Add base fee
        debt_items.append(models.DebtItem(description="Cuota Social", amount=db_club.base_fee))
        total_amount += db_club.base_fee

        # Add activity fees
        for activity in member.activities:
            debt_items.append(models.DebtItem(description=f"Actividad: {activity.name}", amount=activity.monthly_cost))
            total_amount += activity.monthly_cost
        
        # 6. Create the main Debt record if there is any amount to charge
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