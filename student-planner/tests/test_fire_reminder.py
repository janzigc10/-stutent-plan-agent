from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models.course import Course
from app.models.reminder import Reminder
from app.models.user import User
from app.services.push_service import PushResult


@pytest_asyncio.fixture
async def setup_user_and_reminder(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(
            id="user-fire-1",
            username="fireuser",
            hashed_password="x",
            push_subscription={
                "endpoint": "https://fcm.googleapis.com/fcm/send/fake",
                "keys": {"p256dh": "abc", "auth": "def"},
            },
        )
        db.add(user)
        course = Course(
            id="course-fire-1",
            user_id="user-fire-1",
            name="高等数学",
            weekday=1,
            start_time="10:00",
            end_time="11:40",
            location="教学楼A301",
        )
        db.add(course)
        reminder = Reminder(
            id="rem-fire-1",
            user_id="user-fire-1",
            target_type="course",
            target_id="course-fire-1",
            remind_at="2026-04-01T09:45:00",
            advance_minutes=15,
            status="pending",
        )
        db.add(reminder)
        await db.commit()

    yield


@pytest.mark.asyncio
@patch("app.services.reminder_scheduler.send_push")
async def test_fire_reminder_success(mock_send, setup_user_and_reminder):
    from tests.conftest import TestSession
    from app.services.reminder_scheduler import fire_reminder

    mock_send.return_value = PushResult(ok=True, status_code=201)

    with patch("app.services.reminder_scheduler.async_session", TestSession):
        await fire_reminder(reminder_id="rem-fire-1", user_id="user-fire-1")

    mock_send.assert_called_once()
    assert "高等数学" in str(mock_send.call_args)

    async with TestSession() as db:
        result = await db.execute(select(Reminder).where(Reminder.id == "rem-fire-1"))
        reminder = result.scalar_one()
        assert reminder.status == "sent"


@pytest.mark.asyncio
@patch("app.services.reminder_scheduler.send_push")
@patch("app.services.reminder_scheduler.schedule_reminder_job")
async def test_fire_reminder_failure_schedules_retry(mock_schedule, mock_send, setup_user_and_reminder):
    from tests.conftest import TestSession
    from app.services.reminder_scheduler import fire_reminder

    mock_send.return_value = PushResult(ok=False, status_code=500, should_unsubscribe=False)

    with patch("app.services.reminder_scheduler.async_session", TestSession):
        await fire_reminder(reminder_id="rem-fire-1", user_id="user-fire-1")

    mock_schedule.assert_called_once()
    assert mock_schedule.call_args.kwargs["attempt"] == 1


@pytest.mark.asyncio
@patch("app.services.reminder_scheduler.send_push")
async def test_fire_reminder_410_clears_subscription(mock_send, setup_user_and_reminder):
    from tests.conftest import TestSession
    from app.services.reminder_scheduler import fire_reminder

    mock_send.return_value = PushResult(ok=False, status_code=410, should_unsubscribe=True)

    with patch("app.services.reminder_scheduler.async_session", TestSession):
        await fire_reminder(reminder_id="rem-fire-1", user_id="user-fire-1")

    async with TestSession() as db:
        result = await db.execute(select(User).where(User.id == "user-fire-1"))
        user = result.scalar_one()
        assert user.push_subscription is None

        result = await db.execute(select(Reminder).where(Reminder.id == "rem-fire-1"))
        reminder = result.scalar_one()
        assert reminder.status == "failed"