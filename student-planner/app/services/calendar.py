from dataclasses import dataclass


@dataclass
class TimeSlot:
    start: str
    end: str
    type: str = ""
    name: str = ""
    duration_minutes: int = 0

    def __post_init__(self):
        if not self.duration_minutes:
            self.duration_minutes = _minutes(self.end) - _minutes(self.start)


@dataclass
class DaySchedule:
    date: str
    weekday: str
    free_periods: list[TimeSlot]
    occupied: list[TimeSlot]
    summary: str = ""


def _minutes(t: str) -> int:
    hours, minutes = t.split(":")
    return int(hours) * 60 + int(minutes)


def _time_str(total_minutes: int) -> str:
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def compute_free_slots(
    occupied: list[TimeSlot],
    day_start: str = "08:00",
    day_end: str = "22:00",
    min_duration_minutes: int = 30,
) -> list[TimeSlot]:
    start_min = _minutes(day_start)
    end_min = _minutes(day_end)
    intervals = sorted([(_minutes(item.start), _minutes(item.end)) for item in occupied], key=lambda item: item[0])

    merged: list[tuple[int, int]] = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    free: list[TimeSlot] = []
    cursor = start_min
    for occupied_start, occupied_end in merged:
        occupied_start = max(occupied_start, start_min)
        occupied_end = min(occupied_end, end_min)
        if cursor < occupied_start:
            duration = occupied_start - cursor
            if duration >= min_duration_minutes:
                free.append(
                    TimeSlot(
                        start=_time_str(cursor),
                        end=_time_str(occupied_start),
                        duration_minutes=duration,
                    )
                )
        cursor = max(cursor, occupied_end)

    if cursor < end_min:
        duration = end_min - cursor
        if duration >= min_duration_minutes:
            free.append(
                TimeSlot(
                    start=_time_str(cursor),
                    end=_time_str(end_min),
                    duration_minutes=duration,
                )
            )

    return free