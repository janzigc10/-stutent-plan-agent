from datetime import date, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.study_planner import generate_study_plan
from app.models.course import Course
from app.models.memory import Memory
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User
from app.services.calendar import TimeSlot, compute_free_slots
from app.services.memory_service import (
    create_memory,
    delete_memory as delete_memory_record,
    recall_memories,
)
from app.services.reminder_scheduler import (
    compute_next_course_occurrence,
    resolve_fire_time,
    schedule_reminder_job,
)
from app.services.period_converter import convert_periods, normalize_period, parse_time_range
from app.services.schedule_upload_cache import get_schedule_upload, update_schedule_upload_state


async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    db: AsyncSession,
    user_id: str,
) -> dict[str, Any]:
    """Dispatch a tool call to the appropriate handler."""
    handler = TOOL_HANDLERS.get(tool_name)
    if handler is None:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        return await handler(db=db, user_id=user_id, **arguments)
    except Exception as exc:
        return {"error": str(exc)}


async def _list_courses(db: AsyncSession, user_id: str, **kwargs) -> dict[str, Any]:
    result = await db.execute(select(Course).where(Course.user_id == user_id))
    courses = list(result.scalars().all())
    return {
        "courses": [
            {
                "id": course.id,
                "name": course.name,
                "teacher": course.teacher,
                "location": course.location,
                "weekday": course.weekday,
                "start_time": course.start_time,
                "end_time": course.end_time,
                "week_start": course.week_start,
                "week_end": course.week_end,
            }
            for course in courses
        ],
        "count": len(courses),
    }


async def _add_course(db: AsyncSession, user_id: str, **kwargs) -> dict[str, Any]:
    course = Course(user_id=user_id, **kwargs)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return {"id": course.id, "name": course.name, "status": "created"}


async def _delete_course(db: AsyncSession, user_id: str, course_id: str, **kwargs) -> dict[str, Any]:
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == user_id)
    )
    course = result.scalar_one_or_none()
    if course is None:
        return {"error": "Course not found"}

    await db.delete(course)
    await db.commit()
    return {"status": "deleted", "name": course.name}


async def _get_free_slots(
    db: AsyncSession,
    user_id: str,
    start_date: str,
    end_date: str,
    min_duration_minutes: int = 30,
    **kwargs,
) -> dict[str, Any]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    days: list[dict[str, Any]] = []

    current = start
    while current <= end:
        weekday = current.isoweekday()
        date_str = current.isoformat()

        course_result = await db.execute(
            select(Course).where(Course.user_id == user_id, Course.weekday == weekday)
        )
        courses = list(course_result.scalars().all())

        task_result = await db.execute(
            select(Task).where(
                Task.user_id == user_id,
                Task.scheduled_date == date_str,
                Task.status != "skipped",
            )
        )
        tasks = list(task_result.scalars().all())

        occupied: list[TimeSlot] = []
        for course in courses:
            occupied.append(
                TimeSlot(
                    start=course.start_time,
                    end=course.end_time,
                    type="course",
                    name=course.name,
                )
            )
        for task in tasks:
            occupied.append(
                TimeSlot(
                    start=task.start_time,
                    end=task.end_time,
                    type="task",
                    name=task.title,
                )
            )

        free_periods = compute_free_slots(
            occupied,
            min_duration_minutes=min_duration_minutes,
        )

        days.append(
            {
                "date": date_str,
                "weekday": weekday_names[weekday - 1],
                "free_periods": [
                    {
                        "start": slot.start,
                        "end": slot.end,
                        "duration_minutes": slot.duration_minutes,
                    }
                    for slot in free_periods
                ],
                "occupied": [
                    {
                        "start": slot.start,
                        "end": slot.end,
                        "type": slot.type,
                        "name": slot.name,
                    }
                    for slot in occupied
                ],
            }
        )
        current += timedelta(days=1)

    total_free_minutes = sum(
        slot["duration_minutes"]
        for day in days
        for slot in day["free_periods"]
    )
    total_slot_count = sum(len(day["free_periods"]) for day in days)
    return {
        "slots": days,
        "summary": (
            f"{start_date} 至 {end_date} 共 {total_slot_count} 个空闲段，"
            f"总计 {total_free_minutes // 60} 小时 {total_free_minutes % 60} 分钟"
        ),
    }


async def _create_study_plan(
    db: AsyncSession,
    user_id: str,
    exams: list,
    available_slots: dict,
    strategy: str = "balanced",
    **kwargs,
) -> dict[str, Any]:
    tasks = await generate_study_plan(exams, available_slots, strategy)
    if not tasks:
        return {"error": "Failed to generate study plan. Please try again."}
    return {"tasks": tasks, "count": len(tasks)}


async def _list_tasks(
    db: AsyncSession,
    user_id: str,
    date_from: str | None = None,
    date_to: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    query = select(Task).where(Task.user_id == user_id)
    if date_from:
        query = query.where(Task.scheduled_date >= date_from)
    if date_to:
        query = query.where(Task.scheduled_date <= date_to)
    query = query.order_by(Task.scheduled_date, Task.start_time)

    result = await db.execute(query)
    tasks = list(result.scalars().all())
    return {
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "scheduled_date": task.scheduled_date,
                "start_time": task.start_time,
                "end_time": task.end_time,
                "status": task.status,
            }
            for task in tasks
        ],
        "count": len(tasks),
    }


async def _update_task(db: AsyncSession, user_id: str, task_id: str, **kwargs) -> dict[str, Any]:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    task = result.scalar_one_or_none()
    if task is None:
        return {"error": "Task not found"}

    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return {"id": task.id, "title": task.title, "status": "updated"}


async def _complete_task(db: AsyncSession, user_id: str, task_id: str, **kwargs) -> dict[str, Any]:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    task = result.scalar_one_or_none()
    if task is None:
        return {"error": "Task not found"}

    task.status = "completed"
    await db.commit()
    return {"id": task.id, "title": task.title, "status": "completed"}


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




async def _list_reminders(db: AsyncSession, user_id: str, **kwargs) -> dict[str, Any]:
    result = await db.execute(
        select(Reminder).where(Reminder.user_id == user_id).order_by(Reminder.remind_at)
    )
    reminders = list(result.scalars().all())
    return {
        "reminders": [
            {
                "id": reminder.id,
                "target_type": reminder.target_type,
                "target_id": reminder.target_id,
                "remind_at": reminder.remind_at,
                "advance_minutes": reminder.advance_minutes,
                "status": reminder.status,
            }
            for reminder in reminders
        ],
        "count": len(reminders),
    }




async def _ask_user(
    db: AsyncSession | None = None,
    user_id: str | None = None,
    question: str = "",
    type: str = "review",
    **kwargs,
) -> dict[str, Any]:
    return {
        "action": "ask_user",
        "question": question,
        "type": type,
        "options": kwargs.get("options"),
        "data": kwargs.get("data"),
    }


async def _parse_schedule(
    db: AsyncSession,
    user_id: str,
    file_id: str,
    **kwargs,
) -> dict[str, Any]:
    return await _parse_cached_schedule(db, user_id, file_id, expected_kind="spreadsheet")


async def _parse_schedule_image(
    db: AsyncSession,
    user_id: str,
    file_id: str,
    **kwargs,
) -> dict[str, Any]:
    return await _parse_cached_schedule(db, user_id, file_id, expected_kind="image")


async def _parse_cached_schedule(
    db: AsyncSession,
    user_id: str,
    file_id: str,
    expected_kind: str,
) -> dict[str, Any]:
    cached = get_schedule_upload(user_id, file_id)
    if cached is None:
        return {"error": "Schedule upload not found"}
    if cached.kind != expected_kind:
        return {"error": f"Schedule upload kind mismatch: expected {expected_kind}, got {cached.kind}"}

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    schedule = _period_schedule_from_preferences(user.preferences if user else None)

    missing_periods: list[str] = []
    converted: list[dict[str, Any]] = []
    for course in cached.courses:
        course_data = dict(course)
        if "start_time" not in course_data or "end_time" not in course_data:
            raw_period = str(course_data.get("period") or "")
            try:
                period = normalize_period(raw_period)
            except ValueError:
                period = raw_period.strip()

            if not period:
                converted.append(course_data)
                continue

            times = convert_periods(period, schedule)
            if times is None:
                if period not in missing_periods:
                    missing_periods.append(period)
            else:
                course_data.update(times)
        converted.append(course_data)

    if missing_periods:
        update_schedule_upload_state(
            user_id,
            file_id,
            status="NEED_PERIOD_TIMES",
            missing_periods=missing_periods,
            courses=converted,
        )
        return {
            "status": "need_period_times",
            "kind": cached.kind,
            "courses": converted,
            "missing_periods": missing_periods,
            "message": "课表已识别节次，但缺少具体上课时间，请先向用户追问节次时间。",
            "file_id": file_id,
        }

    update_schedule_upload_state(
        user_id,
        file_id,
        status="READY",
        missing_periods=[],
        courses=converted,
    )
    return {
        "status": "ready",
        "kind": cached.kind,
        "courses": converted,
        "count": len(converted),
        "message": "课表已解析，请通过 ask_user 向用户展示识别结果并确认。",
        "file_id": file_id,
    }


def _period_schedule_from_preferences(
    preferences: dict[str, Any] | None,
    term_id: str = "default",
) -> dict[str, dict[str, str]]:
    if not isinstance(preferences, dict):
        return {}

    templates = preferences.get("period_schedule_templates")
    if isinstance(templates, dict):
        schedule = templates.get(term_id)
        if isinstance(schedule, dict):
            return schedule

    schedule = preferences.get("period_schedule")
    if isinstance(schedule, dict):
        return schedule

    return {}


async def _save_period_times(
    db: AsyncSession,
    user_id: str,
    file_id: str,
    entries: list[dict[str, str]],
    term_id: str = "default",
    **kwargs,
) -> dict[str, Any]:
    cached = get_schedule_upload(user_id, file_id)
    if cached is None:
        return {"error": "Schedule upload not found"}

    required_periods = cached.missing_periods or sorted(
        {
            str(course.get("period") or "").strip()
            for course in cached.courses
            if str(course.get("period") or "").strip()
        }
    )

    period_map: dict[str, dict[str, str]] = {}
    for entry in entries:
        try:
            period = normalize_period(str(entry.get("period") or ""))
            start_time, end_time = parse_time_range(str(entry.get("time") or ""))
        except ValueError as exc:
            return {"error": str(exc)}

        period_map[period] = {"start": start_time, "end": end_time}

    still_missing = [period for period in required_periods if period not in period_map]
    if still_missing:
        return {
            "status": "need_period_times",
            "file_id": file_id,
            "missing_periods": still_missing,
            "message": "仍有节次未填写，请继续补充。",
        }

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return {"error": "User not found"}

    preferences = dict(user.preferences or {})
    templates = dict(preferences.get("period_schedule_templates") or {})
    term_schedule = dict(templates.get(term_id) or {})
    term_schedule.update(period_map)
    templates[term_id] = term_schedule
    preferences["period_schedule_templates"] = templates
    user.preferences = preferences

    updated_courses: list[dict[str, Any]] = []
    for course in cached.courses:
        course_data = dict(course)
        if "start_time" not in course_data or "end_time" not in course_data:
            raw_period = str(course_data.get("period") or "")
            try:
                period = normalize_period(raw_period)
            except ValueError:
                period = raw_period.strip()
            times = convert_periods(period, term_schedule) if period else None
            if times is not None:
                course_data.update(times)
        updated_courses.append(course_data)

    update_schedule_upload_state(
        user_id,
        file_id,
        status="READY",
        missing_periods=[],
        courses=updated_courses,
    )
    await db.commit()

    return {
        "status": "ready",
        "file_id": file_id,
        "courses": updated_courses,
        "count": len(updated_courses),
        "message": "节次时间已保存，请确认课表后再导入。",
    }


async def _bulk_import_courses(
    db: AsyncSession,
    user_id: str,
    courses: list[dict[str, Any]],
    **kwargs,
) -> dict[str, Any]:
    created: list[str] = []
    reminders_created = 0
    advance_minutes = await _default_reminder_minutes(db, user_id)
    for course_data in courses:
        start_time = course_data.get("start_time")
        end_time = course_data.get("end_time")
        if not start_time or not end_time:
            period = course_data.get("period")
            return {
                "error": f"课程 {course_data.get('name', '未命名课程')} 缺少具体时间，请先补充节次时间（period={period}）。"
            }

        course = Course(
            user_id=user_id,
            name=course_data["name"],
            teacher=course_data.get("teacher"),
            location=course_data.get("location"),
            weekday=course_data["weekday"],
            start_time=start_time,
            end_time=end_time,
            week_start=course_data.get("week_start", 1),
            week_end=course_data.get("week_end", 16),
        )
        db.add(course)
        await db.flush()

        event_time = compute_next_course_occurrence(
            weekday=course.weekday,
            start_time=course.start_time,
        ).isoformat(timespec="seconds")
        fire_time = resolve_fire_time(event_time, advance_minutes=advance_minutes)
        reminder = Reminder(
            user_id=user_id,
            target_type="course",
            target_id=course.id,
            remind_at=fire_time.isoformat(timespec="seconds"),
            advance_minutes=advance_minutes,
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


async def _default_reminder_minutes(db: AsyncSession, user_id: str) -> int:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    preferences = user.preferences if user else None
    if isinstance(preferences, dict):
        value = preferences.get("default_reminder_minutes")
        if isinstance(value, int) and value > 0:
            return value
    return 15




async def _recall_memory(
    db: AsyncSession,
    user_id: str,
    query: str,
    **kwargs,
) -> dict[str, Any]:
    memories = await recall_memories(db, user_id, query)
    return {
        "memories": [
            {
                "id": memory.id,
                "category": memory.category,
                "content": memory.content,
                "created_at": memory.created_at.isoformat() if memory.created_at else None,
            }
            for memory in memories
        ],
        "count": len(memories),
    }


async def _save_memory(
    db: AsyncSession,
    user_id: str,
    category: str,
    content: str,
    **kwargs,
) -> dict[str, Any]:
    memory = await create_memory(
        db=db,
        user_id=user_id,
        category=category,
        content=content,
    )
    return {
        "status": "saved",
        "id": memory.id,
        "message": f"已保存记忆：{content}",
    }


async def _delete_memory_handler(
    db: AsyncSession,
    user_id: str,
    memory_id: str,
    **kwargs,
) -> dict[str, Any]:
    deleted = await delete_memory_record(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "已删除这条记忆。"}
    return {"error": "Memory not found"}


TOOL_HANDLERS = {
    "list_courses": _list_courses,
    "add_course": _add_course,
    "delete_course": _delete_course,
    "get_free_slots": _get_free_slots,
    "create_study_plan": _create_study_plan,
    "list_tasks": _list_tasks,
    "update_task": _update_task,
    "complete_task": _complete_task,
    "set_reminder": _set_reminder,
    "list_reminders": _list_reminders,
    "ask_user": _ask_user,
    "parse_schedule": _parse_schedule,
    "parse_schedule_image": _parse_schedule_image,
    "save_period_times": _save_period_times,
    "bulk_import_courses": _bulk_import_courses,
    "recall_memory": _recall_memory,
    "save_memory": _save_memory,
    "delete_memory": _delete_memory_handler,
}
