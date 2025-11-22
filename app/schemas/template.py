from __future__ import annotations

from pydantic import BaseModel


class TemplateRequest(BaseModel):
    pass

class TemplateResponse(BaseModel):
    message: str
    detail: str | None = None