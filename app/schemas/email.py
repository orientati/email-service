from __future__ import annotations

from typing import Dict, Any

from pydantic import BaseModel, NameEmail


class EmailRequest(BaseModel):
    to: NameEmail
    subject: str
    template_name: str
    context: Dict[str, Any]


class SendEmailResponseStatus(BaseModel):
    code: int
    message: str
    detail: str
