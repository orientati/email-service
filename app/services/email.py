from __future__ import annotations

import logging
from pathlib import Path

from fastapi.templating import Jinja2Templates
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.email import EmailRequest, SendEmailResponseStatus

logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]  # recupera la directory principale dell'applicazione
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))  # Imposta la directory dei template

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

fast_mail = FastMail(conf)


async def send_email(request: EmailRequest) -> SendEmailResponseStatus:
    template = templates.get_template(
        f"{request.template_name}.html")  # Carica il template Jinja2 specificato dalla richiesta

    if not template:
        raise ValueError(f"Template {request.template_name} not found")

    html_content = template.render(**request.context)  # Rederizza il template con il contesto fornito

    message = MessageSchema(
        subject=request.subject,
        recipients=[request.to],
        body=html_content,
        subtype=MessageType.html
    )

    # Invia l'email in modo asincrono
    await fast_mail.send_message(message)

    return SendEmailResponseStatus(
        code=200,
        message="Email sent successfully",
        detail=f"Email sent to {request.to} using template {request.template_name}"
    )
