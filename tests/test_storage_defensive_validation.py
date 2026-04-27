import pytest
import sqlite3

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


@pytest.mark.parametrize(
    "kwargs",
    [
        {"title": "   ", "body": "Valid body", "priority": "high"},
        {"title": "Valid title", "body": "   ", "priority": "high"},
        {"title": "Valid title", "body": "Valid body", "priority": "urgent"},
    ],
)
def test_storage_rejects_invalid_ticket_fields(tmp_path, kwargs):
    storage = StorageService(db_path=str(tmp_path / "app.db"))

    with pytest.raises(InvalidToolInput):
        storage.create_ticket(**kwargs)


def test_storage_create_ticket_persists_row(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.storage.generate_ticket_id", lambda: "TICK-000123")
    storage = StorageService(db_path=str(tmp_path / "app.db"))

    result = storage.create_ticket(title="Need help", body="Something broke", priority="high")

    assert result == {"ticket_id": "TICK-000123", "status": "created"}

    with sqlite3.connect(storage.db_path) as connection:
        row = connection.execute(
            "SELECT ticket_id, title, body, priority FROM tickets"
        ).fetchone()

    assert row == ("TICK-000123", "Need help", "Something broke", "high")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"datetime_iso": "2025-12-15T10:30:00Z", "contact": "marta@example.com", "channel": "telegram"},
        {"datetime_iso": "2025-12-15T10:30:00Z", "contact": "   ", "channel": "email"},
    ],
)
def test_storage_rejects_invalid_followup_fields(tmp_path, kwargs):
    storage = StorageService(db_path=str(tmp_path / "app.db"))

    with pytest.raises(InvalidToolInput):
        storage.schedule_followup(**kwargs)


def test_storage_schedule_followup_persists_row(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.storage.generate_followup_id", lambda: "FUP-000045")
    storage = StorageService(db_path=str(tmp_path / "app.db"))

    result = storage.schedule_followup(
        datetime_iso="2025-12-15T10:30:00Z",
        contact="marta@example.com",
        channel="whatsapp",
    )

    assert result == {"scheduled": True, "followup_id": "FUP-000045"}

    with sqlite3.connect(storage.db_path) as connection:
        row = connection.execute(
            "SELECT followup_id, datetime_iso, contact, channel FROM followups"
        ).fetchone()

    assert row == (
        "FUP-000045",
        "2025-12-15T10:30:00Z",
        "marta@example.com",
        "whatsapp",
    )
