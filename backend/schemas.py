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
    superadmin = "superadmin"

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
    payment_method: Optional[str] = None
    receipt_url: Optional[str] = None

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

class SuperadminClubUpdate(BaseModel):
    name: Optional[str] = None
    base_fee: Optional[float] = None
    is_active: Optional[bool] = None

class Club(BaseModel):
    id: int
    name: str
    base_fee: Optional[float] = None
    email_domain: Optional[str] = None
    logo_url: Optional[str] = None # URL or path to the club's logo
    is_active: bool
    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole
    club: Optional[Club] = None
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
    activity_id: Optional[int] = None

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

# --- Schemas for Member Account Statement ---
class TransactionType(str, enum.Enum):
    DEBT = "debt"
    PAYMENT = "payment"

class StatementItem(BaseModel):
    transaction_date: date
    transaction_type: TransactionType
    concept: str
    amount: float
    balance: float
    debt_id: int

class MemberStatement(BaseModel):
    items: List[StatementItem]
    final_balance: float

# --- Schemas for Categories ---
class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class CategoryBase(BaseModel):
    name: str
    type: CategoryType

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[CategoryType] = None

class Category(CategoryBase):
    id: int
    club_id: int
    class Config:
        from_attributes = True

# --- Schemas for Club Transactions ---
class ClubTransactionBase(BaseModel):
    transaction_date: date
    description: str
    amount: float
    type: CategoryType # Use CategoryType enum for transaction type
    payment_method: Optional[str] = None
    category_id: Optional[int] = None
    activity_id: Optional[int] = None
    receipt_url: Optional[str] = None

class ClubTransactionCreate(BaseModel):
    transaction_date: date
    description: str
    amount: float
    type: CategoryType
    category_id: Optional[int] = None # Category is optional for creation

class ClubTransaction(ClubTransactionBase):
    id: int
    user_id: int
    club_id: int
    activity: Optional[Activity] = None
    class Config:
        from_attributes = True

class ClubTransactionPage(BaseModel):
    items: List[ClubTransaction]
    total: int

class Balance(BaseModel):
    total: float
    breakdown: dict[str, float]
