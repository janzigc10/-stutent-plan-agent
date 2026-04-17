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


def store_schedule_upload(user_id: str, kind: str, courses: list[dict[str, Any]]) -> str:
    file_id = str(uuid4())
    _CACHE[(user_id, file_id)] = CachedScheduleUpload(
        user_id=user_id,
        file_id=file_id,
        kind=kind,
        courses=deepcopy(courses),
        created_at=datetime.now(UTC),
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
    )


def update_schedule_upload_state(
    user_id: str,
    file_id: str,
    *,
    status: str,
    missing_periods: list[str] | None = None,
    courses: list[dict[str, Any]] | None = None,
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
        missing_periods=deepcopy(missing_periods) if missing_periods is not None else None,
    )
    _CACHE[(user_id, file_id)] = updated
    return get_schedule_upload(user_id, file_id)


def _prune_expired() -> None:
    cutoff = datetime.now(UTC) - _TTL
    expired = [key for key, cached in _CACHE.items() if cached.created_at < cutoff]
    for key in expired:
        _CACHE.pop(key, None)
