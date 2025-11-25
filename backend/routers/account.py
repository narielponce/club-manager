from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import os # For frontend URL from environment

from .. import models, schemas, security
from ..database import get_db
from ..security import get_current_user, verify_password, get_password_hash, create_reset_token
from ..email_service import send_email_async # Import the async email sender

router = APIRouter(
    prefix="/account",
    tags=["account"],
)

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Allows a logged-in user to change their password.
    If 'force_password_change' was true, it will be set to false.
    """
    # If a forced password change is required, bypass current password verification
    if current_user.force_password_change:
        if not password_data.new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be empty")
        # Proceed with new password
    else:
        # For regular password change, current_password is required
        if not password_data.current_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is required")
        
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    # Hash new password
    hashed_new_password = get_password_hash(password_data.new_password)
    current_user.hashed_password = hashed_new_password
    current_user.force_password_change = False # Password changed, no longer forced

    # Clear any reset tokens if they exist (password was changed via normal means)
    current_user.password_reset_token = None
    current_user.password_reset_expires = None

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Password updated successfully"}


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    request: schemas.PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Initiates the password reset process. Sends a reset link to the user's recovery email.
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user:
        # Prevent email enumeration: return generic success message even if user not found
        # Or, log the attempt.
        print(f"Password reset requested for non-existent user: {request.email}")
        return {"message": "If an account with that email exists, a password reset email has been sent."}

    if not user.recovery_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a recovery email configured. Please contact support."
        )

    # Generate token and set expiry
    token_plain = create_reset_token()
    user.password_reset_token = security.get_password_hash(token_plain) # Store hashed token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1) # Token valid for 1 hour
    
    db.add(user)
    db.commit()
    db.refresh(user)

    # Construct frontend reset URL
    # FRONTEND_URL should be set in .env for production
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173") # Default for local dev
    reset_link = f"{FRONTEND_URL}/reset-password?token={token_plain}"

    # Send email
    subject = "Restablecer tu Contraseña de Club Manager"
    body = f"""Hola {user.email.split('@')[0]},

Has solicitado restablecer tu contraseña para Club Manager.

Haz clic en el siguiente enlace para establecer una nueva contraseña:
{reset_link}

Este enlace es válido por 1 hora. Si no solicitaste este cambio, por favor ignora este correo.

Saludos,
El equipo de Club Manager
"""
    await send_email_async(
        recipients=[user.recovery_email],
        subject=subject,
        body=body,
        background_tasks=background_tasks
    )

    return {"message": "If an account with that email exists, a password reset email has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    password_data: schemas.PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Resets the user's password using a valid reset token.
    """
    # Find user by hashed token
    # Note: We store the hash of the token, so we need to iterate and verify
    users_with_tokens = db.query(models.User).filter(models.User.password_reset_token.isnot(None)).all()
    user = None
    for u in users_with_tokens:
        if security.verify_password(password_data.token, u.password_reset_token): # Verify plain token against stored hash
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    # Check token expiry
    if user.password_reset_expires < datetime.utcnow():
        # Invalidate token
        user.password_reset_token = None
        user.password_reset_expires = None
        db.add(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )
    
    # Hash new password
    hashed_new_password = get_password_hash(password_data.new_password)
    user.hashed_password = hashed_new_password
    user.force_password_change = False # Password changed via reset, no longer forced

    # Invalidate token after use
    user.password_reset_token = None
    user.password_reset_expires = None

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Password has been reset successfully."}