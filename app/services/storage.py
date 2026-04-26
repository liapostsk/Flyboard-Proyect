import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Union
from app.core.config import DB_PATH
from app.core.exceptions import InvalidToolInput
from app.utils.ids import generate_ticket_id, generate_followup_id
from app.utils.time import is_valid_iso_datetime

class StorageService:
    def __init__(self, db_path: Union[str, Path] = DB_PATH):
        self.db_path = str(Path(db_path))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializa las tablas si no existen."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    title TEXT,
                    body TEXT,
                    priority TEXT,
                    created_at TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS followups (
                    followup_id TEXT PRIMARY KEY,
                    datetime_iso TEXT,
                    contact TEXT,
                    channel TEXT,
                    created_at TEXT
                )
            """)
            
            conn.commit()
    
    def create_ticket(self, title: str, body: str, priority: str) -> dict:
        """Crea un ticket."""
        if not isinstance(title, str) or not title.strip():
            raise InvalidToolInput(
                message="Invalid title",
                tool_name="create_ticket",
                validation_details={"title": ["must be a non-empty string"]},
            )
        if not isinstance(body, str) or not body.strip():
            raise InvalidToolInput(
                message="Invalid body",
                tool_name="create_ticket",
                validation_details={"body": ["must be a non-empty string"]},
            )
        if priority not in {"low", "medium", "high"}:
            raise InvalidToolInput(
                message="Invalid priority",
                tool_name="create_ticket",
                validation_details={"priority": ["must be one of: low, medium, high"]},
            )

        ticket_id = generate_ticket_id()
        created_at = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tickets (ticket_id, title, body, priority, created_at) VALUES (?, ?, ?, ?, ?)",
                (ticket_id, title, body, priority, created_at)
            )
            conn.commit()
        
        return {
            "ticket_id": ticket_id,
            "status": "created"
        }
    
    def schedule_followup(self, datetime_iso: str, contact: str, channel: str) -> dict:
        """Programa un follow-up."""
        if not isinstance(datetime_iso, str) or not is_valid_iso_datetime(datetime_iso):
            raise InvalidToolInput(
                message="Invalid datetime_iso",
                tool_name="schedule_followup",
                validation_details={"datetime_iso": ["invalid ISO 8601 datetime"]},
            )
        if not isinstance(contact, str) or not contact.strip():
            raise InvalidToolInput(
                message="Invalid contact",
                tool_name="schedule_followup",
                validation_details={"contact": ["must be a non-empty string"]},
            )
        if channel not in {"email", "phone", "whatsapp"}:
            raise InvalidToolInput(
                message="Invalid channel",
                tool_name="schedule_followup",
                validation_details={"channel": ["must be one of: email, phone, whatsapp"]},
            )

        followup_id = generate_followup_id()
        created_at = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO followups (followup_id, datetime_iso, contact, channel, created_at) VALUES (?, ?, ?, ?, ?)",
                (followup_id, datetime_iso, contact, channel, created_at)
            )
            conn.commit()
        
        return {
            "scheduled": True,
            "followup_id": followup_id
        }