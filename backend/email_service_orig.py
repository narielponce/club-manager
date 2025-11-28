import os
from pathlib import Path
from typing import List, Optional

from pydantic import EmailStr, BaseModel
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.background import BackgroundTasks

# A simple Pydantic model for the configuration for better validation
class MailSettings(BaseModel):
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: Optional[str] = "Club Manager"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    TEMPLATE_FOLDER: Optional[Path] = None

# We determine if we are in development (using MailHog) or production
is_development = os.getenv("MAIL_SERVER") == "mailhog"

settings_data = {
    "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
    "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
    "MAIL_FROM": os.getenv("MAIL_FROM", "test@example.com"),
    "MAIL_PORT": int(os.getenv("MAIL_PORT", 1025)),
    "MAIL_SERVER": os.getenv("MAIL_SERVER", "mailhog"),
    "MAIL_FROM_NAME": os.getenv("MAIL_FROM_NAME", "Club Manager Support"),
    # For MailHog, STARTTLS and SSL_TLS should be False
    "MAIL_STARTTLS": False if is_development else bool(os.getenv("MAIL_STARTTLS", "True") == "True"),
    "MAIL_SSL_TLS": False if is_development else bool(os.getenv("MAIL_SSL_TLS", "False") == "True"),
    "TEMPLATE_FOLDER": Path(__file__).parent / 'email_templates',
}

# Use the Pydantic model to create the settings
mail_settings = MailSettings(**settings_data)

# Create the ConnectionConfig from the validated settings
conf = ConnectionConfig(
    **mail_settings.model_dump(),
    USE_CREDENTIALS=bool(mail_settings.MAIL_USERNAME),
    # For development with MailHog, we should not validate certs
    VALIDATE_CERTS=False if is_development else True 
)


fastmail = FastMail(conf)

async def send_email_async(
    recipients: List[EmailStr],
    subject: str,
    body: str,
    background_tasks: BackgroundTasks,
    subtype: MessageType = MessageType.plain
):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=subtype,
    )
    # Using background tasks to send email to avoid blocking the API response
    try:
        background_tasks.add_task(fastmail.send_message, message)
        print(f"INFO: Email sending task added for recipients: {recipients}")
    except Exception as e:
        print(f"ERROR: Failed to add email task to background: {e}")