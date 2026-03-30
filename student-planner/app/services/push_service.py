"""Web Push delivery via pywebpush."""

import json
from dataclasses import dataclass
from typing import Any

from pywebpush import WebPushException, webpush

from app.config import settings


@dataclass(eq=True)
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
    if subscription is None:
        return PushResult(ok=False, error="No subscription")

    payload = json.dumps({"title": title, "body": body}, ensure_ascii=False)

    try:
        response = webpush(
            subscription_info=subscription,
            data=payload,
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": settings.vapid_claims_email},
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