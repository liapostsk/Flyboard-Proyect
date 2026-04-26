from openai import OpenAI
from openai._exceptions import APITimeoutError
from typing import Optional
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT, OPENAI_SYSTEM_PROMPT
from app.core.exceptions import RateLimitError, OpenAIIntegrationError

# Capa de integración con OpenAI Responses API, incluyendo manejo de errores específicos.
class OpenAIResponsesClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT)
        self.model = OPENAI_MODEL
        self.system_prompt = OPENAI_SYSTEM_PROMPT
    
    def call_with_tools(self, messages: list, tools: list, trace_id: str, previous_response_id: Optional[str] = None):
        """
        Llama a OpenAI Responses API con tool definitions.
        
        Args:
            messages: input items para Responses API
            tools: lista de tool definitions (JSON schema)
            trace_id: para logging
            previous_response_id: ID de respuesta previa para continuar el loop
        
        Returns:
            response object de Responses API
        """
        try:
            request_params = {
                "model": self.model,
                "input": messages,
                "tools": tools,
                "instructions": self.system_prompt,
            }
            if previous_response_id:
                request_params["previous_response_id"] = previous_response_id

            response = self.client.responses.create(
                **request_params
            )
            return response
        
        except Exception as e:
            if isinstance(e, APITimeoutError) or "timeout" in str(e).lower():
                raise OpenAIIntegrationError(str(e), trace_id=trace_id)
            if "rate_limit" in str(e).lower():
                raise RateLimitError(str(e), trace_id=trace_id)
            elif "api_error" in str(e).lower():
                raise OpenAIIntegrationError(str(e), trace_id=trace_id)
            else:
                raise OpenAIIntegrationError(str(e), trace_id=trace_id)