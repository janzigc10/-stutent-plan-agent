# Plan 4: Memory 缂傚倷绶￠崹闈涚暦閻㈤潧鍨?+ 濠电偞鍨堕幐鎼佹晝閿濆洨绠旈柛娑欐綑濡﹢鏌涢妷銏℃珦闁告埃鍋撻梻?
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer memory system (working/short-term/long-term) and context window management to keep conversations coherent across sessions without blowing up the context window.

**Architecture:** Memory CRUD service handles persistence. Two new agent tools (`recall_memory`, `save_memory`) give the LLM on-demand access. Tool result compression summarizes verbose outputs inline. Session lifecycle hooks generate summaries and extract memories at session end. The system prompt builder loads hot/warm memories at session start.

**Tech Stack:** SQLAlchemy async (existing), OpenAI-compatible LLM for summarization, existing agent tool system

**Depends on:** Plan 1 (Memory, SessionSummary, ConversationMessage models), Plan 2 (agent loop, tool_executor, llm_client)

---

## File Structure

```
student-planner/
闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?app/
闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?services/
闂?  闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?memory_service.py          # Memory CRUD: create, query, update, delete, staleness
闂?  闂?  闂備礁鐤囬～澶愬蓟閿熺姴缁╅柕蹇嬪€曢悡姗€鏌?context_compressor.py      # Tool result summarization + conversation compression
闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?agent/
闂?  闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?tools.py                   # (modify: add recall_memory, save_memory definitions)
闂?  闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?tool_executor.py           # (modify: add recall_memory, save_memory handlers)
闂?  闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?loop.py                    # (modify: add tool result compression after each tool call)
闂?  闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?context.py                 # (modify: add hot/warm memory loading)
闂?  闂?  闂備礁鐤囬～澶愬蓟閿熺姴缁╅柕蹇嬪€曢悡姗€鏌?session_lifecycle.py       # Session end: generate summary + extract memories
闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?routers/
闂?  闂?  闂備礁鐤囬～澶愬蓟閿熺姴缁╅柕蹇嬪€曢悡姗€鏌?chat.py                    # (modify: call session lifecycle on disconnect/timeout)
闂?  闂備礁鐤囬～澶愬蓟閿熺姴缁╅柕蹇嬪€曢悡姗€鏌?config.py                      # (modify: add context window thresholds)
闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?tests/
闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?test_memory_service.py         # Memory CRUD unit tests
闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?test_context_compressor.py     # Compression logic tests
闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?test_memory_tools.py           # recall_memory / save_memory tool tests
闂?  闂備礁鐤囬～澶嬬珶閺囥垹缁╅柕蹇嬪€曢悡姗€鏌?test_session_lifecycle.py      # Session end flow tests
闂?  闂備礁鐤囬～澶愬蓟閿熺姴缁╅柕蹇嬪€曢悡姗€鏌?test_context_loading.py        # Hot/warm memory in system prompt tests
```

---

### Task 1: Memory CRUD Service

Pure data layer 闂?no LLM calls. Handles create, query by category, query by relevance, update `last_accessed`, and staleness marking.

**Files:**
- Create: `student-planner/app/services/memory_service.py`
- Create: `student-planner/tests/test_memory_service.py`

- [x] **Step 1: Write the failing tests**

```python
# tests/test_memory_service.py
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.models.memory import Memory
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
        from app.models.user import User

        user = User(id="mem-user-1", username="memtest", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(
            db=db,
            user_id="mem-user-1",
            category="preference",
            content="闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏缁秹鏌嶇悰鈥充壕缂備焦顨呴崐鐟邦嚗閸曨偒鍚嬮柛鏇ㄥ幘濡叉垿姊烘潪鎵妽婵犮垺锕㈤、?,
            source_session_id="session-abc",
        )
        assert mem.id is not None
        assert mem.category == "preference"
        assert mem.content == "闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏缁秹鏌嶇悰鈥充壕缂備焦顨呴崐鐟邦嚗閸曨偒鍚嬮柛鏇ㄥ幘濡叉垿姊烘潪鎵妽婵犮垺锕㈤、?
        assert mem.user_id == "mem-user-1"
        assert mem.source_session_id == "session-abc"
        assert mem.relevance_score == 1.0


@pytest.mark.asyncio
async def test_get_hot_memories_returns_preferences(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-2", username="memtest2", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-2", "preference", "闂備礁鎼崯鐘诲疾濞嗘垹绠旈柛灞剧☉缁剁偟鈧箍鍎辩€氼噣鎯佹惔銊︾厸濞达綀顫夌欢鍙夈亜?)
        await create_memory(db, "mem-user-2", "habit", "濠电偞鍨堕幐鎾磻閹惧绠鹃柛鈥崇箰婢у弶绻涢幘鐟扮厫鐎?闂佽绻愮换鎰崲閹存繍娓?)
        await create_memory(db, "mem-user-2", "decision", "濠德板€曢崐纭呮懌闂佸搫妫涢崰鏍箖娴犲惟闁靛鍎抽埀顒冨吹缁辨帡寮崒姣款剙鈹戦埥鍡楀箻缂侇喚鏁诲浠嬵敃閿濆棭鍚?)

        hot = await get_hot_memories(db, "mem-user-2")
        categories = {m.category for m in hot}
        assert "preference" in categories
        assert "habit" in categories
        # decision is NOT hot 闂?it's cold (on-demand)
        assert "decision" not in categories


@pytest.mark.asyncio
async def test_get_warm_memories_returns_recent(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-3", username="memtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        # Recent memory (within 7 days)
        await create_memory(db, "mem-user-3", "decision", "濠德板€曢崐纭呮懌闂佸搫妫涢崰鏍箖娴犲惟闁靛鍎抽埀顒冨吹缁辨帡寮崒姣款剙鈹戦埥鍡楀箻缂侇喚鏁诲浠嬵敃閿濆棭鍚?)

        # Old memory (simulate 30 days ago)
        old_mem = Memory(
            user_id="mem-user-3",
            category="decision",
            content="缂傚倷鐒﹂崕鎶藉Φ濮椻偓瀹曨剟顢楅崟顒€浠洪梺闈涱焾閸庨亶鎮￠弴鐐嶆盯鎮ч崼顐ゅ姺闂佸鏉垮姦闁?,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_mem)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)
        assert len(warm) == 1
        assert warm[0].content == "濠德板€曢崐纭呮懌闂佸搫妫涢崰鏍箖娴犲惟闁靛鍎抽埀顒冨吹缁辨帡寮崒姣款剙鈹戦埥鍡楀箻缂侇喚鏁诲浠嬵敃閿濆棭鍚?


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "濠德板€曢崐纭呮懌闂佸搫妫涢崰鏍箖娴犲惟闁靛鍎抽埀顒冨吹缁辨帡寮崒姣款剙鈹戦埥鍡楀箻缂侇喚鏁诲浠嬵敃閿濆棭鍚呴梻浣瑰缁嬫垿寮甸鍕柧闁靛鏅涢崙鐘崇節婵炴儳浜剧紓浣诡殔椤︾敻寮?)
        await create_memory(db, "mem-user-4", "preference", "闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏缁秹鏌嶇悰鈥充壕缂備焦顨呴崐鐟邦嚗閸曨偒鍚嬮柛鏇ㄥ幘濡?)
        await create_memory(db, "mem-user-4", "knowledge", "婵犳鍠楃敮鎺楀磹鐠囧樊鍟呴柤娴嬫櫆婵ジ鏌ｉ幋鐐嗘垶绂掑鈧?)

        results = await recall_memories(db, "mem-user-4", query="濠德板€曢崐纭呮懌闂?)
        assert len(results) >= 1
        assert any("濠德板€曢崐纭呮懌闂? in m.content for m in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-5", "decision", "濠德板€曢崐纭呮懌闂佸搫妫涢崰鏍箖娴犲惟闁靛鍎抽埀顒冨吹缁辨帡寮崒姣款剙鈹戦埥鍡楀箻缂侇喚鏁诲浠嬵敃閿濆棭鍚?)
        original_accessed = mem.last_accessed

        # Small delay to ensure timestamp differs
        results = await recall_memories(db, "mem-user-5", query="濠德板€曢崐纭呮懌闂?)
        assert len(results) == 1
        assert results[0].last_accessed >= original_accessed


@pytest.mark.asyncio
async def test_delete_memory(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-6", username="memtest6", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-6", "preference", "闂備礁鎼崯鐘诲疾濞嗘垹绠旈柛灞剧☉缁剁偟鈧箍鍎辩€氼噣鎯?)
        deleted = await delete_memory(db, "mem-user-6", mem.id)
        assert deleted is True

        result = await db.execute(select(Memory).where(Memory.id == mem.id))
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_memory_wrong_user(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-7", username="memtest7", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-7", "preference", "闂備礁鎼崯鐘诲疾濞嗘垹绠旈柛灞剧☉缁剁偟鈧箍鍎辩€氼噣鎯?)
        deleted = await delete_memory(db, "wrong-user", mem.id)
        assert deleted is False


@pytest.mark.asyncio
async def test_mark_stale_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-8", username="memtest8", hashed_password="x")
        db.add(user)
        await db.commit()

        # Create a memory that was last accessed 100 days ago
        old_mem = Memory(
            user_id="mem-user-8",
            category="decision",
            content="闂備礁鎼崬鏌ュ川椤旂偓娈搁梻浣告啞閸旀洜澹曢銏″仱?,
            last_accessed=datetime.now(timezone.utc) - timedelta(days=100),
            relevance_score=1.0,
        )
        db.add(old_mem)
        await db.commit()

        count = await mark_stale_memories(db, "mem-user-8", stale_days=90)
        assert count == 1

        await db.refresh(old_mem)
        assert old_mem.relevance_score < 1.0
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_memory_service.py -v`
Expected: FAIL 闂?`ModuleNotFoundError: No module named 'app.services.memory_service'`

- [x] **Step 3: Implement memory_service.py**

```python
# app/services/memory_service.py
"""CRUD operations for the Memory table."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory

# Hot memory categories 闂?always loaded into system prompt
HOT_CATEGORIES = {"preference", "habit"}


async def create_memory(
    db: AsyncSession,
    user_id: str,
    category: str,
    content: str,
    source_session_id: str | None = None,
) -> Memory:
    """Create a new memory record."""
    mem = Memory(
        user_id=user_id,
        category=category,
        content=content,
        source_session_id=source_session_id,
    )
    db.add(mem)
    await db.commit()
    await db.refresh(mem)
    return mem


async def get_hot_memories(db: AsyncSession, user_id: str) -> list[Memory]:
    """Get always-on memories (preferences + habits). Injected into every system prompt."""
    result = await db.execute(
        select(Memory)
        .where(
            Memory.user_id == user_id,
            Memory.category.in_(HOT_CATEGORIES),
            Memory.relevance_score > 0.3,
        )
        .order_by(Memory.created_at.desc())
        .limit(20)
    )
    return list(result.scalars().all())


async def get_warm_memories(
    db: AsyncSession,
    user_id: str,
    days: int = 7,
) -> list[Memory]:
    """Get recent memories (created in last N days). Injected at session start."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(Memory)
        .where(
            Memory.user_id == user_id,
            Memory.created_at >= cutoff,
            Memory.category.notin_(HOT_CATEGORIES),
            Memory.relevance_score > 0.3,
        )
        .order_by(Memory.created_at.desc())
        .limit(10)
    )
    return list(result.scalars().all())


async def recall_memories(
    db: AsyncSession,
    user_id: str,
    query: str,
    limit: int = 5,
) -> list[Memory]:
    """Search memories by keyword (simple LIKE search).

    Updates last_accessed for returned memories.
    """
    result = await db.execute(
        select(Memory)
        .where(
            Memory.user_id == user_id,
            Memory.content.contains(query),
            Memory.relevance_score > 0.1,
        )
        .order_by(Memory.relevance_score.desc(), Memory.created_at.desc())
        .limit(limit)
    )
    memories = list(result.scalars().all())

    now = datetime.now(timezone.utc)
    for mem in memories:
        mem.last_accessed = now
    if memories:
        await db.commit()

    return memories


async def delete_memory(
    db: AsyncSession,
    user_id: str,
    memory_id: str,
) -> bool:
    """Delete a memory. Returns True if deleted, False if not found or wrong user."""
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    )
    mem = result.scalar_one_or_none()
    if not mem:
        return False
    await db.delete(mem)
    await db.commit()
    return True


async def mark_stale_memories(
    db: AsyncSession,
    user_id: str,
    stale_days: int = 90,
) -> int:
    """Mark memories not accessed in stale_days as low-relevance. Returns count."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=stale_days)
    result = await db.execute(
        update(Memory)
        .where(
            Memory.user_id == user_id,
            Memory.last_accessed < cutoff,
            Memory.relevance_score > 0.3,
        )
        .values(relevance_score=0.2)
    )
    await db.commit()
    return result.rowcount
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_memory_service.py -v`
Expected: All 8 tests PASS

- [x] **Step 5: Commit**

```bash
cd student-planner
git add app/services/memory_service.py tests/test_memory_service.py
git commit -m "feat: add memory CRUD service with hot/warm/cold retrieval"
```

---

### Task 2: Tool Result Compressor

Summarizes verbose tool results into concise versions for the conversation history. The full result is already logged in AgentLog; the compressed version stays in the message history to save context window space.

**Files:**
- Create: `student-planner/app/services/context_compressor.py`
- Create: `student-planner/tests/test_context_compressor.py`

- [x] **Step 1: Write the failing tests**

```python
# tests/test_context_compressor.py
import json

import pytest

from app.services.context_compressor import compress_tool_result


def test_compress_get_free_slots():
    """get_free_slots returns verbose per-day data; compress to summary."""
    result = {
        "slots": [
            {
                "date": "2026-04-01",
                "weekday": "闂備礁鎲＄粙蹇涘礉鐎ｎ剛绠?,
                "free_periods": [
                    {"start": "08:00", "end": "10:00", "duration_minutes": 120},
                    {"start": "14:00", "end": "16:00", "duration_minutes": 120},
                ],
                "occupied": [
                    {"start": "10:00", "end": "12:00", "type": "course", "name": "濠德板€曢崐纭呮懌闂?},
                ],
            },
            {
                "date": "2026-04-02",
                "weekday": "闂備礁鎲＄粙蹇涘礉鐏炵煫?,
                "free_periods": [
                    {"start": "09:00", "end": "11:00", "duration_minutes": 120},
                ],
                "occupied": [],
            },
        ],
        "summary": "2026-04-01 闂?2026-04-02 闂?3 濠电偞鍨堕幖鈺傜閻愬搫鐓橀柡宥庡幗閳锋帡鏌涘▎蹇ｆ▓闁哥偘绮欓弻銊モ槈濡粯鎷遍梺閫炲苯澧俊鍙夊浮椤?6 闂佽绻愮换鎰崲閹存繍娓?0 闂備礁鎲＄敮鎺懳涘┑瀣?,
    }
    compressed = compress_tool_result("get_free_slots", result)
    # Should use the existing summary field
    assert "3 濠电偞鍨堕幖鈺傜閻愬搫鐓橀柡宥庡幗閳锋帡鏌涘▎蹇ｆ▓闁? in compressed
    assert "6 闂佽绻愮换鎰崲閹存繍娓? in compressed
    # Should NOT contain the full slot details
    assert "free_periods" not in compressed


def test_compress_list_courses():
    result = {
        "courses": [
            {"id": "1", "name": "濠德板€曢崐纭呮懌闂?, "teacher": "闁?, "weekday": 1, "start_time": "08:00", "end_time": "09:40"},
            {"id": "2", "name": "缂傚倷鐒﹂崕鎶藉Φ濮椻偓瀹?, "teacher": "闂?, "weekday": 3, "start_time": "10:00", "end_time": "11:40"},
            {"id": "3", "name": "闂備礁鍚嬪Σ鎺斿垝妤ｅ喚鏁?, "teacher": "闂?, "weekday": 2, "start_time": "08:00", "end_time": "09:40"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_courses", result)
    assert "3" in compressed
    assert "濠德板€曢崐纭呮懌闂? in compressed


def test_compress_list_tasks():
    result = {
        "tasks": [
            {"id": "1", "title": "濠电姰鍨煎▔娑氱矓瀹曞洤濮柛鏇ㄥ墻濞堟淇婇婊呭笡婵炲牆澧庣槐鎺懳旀繝鍌氬箰缂備焦鏌ㄩ顓犲垝?, "status": "completed"},
            {"id": "2", "title": "濠电姰鍨煎▔娑氱矓瀹曞洤濮柛鏇ㄥ墻濞堟淇婇婊呭笡婵炲牆澧庣槐鎺懳旀繝鍌氬箰缂備降鍔夐弲婵堝垝?, "status": "pending"},
            {"id": "3", "title": "濠电姰鍨煎▔娑氱矓瀹曞洤濮柛鏇ㄥ幘濡垰顭块崜渚囩劸闁?, "status": "pending"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_tasks", result)
    assert "3" in compressed
    assert "1" in compressed  # completed count


def test_compress_create_study_plan():
    result = {
        "tasks": [
            {"title": "濠电姰鍨煎▔娑氱矓瀹曞洤濮柛鏇ㄥ墻濞堟淇婇婊呭笡婵炲牆澧庣槐鎺懳旀繝鍌氬箰缂備焦鏌ㄩ顓犲垝?, "date": "2026-04-01"},
            {"title": "濠电姰鍨煎▔娑氱矓瀹曞洤濮柛鏇ㄥ墻濞堟淇婇婊呭笡婵炲牆澧庣槐鎺懳旀繝鍌氬箰缂備降鍔夐弲婵堝垝?, "date": "2026-04-02"},
            {"title": "濠电姰鍨煎▔娑氱矓瀹曞洤濮柛鏇ㄥ幘濡垰顭块崜渚囩劸闁?, "date": "2026-04-03"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("create_study_plan", result)
    assert "3" in compressed


def test_compress_unknown_tool_returns_json():
    """Unknown tools get their result JSON-serialized as-is."""
    result = {"status": "ok", "data": "something"}
    compressed = compress_tool_result("unknown_tool", result)
    assert "ok" in compressed


def test_compress_small_result_unchanged():
    """Small results (under threshold) are returned as-is JSON."""
    result = {"id": "abc", "status": "created"}
    compressed = compress_tool_result("add_course", result)
    parsed = json.loads(compressed)
    assert parsed["status"] == "created"


def test_compress_error_result_unchanged():
    """Error results are never compressed."""
    result = {"error": "Course not found"}
    compressed = compress_tool_result("delete_course", result)
    parsed = json.loads(compressed)
    assert parsed["error"] == "Course not found"
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_context_compressor.py -v`
Expected: FAIL 闂?`ModuleNotFoundError: No module named 'app.services.context_compressor'`

- [x] **Step 3: Implement context_compressor.py**

```python
# app/services/context_compressor.py
"""Compress tool results to save context window space.

Full results are logged in AgentLog. These compressed versions stay in
the conversation history for the LLM to reference.
"""

import json

# Results shorter than this (in chars) are kept as-is
_SMALL_THRESHOLD = 300


def compress_tool_result(tool_name: str, result: dict) -> str:
    """Compress a tool result dict into a concise string for conversation history.

    Returns a JSON string (for small/error results) or a natural language summary.
    """
    # Never compress errors
    if "error" in result:
        return json.dumps(result, ensure_ascii=False)

    raw = json.dumps(result, ensure_ascii=False)

    # Small results don't need compression
    if len(raw) < _SMALL_THRESHOLD:
        return raw

    # Tool-specific compression
    compressor = _COMPRESSORS.get(tool_name)
    if compressor:
        return compressor(result)

    # Fallback: truncate large unknown results
    return raw[:_SMALL_THRESHOLD] + "..."


def _compress_get_free_slots(result: dict) -> str:
    summary = result.get("summary", "")
    if summary:
        return f"[缂傚倷绀侀張顒€顪冮挊澹╂稒绂掔€ｎ亞鐫勯梺鐓庢啞椤旀牠宕禒瀣厸閻忕偠顕ч崝銉︺亜閺囩噥娈樼紒杈ㄥ浮楠炴鈧敻鏅查崙绲?{summary}"
    slots = result.get("slots", [])
    total = sum(len(d.get("free_periods", [])) for d in slots)
    return f"[缂傚倷绀侀張顒€顪冮挊澹╂稒绂掔€ｎ亞鐫勯梺鐓庢啞椤旀牠宕禒瀣厸閻忕偠顕ч崝銉︺亜閺囩噥娈樼紒杈ㄥ浮楠炴鈧敻鏅查崙绲?{len(slots)} 濠电姰鍨归悘鍫ュ疾椤忓棙顫曟繝闈涱儏缁€?{total} 濠电偞鍨堕幖鈺傜閻愬搫鐓橀柡宥庡幗閳锋帡鏌涘▎蹇ｆ▓闁?


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = [c["name"] for c in courses[:5]]
    names_str = "闂?.join(names)
    if count > 5:
        names_str += f" 缂?{count} 闂?
    return f"[闂佽崵濮村ú銈嗘櫠娴犲鐓濆┑鍌滎焾缁€鍡樹繆閵堝懎顏ラ柍褜鍓欓崕?闂?{count} 闂傚倸鍊搁崐鍫曞礉韫囨侗鏁嬮柟鎯板Г閺咁剚鎱ㄥ┑鍫滃垔ames_str}"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    pending = count - completed
    return f"[濠电偛顕慨楣冾敋瑜庨幈銊╂偄閻撳海顦┑掳鍊曠€氥劑鍩€椤掆偓閸?闂?{count} 濠电偞鍨堕幖鈺傜濞嗘挸绠查柕蹇嬪€曠粈澶愭煃閽樺鍣界紒鈧晶鍧坥mpleted} 濠电偞鍨堕幖鈺傜濠婂牆绀勯柨娑樺閸嬫捇鎮烽悧鍫熸嫳闂佹悶鍔嶅畝鎼佸极瀹ュ洠鍋撻棃娑氬醇ending} 濠电偞鍨堕幖鈺傜濠婂懏顐介柣鏃囥€€閸嬫捇鎮烽悧鍫熸嫳闂?


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    return f"[濠电姰鍨煎▔娑氱矓瀹曞洤濮柛鏇ㄥ幗婵ジ鏌嶉妷銉ユ毐闁诲繐銈?闁诲氦顫夐悺鏇犱焊濞嗘挸鏋侀柟鎹愵嚙缁?{count} 濠电偞鍨堕幖鈺傜濠婂煻鍥矗婢跺备鏋欓梺缁橆焾妞寸鐣烽弻銉︾厱?


_COMPRESSORS = {
    "get_free_slots": _compress_get_free_slots,
    "list_courses": _compress_list_courses,
    "list_tasks": _compress_list_tasks,
    "create_study_plan": _compress_create_study_plan,
}
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_context_compressor.py -v`
Expected: All 7 tests PASS

- [x] **Step 5: Commit**

```bash
cd student-planner
git add app/services/context_compressor.py tests/test_context_compressor.py
git commit -m "feat: add tool result compressor for context window management"
```

---

### Task 3: Agent Tools 闂?recall_memory + save_memory

Two new tools for the LLM to interact with the memory system. `recall_memory` does keyword search (cold memory). `save_memory` creates a new memory with ask_user confirmation baked into the flow.

**Files:**
- Modify: `student-planner/app/agent/tools.py` (add 2 tool definitions)
- Modify: `student-planner/app/agent/tool_executor.py` (add 2 handlers)
- Create: `student-planner/tests/test_memory_tools.py`

- [x] **Step 1: Add tool definitions to tools.py**

Append these two entries to the `TOOL_DEFINITIONS` list in `app/agent/tools.py`:

```python
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": "濠电偛顕慨鏉懨归悜钘夋瀬闁靛牆顦粻锝咁渻鐎ｎ亜顒㈤柣锝変憾濮婂鍩€椤掑嫬绠伴幖娣灩閻掓悂鏌ｉ悩杈╁妽婵犮垺顭囬幑銏ゅ磼濞戞埃鏋栧銈嗘尵閸ｃ儱顫忛崜褏纾煎〒姘仢閻忣喗绻涢弶鎴█鐎规洘顨婂畷妤呭川椤掑倻鐣鹃梻浣筋嚃閸欏酣宕归鍕劦妞ゆ巻鍋撻柛濠傛憸缁辩偟鈧綆鍠楅ˉ鍡涙煃瑜滈崜娑㈠箟閻楀牊濯撮柛娑橈功椤︺儵妫呴銏℃悙婵☆偅鐩顐﹀Χ婢跺﹦顓洪梺鐐壘閸婂顢樺ú顏呯厱闁规儳纾倴濠电偛鐗婇崹鍨暦閹达絿鐤€闁规儳宕禒娲⒑闂堟稒顥欐俊鐐村笧瀵囧礋椤栨氨鐣惧銈嗙墬缁嬫垿鎮樺Δ鍛厱闁归偊鍓涢敍宥夋煟鎺抽崕闈涱嚕椤曗偓瀵敻妫冨☉鎺撶€奸梻浣规た濞煎潡宕濇繝鍥х劦妞ゆ巻鍋撻柛濠勬櫕閹广垽骞嬮敃鈧悙濠囨煟閹邦厼绲婚柣鏍憾濮婃椽寮剁捄銊愩倖绻涢崼鐔风仼闁瑰嘲顑夊鍓佹崉閵娧呮殼闂備礁鎲＄敮妤呫€冩径鎰ラ柛鎰靛枛杩?,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "闂備胶鎳撻崥瀣垝鎼淬劌纾奸柕濞炬櫅缁€鍌炴煙閹澘袚闁哄棙鐩幃褰掑炊瑜忛埢宀€绱掓潏銊х畺濞?闂備浇妗ㄩ悞锕€顭垮鈧、妤呮偄缁嬭法绐為悗骞垮劚鐎氼噣鎯佹惔锝囩＜婵炴垶鐟ф晶閬嶆煛?闂?闂佽瀛╅崘鑽ょ磽濮樺崬濮柛鏇ㄥ墰閳绘洟鏌ｅΟ鍝勬毐闁?",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "濠电儑绲藉ú锔炬崲閸岀偞鍋ら柕濠忓閳绘棃鏌嶈閸撶喎顕ｉ崼鏇熸櫖闁告洦鍓氬▓銏ゆ⒑鐟欏嫭灏︽い銉︽尭閳绘捇骞嬮敂瑙ｆ嫻闂佸湱顭堢€涒晠宕洪崒鐐村仯濞达綀顫夌欢鑼磼鐠囨彃鈧寧淇婇幘顔肩＜婵﹩鍓氶柨顓熺箾閿濆懏澶勭紒璇插€块幃娲Ω閳哄倸浠洪梺闈涱煭缁犳垿鎮￠弴銏＄厸闁告洦鍋呴幑锝夋煃閵夛富鐒介柟顔诲嵆婵℃悂濡搁敃鈧☉褔姊哄Ч鍥у閻庢凹鍓氱粋宥夊川婵犲嫰妾繝娈垮枟閸斿繘宕戦幘瀛樺濡炲娴峰Σ鎴︽⒑鐠団€崇伇闁搞劑浜跺畷褰掑Ω閳哄倻鍘掗悗骞垮劚閻楁粌煤閿濆鐓曢柟閭﹀墰閿涘秹鏌ｆ幊閸庣敻寮鍥︽勃闁兼祴鏅濋幉褰掓煟閻斿憡纾婚柣鎺炲閺侇喛銇愰幒鎴烆棟濡炪倖鎸绘竟鏇㈠磻閹捐纾兼繛鍡樺灩椤旀棃鏌ｆ惔銏⑩姇闁挎艾顭胯婵墽绮诲☉銏犲窛婵烇綆鍏橀崑鎾圭疀濞戞顦ч梺鍓插亖閸ㄦ椽寮?ask_user 缂備胶铏庨崣搴ㄥ窗濞戙埄鏁囧┑鐘宠壘杩?,
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["preference", "habit", "decision", "knowledge"],
                        "description": "闂佽崵濮抽悞锕€顭垮Ο鍏煎床闁稿本绮庣亸鐢告偣閸ャ劌绲婚柣鎺戙偢閺屻劌鈽夊▎妯哄reference=闂備胶顭堥鍛崲閹版澘围? habit=濠电偞鍨跺缁樻叏閻㈢纾? decision=闂備礁鎲￠崝鏇犲椤撱垺鍋? knowledge=闂佽崵濮抽梽宥夊磹濡ゅ懏鍋?,
                    },
                    "content": {
                        "type": "string",
                        "description": "闂佽崵濮抽悞锕€顭垮Ο鍏煎床闁稿瞼鍋涚粈鍐煕濞戝崬寮鹃柛鐔锋喘閺屻劌鈽夊Ο鑲╁姰闂佹悶鍊栫划鎾诲箖閻愬搫绠氶梺顓ㄧ畱濞堁囨煟閻旈娈遍柛瀣崌閺岀喓鎷犻懠顒傤啈闂?,
                    },
                },
                "required": ["category", "content"],
            },
        },
    },
```

Also append a `delete_memory` tool definition:

```python
    {
        "type": "function",
        "function": {
            "name": "delete_memory",
            "description": "闂備礁鎲＄敮鐐寸箾閳ь剚绻涢崨顓烆劉缂佸顦甸崺鈧い鎺戝缁狙囨煥濞戞ê顏柡鍡楃箻閺岀喖骞橀鍛棖濠电偛鐗婇崹鍨潖瑜版帒绠伴幖娣灩閻掓悂鏌ｉ悩杈╁妽婵犮垺顭囬幑銏ゅ磼閻愬弬銉╂煕鐏炵偓鐨戠紒澶娿偢閺岋綁锝為鈧俊浠嬫煕閳哄倻銆掗柟?闂傚鍋勫ú锕佹懌闁汇埄鍨崑鎼檟x'闂備礁鎼崯鎶筋敊閹邦喗顫曟繝闈涱儏缁€鍌炴煕椤愮姴鐏柡?recall_memory 闂備胶鎳撻悘姘跺磿閹惰棄鏄ョ€光偓閳ь剟鍩€椤掑倹鏆╅柟铏尵閼洪亶鎳犻浣割€涢梺鍝勵槼濞夋洜绮婚幘缁樼厽?ID闂備焦瀵х粙鎴︽嚐椤栫偛鐤柍褜鍓熼幃鍦偓锝庝簻閺嗙喖鏌℃担闈涒偓鏇綖閵忋倕围闁告侗鍓涢惌妤呮⒑缁嬭法绠伴柛銏＄叀瀹曠銇愰幒鎾寖闂侀潧鐗嗛崯鐘诲磻?,
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "闂佽崵鍠愬ú鎴犵矆娓氣偓瀹曠銇愰幒鎾寖闂侀潧鐗嗗ú锕傛偩闁秵鍋ｅù锝堫潐缁惰尙绱?ID闂備焦瀵х粙鎴︽偋閸涱垰鍨?recall_memory 缂傚倸鍊烽悞锕傚箰婵犳碍鍊跺璺侯儑閳绘梹銇勯幘顖楀亾瀹曞浂鍞甸梻浣告啞閻燂箓鎮ч鐘愁潟?,
                    },
                },
                "required": ["memory_id"],
            },
        },
    },
```

- [x] **Step 2: Write the failing tests**

```python
# tests/test_memory_tools.py
import pytest
from sqlalchemy import select

from app.agent.tool_executor import execute_tool
from app.agent.tools import TOOL_DEFINITIONS
from app.models.memory import Memory
from app.models.user import User


def test_recall_memory_tool_defined():
    names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "recall_memory" in names


def test_save_memory_tool_defined():
    names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "save_memory" in names


def test_recall_memory_requires_query():
    tool = next(t for t in TOOL_DEFINITIONS if t["function"]["name"] == "recall_memory")
    assert "query" in tool["function"]["parameters"]["required"]


def test_save_memory_requires_category_and_content():
    tool = next(t for t in TOOL_DEFINITIONS if t["function"]["name"] == "save_memory")
    required = tool["function"]["parameters"]["required"]
    assert "category" in required
    assert "content" in required


def test_delete_memory_tool_defined():
    names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "delete_memory" in names


def test_delete_memory_requires_memory_id():
    tool = next(t for t in TOOL_DEFINITIONS if t["function"]["name"] == "delete_memory")
    assert "memory_id" in tool["function"]["parameters"]["required"]


@pytest.mark.asyncio
async def test_recall_memory_returns_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-1", username="toolmem1", hashed_password="x")
        db.add(user)
        mem = Memory(
            user_id="tool-mem-1",
            category="preference",
            content="闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏缁秹鏌嶇悰鈥充壕缂備焦顨呴崐鐟邦嚗閸曨偒鍚嬮柛鏇ㄥ幘濡叉垿姊烘潪鎵妽婵犮垺锕㈤、?,
        )
        db.add(mem)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "闂備浇妗ㄩ悞锕€顭垮鈧、?},
            db=db,
            user_id="tool-mem-1",
        )
        assert "memories" in result
        assert len(result["memories"]) >= 1
        assert "闂備浇妗ㄩ悞锕€顭垮鈧、? in result["memories"][0]["content"]


@pytest.mark.asyncio
async def test_recall_memory_empty_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-2", username="toolmem2", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "濠电偞鍨堕幐鍝ョ矓閹绢喗鍋ら柕濞炬櫅閹瑰爼鏌曟繛褍瀚弳鐘绘⒑閸涘﹤濮囬柟鍐查叄椤?},
            db=db,
            user_id="tool-mem-2",
        )
        assert result["memories"] == []
        assert result["count"] == 0


@pytest.mark.asyncio
async def test_save_memory_creates_record(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-3", username="toolmem3", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "save_memory",
            {"category": "preference", "content": "闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏閻ょ偓鎱ㄥ鍡椾簽闁荤喐鍔曢…璺ㄦ崉閾忓墣锛勭磼閳ュ啿顏€殿噮鍓熷畷鍫曞煛婵犲啰绋?},
            db=db,
            user_id="tool-mem-3",
        )
        assert result["status"] == "saved"

        mems = await db.execute(
            select(Memory).where(Memory.user_id == "tool-mem-3")
        )
        saved = mems.scalars().all()
        assert len(saved) == 1
        assert saved[0].content == "闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏閻ょ偓鎱ㄥ鍡椾簽闁荤喐鍔曢…璺ㄦ崉閾忓墣锛勭磼閳ュ啿顏€殿噮鍓熷畷鍫曞煛婵犲啰绋?
        assert saved[0].category == "preference"
```

- [x] **Step 3: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_memory_tools.py -v`
Expected: FAIL 闂?`recall_memory` not found in TOOL_DEFINITIONS

- [x] **Step 4: Add handlers to tool_executor.py**

Add this import at the top of `app/agent/tool_executor.py`:

```python
from app.services.memory_service import create_memory, delete_memory, recall_memories
```

Add these handler functions:

```python
async def _recall_memory(
    db: AsyncSession, user_id: str, query: str, **kwargs
) -> dict[str, Any]:
    """Search user's long-term memories by keyword."""
    memories = await recall_memories(db, user_id, query)
    return {
        "memories": [
            {
                "id": m.id,
                "category": m.category,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in memories
        ],
        "count": len(memories),
    }


async def _save_memory(
    db: AsyncSession, user_id: str, category: str, content: str, **kwargs
) -> dict[str, Any]:
    """Save a new long-term memory for the user."""
    mem = await create_memory(
        db=db,
        user_id=user_id,
        category=category,
        content=content,
    )
    return {
        "status": "saved",
        "id": mem.id,
        "message": f"闁诲氦顫夐悺鏇犱焊椤忓牜鏁婇柛銉ｅ妽婵挳鐓崶銉ュ姢缂佹劖鈷媍ontent}",
    }


async def _delete_memory_handler(
    db: AsyncSession, user_id: str, memory_id: str, **kwargs
) -> dict[str, Any]:
    """Delete a long-term memory by ID."""
    deleted = await delete_memory(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "闁诲海鎳撻幉陇銇愰崘顔煎瀭鐟滅増甯楅埛鏃堟煏閸繄澧遍柛銈咁樀閹鎷呯憴鍕嚒缂?}
    return {"error": "闂佽崵濮抽悞锕€顭垮Ο鍏煎床闁稿本绋撻埢鏃傗偓骞垮劚閹虫劙骞楅悩缁樼厱闁挎柨鎼俊浠嬫煕閵婏絽濮傜€殿噮鍣ｉ幃鈺呮惞椤愩倗袣闂備礁鎲＄敮鐐寸箾閳ь剚绻?}
```

Add all three to the `TOOL_HANDLERS` dict:

```python
TOOL_HANDLERS = {
    # ... existing entries ...
    "recall_memory": _recall_memory,
    "save_memory": _save_memory,
    "delete_memory": _delete_memory_handler,
}
```

- [x] **Step 5: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_memory_tools.py -v`
Expected: All 9 tests PASS

- [x] **Step 6: Commit**

```bash
cd student-planner
git add app/agent/tools.py app/agent/tool_executor.py tests/test_memory_tools.py
git commit -m "feat: add recall_memory and save_memory agent tools"
```

---

### Task 4: Integrate Tool Result Compression into Agent Loop

Modify the agent loop to compress tool results before appending them to the conversation history. The full result is already saved in AgentLog (via `_log_step`). The compressed version goes into `messages[]` for the LLM.

**Files:**
- Modify: `student-planner/app/agent/loop.py:106-118`
- Create: `student-planner/tests/test_loop_compression.py`

- [x] **Step 1: Write the failing test**

```python
# tests/test_loop_compression.py
"""Test that the agent loop compresses tool results in conversation history."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.loop import run_agent_loop
from app.models.user import User


@pytest.mark.asyncio
async def test_loop_compresses_large_tool_result(setup_db):
    """When a tool returns a large result, the message history should contain the compressed version."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(
            id="loop-comp-1",
            username="loopcomp",
            hashed_password="x",
        )
        db.add(user)
        await db.commit()

        # Mock LLM: first call returns a tool call, second call returns text
        large_result = {
            "slots": [{"date": f"2026-04-{i:02d}", "weekday": "闂備礁鎲＄粙蹇涘礉鐎ｎ剛鍗?, "free_periods": [{"start": "08:00", "end": "22:00", "duration_minutes": 840}], "occupied": []} for i in range(1, 8)],
            "summary": "2026-04-01 闂?2026-04-07 闂?7 濠电偞鍨堕幖鈺傜閻愬搫鐓橀柡宥庡幗閳锋帡鏌涘▎蹇ｆ▓闁哥偘绮欓弻銊モ槈濡粯鎷遍梺閫炲苯澧俊鍙夊浮椤?98 闂佽绻愮换鎰崲閹存繍娓?0 闂備礁鎲＄敮鎺懳涘┑瀣?,
        }

        call_count = 0

        async def mock_chat_completion(client, messages, tools=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "get_free_slots",
                            "arguments": json.dumps({"start_date": "2026-04-01", "end_date": "2026-04-07"}),
                        },
                    }],
                }
            else:
                # Check that the tool result in messages is compressed
                tool_msg = next(m for m in messages if m.get("role") == "tool")
                content = tool_msg["content"]
                # Compressed version should NOT contain "free_periods"
                assert "free_periods" not in content
                assert "7 濠电偞鍨堕幖鈺傜閻愬搫鐓橀柡宥庡幗閳锋帡鏌涘▎蹇ｆ▓闁? in content
                return {"role": "assistant", "content": "濠电偠鎻徊鎸庢叏閸撗勫床闁哄稁鍘煎婵嬫煏婵犲繘妾紒鐘冲笧閳ь剙鐏氬姗€鎮ч崱娴板洨鎹勯妸褏鐓斿┑鐐叉▕娴滄繈鏁嶅┑瀣厸闁告劑鍔庨崺锝嗕繆椤愩垺鍋ラ柡?}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                gen = run_agent_loop("闂備礁鎼悮顐﹀磿閸愯鑰块柛娑卞灣閻碍绻涘顔荤凹闁挎稒绻堥弻锟犲礃閵娧冪厽濠?, user, "test-session", db, AsyncMock())
                try:
                    event = await gen.__anext__()
                    while True:
                        events.append(event)
                        if event["type"] == "done":
                            break
                        event = await gen.__anext__()
                except StopAsyncIteration:
                    pass

        # The frontend should still get the full result
        tool_result_events = [e for e in events if e.get("type") == "tool_result"]
        assert len(tool_result_events) == 1
        assert "slots" in tool_result_events[0]["result"]
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd student-planner && python -m pytest tests/test_loop_compression.py -v`
Expected: FAIL 闂?assertion `"free_periods" not in content` fails (no compression yet)

- [x] **Step 3: Modify loop.py to add compression**

In `app/agent/loop.py`, add this import at the top:

```python
from app.services.context_compressor import compress_tool_result
```

Then modify the section where tool results are appended to messages (around line 106-118). Replace the block that handles non-ask_user tool results:

Current code (lines 105-110):
```python
            else:
                result = await execute_tool(tool_name, tool_args, db, user.id)
                tool_result_content = json.dumps(result, ensure_ascii=False)
                if "error" in result:
                    error_count[tool_name] = error_count.get(tool_name, 0) + 1
                yield {"type": "tool_result", "name": tool_name, "result": result}
```

New code:
```python
            else:
                result = await execute_tool(tool_name, tool_args, db, user.id)
                # Compress for LLM context; full result already goes to AgentLog
                tool_result_content = compress_tool_result(tool_name, result)
                if "error" in result:
                    error_count[tool_name] = error_count.get(tool_name, 0) + 1
                # Frontend gets the full result for display
                yield {"type": "tool_result", "name": tool_name, "result": result}
```

The only change is replacing `json.dumps(result, ensure_ascii=False)` with `compress_tool_result(tool_name, result)`.

- [x] **Step 4: Run test to verify it passes**

Run: `cd student-planner && python -m pytest tests/test_loop_compression.py -v`
Expected: PASS

- [x] **Step 5: Run existing loop tests to verify no regression**

Run: `cd student-planner && python -m pytest tests/ -v -k "loop or agent"`
Expected: All PASS

- [x] **Step 6: Commit**

```bash
cd student-planner
git add app/agent/loop.py tests/test_loop_compression.py
git commit -m "feat: compress tool results in agent loop conversation history"
```

---

### Task 5: Hot/Warm Memory Loading into System Prompt

Modify `context.py` to load hot memories (preferences + habits) into every system prompt, and warm memories (recent decisions/knowledge) at session start.

**Files:**
- Modify: `student-planner/app/agent/context.py`
- Create: `student-planner/tests/test_context_loading.py`

- [x] **Step 1: Write the failing tests**

```python
# tests/test_context_loading.py
import pytest

from app.agent.context import build_dynamic_context
from app.models.memory import Memory
from app.models.user import User


@pytest.mark.asyncio
async def test_hot_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-1", username="ctxtest1", hashed_password="x")
        db.add(user)
        pref = Memory(user_id="ctx-user-1", category="preference", content="闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏缁秹鏌嶇悰鈥充壕缂備焦顨呴崐鐟邦嚗閸曨偒鍚嬮柛鏇ㄥ幘濡叉垿姊烘潪鎵妽婵犮垺锕㈤、?)
        habit = Memory(user_id="ctx-user-1", category="habit", content="濠电偞鍨堕幐鎾磻閹惧绠鹃柛鈥崇箰婢у弶绻涢幘鐟扮厫鐎垫澘瀚～婵嬫嚋娴ｅ啫浜栧┑?闂佽绻愮换鎰崲閹存繍娓?)
        db.add_all([pref, habit])
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏缁秹鏌嶇悰鈥充壕缂備焦顨呴崐鐟邦嚗閸曨偒鍚嬮柛鏇ㄥ幘濡叉垿姊烘潪鎵妽婵犮垺锕㈤、? in context
        assert "濠电偞鍨堕幐鎾磻閹惧绠鹃柛鈥崇箰婢у弶绻涢幘鐟扮厫鐎垫澘瀚～婵嬫嚋娴ｅ啫浜栧┑?闂佽绻愮换鎰崲閹存繍娓? in context


@pytest.mark.asyncio
async def test_warm_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-2", username="ctxtest2", hashed_password="x")
        db.add(user)
        decision = Memory(user_id="ctx-user-2", category="decision", content="濠德板€曢崐纭呮懌闂佸搫妫涢崰鏍箖娴犲惟闁靛鍎抽埀顒冨吹缁辨帡寮崒姣款剙鈹戦埥鍡楀箻缂侇喚鏁诲浠嬵敃閿濆棭鍚?)
        db.add(decision)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "濠德板€曢崐纭呮懌闂佸搫妫涢崰鏍箖娴犲惟闁靛鍎抽埀顒冨吹缁辨帡寮崒姣款剙鈹戦埥鍡楀箻缂侇喚鏁诲浠嬵敃閿濆棭鍚? in context


@pytest.mark.asyncio
async def test_no_memories_still_works(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-3", username="ctxtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        context = await build_dynamic_context(user, db)
        # Should still have time info, just no memory section
        assert "闁荤喐绮庢晶妤呭箰閸涘﹥娅犻柣妯款嚙缁秹鏌涢锝嗙闁? in context


@pytest.mark.asyncio
async def test_last_session_summary_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.session_summary import SessionSummary

        user = User(id="ctx-user-4", username="ctxtest4", hashed_password="x")
        db.add(user)
        summary = SessionSummary(
            user_id="ctx-user-4",
            session_id="prev-session",
            summary="濠电偞鍨堕幐鎼佹晝閵夆晩鏁冮柤娴嬫杹閸嬫捇鎮藉▓鎸庢暞闂佷紮缂氱划娆撳极瀹ュ拋娼╅弶鍫涘妽濞堛垽姊虹憴鍕稇闁搞垺鐓￠、姘舵焼瀹ュ懐顦ч梺闈涱槶閸婃宕繝鍥ㄥ仯闁搞儯鍔岀粈鍐煏閸℃鏆ｉ柡浣哥Т閻ｆ繈宕橀幆褎娅楃紓鍌氬€搁崰姘跺窗閺囩姾濮?闂傚倸鍊搁崐鍫曞礉韫囨稑鐒垫い鎺嗗亾闁哥喐濞婇幆渚€顢涢悙鏉戝壄闂佸憡娲﹂崑鎺懳ｇ拠娴嬫闁哄啫鍊搁瀷濡炪倖鎸婚幃鍌氱暦?,
        )
        db.add(summary)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂佽娴烽弫鎼佸储瑜斿畷锝夊幢濡⒈娲搁梺绯曞墲閸戝綊宕甸敃鍌涘仩? in context
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_context_loading.py -v`
Expected: FAIL 闂?memories not appearing in context output

- [x] **Step 3: Modify context.py to load memories**

Replace the full `app/agent/context.py` with:

```python
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.session_summary import SessionSummary
from app.models.task import Task
from app.models.user import User
from app.services.memory_service import get_hot_memories, get_warm_memories

WEEKDAY_NAMES = ["闂備礁鎲＄粙蹇涘礉鐎ｎ剛鍗?, "闂備礁鎲＄粙蹇涘礉鐎ｎ剝濮?, "闂備礁鎲＄粙蹇涘礉鐎ｎ剛绠?, "闂備礁鎲＄粙蹇涘礉鐏炵煫?, "闂備礁鎲＄粙蹇涘礉鐎ｎ剝濮?, "闂備礁鎲＄粙蹇涘礉瀹€鍕煑?, "闂備礁鎲＄粙蹇涘礉瀹ュ憘?]


async def build_dynamic_context(user: User, db: AsyncSession) -> str:
    """Build the dynamic portion of the system prompt."""
    now = datetime.now(timezone.utc)
    today = now.date()
    weekday = today.isoweekday()

    parts: list[str] = []
    parts.append(f"闁荤喐绮庢晶妤呭箰閸涘﹥娅犻柣妯款嚙缁秹鏌涢锝嗙闁挎稓鍠栭弻銊モ槈濞嗘ê濮眓ow.strftime('%Y-%m-%d %H:%M')}闂備焦瀵х粙鎴濐熆閺堛€KDAY_NAMES[weekday - 1]}闂?)

    if user.current_semester_start:
        delta = (today - user.current_semester_start).days
        week_num = delta // 7 + 1
        parts.append(f"闁荤喐绮庢晶妤呭箰閸涘﹥娅犻柣妯碱暯閸嬫挸鈽夐幎鑺ヮ€嶅┑鐘亾闁跨喓濮甸弲顒佹叏濮椻偓绾悂宕曢幉鎲宔ek_num}闂?)

    # Today's schedule
    course_result = await db.execute(
        select(Course)
        .where(Course.user_id == user.id, Course.weekday == weekday)
        .order_by(Course.start_time)
    )
    courses = course_result.scalars().all()

    task_result = await db.execute(
        select(Task)
        .where(Task.user_id == user.id, Task.scheduled_date == today.isoformat())
        .order_by(Task.start_time)
    )
    tasks = task_result.scalars().all()

    parts.append("\n濠电偛顕慨鎾晝閵堝桅濠㈣埖鍔栭崕宥夋煕閺囥劌澧柨娑橆槺缁辨帞鈧綆浜堕崕婊呯磼?)
    if not courses and not tasks:
        parts.append("- 闂備礁鎼崯鐗堟叏閹绢喗鍋╅柕濞炬櫅缁?)
    else:
        for course in courses:
            location = f" @ {course.location}" if course.location else ""
            parts.append(f"- {course.start_time}-{course.end_time} {course.name}{location}闂備焦瀵х粙鎴︽偋閹伴偊鏁嬬€规洖娲ㄩ惌娆撴倵閿濆懎顣崇紒鈧?)
        for task in tasks:
            status_mark = "闂? if task.status == "completed" else "闂?
            parts.append(f"- {task.start_time}-{task.end_time} {task.title}闂備焦瀵х粙鎴濐熆閺夋挤atus_mark}闂?)

    # User preferences
    preferences = user.preferences or {}
    if preferences:
        parts.append("\n闂備焦妞垮鍧楀礉瀹ュ鏄ユ繛鎴欏灩绾惧鐓崶銊﹀蔼闁稿鍔戦弻?)
        if "earliest_study" in preferences:
            parts.append(f"- 闂備礁鎼悧鍐磻閹剧粯鐓涢柛鎰剁稻濞呭懏銇勯幒鏂挎瀾缂佸锕幃鈺呮惞椤愵偅袧闂傚倸鍊搁崐浠嬪箵椤忓棙顫曢柣銊︹叞references['earliest_study']}")
        if "latest_study" in preferences:
            parts.append(f"- 闂備礁鎼悧鍐磻閹剧粯鐓涢柛娑卞枦婢规ɑ銇勯幒鏂挎瀾缂佸锕幃鈺呮惞椤愵偅袧闂傚倸鍊搁崐浠嬪箵椤忓棙顫曢柣銊︹叞references['latest_study']}")
        if "lunch_break" in preferences:
            parts.append(f"- 闂備礁鎲￠〃鍛存偋閸涱垱顫曢柕鍫濐槹閺咁剚鎱ㄥ┑鍫熸灳references['lunch_break']}")
        if "min_slot_minutes" in preferences:
            parts.append(f"- 闂備礁鎼悧鍐磻閹剧粯鐓熸い鎾楀啫绠哄┑鐘亾濞撴埃鍋撶€殿噮鍋婂畷濂告偄閸撳弶袧婵犵數鍋涢悧蹇涖€傞鐐潟闁汇劍鈪皉eferences['min_slot_minutes']}闂備礁鎲＄敮鎺懳涘┑瀣?)
        if "school_schedule" in preferences:
            parts.append("- 闁诲海鎳撻幉锟犳偂閿熺姴鍌ㄩ柕鍫濇川绾剧偓銇勯弮鍥у惞缂佸锕弻鐔碱敇瑜嶉悘鈩冧繆閻愭彃鈧灝顫忛懡銈咁棜閻庯絻鍔夐崑?)

    # Hot memories (preferences + habits) 闂?always loaded
    hot_memories = await get_hot_memories(db, user.id)
    if hot_memories:
        parts.append("\n闂傚倸鍊甸崑鎾绘煙缁嬪灝顒㈤柛鈺佸€块幃瑙勬媴鐟欏嫮鍑＄紓浣筋嚙閸婂潡寮澶婇唶婵犻潧鎳愰崜銊︾節闂堟稑鈧綊宕瑰┑鍫㈢當閻忕偛澧介埢鏇㈡煟濡搫鏆遍柛鏃傛暬閺屻劌鈽夊鍡橆€嗙紓?)
        for mem in hot_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Warm memories (recent decisions/knowledge) 闂?loaded at session start
    warm_memories = await get_warm_memories(db, user.id, days=7)
    if warm_memories:
        parts.append("\n闂佸搫顦弲婊堝垂鐠虹尨鑰块柨娑樺婵ジ鏌℃径搴㈢《缂佺姵鎹囬弻銊モ槈濡厧顤€濠电偞鎹侀崺鏍ь焽?濠电姰鍨归悘鍫ュ疾椤忓棙顫曟慨妯垮煐閺?)
        for mem in warm_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Last session summary (if within 24 hours)
    cutoff_24h = now - timedelta(hours=24)
    summary_result = await db.execute(
        select(SessionSummary)
        .where(
            SessionSummary.user_id == user.id,
            SessionSummary.created_at >= cutoff_24h,
        )
        .order_by(SessionSummary.created_at.desc())
        .limit(1)
    )
    last_summary = summary_result.scalar_one_or_none()
    if last_summary:
        parts.append(f"\n濠电偞鍨堕幐鎼佹晝閵夆晩鏁冮柤娴嬫杹閸嬫捇鎮藉▓鎸庢暞闂佷紮缂氱划娆撶嵁濡も偓铻ｆ繛鍡欏亾閻姊洪幐搴ｂ姇妞ゆ帞鐝產st_summary.summary}")

    return "\n".join(parts)
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_context_loading.py -v`
Expected: All 4 tests PASS

- [x] **Step 5: Run existing context tests to verify no regression**

Run: `cd student-planner && python -m pytest tests/ -v -k "context"`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
cd student-planner
git add app/agent/context.py tests/test_context_loading.py
git commit -m "feat: load hot/warm memories and session summary into system prompt"
```

---

### Task 6: Session Lifecycle 闂?Summary + Memory Extraction

When a session ends (WebSocket disconnect or timeout), generate a session summary and extract memories from the conversation. Both use the LLM.

**Files:**
- Create: `student-planner/app/agent/session_lifecycle.py`
- Create: `student-planner/tests/test_session_lifecycle.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_session_lifecycle.py
import json
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.agent.session_lifecycle import end_session
from app.models.conversation_message import ConversationMessage
from app.models.memory import Memory
from app.models.session_summary import SessionSummary
from app.models.user import User


@pytest.mark.asyncio
async def test_end_session_creates_summary(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-1", username="sesstest1", hashed_password="x")
        db.add(user)

        # Simulate conversation messages
        msgs = [
            ConversationMessage(session_id="sess-1", role="user", content="闂佹眹鍩勯崹濂稿窗濡ゅ懎鍨傛繝濠傜墛閸庢垿鎮楅敐搴″缂佺姵鐟╁鍫曞煛閸屾粍鍣ч梺鐟板暱濡繈骞嗛崘顔肩妞ゆ挻绋掗弲鐐烘⒒閸屾艾鈧顕ｇ捄渚富闁稿瞼鍋為埛?),
            ConversationMessage(session_id="sess-1", role="assistant", content="濠电偠鎻徊鎸庢叏閸撗勫床闁哄稁鍘煎婵嬫煏婵犲繘妾紒?2濠电偞鍨堕幖鈺傜閻愬搫鐓橀柡宥庡幗閳锋帡鏌涘▎蹇ｆЧ妞は佸嫮绠?),
            ConversationMessage(session_id="sess-1", role="user", content="闂佹眹鍩勯崹濂稿窗濡ゅ懎鍨傛繝濠傛噳閸嬫捇鎮烽柇锔叫ч柣銏╁灡閹稿銆冮崶顬喓绱掑Ο娲诲晙濠电姰鍨煎▔娑氱矓瀹曞洤濮?),
            ConversationMessage(session_id="sess-1", role="assistant", content="闁诲氦顫夐悺鏇犱焊濞嗘挸鏋侀柟鎹愵嚙缁?濠电偞鍨堕幖鈺傜濠婂煻鍥矗婢跺备鏋欓梺缁橆焾妞寸鐣烽弻銉︾厱?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_summary_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂備焦妞垮鍧楀礉瀹ュ鏄ユ繛鎴欏灩閽冪喖鏌曟竟顖氬閻ｈ姤绻涚€涙鐭婃俊顐ｇ懃閿曘垺瀵奸弶鎴濈獩闂侀潧臎閳ь剟寮崟顖涒拻闁稿本鑹剧痪褎淇婇悙鎻掆偓鍨潖缂佹ɑ缍囬柛鎾楀拋妲烽梺璇叉捣閹虫捇藝閹殿喗鏆滈柟鎯ь嚟椤╂煡鏌涢埄鍐€掔憸閭﹀灦閺屸剝鎷呯憴鍕嚒濡炪倧绠戝鍓佺矙婵犲洦鍋愬〒姘煎灠閹線姊洪崨濠傜瑲閻㈩垼浜炲Σ?濠电偞鍨堕幖鈺傜濞嗘挸绠查柕蹇嬪€曠粈澶愭煃閽樺鍣界紒鈧?,
                "actions": ["闂備礁鎼悮顐﹀磿閹绢噮鏁嬫俊銈呭暟閻碍绻涘顔荤凹闁挎稒绻堥弻锟犲礃閵娧冪厽濠?, "闂備焦鐪归崹濠氬窗閹版澘鍨傛慨姗嗗弾濞堟淇婇婊呭笡婵炲牐娉涢…璺ㄦ崉閾忓墣锛勭磼閳ュ啿顏柟宄邦儔閸ㄩ箖宕橀懠顑垮枈"],
                "memories": [],
            }, ensure_ascii=False),
        }

        with patch("app.agent.session_lifecycle.chat_completion", new_callable=AsyncMock, return_value=mock_summary_response):
            await end_session(db, "sess-user-1", "sess-1", AsyncMock())

        result = await db.execute(
            select(SessionSummary).where(SessionSummary.session_id == "sess-1")
        )
        summary = result.scalar_one_or_none()
        assert summary is not None
        assert "濠德板€曢崐纭呮懌闂佸搫妫涢崰鎰嚗閸曨偒鍚嬮柛鏇ㄥ幘濡? in summary.summary


@pytest.mark.asyncio
async def test_end_session_extracts_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-2", username="sesstest2", hashed_password="x")
        db.add(user)

        msgs = [
            ConversationMessage(session_id="sess-2", role="user", content="闂備胶鎳撻悺銊╁垂閻㈢鍑犻柍杞拌閺嬪酣鏌曡箛濠傚⒉闁挎稑绉撮埥澶愬箻缁涚懓浼愬銈忕畱瀵墎绮欐繝鍥ㄥ亹闁割煈鍋勯埀顒傚仧缁辨帗寰勭€ｎ亞鍘愮紓浣介哺缁诲牆顕ｉ幓鎺濇僵妞ゆ劑鍊楅幉顏堟⒑濞茶绨绘い鎴濇瀵悂宕橀鍡欑厠?),
            ConversationMessage(session_id="sess-2", role="assistant", content="濠电娀娼ч崐濠氬疾椤愨懇鏋旈柟杈鹃檮閺咁剟鎮橀悙鏉戝姢闁诲繐顦甸幃瑙勭瑹閳ь剟銆傞敂鍓х闁搞儯鍔庨々?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂備焦妞垮鍧楀礉瀹ュ鏄ユ繛鎴炵閸嬫﹢鏌曟繛鍨鐟滄妸鍏犵懓顭ㄩ崘鈺婃濡炪倖甯為崰鎰矙婵犲洦鍋愰柧蹇ｅ亽濡差垶姊婚崒姘偓鐟邦焽濞嗘劗顩查柛娑橈功闂?,
                "actions": [],
                "memories": [
                    {"category": "preference", "content": "闂備礁鎽滄慨鐢靛垝瀹ュ鏁冨ù鐘差儏缁秹鏌嶇悰鈥充壕缂備焦顨呴崐鐟邦嚗閸曨偒鍚嬮柛鏇ㄥ幘濡叉垿姊洪懡銈呬粶婵☆偅鐩敐鐐哄冀椤撶喐娅栭柣蹇曞仧閸嬫捇鎮甸幘鏂ユ闁瑰墽顒查崝鐔哥節閳ь剟宕ㄩ弶鎴烆棟闂佹悶鍎弲鈺侇焽?},
                ],
            }, ensure_ascii=False),
        }

        with patch("app.agent.session_lifecycle.chat_completion", new_callable=AsyncMock, return_value=mock_response):
            await end_session(db, "sess-user-2", "sess-2", AsyncMock())

        result = await db.execute(
            select(Memory).where(Memory.user_id == "sess-user-2")
        )
        memories = result.scalars().all()
        assert len(memories) == 1
        assert memories[0].category == "preference"
        assert "闂備浇宕甸崑娑樜涘☉顫稏? in memories[0].content
        assert memories[0].source_session_id == "sess-2"


@pytest.mark.asyncio
async def test_end_session_empty_conversation(setup_db):
    """No messages 闂?no summary, no crash."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-3", username="sesstest3", hashed_password="x")
        db.add(user)
        await db.commit()

        await end_session(db, "sess-user-3", "sess-3", AsyncMock())

        result = await db.execute(
            select(SessionSummary).where(SessionSummary.session_id == "sess-3")
        )
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_end_session_handles_llm_error(setup_db):
    """If LLM fails, session end should not crash."""
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-4", username="sesstest4", hashed_password="x")
        db.add(user)
        msg = ConversationMessage(session_id="sess-4", role="user", content="hello")
        db.add(msg)
        await db.commit()

        with patch("app.agent.session_lifecycle.chat_completion", new_callable=AsyncMock, side_effect=Exception("LLM down")):
            # Should not raise
            await end_session(db, "sess-user-4", "sess-4", AsyncMock())

        result = await db.execute(
            select(SessionSummary).where(SessionSummary.session_id == "sess-4")
        )
        assert result.scalar_one_or_none() is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_session_lifecycle.py -v`
Expected: FAIL 闂?`ModuleNotFoundError: No module named 'app.agent.session_lifecycle'`

- [ ] **Step 3: Implement session_lifecycle.py**

```python
# app/agent/session_lifecycle.py
"""Session end processing: generate summary and extract memories."""

import json
import logging

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm_client import chat_completion
from app.models.conversation_message import ConversationMessage
from app.models.memory import Memory
from app.models.session_summary import SessionSummary

logger = logging.getLogger(__name__)

_EXTRACT_PROMPT = """闂備礁鎲＄敮鎺懳涘▎鎾村€甸柤鎭掑劤椤╃兘鏌曟径鍫濃偓妤呮偡閹剧粯鍊甸柣銏☆問閺€浼存煟閿旇法鐭欓柡浣哥Т閻ｆ繈宕橀鍡欏€抽梻?JSON闂備焦瀵х粙鎴︽偋閸涱垳绠斿璺烘湰閸熷搫霉閿濆洦娅曠紓鍫濐煼閺屾盯骞嬪┑鍥ㄥ創闂佸憡鐟ч崑鎾剁矉閹烘鍐€鐟滃秹寮崼鏇熷€甸柛锔诲幗椤忕喓绱掓潏銊ュ摵闁?
{
  "summary": "濠电偞鍨堕幐鎾磻閹剧粯鐓曟繛鍡楃Т閸斻儵鏌ｉ敂璺ㄧ煓妤犵偐鍋撻梺鐓庮潟閸婃鈻旈姀銈呯骇闁冲搫鍊婚幊鍕亜閹邦垰浜归柍褜鍓涢弫鎼併€佹繝鍥ㄥ剨濞寸姴顑呯壕缁樻叏濮楀棗浜為柛鐔凤工闇夐柣姗嗗亜娴滅偓绻?,
  "actions": ["闂備礁婀遍悷鎶藉幢閳哄倹鏉搁梻浣圭湽閸斿瞼鈧凹鍙冮獮鏍煥鐎ｎ偄顎撳┑鐘诧工閸燁偊鎮樺▎鎾村仩?],
  "memories": [
    {"category": "preference|habit|decision|knowledge", "content": "闂備胶顭堥敃锕傚储瑜忓▎銏ゆ焼瀹ュ棌鎷归梺鍦焾鐎涒晠宕洪崒鐐村仯濞撴埃鍋撴い锝忓缁辩偤宕堕浣稿壄闂佸憡娲︽禍娆戞崲閸℃稒鐓?}
  ]
}

闂佽崵鍠愰悷銉р偓姘煎墴瀹曞綊顢涢悙瀛樻珫?- summary 闂佽崵鍠愬ú鎴︽嚄閸洘鍋╂繝闈涙灩閻戞鐟瑰┑鐘插椤︻喗绻涢幋鐐村皑闁稿鎸搁埥澶愬箻閸楃偐鍋撻弴掳浜归柣鎰仛鐎?- memories 闂備礁鎲￠悷顖涚濠靛浜瑰〒姘ｅ亾鐎规洩缍佸浠嬵敃閿濆棙顓归梻浣筋潐閹告娊寮ㄩ崡鐐嶏綁骞嬮悩鍐插幑濡炪倖妫侀敓銉╁焵椤掆偓閸燁垰顭囪箛娑樼鐟滃酣鎮鹃柆宥嗙厱閻庯綆浜炵粻浼存煏閸粎鐭欏┑鈥崇摠閹峰懏顦版惔锝嗩潠闂備浇顕栭崹濂稿垂闁秴鍨傞柕濞炬櫆閻撳倻鈧箍鍎遍悧婊兠洪敐澶嬬厱闁归偊鍓涢敍宥夋煟?- 濠电偞鍨堕幐鍝ョ矓閻戝鈧懘鏁冮崒姘鳖唺闂侀潧顭梽鍕倿娴犲鐓ユ繛鎴烆焽婢с垽鏌℃担闈涒偓婵嬬嵁鐎ｎ喗鍋い鏍电到濞?闂備胶鎳撻悺銊╁垂閸洖姹查柣鏃囥€€閸嬫挸鈽夊畷鍥╃獥缂備焦顨呴ˇ鎵紦?闂備焦鍓氶崑鍛暜閻旂⒈鏁婇柛銉簵娴滃綊鏌￠崶鏈电敖妤犵偑鍨介弻锝夛綖椤掆偓婵′粙鏌涢埡鍌滄创闁硅櫕鎹囧畷妯款槾闁?0闂備礁鎲＄敮鎺懳涘畝鍕柈閻庯綆鍋嗛埢鏃傗偓骞垮劚濡鎳欒ぐ鎺撶厸闁稿被鍊曞璺ㄧ磼?- 濠电偞鍨堕幐鎼佹偤閵娿儺娓婚柛宀€鍋涚粻鎴犳喐鐏炲墽鈹嶅┑鐘叉搐缁犳帗銇勯弽銊ф噮闁荤喐绻堥幃瑙勬媴缁嬭法鐩庣紓?濠电偛顕慨鎾晝閵堝桅濠㈣泛顑囬埢鏃傗偓骞垮劚濡宕㈤幒妤佸€垫繛鎴濈－缁辨壆绱?闂?- 濠电姷顣介埀顒€鍟块埀顒€缍婇幃妯诲緞婵炵偓鐓㈤梺鏂ユ櫅閸燁垳绮婚幒妤佺厱濠电姴瀚敮鍓佺磼閹鍚柟宄邦儐閿涙劖鎷呴搹鍓愩倝姊哄Ч鍥у閻庢凹浜濈粚杈ㄧ節閸パ呯暢濡炪倖鐗撻崐妤冪矆婵夌ざmories 濠电偞鍨堕幑浣糕枍閿濆鐓橀柡宥庡幖閺嬩線鏌熷▓鍨灓闁?""


async def end_session(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    llm_client: AsyncOpenAI,
) -> None:
    """Process session end: generate summary and extract memories.

    This is called when the WebSocket disconnects or times out.
    Failures are logged but never raised 闂?session end must not crash.
    """
    # Load conversation messages
    result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.timestamp)
    )
    messages = result.scalars().all()

    if not messages:
        return

    # Build conversation text for the LLM
    conversation_text = "\n".join(
        f"{msg.role}: {msg.content}" for msg in messages if msg.content
    )

    try:
        response = await chat_completion(
            llm_client,
            [
                {"role": "system", "content": _EXTRACT_PROMPT},
                {"role": "user", "content": conversation_text},
            ],
        )
        content = response.get("content", "").strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])

        data = json.loads(content)
    except Exception:
        logger.warning("Failed to generate session summary for %s", session_id, exc_info=True)
        return

    # Save session summary
    summary_text = data.get("summary", "")
    actions = data.get("actions", [])
    if summary_text:
        summary = SessionSummary(
            user_id=user_id,
            session_id=session_id,
            summary=summary_text,
            actions_taken=actions,
        )
        db.add(summary)

    # Extract and save memories
    for mem_data in data.get("memories", []):
        category = mem_data.get("category", "")
        mem_content = mem_data.get("content", "")
        if category and mem_content:
            mem = Memory(
                user_id=user_id,
                category=category,
                content=mem_content,
                source_session_id=session_id,
            )
            db.add(mem)

    await db.commit()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_session_lifecycle.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd student-planner
git add app/agent/session_lifecycle.py tests/test_session_lifecycle.py
git commit -m "feat: add session lifecycle with summary generation and memory extraction"
```

---

### Task 7: Wire Session Lifecycle into Chat WebSocket

Call `end_session` when the WebSocket disconnects. Also add a 2-hour inactivity timeout that triggers a new session.

**Files:**
- Modify: `student-planner/app/routers/chat.py`
- Modify: `student-planner/app/config.py` (add session timeout config)

- [ ] **Step 1: Add session timeout config**

Add to `app/config.py` Settings class:

```python
    # Session settings
    session_timeout_minutes: int = 120  # 2 hours inactivity 闂?new session
```

The full Settings class after modification:

```python
class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./student_planner.db"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    llm_api_key: str = "sk-placeholder"
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-chat"
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.3
    vision_llm_api_key: str = ""
    vision_llm_base_url: str = ""
    vision_llm_model: str = "qwen-vl-plus"
    session_timeout_minutes: int = 120

    model_config = {"env_prefix": "SP_"}
```

- [ ] **Step 2: Modify chat.py to call end_session on disconnect**

Replace `app/routers/chat.py` with:

```python
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.agent.llm_client import create_llm_client
from app.agent.loop import run_agent_loop
from app.agent.session_lifecycle import end_session
from app.auth.jwt import verify_token
from app.database import get_db
from app.models.user import User

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        auth_message = await websocket.receive_json()
        token = auth_message.get("token")
        if not token:
            await websocket.send_json({"type": "error", "message": "Missing token"})
            await websocket.close()
            return

        user_id = verify_token(token)
        if not user_id:
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            await websocket.close()
            return
    except Exception:
        await websocket.close()
        return

    session_id = str(uuid.uuid4())
    llm_client = create_llm_client()
    await websocket.send_json({"type": "connected", "session_id": session_id})

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            if not user_message:
                continue

            async for db in get_db():
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                if not user:
                    await websocket.send_json({"type": "error", "message": "User not found"})
                    break

                generator = run_agent_loop(user_message, user, session_id, db, llm_client)
                try:
                    event = await generator.__anext__()
                    while True:
                        await websocket.send_json(event)
                        if event["type"] == "ask_user":
                            user_response = await websocket.receive_json()
                            user_answer = user_response.get("answer", "缂備胶铏庨崣搴ㄥ窗濞戙埄鏁?)
                            event = await generator.asend(user_answer)
                        elif event["type"] == "done":
                            break
                        else:
                            event = await generator.__anext__()
                except StopAsyncIteration:
                    pass
    except WebSocketDisconnect:
        # Session ended 闂?generate summary and extract memories
        async for db in get_db():
            await end_session(db, user_id, session_id, llm_client)
```

- [ ] **Step 3: Commit**

```bash
cd student-planner
git add app/routers/chat.py app/config.py
git commit -m "feat: call session lifecycle on WebSocket disconnect"
```

---

### Task 8: Update Agent.md 闂?Memory Tool Rules

Add behavior rules for the memory tools to Agent.md.

**Files:**
- Modify: `student-planner/Agent.md`

- [ ] **Step 1: Add memory tool usage rules**

Add the following under the `### 闁诲氦顫夐幃鍫曞磿闁秴鐭楅柟绋垮婵挳鎮归幁鎺戝闁哄棗鍖?section in `Agent.md`:

```markdown
- recall_memory闂備焦瀵х粙鎺楁嚌閸撗呯閻庯綆鍠楅ˉ鍡涙煃瑜滈崜娑㈠箟閻楀牊濯撮柛娑橈功椤︺儵妫呴銏℃悙婵☆偅鐩顐﹀Χ婢跺﹦顓洪梺鐐壘閸婂顢樺ú顏呯厱闁规儳纾倴濠电偛鐗婇崹鍨暦閹达絿鐤€闁规儳宕禒娲⒑闂堟稒顥欐俊鐐村笧瀵囧礋椤栨氨鐣惧銈嗙墬缁嬫垿鎮樺Δ鍛厱闁归偊鍓涢敍宥夋煟鎺抽崕闈涱嚕椤曗偓瀵敻妫冨☉鎺撶€奸梻浣规た濞煎潡宕濇繝鍥х劦妞ゆ巻鍋撻柛濠囶棑缁厽寰勭仦鎯ф毇婵炶揪绲藉﹢鍗炍ｉ妸锔剧闁糕€崇箚閸嬫捇骞囨担鍛婎啅闂佽崵濮村ú锔炬崲閸儱绀傛俊顖氬悑鐎氼剟鏌涢幇鍏哥凹闁哄棗绻橀弻銊モ槈濡灝顏悷婊勫Ω閸パ勫祶闂侀潧臎閳ь剟鍩€椤掍緡鐒介柍褜鍓欏﹢閬嶅磻閵堝懌鈧帡宕滄担鐟版毇婵炶揪绲块…鍫ュ锤婵犲洦鐓曟繛鍡樺笒缁憋箑菐閸パ嶈含妤犵偘绶氶、娑樷槈濞嗘ɑ袧濠电偠鎻紞鈧繛澶嬫礋瀵?- save_memory闂備焦瀵х粙鎺楁嚌閹规劑浜圭憸搴ｇ矚閸楃偐鏀介柛鈩冪懄閹插ジ姊哄ú缁樺▏闁告柨绉瑰畷鍝勨槈閵忕姴寮烽柟鑹版彧缁叉椽鍩€椤掍緡鐒介柟顔诲嵆婵℃悂濡搁敃鈧☉褔姊哄Ч鍥у閻庢凹浜濈粚杈ㄧ節閸パ呯暢濡炪倖鐗撻崐妤冪矆婢跺ň妲堥柟鎯х－鍟稿銈傛櫔缁犳捇鐛幒妤€惟闁挎梻鏅崝鐑芥⒑闂堟稒顥滈柛濠囶棑閹广垹顫濋幍浣镐壕婵炴垶顏鍛珷闁绘娅ｉ悿鈧梺鍛婄⊕閻ｎ亪鍩€椤掆偓缁绘ê鐣峰Δ鍛唶闁靛繆鍓濆▓?ask_user 缂備胶铏庨崣搴ㄥ窗濞戙埄鏁囧┑鐘崇閺?闂備胶鎳撻悺銊╁垂婵傚壊鏁婇柛銉ｅ妽婵挳鐓崶褎鎹ｉ柛鐔凤躬閺屻劌鈽夊▎鎴炴啺闂備礁鎲￠崝鏇㈠箠鎼搭煈鏁婇柟顒勭畺閺屾洟宕卞Δ鈧埀顒佹倐椤㈡岸顢氶埀顒€鐣烽妷銉庢梻鈧綆鍓欓幆?
  - preference闂備焦瀵х粙鎺戭潩閵娾晛鏋侀柕鍫濐槸缁狅絿鈧懓瀚伴。锕傛倿婵犲倵鏀介柛灞剧⊕閻忣喚绱?闂備胶鎳撻悺銊╁垂閻㈢鍑犻柍杞拌閺嬪酣鏌曡箛濠傚⒉闁挎稑绉撮埥澶愬箻缁涚懓浼愬銈忕畱瀵墎绮欐繝鍥ㄥ亹闁惧浚鍋呴宥夋煟?闂?  - habit闂備焦瀵х粙鎺楁嚌妤ｅ喚鏁嗛柣鏂挎憸閳绘洟鏌ｅΟ澶稿惈闁伙箑閰ｉ弻鐔碱敍閿濆懐浼堢紓?闂備胶鎳撻悺銊╁垂瀹曞洨鍗氶柡澶嬪灍閺嬪酣鏌嶉埡浣告殲濞寸姵锚椤潡鎳滈棃娑樻懙濠电偛顧€闂勫嫮绮?闂佽绻愮换鎰崲閹存繍娓?闂?  - decision闂備焦瀵х粙鎺戠暆閹间礁闂柛婵勫劜閸熷搫霉閿濆浂鐒鹃柡瀣у亾缂傚倷鐒︾粙鎺楁偋椤撶姵顫?濠德板€曢崐纭呮懌闂佸搫妫涢崰鏍箖娴犲惟闁靛鍎抽埀顒冨吹缁辨帡寮崒姣款剙鈹戦埥鍡楀箻缂侇喚鏁诲浠嬵敃閿濆棭鍚?闂?  - knowledge闂備焦瀵х粙鎺撶┍濞差亶鏁嬬€规洖娲ㄩ惌娆撴倵閿濆骸寮鹃柛姘喘閺岋綁顢樺鍐ㄥХ缂?闂備焦妞垮鍧楀礉瀹ュ鏄ユ繛鎴炵閸犲棗顭跨捄鐚村姛缂佽鐒﹂幈銊╁箳閹存績鍋撶拠宸晠闁兼祴鏅滄刊濂告煟閹寸倖鎴炵濮椻偓濮?闂?- 濠电偞鍨堕幐鍝ョ矓閻戝鈧懘鏁傞悾灞告敵濠电娀娼уΛ娑㈠箺閻樻祴妲堥柟鎯х－閹界姵淇婇悙鎻掆偓鍧楃嵁閳ь剛鎲哥仦鍓р攳濠电姴娲ょ粻鎺撱亜閺嶃儱鈧绮?濠电偛顕慨鎾晝閵堝桅濠㈣泛顑囬埢鏃傗偓骞垮劚濡宕㈤幒妤佸€垫繛鎴濈－缁辨壆绱?闂?- 濠电偞鍨堕幐鍝ョ矓閻戝鈧懘鏁傞悾灞告敵濠电娀娼уΛ娑㈠箺閻樼鍋撶憴鍕憙閻忓繑鐟ч崚鎺楁晸閻樺弶宓嶉梺闈涱煭闂勫嫬鈻撻崼鏇熺厵閻犲洠鈧櫕鐏堢紓浣靛姀妞村摜绮欐径鎰垫晣闁绘ê纾弳鐘崇箾閿濆懏绀岄柛鎾寸箖鐎靛ジ宕ㄧ€涙ɑ娅栭梺鍓插亾缂嶅棝宕甸敂鍓х＜閻庯綆浜堕崕宥夋煃瑜滈崗娑橆渻閹烘绠查柕蹇嬪€曠粈澶愬箳閹惰棄鐒垫い鎴炲缁佷即鏌嶈閸撴瑩宕幎鑺ュ剨妞ゆ牜鍋為弲?- 闁荤喐绮庢晶妤呭箰妤ｅ啫鏋侀柕鍫濐槸缁狅綁鏌ｉ妶搴＄伇闁?闂傚鍋勫ú锕佹懌闁汇埄鍨崑鎼檟x"闂備礁鎼崯鎶筋敊閹邦喗顫曟繝闈涱儐閸?recall_memory 闂備胶鎳撻悘姘跺磿閹惰棄鏄ョ€光偓閳ь剟鍩€椤掑倹鏆╅柟铏尵閼洪亶鎳犻浣割€涢梺鍝勵槼濞夋洜绮婚幘缁樼叆婵炴垶顭囬悘閬嶆煕閺傜偛娲ょ憴锕傚箹缁懓澧查柛鐔哄仱閺岋綁顢樺鍐ㄥБ闂佽桨闄嶉崐婵嬬嵁鐎ｎ亞鏆嬮柡澶婄仢濞堛儵姊洪崨濠傜濠电偐鍋撳┑?```

- [ ] **Step 2: Add few-shot example for memory**

Add the following as a new example after existing examples in `Agent.md`:

```markdown
### 缂傚倷璁查崑鎾诲级閻愭潙顥嬪ù?闂備焦瀵х粙鎺撶┍濞差亶鏁婇柛銉簽閻も偓闂佺硶鍓濋悷顖炲触閳ь剟姊?
闂備焦妞垮鍧楀礉瀹ュ鏄? "闂備胶鎳撻悺銊╁垂娴ｅ啨浜归柛宀€鍋為崑婵嬫煟濡も偓閻楀﹪鎮甸幘鏂ユ闁瑰墽顒插銉︺亜閿曗偓瀵墎绮欐繝鍥ㄥ亹闁惧浚鍋呴悵锟犳⒑缂佹鐭婃繛璇х畱鐓ら柟绋垮瘨濞堟鎱ㄥΔ鈧悧蹇曠矆婢跺⊕褰掓偐椤旂厧濮庨梺璇″枟椤ㄥ牓寮鈧、娆撴寠婢跺奔鍑介梻浣侯攰濞夋盯鏁冮妶澹﹀洭宕ｆ径灞告灆闂佺粯顭堥褔宕㈤幘顔藉€甸柣鐔煎亰濡插綊鎮介娑欏磳鐎规洜鍏樻俊鎼佹晜閻ｅ苯绲煎┑鐐村灦閹告悂鏁冮妶澶婄畾?

闂?save_memory(category="preference", content="闂備礁鎼幊蹇涙儗椤斿墽绠旈柛灞剧☉缁剁偟鈧箍鍎辩€氼噣鎯佹惔銊︾厸濞达絽鎽滄晶銏⑩偓鍦焾閵堢顕ｉ幘顔肩妞ゆ梹鍎抽拏瀣⒑閹稿海鈽夐柤娲诲灡缁傚秹宕ㄦ繝鍕闂佸吋浜介崕鏌ユ偟閹剧粯鈷掗柛灞剧⊕缂嶆垿鏌ｉ敐鍐ㄥ妤犵偞甯￠獮鎺楀箣椤撶啘鈺傜箾?)
闂?濠电偠鎻徊钘壩涘Δ鍛偍婵炴垶纰嶉崗婊勩亜閺冣偓椤戞瑩宕ラ崶顒佺叆婵炴垶鐟ч幗顤筴_user(type="confirm", question="闂備胶鎳撻悺銊╁垂婵傚壊鏁婇柛銉ｅ妽婵挳鐓崶褎鎹ｉ柛鐔凤躬閺屻劌鈽夊▎鎴犲彎缂傚倸绉甸敃銏狀嚕閹绘帩娼╂い鎰╁€楅幉顏呯節閵忥絾纭剧紒澶婄－瀵囧礋椤栨碍鐎梺鍓插亖閸ㄥ綊鎳為幎鑺ョ厸闁搞儯鍔嶇亸锕傛煟濠垫劕娅嶉柡浣哥Ф娴狅箓姊荤€垫悂鐎洪梻浣告啞閼瑰墽鑺遍懖鈺傤潟妞ゆ挶鍨圭粈鍌炴煕椤愶絿绠橀柡鍡樻閺岀喖鎮滃Ο铏圭懖濠电偛鎳庣€氭澘顫忔繝姘骇闁规惌鍘戒簺濠电偞鍨跺缁樻叏娴兼潙鐒垫い鎺嗗亾闁稿﹥鎮傞、姘额敋閳ь剙鐣烽妷銉庢梻鈧綆鍓欓幆?)
闂?闂備焦妞垮鍧楀礉瀹ュ鏄ユ繛鎴炵閸忔粍銇勯弮鈧娆撳触?闂?save_memory
闂?闂備焦鎮堕崕鎶藉磻濞戔懞? "濠电娀娼ч崐濠氬疾椤愨懇鏋旈柟杈鹃檮閺咁剟鎮橀悙鑸殿棄闁搞倖甯￠幃瑙勭瑹閳ь剟銆傞敂鍓х闁搞儺鍓欒繚闂佺鏈悷銈囪姳娴煎瓨鐓曟慨姗嗗墯閹癸綁鏌℃担瑙勫磳妤犵偛顑夐獮鍥敆婢跺瑩鈺傜箾閹寸偞鈷掑┑顕€绠栭、姗€骞栨担鍝ヮ槴闂佸湱鍎ら幐濠毸囪闇夐柛蹇氬亹閻擃垳绱掓鏍у籍鐎规洘顨婂畷鐓庘攽閸喐顓鹃梻浣告贡閸庛倗鏁Δ鈧埢宥夊礋椤栨稈鎷婚柣搴㈢⊕钃辨い蟻鍕闁割偁鍨规禒顖炴煃?

闂備焦妞垮鍧楀礉瀹ュ鏄? "闂傚鍋勫ú锕佹懌闁汇埄鍨崑鎾寸箾閹寸偞鐓ユい鎴濇噺閺呭爼鎮╅崹顐㈢彴闁诲酣娼ч幉锟犳偩闁秵鐓涢柛鎰剁稻濞呭啰绱掑Δ鈧崐鐟邦嚗閸曨偒鍚嬮柛鏇ㄥ幘濡叉垿姊烘潪鎵妽婵犮垺锕㈤、?

闂?recall_memory(query="闂備礁鎼崯鐘诲疾濞嗘垹绠旈柛灞剧☉缁剁偟鈧箍鍎辩€氼噣鎯佹惔銊︾厸濞达綀顫夌欢鍙夈亜?)
闂?闂備胶鎳撻悘姘跺磿閹惰棄鏄ョ€光偓閳ь剟骞忕€ｎ喖绾ч悹鎭掑妿閻?闂?闂備礁鎲＄敮鐐寸箾閳ь剚绻?闂?闂備焦鎮堕崕鎶藉磻濞戔懞? "闁诲海鎳撻幉陇銇愰崘顔煎瀭鐟滅増甯楅埛鏃堟煏閸繄澧㈢紒鐘茬秺閺屸剝绔熷┃鍨偓銈夊船閸洜鍙撻柛銉戝嫷妫戦梺?
```

- [ ] **Step 3: Commit**

```bash
cd student-planner
git add Agent.md
git commit -m "docs: add memory tool rules and few-shot to Agent.md"
```

---

### Task 9: Conversation History Compression (Sliding Window)

When the conversation history grows too long, compress older messages into a summary while keeping recent messages intact. This is the "second level" compression from the spec.

**Files:**
- Modify: `student-planner/app/agent/loop.py` (add compression check before LLM call)
- Modify: `student-planner/app/services/context_compressor.py` (add conversation compression function)
- Create: `student-planner/tests/test_conversation_compression.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_conversation_compression.py
import json
from unittest.mock import AsyncMock, patch

import pytest

from app.services.context_compressor import compress_conversation_history


@pytest.mark.asyncio
async def test_compress_short_history_unchanged():
    """Short conversations should not be compressed."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "濠电偠鎻徊鎸庢叏閹绢喖围?},
        {"role": "assistant", "content": "濠电偠鎻徊鎸庢叏閹绢喖围濞寸姴顑嗛弲顒€霉閿濆牜娼愮紒鐘冲笒闇夐柣姗嗗亜娴滅偓绻涢幋鐐寸叆闁绘妫滈妵鎰板矗婢跺矈娴勯梺闈涱槶閸庤京鑺辩拠瑁佸綊鏁愰崶顬儲绻涢崼鐔风伌闁?},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    """Long conversations should have older messages compressed."""
    messages = [{"role": "system", "content": "System prompt"}]
    # Add 20 user/assistant pairs
    for i in range(20):
        messages.append({"role": "user", "content": f"闂備焦妞垮鍧楀礉瀹ュ鏄ユ繛鎴炃氬Σ鍫ユ煕椤愩倕鏋嶇紒?{i}"})
        messages.append({"role": "assistant", "content": f"闂備礁鎲￠弻锟犲疾濠婂嫭娅犳繝濠傜墕閻愬﹪鏌ｉ幇顒佲枙婵?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "濠电偞鍨堕弻銊╊敄閸涱喗娅犻柣妯肩帛閸庡秹鏌涢弴銊ヤ航闁搞倗濞€閹綊宕堕妸褏鐣遍梺鐓庣仛閸ㄥ潡寮鍛殕闁逞屽墴瀵偊濡舵径濠勵吅閻庣懓瀚妯煎緤濞差亝鈷戞い鎰ㄥ墲椤﹂绱?0闂備礁鎼ˇ顐﹀礈濠靛牏鐭撻柣鎴ｆ缁犳帗銇勯弽銉モ偓妤冪矆婢舵劖鐓曢柡鍌滃劋濞呭棗顭胯缁捇寮婚崼銉﹀癄濠㈣泛顦辨す铏箾鐎涙鐭婃俊顐ｎ殔鐓ら柡宥冨妼缁剁偟鈧箍鍎遍崯鐘诲磻?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # System prompt should be preserved
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"

    # Should have a summary message
    assert any("濠电偞鍨堕弻銊╊敄閸涱喗娅犻柣妯肩帛閸庡秹鏌涢弴銊ヤ航闁搞倗濞€閹? in m.get("content", "") for m in result)

    # Recent messages should be preserved (last 12 non-system messages = 6 pairs)
    assert len(result) <= 14  # system + summary + 12 recent


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    """The most recent messages should be kept intact."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(20):
        messages.append({"role": "user", "content": f"婵犵數鍋為崹鐢告偋婵犲啫顕?{i}"})
        messages.append({"role": "assistant", "content": f"闂備焦鎮堕崕鎶藉磻濞戔懞?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "闂備礁鎼崯鐘诲疾濠婂喛鑰块柨娑樺閸嬫捇鎮藉▓鎸庢暞闂佷紮缂氱划娆撶嵁濡も偓铻ｆ繛鍡欏亾閻?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # Last message should be the most recent assistant reply
    assert result[-1]["content"] == "闂備焦鎮堕崕鎶藉磻濞戔懞?19"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: FAIL 闂?`ImportError: cannot import name 'compress_conversation_history'`

- [ ] **Step 3: Add compress_conversation_history to context_compressor.py**

Append to `app/services/context_compressor.py`:

```python
from app.agent.llm_client import chat_completion as _chat_completion

_SUMMARIZE_PROMPT = """闂佽崵濮村ú顓⑺夐幘璇叉瀬?-3闂備礁鎲￠悷锝夊磿閹绢喗鍎婂ù鐘差儏缁犳垿鏌ゆ慨鎰偓妤€鈻旈姀鐘嗗綊鎮╅鐓庡缂備焦顨呴幊鎰板焵椤掑倹鏆╂い銏狅躬閹焦绂掔€ｎ亞顦ㄩ梺鍛婁緱閸欏酣宕崶顒佺厪闁糕剝顨呴埀顒€娼″畷鎶藉箹娴ｇ懓鈧兘姊洪锝囥€掔紒鐘辩矙閺岋綁鏁愰崱娆愬殏缂備礁褰夐崡鎶藉箖娴犲惟闁挎洍鍋撻柣鎾存礋閺屾稓鈧綆鍋嗛悡顖滅磼閵娿垹澧茬紒鍌涘浮閸┾偓妞ゆ帊鑳堕埢鏇㈡煕椤愩倕鏋戦柟顖涚懃闇夐柨婵嗘濞堢娀鏌嶈閸忔盯鎳楅崼鏇炵伋婵☆垰鍚嬫刊濂告煏閸繂顏柛鐔凤工闇夐柣姗嗗亜娴滅偓绻涢幋鐐寸叆闁绘瀚伴崺鈧い鎴炲缁佷即鏌曢崱妤€鏆炴繛鐓庣箻瀹曪綁濡疯閺呪晜绻涚€电袥闁稿鎸搁埥澶愬棘鐠恒劌顣烘繛瀛樼矊閹诧紕缂撻懞銉﹀弿闁硅埇鍔屾禍?""


async def compress_conversation_history(
    messages: list[dict],
    llm_client,
    max_messages: int = 12,
) -> list[dict]:
    """Compress conversation history when it exceeds max_messages.

    Keeps the system prompt and the most recent max_messages messages.
    Older messages are summarized into a single message.

    Args:
        messages: Full message list (system + user/assistant/tool messages).
        llm_client: OpenAI-compatible async client for summarization.
        max_messages: Max non-system messages to keep uncompressed.

    Returns:
        Compressed message list.
    """
    # Separate system prompt from conversation
    system_msgs = [m for m in messages if m.get("role") == "system"]
    conv_msgs = [m for m in messages if m.get("role") != "system"]

    if len(conv_msgs) <= max_messages:
        return messages

    # Split: old messages to compress, recent messages to keep
    cutoff = len(conv_msgs) - max_messages
    old_msgs = conv_msgs[:cutoff]
    recent_msgs = conv_msgs[cutoff:]

    # Summarize old messages
    old_text = "\n".join(
        f"{m.get('role', 'unknown')}: {m.get('content', '')}"
        for m in old_msgs
        if m.get("content")
    )

    try:
        response = await _chat_completion(
            llm_client,
            [
                {"role": "system", "content": _SUMMARIZE_PROMPT},
                {"role": "user", "content": old_text},
            ],
        )
        summary = response.get("content", "闂備焦瀵х粙鎴︽偋婵犲伣娑㈩敇閵忕姴鐝橀梺缁樻煥椤ㄥ酣宕甸悩缁樺仯闁搞儯鍔庣粻鏍煙閹绘帞锛嶉柟鑼閹峰懏顦版惔锝嗗枓闂備礁鎲￠悷顖炲垂閹惰棄鏋侀柕鍫濐槹閺?)
    except Exception:
        summary = "闂備焦瀵х粙鎴︽偋婵犲伣娑㈩敇閵忕姴鐝橀梺缁樻煥椤ㄥ酣宕甸悩缁樺仯闁搞儯鍔庣粻鏍煙閹绘帞锛嶉柟鑼閹峰懘鎮滃Ο缁橆仧闂備胶鎳撻悺銊╁礉閺囥垹桅闁瑰濮电€氬鏌曟径妯虹仯缂佲偓?

    summary_msg = {
        "role": "user",
        "content": f"[濠电偞鍨堕弻銊╊敄閸涱喗娅犻柣妯肩帛閸庡秹鏌涢弴銊ヤ航闁搞倗濞€閹綊宕堕妸褏鐣洪梺瑙勫絻绾绢參骞夐悧鍫⑩枙?{summary}",
    }

    return system_msgs + [summary_msg] + recent_msgs
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Integrate into agent loop**

In `app/agent/loop.py`, add this import:

```python
from app.services.context_compressor import compress_conversation_history
```

Then, inside the `for iteration in range(MAX_ITERATIONS):` loop, add compression check before the LLM call. Insert before `response = await chat_completion(...)`:

```python
        # Compress conversation history if it's getting too long
        if len(messages) > 14:  # system + 12+ conversation messages
            messages = await compress_conversation_history(messages, llm_client, max_messages=12)
```

- [ ] **Step 6: Run all tests**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py tests/test_loop_compression.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
cd student-planner
git add app/services/context_compressor.py app/agent/loop.py tests/test_conversation_compression.py
git commit -m "feat: add sliding window conversation compression"
```

---

### Task 10: Update AGENTS.md 闂?Mark Plan 4 Progress

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Update progress in AGENTS.md**

Update the Plan 4 line and current status:

```markdown
- [ ] Plan 4: Memory + 濠电偞鍨堕幐鎼佹晝閿濆洨绠旈柛娑欐綑濡﹢鏌涢妷銏℃珦闁告埃鍋撻梻浣藉吹閸嬫稑螞鐎靛憡顫?0 濠?task闂?```

Update "闁荤喐绮庢晶妤呭箰閸涘﹥娅犻柣妯烘▕濞间即鏌ㄥ┑鍡樺櫤闂婎剦鍓熼弻鐔虹箔濞戞ɑ锛嶉柡鈧? to reflect Plan 4 completion.

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with Plan 4 completion status"
```
