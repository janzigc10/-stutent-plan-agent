from datetime import date

import pytest

from app.agent.tool_executor import execute_tool
from app.models.user import User
from app.services.schedule_upload_cache import get_schedule_upload, store_schedule_upload
from tests.conftest import TestSession


@pytest.mark.asyncio
async def test_save_period_times_persists_partial_progress_before_all_fields_complete(setup_db) -> None:
    async with TestSession() as db:
        user = User(
            id="schedule-user-partial-save",
            username="scheduleuser-partial-save",
            hashed_password="x",
        )
        db.add(user)
        await db.commit()

        file_id = store_schedule_upload(
            user_id="schedule-user-partial-save",
            kind="spreadsheet",
            courses=[
                {
                    "name": "odd-course",
                    "weekday": 3,
                    "period": "3-4",
                    "week_start": 1,
                    "week_end": 18,
                    "week_pattern": "odd",
                    "week_text": "\u7b2c1-18\u5468(\u5355\u5468)",
                }
            ],
            status="NEED_PERIOD_TIMES",
            missing_periods=["3-4"],
            missing_semester_fields=["semester_start_date", "term_total_weeks"],
        )

        result = await execute_tool(
            "save_period_times",
            {
                "file_id": file_id,
                "entries": [{"period": "3-4", "time": "10:20-11:55"}],
            },
            db=db,
            user_id="schedule-user-partial-save",
        )

        assert result["status"] == "need_period_times"
        assert result["missing_periods"] == []
        assert "semester_start_date" in result["missing_semester_fields"]
        assert "term_total_weeks" in result["missing_semester_fields"]
        assert result["courses"][0]["start_time"] == "10:20"
        assert result["courses"][0]["end_time"] == "11:55"

        await db.refresh(user)
        assert user.preferences is not None
        assert user.preferences["period_schedule_templates"]["default"]["3-4"] == {
            "start": "10:20",
            "end": "11:55",
        }

        cached = get_schedule_upload("schedule-user-partial-save", file_id)
        assert cached is not None
        assert cached.missing_periods == []
        assert cached.missing_semester_fields == ["semester_start_date", "term_total_weeks"]
        assert cached.courses[0]["start_time"] == "10:20"
        assert cached.courses[0]["end_time"] == "11:55"


@pytest.mark.asyncio
async def test_save_period_times_can_finish_on_second_turn_with_semester_meta_only(setup_db) -> None:
    async with TestSession() as db:
        user = User(
            id="schedule-user-partial-finish",
            username="scheduleuser-partial-finish",
            hashed_password="x",
        )
        db.add(user)
        await db.commit()

        file_id = store_schedule_upload(
            user_id="schedule-user-partial-finish",
            kind="spreadsheet",
            courses=[
                {
                    "name": "all-course",
                    "weekday": 1,
                    "period": "1-2",
                    "week_start": 1,
                    "week_end": 18,
                }
            ],
            status="NEED_PERIOD_TIMES",
            missing_periods=["1-2"],
            missing_semester_fields=["semester_start_date", "term_total_weeks"],
        )

        await execute_tool(
            "save_period_times",
            {
                "file_id": file_id,
                "entries": [{"period": "1-2", "time": "08:30-10:15"}],
            },
            db=db,
            user_id="schedule-user-partial-finish",
        )

        result = await execute_tool(
            "save_period_times",
            {
                "file_id": file_id,
                "semester_start_date": "2026-03-02",
                "term_total_weeks": 18,
            },
            db=db,
            user_id="schedule-user-partial-finish",
        )

        assert result["status"] == "ready"
        assert result["semester_start_date"] == "2026-03-02"
        assert result["term_total_weeks"] == 18
        assert result["courses"][0]["start_time"] == "08:30"
        assert result["courses"][0]["end_time"] == "10:15"

        await db.refresh(user)
        assert user.current_semester_start == date(2026, 3, 2)
