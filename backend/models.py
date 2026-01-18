import enum
from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, String, Enum as SQLAlchemyEnum, Date, Numeric, Table, Float, DateTime
)
from sqlalchemy.orm import relationship

from .database import Base

# Association Table for Member <-> Activity
member_activity_association = Table(
    "member_activity",
    Base.metadata,
    Column("member_id", Integer, ForeignKey("members.id"), primary_key=True),
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
)

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    base_fee = Column(Float, nullable=True)
    email_domain = Column(String, nullable=True) # Domain for club emails, e.g., 'example.com'
    logo_url = Column(String, nullable=True) # URL or path to the club's logo
    is_active = Column(Boolean, default=True, index=True)

    users = relationship("User", back_populates="club")
    members = relationship("Member", back_populates="club")
    activities = relationship("Activity", back_populates="club")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(SQLAlchemyEnum("admin", "tesorero", "comision", "profesor", "socio", "superadmin", name="user_roles"), nullable=False)

    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=True)
    club = relationship("Club", back_populates="users")

    # New fields for password recovery and forced change
    recovery_email = Column(String, nullable=True)
    force_password_change = Column(Boolean, default=False)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    monthly_cost = Column(Numeric(10, 2), nullable=False)

    club_id = Column(Integer, ForeignKey("clubs.id"))
    club = relationship("Club", back_populates="activities")

    profesor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    profesor = relationship("User")

    members = relationship(
        "Member",
        secondary=member_activity_association,
        back_populates="activities"
    )

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    email = Column(String, index=True)
    phone = Column(String, nullable=True)
    dni = Column(String, index=True, nullable=True)
    birth_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    club_id = Column(Integer, ForeignKey("clubs.id"))
    club = relationship("Club", back_populates="members")
    

    activities = relationship(
        "Activity",
        secondary=member_activity_association,
        back_populates="members"
    )
    debts = relationship("Debt", back_populates="member", cascade="all, delete-orphan")

class Payment(Base):

    __tablename__ = "payments"



    id = Column(Integer, primary_key=True, index=True)

    amount = Column(Numeric(10, 2), nullable=False)

    payment_date = Column(Date, nullable=False)

    payment_method = Column(String, nullable=True)

    receipt_url = Column(String, nullable=True)



    debt_id = Column(Integer, ForeignKey("debts.id"), nullable=False)

    debt = relationship("Debt", back_populates="payments")

class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Date, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    is_paid = Column(Boolean, default=False, index=True)

    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    member = relationship("Member", back_populates="debts")
    
    items = relationship("DebtItem", back_populates="debt", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="debt")

# --- New Models for Club Finances ---
class CategoryType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    type = Column(SQLAlchemyEnum(CategoryType, name="category_type_enum", values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False)

    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    club = relationship("Club")

    transactions = relationship("ClubTransaction", back_populates="category")

class ClubTransaction(Base):
    __tablename__ = "club_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(SQLAlchemyEnum(CategoryType, name="category_type_enum", values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False)
    payment_method = Column(String, nullable=True)
    receipt_url = Column(String, nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="transactions")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")

    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    club = relationship("Club")

    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    activity = relationship("Activity")

class DebtItem(Base):
    __tablename__ = "debt_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    
    debt_id = Column(Integer, ForeignKey("debts.id"), nullable=False)
    debt = relationship("Debt", back_populates="items")

    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    activity = relationship("Activity")
