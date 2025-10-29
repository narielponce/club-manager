import enum
from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, String, Enum as SQLAlchemyEnum, Date, Numeric, Table
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
    base_fee = Column(Numeric(10, 2), nullable=True)

    members = relationship("Member", back_populates="club")
    users = relationship("User", back_populates="club")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(SQLAlchemyEnum("admin", "tesorero", "comision", "profesor", "socio", name="user_roles"), nullable=False)

    club_id = Column(Integer, ForeignKey("clubs.id"))
    club = relationship("Club", back_populates="users")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    monthly_cost = Column(Numeric(10, 2), nullable=False)

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
    
    payments = relationship("Payment", back_populates="member", cascade="all, delete-orphan")
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
    month_covered = Column(Date, nullable=False)

    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    member = relationship("Member", back_populates="payments")

class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Date, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    is_paid = Column(Boolean, default=False, index=True)

    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    member = relationship("Member", back_populates="debts")
    items = relationship("DebtItem", back_populates="debt", cascade="all, delete-orphan")

class DebtItem(Base):
    __tablename__ = "debt_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    
    debt_id = Column(Integer, ForeignKey("debts.id"), nullable=False)
    debt = relationship("Debt", back_populates="items")
