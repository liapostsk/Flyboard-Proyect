"""
Todos los schemas en un lugar.
"""

from .agent import (
    AgentRunRequest,
    AgentRunResponse,
    ToolCall,
    Metrics
)
from .tools import (
    SearchKBRequest,
    SearchKBResponse,
    SearchKBResult,
    CreateTicketRequest,
    CreateTicketResponse,
    ScheduleFollowupRequest,
    ScheduleFollowupResponse
)

__all__ = [
    # Agent
    "AgentRunRequest",
    "AgentRunResponse",
    "ToolCall",
    "Metrics",
    # Tools
    "SearchKBRequest",
    "SearchKBResponse",
    "SearchKBResult",
    "CreateTicketRequest",
    "CreateTicketResponse",
    "ScheduleFollowupRequest",
    "ScheduleFollowupResponse"
]