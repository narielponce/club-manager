from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# The DATABASE_URL is now expected to be passed as an environment variable
# Example for local development (without Docker): "postgresql://clubuser:local123@localhost/clubdb"
# Example for Docker: "postgresql://clubuser:local123@db/clubdb"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://clubuser:local123@localhost/clubdb")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models to inherit from
class Base(DeclarativeBase):
    pass

# --- DB Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
