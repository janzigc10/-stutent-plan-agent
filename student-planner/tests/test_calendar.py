from app.services.calendar import compute_free_slots, TimeSlot


def test_empty_day():
    result = compute_free_slots(
        occupied=[],
        day_start="08:00",
        day_end="22:00",
        min_duration_minutes=30,
    )
    assert len(result) == 1
    assert result[0].start == "08:00"
    assert result[0].end == "22:00"
    assert result[0].duration_minutes == 840


def test_one_course_splits_day():
    result = compute_free_slots(
        occupied=[TimeSlot(start="10:00", end="12:00", type="course", name="高等数学")],
        day_start="08:00",
        day_end="22:00",
        min_duration_minutes=30,
    )
    assert len(result) == 2
    assert result[0].start == "08:00"
    assert result[0].end == "10:00"
    assert result[1].start == "12:00"
    assert result[1].end == "22:00"


def test_adjacent_courses():
    result = compute_free_slots(
        occupied=[
            TimeSlot(start="08:00", end="10:00", type="course", name="高数"),
            TimeSlot(start="10:00", end="12:00", type="course", name="线代"),
        ],
        day_start="08:00",
        day_end="22:00",
        min_duration_minutes=30,
    )
    assert len(result) == 1
    assert result[0].start == "12:00"


def test_min_duration_filter():
    result = compute_free_slots(
        occupied=[TimeSlot(start="08:00", end="08:20", type="task", name="Quick task")],
        day_start="08:00",
        day_end="08:30",
        min_duration_minutes=30,
    )
    assert len(result) == 0


def test_overlapping_events():
    result = compute_free_slots(
        occupied=[
            TimeSlot(start="09:00", end="11:00", type="course", name="A"),
            TimeSlot(start="10:00", end="12:00", type="task", name="B"),
        ],
        day_start="08:00",
        day_end="22:00",
        min_duration_minutes=30,
    )
    assert result[0].start == "08:00"
    assert result[0].end == "09:00"
    assert result[1].start == "12:00"
    assert result[1].end == "22:00"


def test_lunch_break_excluded():
    result = compute_free_slots(
        occupied=[TimeSlot(start="12:00", end="13:30", type="break", name="午休")],
        day_start="08:00",
        day_end="22:00",
        min_duration_minutes=30,
    )
    starts = [slot.start for slot in result]
    assert "08:00" in starts
    assert "13:30" in starts
    for slot in result:
        assert not (slot.start < "13:30" and slot.end > "12:00")