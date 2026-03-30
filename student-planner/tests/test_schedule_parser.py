from pathlib import Path

from app.services.schedule_parser import RawCourse, parse_excel_schedule

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_schedule.xlsx"


def test_parse_returns_list_of_raw_courses() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    assert isinstance(courses, list)
    assert len(courses) > 0
    assert all(isinstance(course, RawCourse) for course in courses)


def test_parse_extracts_course_name() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    names = {course.name for course in courses}
    assert "高等数学" in names
    assert "线性代数" in names
    assert "大学英语" in names


def test_parse_extracts_weekday() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    gaoshu = next(course for course in courses if course.name == "高等数学")
    assert gaoshu.weekday == 1


def test_parse_extracts_period() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    gaoshu = next(course for course in courses if course.name == "高等数学")
    assert gaoshu.period == "1-2"


def test_parse_extracts_teacher() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    gaoshu = next(course for course in courses if course.name == "高等数学")
    assert gaoshu.teacher == "张老师"


def test_parse_extracts_location() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    gaoshu = next(course for course in courses if course.name == "高等数学")
    assert gaoshu.location == "教学楼A301"


def test_parse_extracts_weeks() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    gaoshu = next(course for course in courses if course.name == "高等数学")
    assert gaoshu.week_start == 1
    assert gaoshu.week_end == 16


def test_parse_handles_missing_teacher() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    tiyu = next(course for course in courses if course.name == "体育")
    assert tiyu.teacher is None


def test_parse_handles_custom_week_range() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    gailv = next(course for course in courses if course.name == "概率论")
    assert gailv.week_start == 3
    assert gailv.week_end == 16


def test_parse_total_course_count() -> None:
    courses = parse_excel_schedule(FIXTURE_PATH)
    assert len(courses) == 6