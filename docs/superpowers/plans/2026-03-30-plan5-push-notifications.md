# Plan 5: 推送系统 — APScheduler + Web Push + 自动提醒

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Execution note (2026-03-30):** This machine now has `python` on PATH. If a future worker environment does not, replace `python` commands with `C:\Users\Chen\anaconda3\python.exe`.

**Goal:** Deliver course and task reminders to users via Web Push notifications, scheduled by APScheduler, with automatic reminder creation on course import and retry on failure.

**Architecture:** APScheduler runs as a background scheduler inside the FastAPI process (lifespan hook). A `push_service` module handles VAPID signing and `pywebpush` delivery. A `reminder_scheduler` module scans pending reminders, resolves their fire times, and registers APScheduler jobs. When a job fires, it sends a Web Push and updates the reminder status. Failed pushes retry up to 3 times with increasing delay. A new REST endpoint lets the frontend register/unregister push subscriptions. The existing `set_reminder` tool executor is updated to schedule the APScheduler job immediately after DB insert.

**Tech Stack:** APScheduler 3.x (AsyncIOScheduler), pywebpush, py-vapid (VAPID key generation), existing FastAPI + SQLAlchemy async stack

**Depends on:** Plan 1 (Reminder model, User.push_subscription, Course/Task models), Plan 2 (agent tools, tool_executor)

---

## File Structure

```
student-planner/
├── app/
│   ├── services/
│   │   ├── push_service.py            # Web Push delivery: send_push(), VAPID config
│   │   └── reminder_scheduler.py      # APScheduler integration: schedule/cancel/fire reminders
│   ├── routers/
│   │   └── push.py                    # POST /api/push/subscribe, DELETE /api/push/subscribe
│   ├── schemas/
│   │   └── push.py                    # PushSubscription Pydantic schema
│   ├── agent/
│   │   └── tool_executor.py           # (modify: _set_reminder schedules APScheduler job)
│   ├── config.py                      # (modify: add VAPID key settings)
│   └── main.py                        # (modify: start/stop scheduler in lifespan)
├── tests/
│   ├── test_push_service.py           # Web Push delivery unit tests (mocked pywebpush)
│   ├── test_reminder_scheduler.py     # Scheduler core logic unit tests
│   ├── test_push_subscribe_api.py     # Subscription endpoint tests
│   ├── test_scheduler_integration.py  # APScheduler job management tests
│   ├── test_fire_reminder.py          # Fire callback + retry logic tests
│   ├── test_set_reminder_scheduling.py # set_reminder tool scheduling tests
│   ├── test_auto_reminder.py          # Auto-reminder on course import tests
│   └── test_reminder_reload.py        # Startup reload tests
└── scripts/
    └── generate_vapid_keys.py         # One-time VAPID key pair generator
```

---

### Task 1: VAPID Key Generator Script + Config

The simplest starting point — generate VAPID keys and wire them into settings. Everything else depends on having keys.

**Files:**
- Create: `student-planner/scripts/generate_vapid_keys.py`
- Modify: `student-planner/app/config.py`

- [x] **Step 1: Create the VAPID key generator script**

```python
# student-planner/scripts/generate_vapid_keys.py
"""Generate a VAPID key pair for Web Push.

Run once:
    python scripts/generate_vapid_keys.py

Copy the output into your .env or environment variables.
"""

from py_vapid import Vapid

vapid = Vapid()
vapid.generate_keys()

print("Add these to your environment:\n")
print(f'SP_VAPID_PRIVATE_KEY="{vapid.private_pem().decode().strip()}"')
print(f'SP_VAPID_PUBLIC_KEY="{vapid.public_key_urlsafe_base64()}"')
print(f'SP_VAPID_CLAIMS_EMAIL="mailto:admin@studentplanner.local"')
```

- [x] **Step 2: Add VAPID settings to config.py**

Add three new fields to the `Settings` class in `student-planner/app/config.py`:

```python
# Add after the existing session_timeout_minutes field:
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_claims_email: str = "mailto:admin@studentplanner.local"
```

- [x] **Step 3: Add pywebpush and py-vapid to dependencies**

Add to the `dependencies` list in `student-planner/pyproject.toml`:

```toml
    "pywebpush>=2.0.0",
    "py-vapid>=1.9.0",
```

- [x] **Step 4: Commit**

```bash
git add student-planner/scripts/generate_vapid_keys.py student-planner/app/config.py student-planner/pyproject.toml
git commit -m "feat: add VAPID key config and generator script"
```

---

### Task 2: Push Service — Web Push Delivery

Pure delivery module. Takes a subscription dict and a payload string, sends via pywebpush. No scheduling logic — just "send this push to this user."

**Files:**
- Create: `student-planner/app/services/push_service.py`
- Create: `student-planner/tests/test_push_service.py`

- [x] **Step 1: Write the failing tests**

```python
# student-planner/tests/test_push_service.py
import pytest
from unittest.mock import patch, MagicMock

from app.services.push_service import send_push, PushResult


def _make_subscription():
    return {
        "endpoint": "https://fcm.googleapis.com/fcm/send/fake-token",
        "keys": {
            "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8p8REfWPU=",
            "auth": "tBHItJI5svbpC7-BnWW_IA==",
        },
    }


@patch("app.services.push_service.webpush")
def test_send_push_success(mock_webpush):
    """Successful push returns PushResult with ok=True."""
    mock_webpush.return_value = MagicMock(status_code=201)

    result = send_push(
        subscription=_make_subscription(),
        title="高等数学",
        body="10:00 @ 教学楼A301",
    )

    assert result.ok is True
    assert result.status_code == 201
    mock_webpush.assert_called_once()


@patch("app.services.push_service.webpush")
def test_send_push_expired_subscription(mock_webpush):
    """410 Gone means subscription expired — result signals unsubscribe."""
    from pywebpush import WebPushException

    response_mock = MagicMock()
    response_mock.status_code = 410
    mock_webpush.side_effect = WebPushException("Gone", response=response_mock)

    result = send_push(
        subscription=_make_subscription(),
        title="Test",
        body="Test body",
    )

    assert result.ok is False
    assert result.should_unsubscribe is True


@patch("app.services.push_service.webpush")
def test_send_push_other_failure(mock_webpush):
    """Non-410 failure returns ok=False, should_unsubscribe=False."""
    from pywebpush import WebPushException

    response_mock = MagicMock()
    response_mock.status_code = 500
    mock_webpush.side_effect = WebPushException("Server error", response=response_mock)

    result = send_push(
        subscription=_make_subscription(),
        title="Test",
        body="Test body",
    )

    assert result.ok is False
    assert result.should_unsubscribe is False
    assert result.status_code == 500


def test_send_push_no_subscription():
    """None subscription returns ok=False immediately."""
    result = send_push(subscription=None, title="Test", body="Test body")
    assert result.ok is False
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_push_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.push_service'`

- [x] **Step 3: Implement push_service.py**

```python
# student-planner/app/services/push_service.py
"""Web Push delivery via pywebpush."""

import json
from dataclasses import dataclass, field
from typing import Any

from pywebpush import WebPushException, webpush

from app.config import settings


@dataclass
class PushResult:
    ok: bool
    status_code: int = 0
    should_unsubscribe: bool = False
    error: str = ""


def send_push(
    subscription: dict[str, Any] | None,
    title: str,
    body: str,
) -> PushResult:
    """Send a Web Push notification. Returns a PushResult."""
    if subscription is None:
        return PushResult(ok=False, error="No subscription")

    payload = json.dumps({"title": title, "body": body}, ensure_ascii=False)

    vapid_claims = {"sub": settings.vapid_claims_email}
    try:
        response = webpush(
            subscription_info=subscription,
            data=payload,
            vapid_private_key=settings.vapid_private_key,
            vapid_claims=vapid_claims,
        )
        return PushResult(ok=True, status_code=response.status_code)
    except WebPushException as exc:
        status = getattr(exc.response, "status_code", 0) if exc.response else 0
        return PushResult(
            ok=False,
            status_code=status,
            should_unsubscribe=(status == 410),
            error=str(exc),
        )
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_push_service.py -v`
Expected: 4 passed

- [x] **Step 5: Commit**

```bash
git add student-planner/app/services/push_service.py student-planner/tests/test_push_service.py
git commit -m "feat: add push_service with Web Push delivery via pywebpush"
```

---

### Task 3: Push Subscription Endpoint

Frontend calls this to register/unregister its push subscription. Stores the subscription JSON in `User.push_subscription`.

**Files:**
- Create: `student-planner/app/schemas/push.py`
- Create: `student-planner/app/routers/push.py`
- Modify: `student-planner/app/main.py`
- Create: `student-planner/tests/test_push_subscribe_api.py`

- [x] **Step 1: Write the failing tests**

```python
# student-planner/tests/test_push_subscribe_api.py
import pytest
import pytest_asyncio
from httpx import AsyncClient


SUBSCRIPTION_PAYLOAD = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/fake-token",
    "keys": {
        "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8p8REfWPU=",
        "auth": "tBHItJI5svbpC7-BnWW_IA==",
    },
}


@pytest.mark.asyncio
async def test_subscribe_push(auth_client: AsyncClient):
    """POST /api/push/subscribe stores subscription on user."""
    response = await auth_client.post("/api/push/subscribe", json=SUBSCRIPTION_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["status"] == "subscribed"


@pytest.mark.asyncio
async def test_subscribe_then_get_vapid_key(auth_client: AsyncClient):
    """GET /api/push/vapid-key returns the public VAPID key."""
    response = await auth_client.get("/api/push/vapid-key")
    assert response.status_code == 200
    assert "public_key" in response.json()


@pytest.mark.asyncio
async def test_unsubscribe_push(auth_client: AsyncClient):
    """DELETE /api/push/subscribe clears subscription."""
    await auth_client.post("/api/push/subscribe", json=SUBSCRIPTION_PAYLOAD)
    response = await auth_client.delete("/api/push/subscribe")
    assert response.status_code == 200
    assert response.json()["status"] == "unsubscribed"


@pytest.mark.asyncio
async def test_subscribe_requires_auth(client: AsyncClient):
    """Unauthenticated request is rejected."""
    response = await client.post("/api/push/subscribe", json=SUBSCRIPTION_PAYLOAD)
    assert response.status_code == 403
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_push_subscribe_api.py -v`
Expected: FAIL — route not found (404)

- [x] **Step 3: Create the Pydantic schema**

```python
# student-planner/app/schemas/push.py
from pydantic import BaseModel


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionIn(BaseModel):
    endpoint: str
    keys: PushSubscriptionKeys
```

- [x] **Step 4: Create the push router**

```python
# student-planner/app/routers/push.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.push import PushSubscriptionIn

router = APIRouter(prefix="/push", tags=["push"])


@router.post("/subscribe")
async def subscribe(
    body: PushSubscriptionIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user.push_subscription = body.model_dump()
    db.add(user)
    await db.commit()
    return {"status": "subscribed"}


@router.delete("/subscribe")
async def unsubscribe(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user.push_subscription = None
    db.add(user)
    await db.commit()
    return {"status": "unsubscribed"}


@router.get("/vapid-key")
async def get_vapid_key(user: User = Depends(get_current_user)):
    return {"public_key": settings.vapid_public_key}
```

- [x] **Step 5: Mount the push router in main.py**

In `student-planner/app/main.py`, add the import and include:

```python
from app.routers import auth, chat, courses, exams, push, reminders, schedule_import, tasks
```

And in `create_app()`, add:

```python
    app.include_router(push.router, prefix="/api")
```

- [x] **Step 6: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_push_subscribe_api.py -v`
Expected: 4 passed

- [x] **Step 7: Commit**

```bash
git add student-planner/app/schemas/push.py student-planner/app/routers/push.py student-planner/app/main.py student-planner/tests/test_push_subscribe_api.py
git commit -m "feat: add push subscription endpoints and VAPID key endpoint"
```

---

### Task 4: Reminder Scheduler — Core Logic

The brain of the push system. Resolves reminder fire times, registers APScheduler jobs, handles the fire callback (send push + update status + retry).

**Files:**
- Create: `student-planner/app/services/reminder_scheduler.py`
- Create: `student-planner/tests/test_reminder_scheduler.py`

- [x] **Step 1: Write the failing tests**

```python
# student-planner/tests/test_reminder_scheduler.py
import pytest
from datetime import datetime, date
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.reminder_scheduler import (
    resolve_fire_time,
    build_push_payload,
)


def test_resolve_fire_time_task_reminder():
    """Task reminder: remind_at is an ISO datetime string, advance_minutes subtracted."""
    remind_at = "2026-04-01T10:00:00"
    result = resolve_fire_time(remind_at, advance_minutes=15)
    assert result == datetime(2026, 4, 1, 9, 45)


def test_resolve_fire_time_course_reminder():
    """Course reminder: remind_at is 'course:<id>:-15min', needs course lookup.
    For the scheduler, we pre-resolve course reminders to concrete datetimes
    before storing, so this format should not appear at fire-time resolution.
    We test the concrete datetime path only."""
    remind_at = "2026-04-01T08:00:00"
    result = resolve_fire_time(remind_at, advance_minutes=15)
    assert result == datetime(2026, 4, 1, 7, 45)


def test_resolve_fire_time_zero_advance():
    """Zero advance means fire at exact time."""
    remind_at = "2026-04-01T10:00:00"
    result = resolve_fire_time(remind_at, advance_minutes=0)
    assert result == datetime(2026, 4, 1, 10, 0)


def test_build_push_payload_course():
    """Course reminder payload includes name, time, location."""
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
    """Task reminder payload includes title and time."""
    payload = build_push_payload(
        target_type="task",
        target_name="复习线性代数",
        target_time="14:00-16:00",
    )
    assert payload["title"] == "任务提醒"
    assert "复习线性代数" in payload["body"]
    assert "14:00-16:00" in payload["body"]
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_reminder_scheduler.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.reminder_scheduler'`

- [x] **Step 3: Implement reminder_scheduler.py**

```python
# student-planner/app/services/reminder_scheduler.py
"""Reminder scheduling and fire logic."""

from datetime import datetime, timedelta
from typing import Any


def resolve_fire_time(event_time: str, advance_minutes: int = 15) -> datetime:
    """Parse an event_time string and subtract advance_minutes to get the fire time."""
    dt = datetime.fromisoformat(event_time)
    return dt - timedelta(minutes=advance_minutes)


def build_push_payload(
    target_type: str,
    target_name: str,
    target_time: str,
    target_location: str | None = None,
) -> dict[str, str]:
    """Build the push notification title and body."""
    if target_type == "course":
        title = "课程提醒"
        location_part = f" @ {target_location}" if target_location else ""
        body = f"{target_time} {target_name}{location_part}"
    else:
        title = "任务提醒"
        body = f"该{target_name}了（{target_time}）"
    return {"title": title, "body": body}
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_reminder_scheduler.py -v`
Expected: 5 passed

- [x] **Step 5: Commit**

```bash
git add student-planner/app/services/reminder_scheduler.py student-planner/tests/test_reminder_scheduler.py
git commit -m "feat: add reminder_scheduler with fire time resolution and payload builder"
```

---

### Task 5: APScheduler Integration — Lifespan + Job Management

Wire APScheduler into the FastAPI app. Add functions to schedule a reminder job and cancel one. The scheduler starts on app startup and shuts down on app shutdown.

**Files:**
- Modify: `student-planner/app/services/reminder_scheduler.py`
- Modify: `student-planner/app/main.py`
- Create: `student-planner/tests/test_scheduler_integration.py`

- [x] **Step 1: Write the failing tests**

```python
# student-planner/tests/test_scheduler_integration.py
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.reminder_scheduler import (
    schedule_reminder_job,
    cancel_reminder_job,
    get_scheduler,
)


def test_get_scheduler_returns_singleton():
    """get_scheduler() returns the same instance each time."""
    s1 = get_scheduler()
    s2 = get_scheduler()
    assert s1 is s2


def test_schedule_reminder_job_adds_job():
    """schedule_reminder_job adds a date-trigger job to the scheduler."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start(paused=True)

    fire_time = datetime.now() + timedelta(hours=1)
    job = schedule_reminder_job(
        reminder_id="rem-123",
        fire_time=fire_time,
        user_id="user-456",
    )

    assert job is not None
    assert job.id == "reminder:rem-123"

    # Cleanup
    scheduler.remove_job(job.id)


def test_cancel_reminder_job():
    """cancel_reminder_job removes the job without error."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start(paused=True)

    fire_time = datetime.now() + timedelta(hours=1)
    schedule_reminder_job(
        reminder_id="rem-789",
        fire_time=fire_time,
        user_id="user-456",
    )

    # Should not raise
    cancel_reminder_job("rem-789")

    # Cancelling again should also not raise
    cancel_reminder_job("rem-789")
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_scheduler_integration.py -v`
Expected: FAIL — `ImportError: cannot import name 'schedule_reminder_job'`

- [x] **Step 3: Add scheduler functions to reminder_scheduler.py**

Append to `student-planner/app/services/reminder_scheduler.py`:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    """Return the singleton AsyncIOScheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


def schedule_reminder_job(
    reminder_id: str,
    fire_time: datetime,
    user_id: str,
) -> Any:
    """Add a one-shot job that fires at fire_time."""
    scheduler = get_scheduler()
    job_id = f"reminder:{reminder_id}"
    job = scheduler.add_job(
        "app.services.reminder_scheduler:fire_reminder",
        trigger="date",
        run_date=fire_time,
        id=job_id,
        replace_existing=True,
        kwargs={"reminder_id": reminder_id, "user_id": user_id},
    )
    return job


def cancel_reminder_job(reminder_id: str) -> None:
    """Remove a scheduled reminder job. No-op if not found."""
    scheduler = get_scheduler()
    try:
        scheduler.remove_job(f"reminder:{reminder_id}")
    except JobLookupError:
        pass


async def fire_reminder(reminder_id: str, user_id: str) -> None:
    """Callback when a reminder fires. Sends push and updates status.
    Implemented in Task 6."""
    pass
```

- [x] **Step 4: Add APScheduler to dependencies**

Add to the `dependencies` list in `student-planner/pyproject.toml`:

```toml
    "apscheduler>=3.10.0,<4.0.0",
```

- [x] **Step 5: Wire scheduler into FastAPI lifespan in main.py**

Replace the `create_app` function in `student-planner/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import auth, chat, courses, exams, push, reminders, schedule_import, tasks
from app.services.reminder_scheduler import get_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = get_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    app = FastAPI(title="Student Planner", version="0.1.0", lifespan=lifespan)
    app.include_router(auth.router, prefix="/api")
    app.include_router(courses.router, prefix="/api")
    app.include_router(exams.router, prefix="/api")
    app.include_router(tasks.router, prefix="/api")
    app.include_router(reminders.router, prefix="/api")
    app.include_router(schedule_import.router, prefix="/api")
    app.include_router(push.router, prefix="/api")
    app.include_router(chat.router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

- [x] **Step 6: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_scheduler_integration.py -v`
Expected: 3 passed

- [x] **Step 7: Commit**

```bash
git add student-planner/app/services/reminder_scheduler.py student-planner/app/main.py student-planner/pyproject.toml student-planner/tests/test_scheduler_integration.py
git commit -m "feat: add APScheduler integration with lifespan and job management"
```

---

### Task 6: Fire Reminder — Send Push + Retry Logic

Implement the `fire_reminder` callback. When a reminder fires: look up the user's push subscription, look up the target (course/task) for display info, send the push, update reminder status. On failure, retry up to 3 times with increasing delay (1min, 5min, 15min). On 410 Gone, clear the user's push_subscription.

**Files:**
- Modify: `student-planner/app/services/reminder_scheduler.py`
- Create: `student-planner/tests/test_fire_reminder.py`

- [x] **Step 1: Write the failing tests**

```python
# student-planner/tests/test_fire_reminder.py
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.reminder import Reminder
from app.models.course import Course
from app.models.task import Task
from app.services.push_service import PushResult


@pytest_asyncio.fixture
async def setup_user_and_reminder(setup_db):
    """Create a user with push subscription and a pending reminder."""
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
            remind_at="2026-04-01T10:00:00",
            status="pending",
        )
        db.add(reminder)
        await db.commit()

    yield

    async with TestSession() as db:
        from sqlalchemy import text
        await db.execute(text("DELETE FROM reminders WHERE id = 'rem-fire-1'"))
        await db.execute(text("DELETE FROM courses WHERE id = 'course-fire-1'"))
        await db.execute(text("DELETE FROM users WHERE id = 'user-fire-1'"))
        await db.commit()


@pytest.mark.asyncio
@patch("app.services.reminder_scheduler.send_push")
async def test_fire_reminder_success(mock_send, setup_user_and_reminder):
    """Successful fire sends push and marks reminder as 'sent'."""
    mock_send.return_value = PushResult(ok=True, status_code=201)

    from app.services.reminder_scheduler import fire_reminder
    await fire_reminder(reminder_id="rem-fire-1", user_id="user-fire-1")

    mock_send.assert_called_once()
    call_kwargs = mock_send.call_args
    assert "高等数学" in call_kwargs.kwargs.get("body", "") or "高等数学" in str(call_kwargs)

    # Verify reminder status updated
    from tests.conftest import TestSession
    from sqlalchemy import select
    async with TestSession() as db:
        result = await db.execute(select(Reminder).where(Reminder.id == "rem-fire-1"))
        reminder = result.scalar_one()
        assert reminder.status == "sent"


@pytest.mark.asyncio
@patch("app.services.reminder_scheduler.send_push")
@patch("app.services.reminder_scheduler.schedule_reminder_job")
async def test_fire_reminder_failure_schedules_retry(mock_schedule, mock_send, setup_user_and_reminder):
    """Failed push schedules a retry job."""
    mock_send.return_value = PushResult(ok=False, status_code=500, should_unsubscribe=False)

    from app.services.reminder_scheduler import fire_reminder
    await fire_reminder(reminder_id="rem-fire-1", user_id="user-fire-1")

    # Should schedule a retry
    mock_schedule.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.reminder_scheduler.send_push")
async def test_fire_reminder_410_clears_subscription(mock_send, setup_user_and_reminder):
    """410 Gone clears user's push_subscription and marks reminder failed."""
    mock_send.return_value = PushResult(ok=False, status_code=410, should_unsubscribe=True)

    from app.services.reminder_scheduler import fire_reminder
    await fire_reminder(reminder_id="rem-fire-1", user_id="user-fire-1")

    from tests.conftest import TestSession
    from sqlalchemy import select
    async with TestSession() as db:
        result = await db.execute(select(User).where(User.id == "user-fire-1"))
        user = result.scalar_one()
        assert user.push_subscription is None

        result = await db.execute(select(Reminder).where(Reminder.id == "rem-fire-1"))
        reminder = result.scalar_one()
        assert reminder.status == "failed"
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_fire_reminder.py -v`
Expected: FAIL — `fire_reminder` is a no-op pass

- [x] **Step 3: Implement fire_reminder in reminder_scheduler.py**

Replace the `fire_reminder` function in `student-planner/app/services/reminder_scheduler.py`:

```python
from app.database import async_session
from app.services.push_service import send_push, PushResult

# Retry delays in minutes: attempt 1 → 1min, attempt 2 → 5min, attempt 3 → 15min
RETRY_DELAYS = [1, 5, 15]


async def fire_reminder(reminder_id: str, user_id: str, attempt: int = 0) -> None:
    """Callback when a reminder fires. Sends push and updates status."""
    from sqlalchemy import select
    from app.models.reminder import Reminder
    from app.models.user import User
    from app.models.course import Course
    from app.models.task import Task

    async with async_session() as db:
        # Load reminder
        result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
        reminder = result.scalar_one_or_none()
        if reminder is None or reminder.status == "sent":
            return

        # Load user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None or user.push_subscription is None:
            reminder.status = "failed"
            await db.commit()
            return

        # Load target for display info
        if reminder.target_type == "course":
            result = await db.execute(select(Course).where(Course.id == reminder.target_id))
            target = result.scalar_one_or_none()
            target_name = target.name if target else "未知课程"
            target_time = f"{target.start_time}" if target else ""
            target_location = target.location if target else None
        else:
            result = await db.execute(select(Task).where(Task.id == reminder.target_id))
            target = result.scalar_one_or_none()
            target_name = target.title if target else "未知任务"
            target_time = f"{target.start_time}-{target.end_time}" if target else ""
            target_location = None

        payload = build_push_payload(
            target_type=reminder.target_type,
            target_name=target_name,
            target_time=target_time,
            target_location=target_location,
        )

        push_result = send_push(
            subscription=user.push_subscription,
            title=payload["title"],
            body=payload["body"],
        )

        if push_result.ok:
            reminder.status = "sent"
            await db.commit()
            return

        if push_result.should_unsubscribe:
            user.push_subscription = None
            reminder.status = "failed"
            await db.commit()
            return

        # Retry logic
        if attempt < len(RETRY_DELAYS):
            retry_time = datetime.now() + timedelta(minutes=RETRY_DELAYS[attempt])
            schedule_reminder_job(
                reminder_id=reminder_id,
                fire_time=retry_time,
                user_id=user_id,
                attempt=attempt + 1,
            )
        else:
            reminder.status = "failed"
            await db.commit()
```

- [x] **Step 4: Update schedule_reminder_job to accept attempt parameter**

Update the `schedule_reminder_job` function signature and kwargs:

```python
def schedule_reminder_job(
    reminder_id: str,
    fire_time: datetime,
    user_id: str,
    attempt: int = 0,
) -> Any:
    """Add a one-shot job that fires at fire_time."""
    scheduler = get_scheduler()
    job_id = f"reminder:{reminder_id}"
    if attempt > 0:
        job_id = f"reminder:{reminder_id}:retry{attempt}"
    job = scheduler.add_job(
        "app.services.reminder_scheduler:fire_reminder",
        trigger="date",
        run_date=fire_time,
        id=job_id,
        replace_existing=True,
        kwargs={"reminder_id": reminder_id, "user_id": user_id, "attempt": attempt},
    )
    return job
```

- [x] **Step 5: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_fire_reminder.py -v`
Expected: 3 passed

- [x] **Step 6: Commit**

```bash
git add student-planner/app/services/reminder_scheduler.py student-planner/tests/test_fire_reminder.py
git commit -m "feat: implement fire_reminder with push delivery and retry logic"
```

---

### Task 7: Update set_reminder Tool — Schedule APScheduler Job on Create

Currently `_set_reminder` in `tool_executor.py` creates a Reminder row but doesn't schedule anything. Now it needs to: (1) compute the next event start time, (2) store `remind_at` as the actual trigger-time ISO datetime, (3) persist `advance_minutes`, and (4) call `schedule_reminder_job` to register the APScheduler job.

**Files:**
- Modify: `student-planner/app/agent/tool_executor.py:250-284`
- Create: `student-planner/tests/test_set_reminder_scheduling.py`

- [x] **Step 1: Write the failing tests**

```python
# student-planner/tests/test_set_reminder_scheduling.py
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.task import Task
from app.models.reminder import Reminder
from app.models.user import User
from app.agent.tool_executor import execute_tool


@pytest_asyncio.fixture
async def setup_course_and_task(setup_db):
    """Create a user, course, and task for reminder tests."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(
            id="user-sched-1",
            username="scheduser",
            hashed_password="x",
        )
        db.add(user)

        course = Course(
            id="course-sched-1",
            user_id="user-sched-1",
            name="线性代数",
            weekday=2,
            start_time="14:00",
            end_time="15:40",
            location="理学楼B201",
        )
        db.add(course)

        task = Task(
            id="task-sched-1",
            user_id="user-sched-1",
            title="复习概率论",
            scheduled_date="2026-04-02",
            start_time="10:00",
            end_time="12:00",
            status="pending",
        )
        db.add(task)
        await db.commit()

    yield

    async with TestSession() as db:
        from sqlalchemy import text
        await db.execute(text("DELETE FROM reminders WHERE user_id = 'user-sched-1'"))
        await db.execute(text("DELETE FROM tasks WHERE id = 'task-sched-1'"))
        await db.execute(text("DELETE FROM courses WHERE id = 'course-sched-1'"))
        await db.execute(text("DELETE FROM users WHERE id = 'user-sched-1'"))
        await db.commit()


@pytest.mark.asyncio
@patch("app.agent.tool_executor.schedule_reminder_job")
async def test_set_reminder_task_schedules_job(mock_schedule, setup_course_and_task):
    """set_reminder for a task creates a Reminder and schedules an APScheduler job."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        result = await execute_tool(
            "set_reminder",
            {"target_type": "task", "target_id": "task-sched-1", "advance_minutes": 15},
            db,
            "user-sched-1",
        )

    assert result["status"] == "reminder_set"
    mock_schedule.assert_called_once()
    call_kwargs = mock_schedule.call_args.kwargs
    assert call_kwargs["user_id"] == "user-sched-1"


@pytest.mark.asyncio
@patch("app.agent.tool_executor.schedule_reminder_job")
async def test_set_reminder_task_stores_iso_datetime(mock_schedule, setup_course_and_task):
    """set_reminder for a task stores remind_at as ISO datetime."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        result = await execute_tool(
            "set_reminder",
            {"target_type": "task", "target_id": "task-sched-1", "advance_minutes": 15},
            db,
            "user-sched-1",
        )

    assert "T" in result["remind_at"]  # ISO datetime format


@pytest.mark.asyncio
@patch("app.agent.tool_executor.schedule_reminder_job")
async def test_set_reminder_course_stores_iso_datetime(mock_schedule, setup_course_and_task):
    """set_reminder for a course stores remind_at as ISO datetime (next occurrence)."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        result = await execute_tool(
            "set_reminder",
            {"target_type": "course", "target_id": "course-sched-1", "advance_minutes": 15},
            db,
            "user-sched-1",
        )

    assert "T" in result["remind_at"]
    mock_schedule.assert_called_once()
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_set_reminder_scheduling.py -v`
Expected: FAIL — `schedule_reminder_job` not imported in tool_executor

- [x] **Step 3: Update _set_reminder in tool_executor.py**

Replace the `_set_reminder` function in `student-planner/app/agent/tool_executor.py`:

```python
from app.services.reminder_scheduler import (
    compute_next_course_occurrence,
    resolve_fire_time,
    schedule_reminder_job,
)


async def _set_reminder(
    db: AsyncSession,
    user_id: str,
    target_type: str,
    target_id: str,
    advance_minutes: int = 15,
    **kwargs,
) -> dict[str, Any]:
    if target_type == "course":
        result = await db.execute(
            select(Course).where(Course.id == target_id, Course.user_id == user_id)
        )
        target = result.scalar_one_or_none()
        if target is None:
            return {"error": "Course not found"}
        event_time = compute_next_course_occurrence(
            weekday=target.weekday,
            start_time=target.start_time,
        ).isoformat(timespec="seconds")
    else:
        result = await db.execute(
            select(Task).where(Task.id == target_id, Task.user_id == user_id)
        )
        target = result.scalar_one_or_none()
        if target is None:
            return {"error": "Task not found"}
        event_time = f"{target.scheduled_date}T{target.start_time}:00"

    fire_time = resolve_fire_time(event_time, advance_minutes=advance_minutes)
    remind_at = fire_time.isoformat(timespec="seconds")

    reminder = Reminder(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        remind_at=remind_at,
        advance_minutes=advance_minutes,
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)

    schedule_reminder_job(
        reminder_id=reminder.id,
        fire_time=fire_time,
        user_id=user_id,
    )

    return {
        "id": reminder.id,
        "status": "reminder_set",
        "remind_at": remind_at,
        "advance_minutes": advance_minutes,
    }
```

Also add the import at the top of `tool_executor.py`:

```python
from app.services.reminder_scheduler import resolve_fire_time, schedule_reminder_job
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_set_reminder_scheduling.py -v`
Expected: 3 passed

- [x] **Step 5: Run existing reminder tests to check for regressions**

Run: `cd student-planner && python -m pytest tests/ -k "reminder" -v`
Expected: All reminder-related tests pass

- [x] **Step 6: Commit**

```bash
git add student-planner/app/agent/tool_executor.py student-planner/tests/test_set_reminder_scheduling.py
git commit -m "feat: set_reminder now stores ISO datetime and schedules APScheduler job"
```

---

### Task 8: Auto-Reminder on Course Import

When courses are bulk-imported (via `bulk_import_courses` tool), automatically create a reminder for each course with the default 15-minute advance. This implements the design doc's "课前提醒是确定性流程" — no LLM involvement needed.

**Files:**
- Modify: `student-planner/app/agent/tool_executor.py` (the `_bulk_import_courses` function)
- Create: `student-planner/tests/test_auto_reminder.py`

- [x] **Step 1: Write the failing tests**

```python
# student-planner/tests/test_auto_reminder.py
import pytest
import pytest_asyncio
from unittest.mock import patch
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.reminder import Reminder
from app.models.user import User
from app.agent.tool_executor import execute_tool


@pytest_asyncio.fixture
async def setup_import_user(setup_db):
    """Create a user for import tests."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(
            id="user-import-1",
            username="importuser",
            hashed_password="x",
        )
        db.add(user)
        await db.commit()

    yield

    async with TestSession() as db:
        from sqlalchemy import text
        await db.execute(text("DELETE FROM reminders WHERE user_id = 'user-import-1'"))
        await db.execute(text("DELETE FROM courses WHERE user_id = 'user-import-1'"))
        await db.execute(text("DELETE FROM users WHERE id = 'user-import-1'"))
        await db.commit()


@pytest.mark.asyncio
@patch("app.agent.tool_executor.schedule_reminder_job")
async def test_bulk_import_creates_reminders(mock_schedule, setup_import_user):
    """bulk_import_courses creates a Reminder for each imported course."""
    from tests.conftest import TestSession

    courses_data = [
        {
            "name": "高等数学",
            "weekday": 1,
            "start_time": "08:00",
            "end_time": "09:40",
            "location": "教学楼A301",
        },
        {
            "name": "线性代数",
            "weekday": 3,
            "start_time": "10:00",
            "end_time": "11:40",
            "location": "理学楼B201",
        },
    ]

    async with TestSession() as db:
        result = await execute_tool(
            "bulk_import_courses",
            {"courses": courses_data},
            db,
            "user-import-1",
        )

    assert result["status"] == "imported"
    assert result["count"] == 2
    assert result["reminders_created"] == 2

    # Verify reminders exist in DB
    async with TestSession() as db:
        rem_result = await db.execute(
            select(Reminder).where(Reminder.user_id == "user-import-1")
        )
        reminders = list(rem_result.scalars().all())
        assert len(reminders) == 2
        assert all(r.target_type == "course" for r in reminders)


@pytest.mark.asyncio
@patch("app.agent.tool_executor.schedule_reminder_job")
async def test_bulk_import_reminder_has_iso_datetime(mock_schedule, setup_import_user):
    """Auto-created reminders store remind_at as ISO datetime."""
    from tests.conftest import TestSession

    courses_data = [
        {
            "name": "概率论",
            "weekday": 5,
            "start_time": "14:00",
            "end_time": "15:40",
        },
    ]

    async with TestSession() as db:
        await execute_tool(
            "bulk_import_courses",
            {"courses": courses_data},
            db,
            "user-import-1",
        )

    async with TestSession() as db:
        rem_result = await db.execute(
            select(Reminder).where(Reminder.user_id == "user-import-1")
        )
        reminder = rem_result.scalar_one()
        assert "T" in reminder.remind_at
        assert "14:00" in reminder.remind_at
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_auto_reminder.py -v`
Expected: FAIL — `reminders_created` key not in result / no reminders created

- [x] **Step 3: Update _bulk_import_courses in tool_executor.py**

Replace the `_bulk_import_courses` function in `student-planner/app/agent/tool_executor.py`:

```python
async def _bulk_import_courses(
    db: AsyncSession,
    user_id: str,
    courses: list[dict[str, Any]],
    **kwargs,
) -> dict[str, Any]:
    created: list[str] = []
    reminders_created = 0

    for course_data in courses:
        course = Course(
            user_id=user_id,
            name=course_data["name"],
            teacher=course_data.get("teacher"),
            location=course_data.get("location"),
            weekday=course_data["weekday"],
            start_time=course_data["start_time"],
            end_time=course_data["end_time"],
            week_start=course_data.get("week_start", 1),
            week_end=course_data.get("week_end", 16),
        )
        db.add(course)
        await db.flush()

        event_time = compute_next_course_occurrence(
            weekday=course.weekday,
            start_time=course.start_time,
        ).isoformat(timespec="seconds")
        fire_time = resolve_fire_time(event_time, advance_minutes=15)
        reminder = Reminder(
            user_id=user_id,
            target_type="course",
            target_id=course.id,
            remind_at=fire_time.isoformat(timespec="seconds"),
            advance_minutes=15,
        )
        db.add(reminder)
        await db.flush()

        schedule_reminder_job(
            reminder_id=reminder.id,
            fire_time=fire_time,
            user_id=user_id,
        )

        created.append(course_data["name"])
        reminders_created += 1

    await db.commit()
    return {
        "status": "imported",
        "count": len(created),
        "courses": created,
        "reminders_created": reminders_created,
    }
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_auto_reminder.py -v`
Expected: 2 passed

- [x] **Step 5: Run all tests to check for regressions**

Run: `cd student-planner && python -m pytest tests/ -v`
Expected: All tests pass

- [x] **Step 6: Commit**

```bash
git add student-planner/app/agent/tool_executor.py student-planner/tests/test_auto_reminder.py
git commit -m "feat: auto-create reminders on bulk course import"
```

---

### Task 9: Startup Reminder Reload

When the server restarts, all pending reminders in the DB need to be re-registered with APScheduler (since APScheduler's in-memory job store is lost on restart). Add a startup function that queries all pending reminders and schedules them.

**Files:**
- Modify: `student-planner/app/services/reminder_scheduler.py`
- Modify: `student-planner/app/main.py`
- Create: `student-planner/tests/test_reminder_reload.py`

- [x] **Step 1: Write the failing tests**

```python
# student-planner/tests/test_reminder_reload.py
import pytest
import pytest_asyncio
from unittest.mock import patch, call
from datetime import datetime

from sqlalchemy import select

from app.models.user import User
from app.models.reminder import Reminder


@pytest_asyncio.fixture
async def setup_pending_reminders(setup_db):
    """Create pending reminders for reload test."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(
            id="user-reload-1",
            username="reloaduser",
            hashed_password="x",
        )
        db.add(user)

        r1 = Reminder(
            id="rem-reload-1",
            user_id="user-reload-1",
            target_type="task",
            target_id="task-fake-1",
            remind_at="2026-04-05T10:00:00",
            status="pending",
        )
        r2 = Reminder(
            id="rem-reload-2",
            user_id="user-reload-1",
            target_type="course",
            target_id="course-fake-1",
            remind_at="2026-04-05T14:00:00",
            status="pending",
        )
        r3 = Reminder(
            id="rem-reload-3",
            user_id="user-reload-1",
            target_type="task",
            target_id="task-fake-2",
            remind_at="2026-04-05T16:00:00",
            status="sent",  # Already sent — should NOT be reloaded
        )
        db.add_all([r1, r2, r3])
        await db.commit()

    yield

    async with TestSession() as db:
        from sqlalchemy import text
        await db.execute(text("DELETE FROM reminders WHERE user_id = 'user-reload-1'"))
        await db.execute(text("DELETE FROM users WHERE id = 'user-reload-1'"))
        await db.commit()


@pytest.mark.asyncio
@patch("app.services.reminder_scheduler.schedule_reminder_job")
async def test_reload_pending_reminders(mock_schedule, setup_pending_reminders):
    """reload_pending_reminders schedules jobs for pending reminders only."""
    from app.services.reminder_scheduler import reload_pending_reminders

    await reload_pending_reminders()

    # Should schedule exactly 2 (the pending ones, not the sent one)
    assert mock_schedule.call_count == 2
    scheduled_ids = {c.kwargs["reminder_id"] for c in mock_schedule.call_args_list}
    assert scheduled_ids == {"rem-reload-1", "rem-reload-2"}
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_reminder_reload.py -v`
Expected: FAIL — `ImportError: cannot import name 'reload_pending_reminders'`

- [x] **Step 3: Implement reload_pending_reminders**

Add to `student-planner/app/services/reminder_scheduler.py`:

```python
async def reload_pending_reminders() -> int:
    """Re-schedule all pending reminders from the database.
    Called on server startup to restore APScheduler jobs."""
    from sqlalchemy import select
    from app.models.reminder import Reminder

    count = 0
    async with async_session() as db:
        result = await db.execute(
            select(Reminder).where(Reminder.status == "pending")
        )
        reminders = list(result.scalars().all())

        now = datetime.now()
        for reminder in reminders:
            fire_time = datetime.fromisoformat(reminder.remind_at)
            if fire_time <= now:
                fire_time = now
            schedule_reminder_job(
                reminder_id=reminder.id,
                fire_time=fire_time,
                user_id=reminder.user_id,
            )
            count += 1

    return count
```

- [x] **Step 4: Call reload in lifespan**

Update the `lifespan` function in `student-planner/app/main.py`:

```python
from app.services.reminder_scheduler import get_scheduler, reload_pending_reminders


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = get_scheduler()
    scheduler.start()
    await reload_pending_reminders()
    yield
    scheduler.shutdown(wait=False)
```

- [x] **Step 5: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_reminder_reload.py -v`
Expected: 1 passed

- [x] **Step 6: Run all tests**

Run: `cd student-planner && python -m pytest tests/ -v`
Expected: All tests pass

- [x] **Step 7: Commit**

```bash
git add student-planner/app/services/reminder_scheduler.py student-planner/app/main.py student-planner/tests/test_reminder_reload.py
git commit -m "feat: reload pending reminders from DB on server startup"
```
