import pytest

from app.core.exceptions import InvalidToolInput
from app.services.storage import StorageService


def test_storage_rejects_invalid_ticket_priority(tmp_path):
    storage = StorageService(db_path=str(tmp_path / "app.db"))

    with pytest.raises(InvalidToolInput) as exc_info:
        storage.create_ticket(title="Valid", body="Valid", priority="urgent")

    assert exc_info.value.tool_name == "create_ticket"


def test_storage_rejects_empty_contact(tmp_path):
    storage = StorageService(db_path=str(tmp_path / "app.db"))

    with pytest.raises(InvalidToolInput) as exc_info:
        storage.schedule_followup(
            datetime_iso="2025-12-15T10:30:00Z",
            contact="   ",
            channel="email",
        )

    assert exc_info.value.tool_name == "schedule_followup"


def test_storage_rejects_invalid_datetime(tmp_path):
    storage = StorageService(db_path=str(tmp_path / "app.db"))

    with pytest.raises(InvalidToolInput) as exc_info:
        storage.schedule_followup(
            datetime_iso="not-a-datetime",
            contact="marta@example.com",
            channel="email",
        )

    assert exc_info.value.tool_name == "schedule_followup"
