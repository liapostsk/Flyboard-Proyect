"""
Excepciones personalizadas para mejor manejo de errores.
"""

from typing import Any, Optional

class FlyboardException(Exception):
    """Excepción base."""
    def __init__(self, message: str, trace_id: Optional[str] = None):
        super().__init__(message)
        self.trace_id = trace_id


class IterationLimitExceeded(FlyboardException):
    """Se alcanzó el máximo de iteraciones."""
    pass


class OpenAIIntegrationError(FlyboardException):
    """Error al llamar a OpenAI."""
    pass


class RateLimitError(OpenAIIntegrationError):
    """Rate limit de OpenAI."""
    pass


class ToolExecutionError(FlyboardException):
    """Error al ejecutar una tool."""
    pass


class InvalidToolInput(FlyboardException):
    """Argumentos inválidos para una tool."""
    def __init__(
        self,
        message: str,
        trace_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        validation_details: Optional[Any] = None,
    ):
        super().__init__(message, trace_id=trace_id)
        self.tool_name = tool_name
        self.validation_details = validation_details