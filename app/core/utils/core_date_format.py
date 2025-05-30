from typing import Union
from datetime import datetime
from zoneinfo import ZoneInfo


def core_date_format(iso_date: Union[str, datetime], split: bool = False):
    if isinstance(iso_date, datetime):
        dt = iso_date
    elif isinstance(iso_date, str):
        dt = datetime.fromisoformat(iso_date.rstrip("Z"))
    else:
        return ("", "") if split else ""

    # Convert to Asia/Phnom_Penh timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))  # Assume UTC if no timezone
    dt = dt.astimezone(ZoneInfo("Asia/Phnom_Penh"))

    date_part = dt.strftime("%d %b %Y")
    time_part = dt.strftime("%I:%M %p").lstrip("0")

    if split:
        return date_part, time_part
    return f"{date_part} / {time_part}"
