"""
Structured Logging Service for LLM Eval Guardrails Platform
Implements structured logging with correlation IDs and context
"""
import json
import uuid
import time
from typing import Optional, Dict, Any

class LogContext:
    def __init__(
        self,
        correlation_id: str,
        user_id: Optional[str] = None,
        eval_id: Optional[str] = None,
        model_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        self.correlation_id = correlation_id
        self.user_id = user_id
        self.eval_id = eval_id
        self.model_id = model_id
        self.request_id = request_id
        self.ip_address = ip_address
        self.user_agent = user_agent

    def to_dict(self) -> Dict[str, Any]:
        return {
            'correlationId': self.correlation_id,
            'userId': self.user_id,
            'evalId': self.eval_id,
            'modelId': self.model_id,
            'requestId': self.request_id,
            'ipAddress': self.ip_address,
            'userAgent': self.user_agent
        }

class LogEntry:
    def __init__(
        self,
        timestamp: str,
        level: str,
        message: str,
        context: LogContext,
        additional_context: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.context = context.to_dict()
        self.additional_context = additional_context
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'level': self.level,
            'message': self.message,
            'context': self.context,
            'additionalContext': self.additional_context,
            'error': self.error
        }

class StructuredLoggingService:
    def __init__(self):
        self.current_context: Optional[LogContext] = None

    def set_context(self, context: LogContext) -> None:
        """Set the current logging context"""
        self.current_context = context

    def get_context(self) -> Optional[LogContext]:
        """Get the current logging context"""
        return self.current_context

    def log_information(self, message: str, additional_context: Optional[Dict[str, Any]] = None) -> None:
        """Log an information message"""
        log_entry = self._create_log_entry('Information', message, additional_context, None)
        print(json.dumps(log_entry.to_dict()))

    def log_warning(self, message: str, additional_context: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning message"""
        log_entry = self._create_log_entry('Warning', message, additional_context, None)
        print(json.dumps(log_entry.to_dict()))

    def log_error(self, message: str, error: str, additional_context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error message"""
        log_entry = self._create_log_entry('Error', message, additional_context, error)
        print(json.dumps(log_entry.to_dict()))

    def log_audit_event(self, event_type: str, description: str, additional_context: Optional[Dict[str, Any]] = None) -> None:
        """Log an audit event"""
        context = {**(additional_context or {})}
        context['auditEventType'] = event_type
        context['auditDescription'] = description

        log_entry = self._create_log_entry('Audit', f'AUDIT: {description}', context, None)
        print(json.dumps(log_entry.to_dict()))

    @staticmethod
    def create_correlation_id() -> str:
        """Create a new correlation ID"""
        return str(uuid.uuid4())

    def _create_log_entry(self, level: str, message: str, additional_context: Optional[Dict[str, Any]], error: Optional[str]) -> LogEntry:
        """Create a log entry"""
        context = self.current_context or self._default_context()

        return LogEntry(
            timestamp=time.time(),
            level=level,
            message=message,
            context=context,
            additional_context=additional_context,
            error=error
        )

    def _default_context(self) -> LogContext:
        """Create a default logging context"""
        return LogContext(correlation_id=self.create_correlation_id())
