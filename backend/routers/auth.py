from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import os

from .. import schemas, models
from ..database import get_db
from ..security import verify_password, create_access_token, create_refresh_token
from ..schemas import TokenResponseWithForceChange, RefreshTokenRequest


router = APIRouter()

@router.post("/token", response_model=TokenResponseWithForceChange)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password, or user is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "force_password_change": user.force_password_change
    }

@router.post("/token/refresh", response_model=schemas.Token)
def refresh_access_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    SECRET_KEY = os.getenv("SECRET_KEY")
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=["HS256"])
        token_type = payload.get("type")
        if token_type != "refresh":
            raise credentials_exception
            
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None or not user.is_active:
        raise credentials_exception
        
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
