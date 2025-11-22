from __future__ import annotations

from app.schemas.template import TemplateRequest, TemplateResponse

def template(request: TemplateRequest) -> TemplateResponse:
    #db.add(user)
    #db.commit()
    #db.refresh(user)
    return TemplateResponse(
        message="Template works!",
        detail= {
            "ciao": "mondo"
        }
    )

