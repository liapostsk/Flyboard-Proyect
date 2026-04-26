from app.core.logging import get_logger
from app.core.exceptions import InvalidToolInput
from app.schemas.tools import validate_tool_input
from app.tools.definitions import get_tool_definitions
from app.utils.time import is_valid_iso_datetime

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
        validated_input = validate_tool_input(tool_name, tool_input)

        if tool_name == "search_kb":
            return self.kb_service.search_kb(
                query=validated_input["query"],
                top_k=validated_input.get("top_k", 5),
                filters=validated_input.get("filters")
            )
        
        elif tool_name == "create_ticket":
            return self.storage_service.create_ticket(
                title=validated_input["title"],
                body=validated_input["body"],
                priority=validated_input["priority"]
            )
        
        elif tool_name == "schedule_followup":
            datetime_iso = validated_input["datetime_iso"]
            if not is_valid_iso_datetime(datetime_iso):
                raise InvalidToolInput(
                    message="Invalid ISO datetime",
                    tool_name="schedule_followup",
                    validation_details={"datetime_iso": ["invalid ISO 8601 datetime"]},
                )

            return self.storage_service.schedule_followup(
                datetime_iso=datetime_iso,
                contact=validated_input["contact"],
                channel=validated_input["channel"],
            )
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")