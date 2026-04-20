"""Short-lived in-process cache for parsed schedule uploads."""

from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4


_TTL = timedelta(minutes=30)
_CACHE: dict[tuple[str, str], "CachedScheduleUpload"] = {}


@dataclass(frozen=True)
class CachedScheduleUpload:
    user_id: str
    file_id: str
    kind: str
    courses: list[dict[str, Any]]
    created_at: datetime
    status: str = "PARSED"
    missing_periods: list[str] | None = None
    missing_semester_fields: list[str] | None = None
    progress: int = 100
    error: str | None = None
    source_file_count: int = 1


def store_schedule_upload(
    user_id: str,
    kind: str,
    courses: list[dict[str, Any]],
    *,
    status: str = "PARSED",
    missing_periods: list[str] | None = None,
    missing_semester_fields: list[str] | None = None,
    progress: int = 100,
    error: str | None = None,
    source_file_count: int = 1,
) -> str:
    file_id = str(uuid4())
    _CACHE[(user_id, file_id)] = CachedScheduleUpload(
        user_id=user_id,
        file_id=file_id,
        kind=kind,
        courses=deepcopy(courses),
        created_at=datetime.now(UTC),
        status=status,
        missing_periods=deepcopy(missing_periods),
        missing_semester_fields=deepcopy(missing_semester_fields),
        progress=max(0, min(100, progress)),
        error=error,
        source_file_count=max(1, source_file_count),
    )
    _prune_expired()
    return file_id


def get_schedule_upload(user_id: str, file_id: str) -> CachedScheduleUpload | None:
    _prune_expired()
    cached = _CACHE.get((user_id, file_id))
    if cached is None:
        return None
    return CachedScheduleUpload(
        user_id=cached.user_id,
        file_id=cached.file_id,
        kind=cached.kind,
        courses=deepcopy(cached.courses),
        created_at=cached.created_at,
        status=cached.status,
        missing_periods=deepcopy(cached.missing_periods),
        missing_semester_fields=deepcopy(cached.missing_semester_fields),
        progress=cached.progress,
        error=cached.error,
        source_file_count=cached.source_file_count,
    )


def update_schedule_upload_state(
    user_id: str,
    file_id: str,
    *,
    status: str,
    missing_periods: list[str] | None = None,
    missing_semester_fields: list[str] | None = None,
    courses: list[dict[str, Any]] | None = None,
    progress: int | None = None,
    error: str | None = None,
    source_file_count: int | None = None,
) -> CachedScheduleUpload | None:
    _prune_expired()
    cached = _CACHE.get((user_id, file_id))
    if cached is None:
        return None

    updated = CachedScheduleUpload(
        user_id=cached.user_id,
        file_id=cached.file_id,
        kind=cached.kind,
        courses=deepcopy(courses) if courses is not None else deepcopy(cached.courses),
        created_at=cached.created_at,
        status=status,
        missing_periods=deepcopy(missing_periods) if missing_periods is not None else deepcopy(cached.missing_periods),
        missing_semester_fields=(
            deepcopy(missing_semester_fields)
            if missing_semester_fields is not None
            else deepcopy(cached.missing_semester_fields)
        ),
        progress=max(0, min(100, progress)) if progress is not None else cached.progress,
        error=error if error is not None else cached.error,
        source_file_count=max(1, source_file_count) if source_file_count is not None else cached.source_file_count,
    )
    _CACHE[(user_id, file_id)] = updated
    return get_schedule_upload(user_id, file_id)


def _prune_expired() -> None:
    cutoff = datetime.now(UTC) - _TTL
    expired = [key for key, cached in _CACHE.items() if cached.created_at < cutoff]
    for key in expired:
        _CACHE.pop(key, None)
