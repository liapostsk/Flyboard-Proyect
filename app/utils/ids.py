import random
import uuid

def generate_trace_id() -> str:
    return f"trace-{uuid.uuid4().hex[:12]}"

def generate_ticket_id() -> str:
    return f"TICK-{random.randint(100000, 999999)}"  # TICK-587392

def generate_followup_id() -> str:
    return f"FUP-{random.randint(10000, 99999)}"    # FUP-43821