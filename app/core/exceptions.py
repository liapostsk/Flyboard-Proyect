"""
Excepciones personalizadas para mejor manejo de errores.
"""

class FlyboardException(Exception):
    """Excepción base."""
    def __init__(self, message: str, trace_id: str = None):
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
    pass