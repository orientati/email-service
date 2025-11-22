from __future__ import annotations

from fastapi import APIRouter

from app.schemas.email import SendEmail, SendEmailResponseStatus

router = APIRouter()


@router.post("/", response_model=SendEmailResponseStatus)
def template(request: SendEmail):
    pass
