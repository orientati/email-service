from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.template import TemplateResponse, TemplateRequest
from app.services.template import template

router = APIRouter()


@router.get("/", response_model=TemplateResponse)
def template(request: TemplateRequest):
    return template(request)
