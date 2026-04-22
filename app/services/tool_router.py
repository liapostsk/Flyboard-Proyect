from app.core.logging import get_logger
from app.tools.definitions import get_tool_definitions

class ToolRouter:
    def __init__(self, kb_service, storage_service):
        self.kb_service = kb_service
        self.storage_service = storage_service
        self.logger = get_logger(__name__)
    
    def get_tool_definitions(self) -> list:
        """Devuelve las definiciones de tools."""
        return get_tool_definitions()
    
    def execute(self, tool_name: str, tool_input: dict) -> dict:
        """
        Ejecuta una tool por nombre.
        """
        if tool_name == "search_kb":
            return self.kb_service.search_kb(
                query=tool_input.get("query"),
                top_k=tool_input.get("top_k", 5),
                filters=tool_input.get("filters")
            )
        
        elif tool_name == "create_ticket":
            return self.storage_service.create_ticket(
                title=tool_input.get("title"),
                body=tool_input.get("body"),
                priority=tool_input.get("priority")
            )
        
        elif tool_name == "schedule_followup":
            return self.storage_service.schedule_followup(
                datetime_iso=tool_input.get("datetime_iso"),
                contact=tool_input.get("contact"),
                channel=tool_input.get("channel")
            )
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")