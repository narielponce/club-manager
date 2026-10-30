import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from starlette.background import BackgroundTasks

N8N_NEW_CLIENT_WEBHOOK_URL = os.getenv("N8N_NEW_CLIENT_WEBHOOK_URL")
N8N_WEBHOOK_SECRET = os.getenv("N8N_WEBHOOK_SECRET")


def _send_webhook_request(url: str, payload: dict, secret: str = None):
    """
    Realiza la petición HTTP POST al Webhook de n8n de manera síncrona dentro del background task.
    """
    try:
        data = json.dumps(payload, default=str).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ClubManager-FastAPI/1.0"
        }
        if secret:
            headers["X-Webhook-Secret"] = secret

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=12) as response:
            status = response.getcode()
            print(f"[INFO] Webhook n8n enviado con éxito. HTTP Status: {status}")
            return status
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Error HTTP al enviar webhook a n8n ({url}): {e.code} - {e.reason}")
    except Exception as e:
        print(f"[ERROR] Error al conectar con n8n ({url}): {e}")


def notify_new_client_created(
    club,
    user,
    temporary_password: str,
    background_tasks: BackgroundTasks = None
):
    """
    Envía un webhook a n8n con los datos del nuevo cliente (Club + Usuario Admin)
    para despachar el correo de bienvenida con la contraseña temporal.
    """
    webhook_url = os.getenv("N8N_NEW_CLIENT_WEBHOOK_URL")
    if not webhook_url:
        print("[WARNING] N8N_NEW_CLIENT_WEBHOOK_URL no configurada en el .env. Webhook omitido.")
        return

    frontend_url = os.getenv("FRONTEND_URL", "https://sociosass.raizdigital.com.ar").rstrip("/")
    login_url = f"{frontend_url}/login"

    recipient = user.recovery_email or user.email

    payload = {
        "event": "client_created",
        "timestamp": datetime.utcnow().isoformat(),
        "recipient_email": recipient,
        "temporary_password": temporary_password,
        "login_url": login_url,
        "club": {
            "id": club.id,
            "name": club.name,
            "tenant_type": club.tenant_type,
            "email_domain": club.email_domain,
            "logo_url": club.logo_url
        },
        "user": {
            "id": user.id,
            "email": user.email,
            "recovery_email": user.recovery_email,
            "role": user.role,
            "force_password_change": user.force_password_change
        }
    }

    secret = os.getenv("N8N_WEBHOOK_SECRET")

    if background_tasks:
        background_tasks.add_task(_send_webhook_request, webhook_url, payload, secret)
        print(f"[INFO] Tarea de webhook n8n programada en segundo plano para destinatario: {recipient}")
    else:
        _send_webhook_request(webhook_url, payload, secret)
