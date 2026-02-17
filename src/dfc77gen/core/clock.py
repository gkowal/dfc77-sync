from __future__ import annotations

from datetime import datetime, UTC


def now_dt(use_utc: bool) -> datetime:
    return datetime.now(UTC) if use_utc else datetime.now()