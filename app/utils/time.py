from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "Europe/Madrid"


def parse_iso_datetime(datetime_str: str) -> datetime:
    """
    Parsea una cadena ISO 8601 a datetime.
    Maneja timezones.
    """
    try:
        if datetime_str.endswith("Z"):
            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        return datetime.fromisoformat(datetime_str)
    except ValueError:
        raise ValueError(f"Invalid ISO datetime: {datetime_str}")


def get_current_iso(timezone: str = DEFAULT_TIMEZONE) -> str:
    """Devuelve el timestamp actual en ISO 8601 con timezone."""
    return datetime.now(ZoneInfo(timezone)).isoformat()


def get_current_context(timezone: str = DEFAULT_TIMEZONE) -> str:
    """Devuelve contexto temporal para el modelo."""
    now = datetime.now(ZoneInfo(timezone))
    return (
        f"Current datetime: {now.isoformat()}\n"
        f"Current date: {now.date().isoformat()}\n"
        f"Timezone: {timezone}"
    )


def is_valid_iso_datetime(datetime_str: str) -> bool:
    """Comprueba si una cadena es un datetime ISO válido."""
    try:
        parse_iso_datetime(datetime_str)
        return True
    except ValueError:
        return False