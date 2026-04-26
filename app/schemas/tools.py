from pydantic import BaseModel, Field, ValidationError
from typing import Any, Optional

from app.core.exceptions import InvalidToolInput
from typing import Literal


# ============ SEARCH_KB ============

class SearchKBRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, ge=1, le=10, description="Number of results")
    filters: Optional[dict] = Field(None, description="Optional filters")

class SearchKBResult(BaseModel):
    id: str
    title: str
    score: float
    snippet: str
    tags: list[str]

class SearchKBResponse(BaseModel):
    results: list[SearchKBResult]

# ============ CREATE_TICKET ============

class CreateTicketRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1, max_length=5000)
    priority: Literal["low", "medium", "high"]



class CreateTicketResponse(BaseModel):
    ticket_id: str
    status: str

# ============ SCHEDULE_FOLLOWUP ============

class ScheduleFollowupRequest(BaseModel):
    datetime_iso: str = Field(..., description="ISO 8601 datetime")
    contact: str = Field(..., min_length=1, max_length=500)
    channel: Literal["email", "phone", "whatsapp"]

class ScheduleFollowupResponse(BaseModel):
    scheduled: bool
    followup_id: str


TOOL_REQUEST_SCHEMAS = {
    "search_kb": SearchKBRequest,
    "create_ticket": CreateTicketRequest,
    "schedule_followup": ScheduleFollowupRequest,
}


def validate_tool_input(tool_name: str, tool_input: Any) -> dict:
    """Valida y normaliza el payload de una tool usando schemas Pydantic."""
    schema = TOOL_REQUEST_SCHEMAS.get(tool_name)
    if schema is None:
        raise InvalidToolInput(
            message=f"Unknown tool: {tool_name}",
            tool_name=tool_name,
            validation_details={"tool_name": ["unknown tool"]},
        )

    if not isinstance(tool_input, dict):
        raise InvalidToolInput(
            message="Tool input must be an object",
            tool_name=tool_name,
            validation_details={"input": ["must be a JSON object"]},
        )

    try:
        validated = schema(**tool_input)
        return validated.model_dump(exclude_none=True)
    except ValidationError as exc:
        raise InvalidToolInput(
            message=f"Invalid input for tool: {tool_name}",
            tool_name=tool_name,
            validation_details=exc.errors(),
        ) from exc