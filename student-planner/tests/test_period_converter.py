from app.services.period_converter import DEFAULT_SCHEDULE, convert_periods


def test_default_schedule_has_five_periods() -> None:
    assert "1-2" in DEFAULT_SCHEDULE
    assert "3-4" in DEFAULT_SCHEDULE
    assert "5-6" in DEFAULT_SCHEDULE
    assert "7-8" in DEFAULT_SCHEDULE
    assert "9-10" in DEFAULT_SCHEDULE


def test_convert_single_period() -> None:
    result = convert_periods("1-2", DEFAULT_SCHEDULE)
    assert result == {"start_time": "08:00", "end_time": "09:40"}


def test_convert_period_5_6() -> None:
    result = convert_periods("5-6", DEFAULT_SCHEDULE)
    assert result == {"start_time": "14:00", "end_time": "15:40"}


def test_convert_with_custom_schedule() -> None:
    custom = {"1-2": {"start": "08:30", "end": "10:10"}}
    result = convert_periods("1-2", custom)
    assert result == {"start_time": "08:30", "end_time": "10:10"}


def test_convert_unknown_period_returns_none() -> None:
    result = convert_periods("11-12", DEFAULT_SCHEDULE)
    assert result is None


def test_convert_normalizes_chinese_dash() -> None:
    result = convert_periods("1—2", DEFAULT_SCHEDULE)
    assert result == {"start_time": "08:00", "end_time": "09:40"}


def test_convert_strips_whitespace() -> None:
    result = convert_periods(" 3-4 ", DEFAULT_SCHEDULE)
    assert result == {"start_time": "10:00", "end_time": "11:40"}