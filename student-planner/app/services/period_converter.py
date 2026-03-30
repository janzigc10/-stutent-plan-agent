"""Convert schedule periods to concrete start and end times."""

DEFAULT_SCHEDULE: dict[str, dict[str, str]] = {
    "1-2": {"start": "08:00", "end": "09:40"},
    "3-4": {"start": "10:00", "end": "11:40"},
    "5-6": {"start": "14:00", "end": "15:40"},
    "7-8": {"start": "16:00", "end": "17:40"},
    "9-10": {"start": "19:00", "end": "20:40"},
}


def convert_periods(
    period: str,
    schedule: dict[str, dict[str, str]],
) -> dict[str, str] | None:
    normalized = period.strip().replace("—", "-").replace("–", "-")
    times = schedule.get(normalized)
    if times is None:
        return None
    return {"start_time": times["start"], "end_time": times["end"]}