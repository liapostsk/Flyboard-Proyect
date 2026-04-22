from pydantic import BaseModel, Field
from typing import Optional

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
    priority: str = Field(..., pattern="^(low|medium|high)$")


class CreateTicketResponse(BaseModel):
    ticket_id: str
    status: str

# ============ SCHEDULE_FOLLOWUP ============

class ScheduleFollowupRequest(BaseModel):
    datetime_iso: str = Field(..., description="ISO 8601 datetime")
    contact: str = Field(..., min_length=1, max_length=500)
    channel: str = Field(..., pattern="^(email|phone|whatsapp)$")

class ScheduleFollowupResponse(BaseModel):
    scheduled: bool
    followup_id: str