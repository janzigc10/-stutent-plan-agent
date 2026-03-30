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