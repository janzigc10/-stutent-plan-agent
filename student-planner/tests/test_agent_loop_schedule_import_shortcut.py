from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.agent.loop import run_agent_loop
from app.models.course import Course
from app.models.user import User
from app.services.schedule_upload_cache import store_schedule_upload
from tests.conftest import TestSession


@pytest.mark.asyncio
async def test_schedule_import_shortcut_collects_missing_info_and_imports_without_llm(setup_db):
    mock_client = AsyncMock()

    with patch(
        "app.agent.loop.chat_completion_stream",
        side_effect=AssertionError("LLM should not be called for local schedule import shortcut"),
    ), patch(
        "app.agent.loop.chat_completion",
        side_effect=AssertionError("LLM fallback should not be called for local schedule import shortcut"),
    ):
        async with TestSession() as db:
            user = User(id="u8", username="test8", hashed_password="x")
            db.add(user)
            await db.commit()

            file_id = store_schedule_upload(
                user_id="u8",
                kind="spreadsheet",
                courses=[
                    {
                        "name": "all-course",
                        "teacher": "Teacher A",
                        "location": "Room 301",
                        "weekday": 1,
                        "period": "1-2",
                        "week_start": 1,
                        "week_end": 16,
                        "week_pattern": "all",
                        "week_text": "\u7b2c1-16\u5468",
                    },
                    {
                        "name": "odd-course",
                        "teacher": "Teacher B",
                        "location": "A301",
                        "weekday": 3,
                        "period": "3-4",
                        "week_start": 1,
                        "week_end": 18,
                        "week_pattern": "odd",
                        "week_text": "\u7b2c1-18\u5468(\u5355\u5468)",
                    },
                ],
            )

            generator = run_agent_loop(
                f"please import this schedule file_id={file_id}",
                user,
                "session-8",
                db,
                mock_client,
            )

            event = await generator.__anext__()
            assert event["type"] == "tool_call"
            assert event["name"] == "parse_schedule"
            assert event["args"] == {"file_id": file_id}

            event = await generator.__anext__()
            assert event["type"] == "tool_result"
            assert event["result"]["status"] == "need_period_times"

            ask_event = await generator.__anext__()
            assert ask_event["type"] == "ask_user"
            assert ask_event["ask_type"] == "review"
            assert ask_event["options"] == []
            assert "missing_periods" not in ask_event["question"]
            assert "missing_semester_fields" not in ask_event["question"]
            assert "1-2" in ask_event["question"]
            assert "3-4" in ask_event["question"]

            event = await generator.asend("1-2节 08:30-10:15 3-4节 10:20-11:55")
            assert event["type"] == "tool_call"
            assert event["name"] == "save_period_times"

            event = await generator.__anext__()
            assert event["type"] == "tool_result"
            assert event["result"]["status"] == "need_period_times"
            assert event["result"]["missing_periods"] == []
            assert "semester_start_date" in event["result"]["missing_semester_fields"]
            assert "term_total_weeks" in event["result"]["missing_semester_fields"]

            ask_event = await generator.__anext__()
            assert ask_event["type"] == "ask_user"
            assert ask_event["ask_type"] == "review"
            assert ask_event["options"] == []
            assert "1-2" not in ask_event["question"]
            assert "3-4" not in ask_event["question"]
            assert "2026-03-02" in ask_event["question"]

            event = await generator.asend("2026-03-02 这学期一共18周")
            assert event["type"] == "tool_call"
            assert event["name"] == "save_period_times"

            event = await generator.__anext__()
            assert event["type"] == "tool_result"
            assert event["result"]["status"] == "ready"
            assert event["result"]["courses"][0]["start_time"] == "08:30"
            assert event["result"]["courses"][0]["end_time"] == "10:15"
            assert event["result"]["courses"][1]["start_time"] == "10:20"
            assert event["result"]["courses"][1]["end_time"] == "11:55"
            assert event["result"]["courses"][1]["week_pattern"] == "odd"

            review_event = await generator.__anext__()
            assert review_event["type"] == "ask_user"
            assert review_event["ask_type"] == "review"
            assert review_event["options"] == ["确认", "取消"]
            assert review_event["data"]["count"] == 2
            assert len(review_event["data"]["courses"]) == 2
            assert review_event["data"]["courses"][1]["week_pattern"] == "odd"

            event = await generator.asend("确认")
            assert event["type"] == "tool_call"
            assert event["name"] == "bulk_import_courses"

            event = await generator.__anext__()
            assert event["type"] == "tool_result"
            assert event["result"]["status"] == "imported"
            assert event["result"]["count"] == 2

            text_event = await generator.__anext__()
            assert text_event["type"] == "text"
            assert text_event["content"]

            done_event = await generator.__anext__()
            assert done_event["type"] == "done"

            result = await db.execute(
                select(Course).where(Course.user_id == "u8").order_by(Course.name)
            )
            imported_courses = list(result.scalars().all())
            assert [
                (course.name, course.start_time, course.end_time, course.week_pattern)
                for course in imported_courses
            ] == [
                ("all-course", "08:30", "10:15", "all"),
                ("odd-course", "10:20", "11:55", "odd"),
            ]
