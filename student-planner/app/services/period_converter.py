"""Convert schedule periods to concrete start and end times."""

from __future__ import annotations

import re


_PERIOD_RE = re.compile(r"^\d{1,2}-\d{1,2}$")
_TIME_RANGE_RE = re.compile(
    r"^\s*([01]\d|2[0-3]):([0-5]\d)\s*-\s*([01]\d|2[0-3]):([0-5]\d)\s*$"
)


def convert_periods(
    period: str,
    schedule: dict[str, dict[str, str]],
) -> dict[str, str] | None:
    normalized = period.strip().replace("〞", "-").replace("每", "-")
    times = schedule.get(normalized)
    if times is None:
        return None
    return {"start_time": times["start"], "end_time": times["end"]}


def normalize_period(period: str) -> str:
    normalized = period.strip().replace("〞", "-").replace("每", "-")
    if not _PERIOD_RE.match(normalized):
        raise ValueError(f"非法节次: {period}")
    return normalized


def parse_time_range(raw: str) -> tuple[str, str]:
    match = _TIME_RANGE_RE.match(raw or "")
    if match is None:
        raise ValueError("时间格式应为 HH:MM-HH:MM")

    sh, sm, eh, em = map(int, match.groups())
    start_minutes = sh * 60 + sm
    end_minutes = eh * 60 + em
    if end_minutes <= start_minutes:
        raise ValueError("结束时间必须晚于开始时间")

    return f"{sh:02d}:{sm:02d}", f"{eh:02d}:{em:02d}"
