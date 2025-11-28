import os
from typing import List

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To
from pydantic import EmailStr
from starlette.background import BackgroundTasks


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM = os.getenv("SENDGRID_FROM", "no-reply@example.com")
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "My App")


class EmailService:

    def __init__(self):
        if not SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY no está configurada en el .env")
        self.sg = SendGridAPIClient(SENDGRID_API_KEY)

    async def send_email_async(
        self,
        recipients: List[EmailStr],
        subject: str,
        body: str,
        background_tasks: BackgroundTasks,
        is_html: bool = False
    ):

        message = Mail(
            from_email=Email(SENDGRID_FROM, SENDGRID_FROM_NAME),
            subject=subject,
            html_content=body if is_html else None,
            plain_text_content=body if not is_html else None,
        )

        for r in recipients:
            message.add_to(To(r))

        background_tasks.add_task(self._send_in_background, message)

        print(f"[INFO] Email SendGrid programado para {recipients}")

    def _send_in_background(self, message: Mail):
        try:
            response = self.sg.send(message)
            print(f"[INFO] SendGrid Status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Envío fallido: {e}")


email_service = EmailService()
