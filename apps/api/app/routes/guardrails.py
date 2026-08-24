from fastapi import APIRouter
from pydantic import BaseModel

from app.services.guardrails import guardrails_service

router = APIRouter(prefix="/guardrails", tags=["guardrails"])


class GuardrailsCheckRequest(BaseModel):
    text: str
    check_type: str
    context: str | None = None


class GuardrailsCheckResponse(BaseModel):
    valid: bool
    output: str | None = None
    error: str | None = None


@router.post("/check", response_model=GuardrailsCheckResponse)
def check_guardrails(payload: GuardrailsCheckRequest) -> GuardrailsCheckResponse:
    """Run guardrails check on text"""
    if payload.check_type == "python":
        return guardrails_service.validate_python(payload.text)
    elif payload.check_type == "sql":
        return guardrails_service.validate_sql(payload.text)
    elif payload.check_type == "json":
        return guardrails_service.validate_json(payload.text)
    elif payload.check_type == "hallucination":
        if not payload.context:
            return GuardrailsCheckResponse(
                valid=False,
                error="Context required for hallucination check"
            )
        return guardrails_service.hallucination_check(payload.text, payload.context)
    elif payload.check_type == "toxic":
        return guardrails_service.toxic_content_check(payload.text)
    elif payload.check_type == "pii":
        return guardrails_service.pii_detection(payload.text)
    else:
        return GuardrailsCheckResponse(
            valid=False,
            error=f"Unknown check type: {payload.check_type}"
        )


class CustomGuardRequest(BaseModel):
    schema: dict
    text: str


@router.post("/custom", response_model=GuardrailsCheckResponse)
def check_custom_guard(payload: CustomGuardRequest) -> GuardrailsCheckResponse:
    """Run custom schema guardrails check"""
    guard = guardrails_service.create_custom_guard(payload.schema)
    return guardrails_service.validate_with_schema(guard, payload.text)
