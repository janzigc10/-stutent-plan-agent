from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.models.memory import Memory
from app.models.user import User
from app.services.memory_service import (
    create_memory,
    delete_memory,
    get_hot_memories,
    get_warm_memories,
    mark_stale_memories,
    recall_memories,
)


@pytest.mark.asyncio
async def test_create_memory(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="mem-user-1", username="memtest", hashed_password="x")
        db.add(user)
        await db.commit()

        memory = await create_memory(
            db=db,
            user_id="mem-user-1",
            category="preference",
            content="喜欢早上复习数学",
            source_session_id="session-abc",
        )

        assert memory.id is not None
        assert memory.category == "preference"
        assert memory.content == "喜欢早上复习数学"
        assert memory.user_id == "mem-user-1"
        assert memory.source_session_id == "session-abc"
        assert memory.relevance_score == 1.0


@pytest.mark.asyncio
async def test_get_hot_memories_returns_preferences_and_habits(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="mem-user-2", username="memtest2", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-2", "preference", "早上复习数学")
        await create_memory(db, "mem-user-2", "habit", "一次最多专注 1 小时")
        await create_memory(db, "mem-user-2", "decision", "高数用分章节策略")

        hot = await get_hot_memories(db, "mem-user-2")
        categories = {memory.category for memory in hot}

        assert "preference" in categories
        assert "habit" in categories
        assert "decision" not in categories


@pytest.mark.asyncio
async def test_get_warm_memories_returns_recent_non_hot_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="mem-user-3", username="memtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-3", "decision", "高数用分章节策略")

        old_memory = Memory(
            user_id="mem-user-3",
            category="decision",
            content="线代用刷题策略",
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_memory)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)

        assert len(warm) == 1
        assert warm[0].content == "高数用分章节策略"


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "高数用分章节策略，效果不错")
        await create_memory(db, "mem-user-4", "preference", "喜欢早上复习")
        await create_memory(db, "mem-user-4", "knowledge", "概率论最难")

        results = await recall_memories(db, "mem-user-4", query="高数")

        assert len(results) >= 1
        assert any("高数" in memory.content for memory in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        memory = await create_memory(db, "mem-user-5", "decision", "高数用分章节策略")
        original_accessed = memory.last_accessed

        results = await recall_memories(db, "mem-user-5", query="高数")

        assert len(results) == 1
        assert results[0].last_accessed >= original_accessed


@pytest.mark.asyncio
async def test_delete_memory(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="mem-user-6", username="memtest6", hashed_password="x")
        db.add(user)
        await db.commit()

        memory = await create_memory(db, "mem-user-6", "preference", "早上复习")
        deleted = await delete_memory(db, "mem-user-6", memory.id)

        assert deleted is True

        result = await db.execute(select(Memory).where(Memory.id == memory.id))
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_memory_wrong_user(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="mem-user-7", username="memtest7", hashed_password="x")
        db.add(user)
        await db.commit()

        memory = await create_memory(db, "mem-user-7", "preference", "早上复习")
        deleted = await delete_memory(db, "wrong-user", memory.id)

        assert deleted is False


@pytest.mark.asyncio
async def test_mark_stale_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="mem-user-8", username="memtest8", hashed_password="x")
        db.add(user)
        await db.commit()

        old_memory = Memory(
            user_id="mem-user-8",
            category="decision",
            content="旧的决策",
            last_accessed=datetime.now(timezone.utc) - timedelta(days=100),
            relevance_score=1.0,
        )
        db.add(old_memory)
        await db.commit()

        count = await mark_stale_memories(db, "mem-user-8", stale_days=90)

        assert count == 1

        await db.refresh(old_memory)
        assert old_memory.relevance_score < 1.0