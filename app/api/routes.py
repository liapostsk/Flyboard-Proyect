from fastapi import APIRouter, HTTPException
from app.core.exceptions import InvalidToolInput
from app.schemas.agent import AgentRunRequest, AgentRunResponse
from app.services.agent import AgentService
from app.core.logging import get_logger
import time

router = APIRouter(prefix="/v1", tags=["agent"])
logger = get_logger(__name__)

@router.post("/agent/run")
async def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    """
    Run the agent orchestrator with tool calling.
    """
    start_time = time.time()
    
    try:
        # Crear instancia del servicio
        agent_service = AgentService()
        
        # Ejecutar agente
        result = agent_service.run(
            task=request.task,
            customer_id=request.customer_id,
            language=request.language
        )
        
        # Inyectar latencia
        latency_ms = int((time.time() - start_time) * 1000)
        result.metrics.latency_ms = latency_ms
        
        return result

    except InvalidToolInput as e:
        logger.warning(f"Invalid tool input: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "invalid_tool_input",
            "tool_name": e.tool_name,
            "validation_errors": e.validation_details,
            "trace_id": getattr(e, 'trace_id', 'unknown')
        })
        
    except Exception as e:
        # Loggear y devolver error controlado
        logger.error(f"Agent run failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=502, detail={
            "error": "OpenAI integration error",
            "trace_id": getattr(e, 'trace_id', 'unknown')
        })
