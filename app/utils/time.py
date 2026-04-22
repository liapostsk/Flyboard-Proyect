from datetime import datetime

def parse_iso_datetime(datetime_str: str) -> datetime:
    """
    Parsea una cadena ISO 8601 a datetime.
    Maneja timezones.
    """
    try:
        # Intenta parsear con timezone
        if datetime_str.endswith('Z'):
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        else:
            return datetime.fromisoformat(datetime_str)
    except ValueError:
        raise ValueError(f"Invalid ISO datetime: {datetime_str}")


def get_current_iso() -> str:
    """Devuelve el timestamp actual en ISO 8601."""
    return datetime.utcnow().isoformat() + 'Z'


def is_valid_iso_datetime(datetime_str: str) -> bool:
    """Comprueba si una cadena es un datetime ISO válido."""
    try:
        parse_iso_datetime(datetime_str)
        return True
    except ValueError:
        return False