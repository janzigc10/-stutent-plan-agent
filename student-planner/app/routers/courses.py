from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate

router = APIRouter(prefix="/courses", tags=["courses"])


def _build_week_text(week_start: int, week_end: int, week_pattern: str) -> str:
    if week_pattern == "odd":
        return f"Week {week_start}-{week_end} (odd)"
    if week_pattern == "even":
        return f"Week {week_start}-{week_end} (even)"
    return f"Week {week_start}-{week_end}"


def _normalize_course_payload(payload: dict) -> dict:
    normalized = dict(payload)
    week_start = int(normalized.get("week_start", 1))
    week_end = int(normalized.get("week_end", 16))
    if week_end < week_start:
        week_end = week_start
    week_pattern = str(normalized.get("week_pattern") or "all").lower()
    if week_pattern not in {"all", "odd", "even"}:
        week_pattern = "all"
    normalized["week_start"] = week_start
    normalized["week_end"] = week_end
    normalized["week_pattern"] = week_pattern
    normalized["week_text"] = normalized.get("week_text") or _build_week_text(week_start, week_end, week_pattern)
    return normalized


@router.post("/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(
    body: CourseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    course = Course(user_id=user.id, **_normalize_course_payload(body.model_dump()))
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@router.get("/", response_model=list[CourseOut])
async def list_courses(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.user_id == user.id))
    return result.scalars().all()


@router.get("/{course_id}", response_model=CourseOut)
async def get_course(
    course_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.id == course_id, Course.user_id == user.id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.patch("/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: str,
    body: CourseUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.id == course_id, Course.user_id == user.id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    updates = body.model_dump(exclude_unset=True)
    next_values = _normalize_course_payload(
        {
            "week_start": course.week_start,
            "week_end": course.week_end,
            "week_pattern": course.week_pattern,
            "week_text": course.week_text,
            **updates,
        }
    )
    if "week_text" not in updates and {"week_start", "week_end", "week_pattern"} & updates.keys():
        next_values["week_text"] = _build_week_text(
            next_values["week_start"], next_values["week_end"], next_values["week_pattern"]
        )
    for key, value in next_values.items():
        setattr(course, key, value)
    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.id == course_id, Course.user_id == user.id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    await db.delete(course)
    await db.commit()
