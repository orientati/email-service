from __future__ import annotations

from pydantic import BaseModel, EmailStr


class SendEmail(BaseModel):
    to: EmailStr
    subject: str
    body: str


class SendEmailResponseStatus(BaseModel):
    code: int
    message: str
    detail: str
