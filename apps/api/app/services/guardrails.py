"""Native guardrails checks — no third-party guardrails package required."""
from __future__ import annotations

import ast
import json
import re
from typing import Any


class GuardrailsService:
    def validate_python(self, code: str) -> dict[str, Any]:
        try:
            ast.parse(code)
            return {"valid": True, "output": code, "error": None}
        except SyntaxError as exc:
            return {"valid": False, "output": None, "error": str(exc)}

    def validate_sql(self, query: str) -> dict[str, Any]:
        stripped = query.strip().upper()
        if not stripped:
            return {"valid": False, "output": None, "error": "Empty SQL query"}
        valid_starts = (
            "SELECT", "INSERT", "UPDATE", "DELETE",
            "CREATE", "DROP", "ALTER", "WITH", "MERGE",
        )
        if not any(stripped.startswith(k) for k in valid_starts):
            return {
                "valid": False,
                "output": None,
                "error": "Query does not start with a recognised SQL keyword",
            }
        return {"valid": True, "output": query, "error": None}

    def validate_json(self, json_string: str) -> dict[str, Any]:
        try:
            parsed = json.loads(json_string)
            return {"valid": True, "output": json.dumps(parsed), "error": None}
        except json.JSONDecodeError as exc:
            return {"valid": False, "output": None, "error": str(exc)}

    def hallucination_check(self, text: str, context: str) -> dict[str, Any]:
        sentences = [s.strip() for s in re.split(r"[.!?]", text) if len(s.strip()) > 20]
        context_lower = context.lower()
        for sentence in sentences[:6]:
            words = [w for w in sentence.lower().split() if len(w) > 4]
            if words and not any(w in context_lower for w in words[:6]):
                return {
                    "valid": False,
                    "output": None,
                    "error": f"Potential hallucination — not grounded in context: '{sentence[:100]}'",
                }
        return {"valid": True, "output": text, "error": None}

    def toxic_content_check(self, text: str) -> dict[str, Any]:
        patterns = [
            r"\b(hate|kill|murder|terrorist|bomb|attack)\b",
            r"\b(racist|sexist|homophob\w*|transphob\w*)\b",
            r"\b(slur|abuse|threat|harassment)\b",
        ]
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return {
                    "valid": False,
                    "output": None,
                    "error": f"Potentially toxic content detected: '{match.group()}'",
                }
        return {"valid": True, "output": text, "error": None}

    def pii_detection(self, text: str) -> dict[str, Any]:
        pii_patterns: dict[str, str] = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            "phone": r"\b(?:\+?\d[\d\s\-(). ]{7,14}\d)\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b(?:\d[ -]?){13,16}\b",
            "aadhaar": r"\b\d{4}\s\d{4}\s\d{4}\b",
        }
        found: list[str] = []
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, text):
                found.append(pii_type)
        if found:
            return {
                "valid": False,
                "output": None,
                "error": f"PII detected: {', '.join(found)}",
            }
        return {"valid": True, "output": text, "error": None}

    # -- Custom schema guard (schema kept as opaque dict; no external validator) --

    def create_custom_guard(self, schema: dict[str, Any]) -> dict[str, Any]:
        return schema

    def validate_with_schema(self, guard: dict[str, Any], text: str) -> dict[str, Any]:
        required_keys: list[str] = guard.get("required_fields", [])
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return {"valid": False, "output": None, "error": "Text is not valid JSON"}
        missing = [k for k in required_keys if k not in parsed]
        if missing:
            return {
                "valid": False,
                "output": None,
                "error": f"Missing required fields: {missing}",
            }
        return {"valid": True, "output": text, "error": None}


guardrails_service = GuardrailsService()
