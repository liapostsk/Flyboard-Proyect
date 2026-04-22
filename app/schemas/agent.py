from pydantic import BaseModel, Field
from typing import Optional

class AgentRunRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=5000, description="User task")
    customer_id: Optional[str] = Field(None, description="Optional customer ID")
    language: Optional[str] = Field(None, pattern="^[a-z]{2}$", description="ISO 639-1 language code")

class ToolCall(BaseModel):
    name: str
    arguments: dict
    result: dict

class Metrics(BaseModel):
    latency_ms: int
    model: str
    openai_calls: int

class AgentRunResponse(BaseModel):
    trace_id: str
    final_answer: str
    tool_calls: list[ToolCall]
    metrics: Metrics