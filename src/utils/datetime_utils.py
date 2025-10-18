# utils/datetime_utils.py
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_LOCAL = ZoneInfo("America/Sao_Paulo")

def normalize_input_datetime(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(TZ_LOCAL)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ_LOCAL)
    return dt
