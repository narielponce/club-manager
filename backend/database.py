from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# IMPORTANT: Replace with your actual database URL
# Format: "postgresql://<user>:<password>@<host>/<dbname>"
SQLALCHEMY_DATABASE_URL = "postgresql://clubuser:local123@localhost/clubdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models to inherit from
class Base(DeclarativeBase):
    pass
