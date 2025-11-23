from __future__ import annotations

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.schemas.email import SendEmail, SendEmailResponseStatus
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

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

async def send_email(request: SendEmail) -> SendEmailResponseStatus:
    message = MessageSchema(
        subject=request.subject,
        recipients=[request.to],
        body=request.body,
        subtype=MessageType.html
    )

    try:
        await fast_mail.send_message(message)
        return SendEmailResponseStatus(
            code=200,
            message="Email sent successfully",
            detail="Email sent to " + request.to
        )
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return SendEmailResponseStatus(
            code=500,
            message="Failed to send email",
            detail=str(e)
        )
