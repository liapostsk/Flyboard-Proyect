import json
import time
from typing import Any, Optional

from app.clients.openai_client import OpenAIResponsesClient
from app.core.exceptions import InvalidToolInput, IterationLimitExceeded
from app.core.logging import get_logger
from app.schemas.agent import AgentRunResponse, Metrics
from app.services.kb import KBService
from app.services.storage import StorageService
from app.services.tool_router import ToolRouter
from app.utils.ids import generate_trace_id
from app.utils.time import get_current_context

class AgentService:
    def __init__(self):
        self.openai_client = OpenAIResponsesClient()
        self.kb_service = KBService()
        self.storage_service = StorageService()
        self.tool_router = ToolRouter(self.kb_service, self.storage_service)
        self.logger = get_logger(__name__)
        self.max_iterations = 6
    
    def run(self, task: str, customer_id: Optional[str] = None, language: Optional[str] = None) -> AgentRunResponse:
        
        # 1. Setup inicial
        trace_id = generate_trace_id()
        start_time = time.time()
        openai_call_count = 0
        tool_calls_log = []
        previous_response_id = None
        
        self.logger.info(f"[{trace_id}] Starting agent run. Task: {task[:50]}...")
        
        # 2. Construir messages iniciales
        messages = [
            {
                "role": "user",
                "content": self._build_user_message(task, customer_id, language)
            }
        ]
        
        # 3. Bucle de iteraciones
        for iteration in range(1, self.max_iterations + 1):
            self.logger.info(f"[{trace_id}] Iteration {iteration}")
            
            # Llamada a OpenAI
            response = self.openai_client.call_with_tools(
                messages=messages,
                tools=self.tool_router.get_tool_definitions(),
                trace_id=trace_id,
                previous_response_id=previous_response_id,
            )
            previous_response_id = response.id
            openai_call_count += 1
            
            # Parsear respuesta
            response_type, content = self._parse_response(response)
            
            if response_type == "final":
                # Final answer: salir del loop
                self.logger.info(f"[{trace_id}] Final answer received at iteration {iteration}")
                final_answer = content
                break
            
            elif response_type == "tool_use":
                # Hay tool calls: ejecutar
                tool_calls = content  # Lista de tool_use blocks

                tool_outputs = []
                for tool_call in tool_calls:
                    tool_result = self._execute_tool(tool_call, trace_id)
                    tool_calls_log.append({
                        "name": tool_call["name"],
                        "arguments": tool_call["input"],
                        "result": tool_result
                    })

                    tool_outputs.append({
                        "type": "function_call_output",
                        "call_id": tool_call["call_id"],
                        "output": json.dumps(tool_result),
                    })

                # En Responses API el siguiente turno usa function_call_output como input.
                messages = tool_outputs
            
            else:
                # Error: salir
                raise Exception(f"Unexpected response type: {response_type}")
        
        else:
            # Max iterations reached
            raise IterationLimitExceeded(f"Max iterations ({self.max_iterations}) exceeded", trace_id=trace_id)
        
        # 4. Construir respuesta final
        latency_ms = int((time.time() - start_time) * 1000)

        final_answer = self._ensure_required_ids(final_answer, tool_calls_log)
        
        self.logger.info(f"[{trace_id}] Complete. Latency: {latency_ms}ms, OpenAI calls: {openai_call_count}")
        
        return AgentRunResponse(
            trace_id=trace_id,
            final_answer=final_answer,
            tool_calls=tool_calls_log,
            metrics=Metrics(
                latency_ms=latency_ms,
                model=self.openai_client.model,
                openai_calls=openai_call_count
            )
        )
    
    def _build_user_message(self, task: str, customer_id: Optional[str], language: Optional[str]) -> str:
        """
        Construye el mensaje de usuario con contexto.
        """
        msg = f"""{get_current_context()}

    Customer ID: {customer_id or "not provided"}

    Task:
    {task}
    """

        if language:
            msg += f"\nPlease respond in {language}."

        return msg
    
    def _parse_response(self, response) -> tuple[str, Any]:
        """
        Parsea la respuesta de OpenAI.
        Devuelve: ("final", text) o ("tool_use", [tool_calls])
        """
        has_text = False
        has_tool_use = False
        text_content = ""
        tool_calls = []
        
        for block in response.output:
            if block.type == "function_call":
                has_tool_use = True
                try:
                    parsed_args = json.loads(block.arguments) if block.arguments else {}
                except json.JSONDecodeError as exc:
                    raise InvalidToolInput(
                        message="Model returned invalid JSON arguments",
                        tool_name=block.name,
                        validation_details={"arguments": ["invalid JSON"]},
                    ) from exc
                tool_calls.append({
                    "call_id": block.call_id,
                    "name": block.name,
                    "input": parsed_args
                })

        text_content = response.output_text or ""
        if text_content:
            has_text = True
        
        if has_tool_use:
            return ("tool_use", tool_calls)
        elif has_text:
            return ("final", text_content)
        else:
            return ("error", None)
    
    def _execute_tool(self, tool_call: dict, trace_id: str) -> dict:
        """
        Ejecuta una tool individual.
        """
        tool_name = tool_call["name"]
        tool_input = tool_call["input"]
        
        self.logger.info(f"[{trace_id}] Executing tool: {tool_name}")
        start = time.time()
        
        try:
            result = self.tool_router.execute(tool_name, tool_input)
            duration = int((time.time() - start) * 1000)
            self.logger.info(f"[{trace_id}] Tool {tool_name} completed in {duration}ms")
            return result

        except InvalidToolInput as exc:
            if exc.trace_id is None:
                exc.trace_id = trace_id
            self.logger.error(f"[{trace_id}] Invalid input for tool {tool_name}: {exc}")
            raise
        
        except Exception as e:
            self.logger.error(f"[{trace_id}] Tool {tool_name} failed: {str(e)}")
            raise
    
    def _ensure_required_ids(self, final_answer: str, tool_calls_log: list[dict]) -> str:
        for tool_call in tool_calls_log:
            if tool_call["name"] == "create_ticket":
                ticket_id = tool_call["result"].get("ticket_id")
                if ticket_id and ticket_id not in final_answer:
                    final_answer += f"\n\nTicket ID: {ticket_id}"

            if tool_call["name"] == "schedule_followup":
                followup_id = tool_call["result"].get("followup_id")
                if followup_id and followup_id not in final_answer:
                    final_answer += f"\n\nFollow-up ID: {followup_id}"

        return final_answer