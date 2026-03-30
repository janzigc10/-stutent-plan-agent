from datetime import datetime

from app.services.reminder_scheduler import (
    build_push_payload,
    compute_next_course_occurrence,
    resolve_fire_time,
)


def test_resolve_fire_time_task_reminder():
    event_time = "2026-04-01T10:00:00"
    result = resolve_fire_time(event_time, advance_minutes=15)
    assert result == datetime(2026, 4, 1, 9, 45)


def test_resolve_fire_time_zero_advance():
    event_time = "2026-04-01T10:00:00"
    result = resolve_fire_time(event_time, advance_minutes=0)
    assert result == datetime(2026, 4, 1, 10, 0)


def test_compute_next_course_occurrence_same_day_future():
    now = datetime(2026, 3, 30, 9, 0)
    result = compute_next_course_occurrence(weekday=1, start_time="10:00", now=now)
    assert result == datetime(2026, 3, 30, 10, 0)


def test_compute_next_course_occurrence_same_day_past():
    now = datetime(2026, 3, 30, 11, 0)
    result = compute_next_course_occurrence(weekday=1, start_time="10:00", now=now)
    assert result == datetime(2026, 4, 6, 10, 0)


def test_build_push_payload_course():
    payload = build_push_payload(
        target_type="course",
        target_name="高等数学",
        target_time="10:00",
        target_location="教学楼A301",
    )
    assert payload["title"] == "课程提醒"
    assert "高等数学" in payload["body"]
    assert "10:00" in payload["body"]
    assert "教学楼A301" in payload["body"]


def test_build_push_payload_task():
    payload = build_push_payload(
        target_type="task",
        target_name="复习线性代数",
        target_time="14:00-16:00",
    )
    assert payload["title"] == "任务提醒"
    assert "复习线性代数" in payload["body"]
    assert "14:00-16:00" in payload["body"]