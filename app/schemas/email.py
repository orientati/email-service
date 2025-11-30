from __future__ import annotations

from pydantic import BaseModel, EmailStr


class SendEmail(BaseModel):
    to: EmailStr
    template_alias: str
    data: dict


class SendEmailResponseStatus(BaseModel):
    code: int
    message: str
    detail: str
