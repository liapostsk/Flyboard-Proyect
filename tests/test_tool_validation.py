import pytest

from app.core.exceptions import InvalidToolInput
from app.services.kb import KBService
from app.services.storage import StorageService
from app.services.tool_router import ToolRouter
from app.schemas.tools import validate_tool_input


def _build_router(tmp_path):
    storage = StorageService(db_path=str(tmp_path / "app.db"))
    kb_service = KBService()
    return ToolRouter(kb_service=kb_service, storage_service=storage)


def test_search_kb_missing_query_raises_invalid_tool_input(tmp_path):
    router = _build_router(tmp_path)

    with pytest.raises(InvalidToolInput) as exc_info:
        router.execute("search_kb", {"top_k": 5})

    assert exc_info.value.tool_name == "search_kb"


def test_create_ticket_invalid_priority_raises_invalid_tool_input(tmp_path):
    router = _build_router(tmp_path)

    with pytest.raises(InvalidToolInput) as exc_info:
        router.execute(
            "create_ticket",
            {"title": "Issue", "body": "Details", "priority": "urgent"},
        )

    assert exc_info.value.tool_name == "create_ticket"


def test_schedule_followup_invalid_channel_raises_invalid_tool_input(tmp_path):
    router = _build_router(tmp_path)

    with pytest.raises(InvalidToolInput) as exc_info:
        router.execute(
            "schedule_followup",
            {
                "datetime_iso": "2025-12-15T10:30:00Z",
                "contact": "marta@example.com",
                "channel": "telegram",
            },
        )

    assert exc_info.value.tool_name == "schedule_followup"


def test_schedule_followup_invalid_datetime_raises_invalid_tool_input(tmp_path):
    router = _build_router(tmp_path)

    with pytest.raises(InvalidToolInput) as exc_info:
        router.execute(
            "schedule_followup",
            {
                "datetime_iso": "2025-99-99T10:30:00",
                "contact": "marta@example.com",
                "channel": "whatsapp",
            },
        )

    assert exc_info.value.tool_name == "schedule_followup"


def test_validate_tool_input_rejects_unknown_tool():
    with pytest.raises(InvalidToolInput) as exc_info:
        validate_tool_input("unknown_tool", {})

    assert exc_info.value.tool_name == "unknown_tool"


def test_validate_tool_input_rejects_non_object_payload():
    with pytest.raises(InvalidToolInput) as exc_info:
        validate_tool_input("search_kb", "query")

    assert exc_info.value.tool_name == "search_kb"
