import sqlite3
import json
from datetime import datetime
from app.utils.ids import generate_ticket_id, generate_followup_id

class StorageService:
    def __init__(self, db_path: str = "data/app.db"):
        self.db_path = db_path
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