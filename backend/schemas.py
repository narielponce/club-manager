from pydantic import BaseModel
from typing import List, Optional
import enum
from datetime import date

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
    club_id: int
    class Config:
        from_attributes = True

class Member(MemberBase):
    id: int
    is_active: bool
    activities: List[Activity] = []
    class Config:
        from_attributes = True

class MemberPage(BaseModel):
    items: List[Member]
    total: int

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

class UserCreateByAdmin(BaseModel):
    email_local_part: str
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
    email_domain: Optional[str] = None
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
