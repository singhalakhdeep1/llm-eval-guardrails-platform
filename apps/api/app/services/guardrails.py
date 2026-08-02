# Guardrails AI integration for llm-eval-guardrails-platform

from guardrails import Guard
from guardrails.hub import ValidPython, ValidSQL, ValidJSON
from typing import Dict, Any, List
import os

class GuardrailsService:
    def __init__(self):
        self.api_key = os.getenv("GUARDRAILS_API_KEY")

    def create_guard(self, validators: List[str]):
        """Create a guard with specified validators"""
        validator_map = {
            "python": ValidPython(),
            "sql": ValidSQL(),
            "json": ValidJSON()
        }
        
        selected_validators = [validator_map[v] for v in validators if v in validator_map]
        return Guard().use_many(*selected_validators)

    def validate(self, guard: Guard, text: str):
        """Validate text against guard"""
        result = guard.parse(text)
        return {
            "valid": result.validation_passed,
            "output": result.validated_output if result.validation_passed else None,
            "error": result.error if not result.validation_passed else None
        }

    def validate_python(self, code: str):
        """Validate Python code"""
        guard = Guard().use(ValidPython())
        return self.validate(guard, code)

    def validate_sql(self, query: str):
        """Validate SQL query"""
        guard = Guard().use(ValidSQL())
        return self.validate(guard, query)

    def validate_json(self, json_string: str):
        """Validate JSON string"""
        guard = Guard().use(ValidJSON())
        return self.validate(guard, json_string)

    def create_custom_guard(self, schema: Dict[str, Any]):
        """Create a guard with custom schema"""
        guard = Guard.from_rail(schema)
        return guard

    def validate_with_schema(self, guard: Guard, text: str):
        """Validate text with custom schema guard"""
        result = guard.parse(text)
        return {
            "valid": result.validation_passed,
            "output": result.validated_output if result.validation_passed else None,
            "error": result.error if not result.validation_passed else None
        }

    def hallucination_check(self, text: str, context: str):
        """Check for hallucinations"""
        from guardrails.hub import HallucinationCheck
        guard = Guard().use(HallucinationCheck(context=context))
        return self.validate(guard, text)

    def toxic_content_check(self, text: str):
        """Check for toxic content"""
        from guardrails.hub import ToxicCheck
        guard = Guard().use(ToxicCheck())
        return self.validate(guard, text)

    def pii_detection(self, text: str):
        """Detect PII in text"""
        from guardrails.hub import PIIDetection
        guard = Guard().use(PIIDetection())
        return self.validate(guard, text)
