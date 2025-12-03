from __future__ import annotations

from fastapi import APIRouter

from app.schemas.email import EmailRequest, SendEmailResponseStatus
from app.services.email import send_email

router = APIRouter()


@router.post("/", response_model=SendEmailResponseStatus)
async def send_email_endpoint(request: EmailRequest):
    return await send_email(request)
