from __future__ import annotations

from fastapi import APIRouter

from app.schemas.email import SendEmail, SendEmailResponseStatus

router = APIRouter()


from app.services.email import send_email

@router.post("/", response_model=SendEmailResponseStatus)
async def template(request: SendEmail):
    return await send_email(request)
