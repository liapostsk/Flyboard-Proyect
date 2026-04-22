from openai import OpenAI
import os
from typing import Optional
from app.core.exceptions import RateLimitError, OpenAIIntegrationError

# Capa de integración con OpenAI Responses API, incluyendo manejo de errores específicos.
class OpenAIResponsesClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """
        Define el comportamiento del modelo.
        """
        return """You are a helpful Flyboard support agent.

Your responsibilities:
1. Use search_kb to find information from the knowledge base
2. Use create_ticket when users report issues and request help
3. Use schedule_followup to arrange follow-up calls/emails
4. Never invent facts outside the KB results
5. If information is missing, say so and offer to create a ticket

You must:
- Be concise and helpful
- Use tools appropriately to solve the user's problem
- Respond in the user's language when specified
- Avoid hallucinations
"""
    
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
            # Manejar errores específicos de OpenAI
            if "rate_limit" in str(e).lower():
                raise RateLimitError(str(e), trace_id=trace_id)
            elif "api_error" in str(e).lower():
                raise OpenAIIntegrationError(str(e), trace_id=trace_id)
            else:
                raise OpenAIIntegrationError(str(e), trace_id=trace_id)