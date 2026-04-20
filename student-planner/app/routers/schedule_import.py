import asyncio
from io import BytesIO
from typing import Any
from zipfile import BadZipFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from openpyxl.utils.exceptions import InvalidFileException

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.schedule_upload_cache import (
    CachedScheduleUpload,
    get_schedule_upload,
    store_schedule_upload,
    update_schedule_upload_state,
)
from app.services.schedule_parser import RawCourse, parse_excel_schedule

router = APIRouter(prefix="/schedule", tags=["schedule-import"])

_EXCEL_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}
_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
_ALLOWED_TYPES = _EXCEL_TYPES | _IMAGE_TYPES
_MAX_IMAGE_FILES = 3
_MAX_SPREADSHEET_FILES = 1
_UPLOAD_ERROR = "不支持的文件格式: {content_type}。支持 xlsx、xls、png、jpg、jpeg、webp。"
_UPLOAD_PARSE_TASKS: set[asyncio.Task[None]] = set()


@router.post("/upload")
async def upload_schedule(
    file: list[UploadFile] | None = File(None),
    user: User = Depends(get_current_user),
) -> dict:
    uploads = file or []
    if not uploads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请至少上传一个课表文件。",
        )

    classified = [_classify_upload(upload) for upload in uploads]
    kinds = {kind for kind, _ in classified}
    if len(kinds) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持同时上传课表图片和表格文件，请选择一种格式。",
        )

    kind = classified[0][0]
    if kind == "image" and len(classified) > _MAX_IMAGE_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"课表图片最多支持 {_MAX_IMAGE_FILES} 张。",
        )
    if kind == "spreadsheet" and len(classified) > _MAX_SPREADSHEET_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="课表表格文件最多支持 1 个。",
        )

    course_dicts: list[dict[str, Any]] = []
    if kind == "spreadsheet":
        file_bytes = await uploads[0].read()
        try:
            courses = parse_excel_schedule(BytesIO(file_bytes))
        except (BadZipFile, InvalidFileException, ValueError, OSError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="课表文件无法解析，请确认文件有效；当前支持 xlsx、xls，若为 et 请另存为 xlsx 后重试。",
            ) from exc
        course_dicts.extend(_raw_course_to_dict(course) for course in courses)
        file_id = store_schedule_upload(
            user.id,
            kind,
            course_dicts,
            status="PARSED",
            progress=100,
            source_file_count=len(uploads),
        )
        return {
            "file_id": file_id,
            "kind": kind,
            "status": "parsed",
            "courses": course_dicts,
            "count": len(course_dicts),
            "source_file_count": len(uploads),
        }

    image_payloads: list[tuple[bytes, str]] = []
    for upload in uploads:
        file_bytes = await upload.read()
        image_payloads.append((file_bytes, upload.content_type or ""))

    file_id = store_schedule_upload(
        user.id,
        kind,
        [],
        status="QUEUED",
        progress=5,
        source_file_count=len(image_payloads),
    )
    _dispatch_image_parse_task(user.id, file_id, image_payloads)

    return {
        "file_id": file_id,
        "kind": kind,
        "status": "processing",
        "courses": [],
        "count": 0,
        "source_file_count": len(image_payloads),
    }


@router.get("/upload/{file_id}")
async def get_upload_status(
    file_id: str,
    user: User = Depends(get_current_user),
) -> dict:
    cached = get_schedule_upload(user.id, file_id)
    if cached is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule upload not found",
        )
    return _status_payload(cached)


def _classify_upload(upload: UploadFile) -> tuple[str, UploadFile]:
    content_type = upload.content_type or ""
    if content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_UPLOAD_ERROR.format(content_type=content_type),
        )
    if content_type in _IMAGE_TYPES:
        return "image", upload
    return "spreadsheet", upload


def _raw_course_to_dict(course: RawCourse) -> dict:
    return {
        "name": course.name,
        "teacher": course.teacher,
        "location": course.location,
        "weekday": course.weekday,
        "period": course.period,
        "week_start": course.week_start,
        "week_end": course.week_end,
        "week_pattern": course.week_pattern,
        "week_text": course.week_text,
    }


def _dispatch_image_parse_task(
    user_id: str,
    file_id: str,
    image_payloads: list[tuple[bytes, str]],
) -> None:
    task = asyncio.create_task(_parse_image_uploads(user_id, file_id, image_payloads))
    _UPLOAD_PARSE_TASKS.add(task)
    task.add_done_callback(_UPLOAD_PARSE_TASKS.discard)


async def _parse_image_uploads(
    user_id: str,
    file_id: str,
    image_payloads: list[tuple[bytes, str]],
) -> None:
    from app.agent.schedule_ocr import detect_schedule_week, parse_schedule_image

    total = len(image_payloads)
    if total <= 0:
        update_schedule_upload_state(
            user_id,
            file_id,
            status="FAILED",
            progress=100,
            error="empty image batch",
        )
        return

    update_schedule_upload_state(
        user_id,
        file_id,
        status="PARSING",
        progress=10,
        source_file_count=total,
    )

    parsed_courses: list[RawCourse] = []
    try:
        for index, (payload, mime_type) in enumerate(image_payloads, start=1):
            week_hint = await detect_schedule_week(payload, mime_type)
            courses = await parse_schedule_image(
                payload,
                mime_type,
                fallback_week_number=week_hint,
                prefer_parity_from_week_hint=total > 1,
            )
            parsed_courses.extend(courses)
            merged = _merge_image_courses(parsed_courses)
            progress = min(95, 10 + int(index / total * 85))
            update_schedule_upload_state(
                user_id,
                file_id,
                status="PARSING",
                progress=progress,
                courses=[_raw_course_to_dict(course) for course in merged],
                source_file_count=total,
            )
    except Exception as exc:
        update_schedule_upload_state(
            user_id,
            file_id,
            status="FAILED",
            progress=100,
            error=str(exc) or "schedule image parsing failed",
            source_file_count=total,
        )
        return

    merged_courses = _merge_image_courses(parsed_courses)
    update_schedule_upload_state(
        user_id,
        file_id,
        status="PARSED",
        progress=100,
        courses=[_raw_course_to_dict(course) for course in merged_courses],
        source_file_count=total,
    )


def _merge_image_courses(courses: list[RawCourse]) -> list[RawCourse]:
    merged: dict[tuple[Any, ...], RawCourse] = {}
    for course in courses:
        key = (
            course.name,
            course.teacher,
            course.location,
            course.weekday,
            course.period,
        )
        existing = merged.get(key)
        if existing is None:
            merged[key] = RawCourse(
                name=course.name,
                teacher=course.teacher,
                location=course.location,
                weekday=course.weekday,
                period=course.period,
                week_start=course.week_start,
                week_end=course.week_end,
                week_pattern=course.week_pattern,
                week_text=course.week_text,
            )
            continue

        existing.week_start = min(existing.week_start, course.week_start)
        existing.week_end = max(existing.week_end, course.week_end)
        existing.week_pattern = _merge_week_pattern(existing.week_pattern, course.week_pattern)
        existing.week_text = _build_week_text(existing.week_start, existing.week_end, existing.week_pattern)

    return list(merged.values())


def _merge_week_pattern(left: str, right: str) -> str:
    normalized_left = (left or "all").lower()
    normalized_right = (right or "all").lower()
    if normalized_left == normalized_right:
        return normalized_left
    if "all" in {normalized_left, normalized_right}:
        return "all"
    if {normalized_left, normalized_right} == {"odd", "even"}:
        return "all"
    if normalized_left in {"odd", "even"}:
        return normalized_left
    if normalized_right in {"odd", "even"}:
        return normalized_right
    return "all"


def _build_week_text(week_start: int, week_end: int, week_pattern: str) -> str:
    if week_pattern == "odd":
        return f"第{week_start}-{week_end}周(单周)"
    if week_pattern == "even":
        return f"第{week_start}-{week_end}周(双周)"
    return f"第{week_start}-{week_end}周"


def _status_payload(cached: CachedScheduleUpload) -> dict[str, Any]:
    return {
        "file_id": cached.file_id,
        "kind": cached.kind,
        "status": cached.status,
        "progress": cached.progress,
        "error": cached.error,
        "courses": cached.courses,
        "count": len(cached.courses),
        "missing_periods": cached.missing_periods or [],
        "missing_semester_fields": cached.missing_semester_fields or [],
        "source_file_count": cached.source_file_count,
    }
