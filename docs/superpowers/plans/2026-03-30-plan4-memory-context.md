# Plan 4: Memory 缂侇垵宕电划?+ 濞戞挸锕ｇ粭鍛村棘閸モ晩鍚€闁?
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer memory system (working/short-term/long-term) and context window management to keep conversations coherent across sessions without blowing up the context window.

**Architecture:** Memory CRUD service handles persistence. Two new agent tools (`recall_memory`, `save_memory`) give the LLM on-demand access. Tool result compression summarizes verbose outputs inline. Session lifecycle hooks generate summaries and extract memories at session end. The system prompt builder loads hot/warm memories at session start.

**Tech Stack:** SQLAlchemy async (existing), OpenAI-compatible LLM for summarization, existing agent tool system

**Depends on:** Plan 1 (Memory, SessionSummary, ConversationMessage models), Plan 2 (agent loop, tool_executor, llm_client)

---

## File Structure

```
student-planner/
闁宠澹曢弨銏ゅ煘閳?app/
闁?  闁宠澹曢弨銏ゅ煘閳?services/
闁?  闁?  闁宠澹曢弨銏ゅ煘閳?memory_service.py          # Memory CRUD: create, query, update, delete, staleness
闁?  闁?  闁宠鏌￠弨銏ゅ煘閳?context_compressor.py      # Tool result summarization + conversation compression
闁?  闁宠澹曢弨銏ゅ煘閳?agent/
闁?  闁?  闁宠澹曢弨銏ゅ煘閳?tools.py                   # (modify: add recall_memory, save_memory definitions)
闁?  闁?  闁宠澹曢弨銏ゅ煘閳?tool_executor.py           # (modify: add recall_memory, save_memory handlers)
闁?  闁?  闁宠澹曢弨銏ゅ煘閳?loop.py                    # (modify: add tool result compression after each tool call)
闁?  闁?  闁宠澹曢弨銏ゅ煘閳?context.py                 # (modify: add hot/warm memory loading)
闁?  闁?  闁宠鏌￠弨銏ゅ煘閳?session_lifecycle.py       # Session end: generate summary + extract memories
闁?  闁宠澹曢弨銏ゅ煘閳?routers/
闁?  闁?  闁宠鏌￠弨銏ゅ煘閳?chat.py                    # (modify: call session lifecycle on disconnect/timeout)
闁?  闁宠鏌￠弨銏ゅ煘閳?config.py                      # (modify: add context window thresholds)
闁宠澹曢弨銏ゅ煘閳?tests/
闁?  闁宠澹曢弨銏ゅ煘閳?test_memory_service.py         # Memory CRUD unit tests
闁?  闁宠澹曢弨銏ゅ煘閳?test_context_compressor.py     # Compression logic tests
闁?  闁宠澹曢弨銏ゅ煘閳?test_memory_tools.py           # recall_memory / save_memory tool tests
闁?  闁宠澹曢弨銏ゅ煘閳?test_session_lifecycle.py      # Session end flow tests
闁?  闁宠鏌￠弨銏ゅ煘閳?test_context_loading.py        # Hot/warm memory in system prompt tests
```

---

### Task 1: Memory CRUD Service

Pure data layer 闁?no LLM calls. Handles create, query by category, query by relevance, update `last_accessed`, and staleness marking.

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
            content="闁哥姵绮嶉浠嬪籍閳衡偓缁楀倹寰勫鍕槑闁轰焦婢橀?,
            source_session_id="session-abc",
        )
        assert mem.id is not None
        assert mem.category == "preference"
        assert mem.content == "闁哥姵绮嶉浠嬪籍閳衡偓缁楀倹寰勫鍕槑闁轰焦婢橀?
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

        await create_memory(db, "mem-user-2", "preference", "闁哄啠鏅欑粭鍌涘緞瀹ュ嫮鐦庨柡浣规緲椤?)
        await create_memory(db, "mem-user-2", "habit", "濞戞挴鍋撴繛鍡忓墲濞撹埖寰?閻忓繐绻戝?)
        await create_memory(db, "mem-user-2", "decision", "濡ゅ倹蓱閺嗙喖鎮介妸銉ョ€荤紒鏃傚Ь婵☆厾绮甸弽顐ｆ")

        hot = await get_hot_memories(db, "mem-user-2")
        categories = {m.category for m in hot}
        assert "preference" in categories
        assert "habit" in categories
        # decision is NOT hot 闁?it's cold (on-demand)
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
        await create_memory(db, "mem-user-3", "decision", "濡ゅ倹蓱閺嗙喖鎮介妸銉ョ€荤紒鏃傚Ь婵☆厾绮甸弽顐ｆ")

        # Old memory (simulate 30 days ago)
        old_mem = Memory(
            user_id="mem-user-3",
            category="decision",
            content="缂佹儳銇橀崬顒勬偨閵娿儱鐓曞Λ鐗堫焽閻°儵鎮?,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_mem)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)
        assert len(warm) == 1
        assert warm[0].content == "濡ゅ倹蓱閺嗙喖鎮介妸銉ョ€荤紒鏃傚Ь婵☆厾绮甸弽顐ｆ"


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "濡ゅ倹蓱閺嗙喖鎮介妸銉ョ€荤紒鏃傚Ь婵☆厾绮甸弽顐ｆ闁挎稑鏈弲銉╁几濠娾偓缁楀鏌?)
        await create_memory(db, "mem-user-4", "preference", "闁哥姵绮嶉浠嬪籍閳衡偓缁楀倹寰勫鍕槑")
        await create_memory(db, "mem-user-4", "knowledge", "婵帒鍊诲鑲╂媼閻戞ɑ浠橀梻?)

        results = await recall_memories(db, "mem-user-4", query="濡ゅ倹蓱閺?)
        assert len(results) >= 1
        assert any("濡ゅ倹蓱閺? in m.content for m in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-5", "decision", "濡ゅ倹蓱閺嗙喖鎮介妸銉ョ€荤紒鏃傚Ь婵☆厾绮甸弽顐ｆ")
        original_accessed = mem.last_accessed

        # Small delay to ensure timestamp differs
        results = await recall_memories(db, "mem-user-5", query="濡ゅ倹蓱閺?)
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

        mem = await create_memory(db, "mem-user-6", "preference", "闁哄啠鏅欑粭鍌涘緞瀹ュ嫮鐦?)
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

        mem = await create_memory(db, "mem-user-7", "preference", "闁哄啠鏅欑粭鍌涘緞瀹ュ嫮鐦?)
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
            content="闁哄唲鍛暠闁告劕纾悺?,
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
Expected: FAIL 闁?`ModuleNotFoundError: No module named 'app.services.memory_service'`

- [x] **Step 3: Implement memory_service.py**

```python
# app/services/memory_service.py
"""CRUD operations for the Memory table."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory

# Hot memory categories 闁?always loaded into system prompt
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
                "weekday": "闁告稏鍔嬬粭?,
                "free_periods": [
                    {"start": "08:00", "end": "10:00", "duration_minutes": 120},
                    {"start": "14:00", "end": "16:00", "duration_minutes": 120},
                ],
                "occupied": [
                    {"start": "10:00", "end": "12:00", "type": "course", "name": "濡ゅ倹蓱閺?},
                ],
            },
            {
                "date": "2026-04-02",
                "weekday": "闁告稏鍔屽ú?,
                "free_periods": [
                    {"start": "09:00", "end": "11:00", "duration_minutes": 120},
                ],
                "occupied": [],
            },
        ],
        "summary": "2026-04-01 闁?2026-04-02 闁?3 濞戞搩浜為埞鏍⒒閸欏鍞介柨娑樻湰閳ь剚妲掗?6 閻忓繐绻戝?0 闁告帒妫濋幐?,
    }
    compressed = compress_tool_result("get_free_slots", result)
    # Should use the existing summary field
    assert "3 濞戞搩浜為埞鏍⒒閸欏鍞? in compressed
    assert "6 閻忓繐绻戝? in compressed
    # Should NOT contain the full slot details
    assert "free_periods" not in compressed


def test_compress_list_courses():
    result = {
        "courses": [
            {"id": "1", "name": "濡ゅ倹蓱閺?, "teacher": "鐎?, "weekday": 1, "start_time": "08:00", "end_time": "09:40"},
            {"id": "2", "name": "缂佹儳銇橀崬?, "teacher": "闁?, "weekday": 3, "start_time": "10:00", "end_time": "11:40"},
            {"id": "3", "name": "闁兼槒绮鹃?, "teacher": "闁?, "weekday": 2, "start_time": "08:00", "end_time": "09:40"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_courses", result)
    assert "3" in compressed
    assert "濡ゅ倹蓱閺? in compressed


def test_compress_list_tasks():
    result = {
        "tasks": [
            {"id": "1", "title": "濠㈣泛绉崇弧鍕殗濡粯娈剁紒妤婂厸缁斿绮?, "status": "completed"},
            {"id": "2", "title": "濠㈣泛绉崇弧鍕殗濡粯娈剁紒妤婂厸缁ㄢ晝绮?, "status": "pending"},
            {"id": "3", "title": "濠㈣泛绉崇弧鍕棯婢剁鏁?, "status": "pending"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_tasks", result)
    assert "3" in compressed
    assert "1" in compressed  # completed count


def test_compress_create_study_plan():
    result = {
        "tasks": [
            {"title": "濠㈣泛绉崇弧鍕殗濡粯娈剁紒妤婂厸缁斿绮?, "date": "2026-04-01"},
            {"title": "濠㈣泛绉崇弧鍕殗濡粯娈剁紒妤婂厸缁ㄢ晝绮?, "date": "2026-04-02"},
            {"title": "濠㈣泛绉崇弧鍕棯婢剁鏁?, "date": "2026-04-03"},
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
Expected: FAIL 闁?`ModuleNotFoundError: No module named 'app.services.context_compressor'`

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
        return f"[缂佸本妞藉Λ浠嬪籍閼告鍞介柡灞诲劥椤曟绱掗幘瀵镐函] {summary}"
    slots = result.get("slots", [])
    total = sum(len(d.get("free_periods", [])) for d in slots)
    return f"[缂佸本妞藉Λ浠嬪籍閼告鍞介柡灞诲劥椤曟绱掗幘瀵镐函] {len(slots)} 濠㈠灈鏅槐婵嬪礂?{total} 濞戞搩浜為埞鏍⒒閸欏鍞?


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = [c["name"] for c in courses[:5]]
    names_str = "闁?.join(names)
    if count > 5:
        names_str += f" 缂?{count} 闂?
    return f"[閻犲洤澧介埢濂稿礆濡ゅ嫨鈧儩 闁?{count} 闂傚倶鍔忛鎶芥晬濮濈俯ames_str}"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    pending = count - completed
    return f"[濞寸姾顕ф慨鐔煎礆濡ゅ嫨鈧儩 闁?{count} 濞戞搩浜欓幑銏ゅ礉閳藉懐绀墈completed} 濞戞搩浜滈崙锛勨偓鐟版湰閸ㄦ岸鏁嶇€靛獫ending} 濞戞搩浜滅欢鐔衡偓鐟版湰閸?


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    return f"[濠㈣泛绉崇弧鍕媼閳ュ啿鐏奭 鐎规瓕灏欓弫鎾诲箣?{count} 濞戞搩浜滈ˇ鍙夌▕閻樿鲸宕查柛?


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

### Task 3: Agent Tools 闁?recall_memory + save_memory

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
            "description": "濞寸姴娴烽弫銈夊箣妞嬪孩鐣遍梻鈧幐搴㈠焸閻犱焦婢樼换鍌涚▔椤撶噥姊剧紒渚垮灮濞村宕楅崗鍛箚闁诡収鍨埀顒€鍊哥紞瀣閳ь剛鎲版担鍛婄闊洤妫涢弫銈夊箣閾氬倻顓洪柛鎾崇Ф濞堟垿宕戣箛鎾卞仺闁靛棔妞掔弧鍕箚椤栨稑鐏楅柛鎰－閻°儵寮張闈涒枏闁活潿鍔婇埀顒€鍊界换鎴﹀炊閻愭彃鐖遍梺鏉跨Ф濞堟垹鎷嬮弶璺ㄧ畵闁告帗顨夐妴鍐Υ?,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "闁瑰吋绮庨崒銊╁礂閹惰姤鏆涢悹鍥х▌缁辨繃淇?闁轰焦婢橀鐔稿緞瀹ュ嫮鐦庣紒娑欑墱閺?闁?閻庢冻缂氱弧鍕▕閻樺啿鍔?",
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
            "description": "濞ｅ洦绻傞悺銊︾▔閳ь剟寮堕敍鍕殢闁规挳顥撳▓鎴︽⒐閹稿孩鍩傞悹浣规緲缁诲倿濡撮崒姘锭濞ｅ洦绻傞悺銊╂偨閵婏箑鐓曢柡鍕捣閳ユ鎮伴妸銊﹀涧闁汇劌瀚禍鍛婄附婵劏鍋撴担椋庣槑闁诡垼鍨遍崹銊╂煂瀹ュ牜娲ｉ柛鎰－閻°儵鏁嶇仦鑲╃憹閻熸洑鐒︾敮褰掑棘椤撴壕鍋撻崒娆戠閻庢稒锚婢х姾绠涢崨娣偓蹇涘礂閸垺鏆?ask_user 缁绢収鍠涢濠氬Υ?,
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["preference", "habit", "decision", "knowledge"],
                        "description": "閻犱焦婢樼换鍌滅尵鐠囨彃鐒奸柨娑欘劒reference=闁稿绻愰妶? habit=濞戞梻濮甸崕? decision=闁告劕纾悺? knowledge=閻犱降鍊楅悡?,
                    },
                    "content": {
                        "type": "string",
                        "description": "閻犱焦婢樼换鍌炲礃閸涱収鍟囬柨娑樼焷閸ゆ粓鎮為幆閭﹀殧閻熷皝鍋撻柟璇茬箺閸?,
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
            "description": "闁告帞濞€濞呭孩绋夐埀顒勫级閿涘嫭鏆忛柟鎾棑濞堟垿姊归幐搴㈠焸閻犱焦婢樼换鍌炲Υ閸屾氨绉奸柣顫妽閸╂稓鎷?闊洦蓱鐢偓xxx'闁哄啳顔愮槐婵嬪礂閸垺鏆?recall_memory 闁瑰灚鍎抽崺宀€鈧數鎳撶花鑼媼閺夎法绠撻柣?ID闁挎稑鑻崯鈧悹瀣暟閺併倕顫㈤妶鍛矗闁稿繐鍢查崹褰掓⒔閵堝啠鍋?,
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "閻熸洑绀侀崹褰掓⒔閵堝洦鐣遍悹浣规緲缁?ID闁挎稑鐗呯划?recall_memory 缂備焦鎸婚悘澶嬬▔椤撯€崇闁告瑦鐗槐?,
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
            content="闁哥姵绮嶉浠嬪籍閳衡偓缁楀倹寰勫鍕槑闁轰焦婢橀?,
        )
        db.add(mem)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "闁轰焦婢橀?},
            db=db,
            user_id="tool-mem-1",
        )
        assert "memories" in result
        assert len(result["memories"]) >= 1
        assert "闁轰焦婢橀? in result["memories"][0]["content"]


@pytest.mark.asyncio
async def test_recall_memory_empty_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-2", username="toolmem2", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "濞戞挸绉撮悺銊╁捶閵娧勭暠闁告劕鎳庨?},
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
            {"category": "preference", "content": "闁哥姵绮嶉浠嬪疾濮橆偆鐟愬璺虹С缁″嫰寮崶鈺婃綘"},
            db=db,
            user_id="tool-mem-3",
        )
        assert result["status"] == "saved"

        mems = await db.execute(
            select(Memory).where(Memory.user_id == "tool-mem-3")
        )
        saved = mems.scalars().all()
        assert len(saved) == 1
        assert saved[0].content == "闁哥姵绮嶉浠嬪疾濮橆偆鐟愬璺虹С缁″嫰寮崶鈺婃綘"
        assert saved[0].category == "preference"
```

- [x] **Step 3: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_memory_tools.py -v`
Expected: FAIL 闁?`recall_memory` not found in TOOL_DEFINITIONS

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
        "message": f"鐎规瓕灏鍥ㄦ媴韫囥儳绐梴content}",
    }


async def _delete_memory_handler(
    db: AsyncSession, user_id: str, memory_id: str, **kwargs
) -> dict[str, Any]:
    """Delete a long-term memory by ID."""
    deleted = await delete_memory(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "鐎瑰憡褰冮崹褰掓⒔閵堝牜鍤夐悹浣规緲缁?}
    return {"error": "閻犱焦婢樼换鍌涚▔瀹ュ懐鎽犻柛锔哄妽閸ㄣ劑寮悩铏秬闁告帞濞€濞?}
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

- [ ] **Step 6: Commit**

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

- [ ] **Step 1: Write the failing test**

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
            "slots": [{"date": f"2026-04-{i:02d}", "weekday": "闁告稏鍔嬬粩?, "free_periods": [{"start": "08:00", "end": "22:00", "duration_minutes": 840}], "occupied": []} for i in range(1, 8)],
            "summary": "2026-04-01 闁?2026-04-07 闁?7 濞戞搩浜為埞鏍⒒閸欏鍞介柨娑樻湰閳ь剚妲掗?98 閻忓繐绻戝?0 闁告帒妫濋幐?,
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
                assert "7 濞戞搩浜為埞鏍⒒閸欏鍞? in content
                return {"role": "assistant", "content": "濞达絿濮剧换鏍川閵婏附绠掔€垫澘鐗嗛ˇ璺ㄧ矚濞差亝锛濋柡鍐ㄧ埣濡潡鏁?}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                gen = run_agent_loop("闁哄被鍎冲﹢鍛矚濞差亝锛濋柡鍐ㄧ埣濡?, user, "test-session", db, AsyncMock())
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

- [ ] **Step 2: Run test to verify it fails**

Run: `cd student-planner && python -m pytest tests/test_loop_compression.py -v`
Expected: FAIL 闁?assertion `"free_periods" not in content` fails (no compression yet)

- [ ] **Step 3: Modify loop.py to add compression**

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

- [ ] **Step 4: Run test to verify it passes**

Run: `cd student-planner && python -m pytest tests/test_loop_compression.py -v`
Expected: PASS

- [ ] **Step 5: Run existing loop tests to verify no regression**

Run: `cd student-planner && python -m pytest tests/ -v -k "loop or agent"`
Expected: All PASS

- [ ] **Step 6: Commit**

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

- [ ] **Step 1: Write the failing tests**

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
        pref = Memory(user_id="ctx-user-1", category="preference", content="闁哥姵绮嶉浠嬪籍閳衡偓缁楀倹寰勫鍕槑闁轰焦婢橀?)
        habit = Memory(user_id="ctx-user-1", category="habit", content="濞戞挴鍋撴繛鍡忓墲濞撹埖寰勫鑸佃偁濞?閻忓繐绻戝?)
        db.add_all([pref, habit])
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闁哥姵绮嶉浠嬪籍閳衡偓缁楀倹寰勫鍕槑闁轰焦婢橀? in context
        assert "濞戞挴鍋撴繛鍡忓墲濞撹埖寰勫鑸佃偁濞?閻忓繐绻戝? in context


@pytest.mark.asyncio
async def test_warm_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-2", username="ctxtest2", hashed_password="x")
        db.add(user)
        decision = Memory(user_id="ctx-user-2", category="decision", content="濡ゅ倹蓱閺嗙喖鎮介妸銉ョ€荤紒鏃傚Ь婵☆厾绮甸弽顐ｆ")
        db.add(decision)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "濡ゅ倹蓱閺嗙喖鎮介妸銉ョ€荤紒鏃傚Ь婵☆厾绮甸弽顐ｆ" in context


@pytest.mark.asyncio
async def test_no_memories_still_works(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-3", username="ctxtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        context = await build_dynamic_context(user, db)
        # Should still have time info, just no memory section
        assert "鐟滅増鎸告晶鐘诲籍閸洘锛? in context


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
            summary="濞戞挸锕ラ鑲┾偓鐢殿攰閻︿粙鏁嶅杈ㄦ殢闁规潙鍢查閬嶅礂閵夈倗鍟婇悹鍥ㄥ礃閵嗗啴鏁嶅畝鍐惧晭缂傚喚鍠曠花?闂傚倶鍔忛埀顒€鍟抽惁顖炴儍閸曨偒妲诲☉鏃傚Ь椤撴悂宕?,
        )
        db.add(summary)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "閻庣數鍘ч崣鍡樼閸℃凹鍤﹂悶? in context
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_context_loading.py -v`
Expected: FAIL 闁?memories not appearing in context output

- [ ] **Step 3: Modify context.py to load memories**

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

WEEKDAY_NAMES = ["闁告稏鍔嬬粩?, "闁告稏鍔嬬花?, "闁告稏鍔嬬粭?, "闁告稏鍔屽ú?, "闁告稏鍔嬬花?, "闁告稏鍔岄崣?, "闁告稏鍔嶅Λ?]


async def build_dynamic_context(user: User, db: AsyncSession) -> str:
    """Build the dynamic portion of the system prompt."""
    now = datetime.now(timezone.utc)
    today = now.date()
    weekday = today.isoweekday()

    parts: list[str] = []
    parts.append(f"鐟滅増鎸告晶鐘诲籍閸洘锛熼柨娑欘劯now.strftime('%Y-%m-%d %H:%M')}闁挎稑婢朩EEKDAY_NAMES[weekday - 1]}闁?)

    if user.current_semester_start:
        delta = (today - user.current_semester_start).days
        week_num = delta // 7 + 1
        parts.append(f"鐟滅増鎸告晶鐘碘偓娑抽檮濠€锟犳晬濮橀硸鍎憑week_num}闁?)

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

    parts.append("\n濞寸姴锕ら妵澶愭儍閸曨剚锛夌紒瀣儜缁?)
    if not courses and not tasks:
        parts.append("- 闁哄啰濮撮悾銊╁箳?)
    else:
        for course in courses:
            location = f" @ {course.location}" if course.location else ""
            parts.append(f"- {course.start_time}-{course.end_time} {course.name}{location}闁挎稑鐗愰宕囩矙鐎ｅ墎绀?)
        for task in tasks:
            status_mark = "闁? if task.status == "completed" else "闁?
            parts.append(f"- {task.start_time}-{task.end_time} {task.title}闁挎稑婢杝tatus_mark}闁?)

    # User preferences
    preferences = user.preferences or {}
    if preferences:
        parts.append("\n闁活潿鍔嶉崺娑㈠磻韫囨挶鍋ㄩ柨?)
        if "earliest_study" in preferences:
            parts.append(f"- 闁哄牃鍋撻柡鍐ｆ櫅椤掔喐绋婇悩铏槯闂傚倽鎻槐鐨梡references['earliest_study']}")
        if "latest_study" in preferences:
            parts.append(f"- 闁哄牃鍋撻柡鍛壘椤掔喐绋婇悩铏槯闂傚倽鎻槐鐨梡references['latest_study']}")
        if "lunch_break" in preferences:
            parts.append(f"- 闁告鐗呯槐銈夋晬濮濈斧references['lunch_break']}")
        if "min_slot_minutes" in preferences:
            parts.append(f"- 闁哄牃鍋撻柣顓у幗濠€渚€寮崼鐔割槯婵炲牏顣槐鐨梡references['min_slot_minutes']}闁告帒妫濋幐?)
        if "school_schedule" in preferences:
            parts.append("- 鐎瑰憡鐓￠崢銈囩磾椤旇崵绋婇柟顓у灡濡炲倿姊荤壕瀣ㄢ偓?)

    # Hot memories (preferences + habits) 闁?always loaded
    hot_memories = await get_hot_memories(db, user.id)
    if hot_memories:
        parts.append("\n闂傗偓閹稿孩鍩傞悹浣规緲缁诲倿鏁嶉崼婵呯剨濠靛倹鍨濈粭灞剧▕閻樺啿鍔甸柨娑橆檧缁?)
        for mem in hot_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Warm memories (recent decisions/knowledge) 闁?loaded at session start
    warm_memories = await get_warm_memories(db, user.id, days=7)
    if warm_memories:
        parts.append("\n閺夆晜鍨跺﹢锛勬媼閺夎法绠撻柨娑樼墛濞撹埖娼?濠㈠灈鏅槐姘舵晬?)
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
        parts.append(f"\n濞戞挸锕ラ鑲┾偓鐢殿攰閻︿粙骞楀Ο娆炬矗闁挎稒顒竘ast_summary.summary}")

    return "\n".join(parts)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_context_loading.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Run existing context tests to verify no regression**

Run: `cd student-planner && python -m pytest tests/ -v -k "context"`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
cd student-planner
git add app/agent/context.py tests/test_context_loading.py
git commit -m "feat: load hot/warm memories and session summary into system prompt"
```

---

### Task 6: Session Lifecycle 闁?Summary + Memory Extraction

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
            ConversationMessage(session_id="sess-1", role="user", content="閻㈩垼鍠楅崹婊堟儑鐎ｎ剚绠欓弶鈺傜懃閹冲棝鎯冮崟顓涙晞闂傚倸寮跺鍌炴⒒?),
            ConversationMessage(session_id="sess-1", role="assistant", content="濞达絿濮剧换鏍川閵婏附绠?2濞戞搩浜為埞鏍⒒閸欏顦ф繛?),
            ConversationMessage(session_id="sess-1", role="user", content="閻㈩垼鍠楅崹婊呪偓鐟邦槹鐢挻顨囧Ο缁樻濠㈣泛绉崇弧?),
            ConversationMessage(session_id="sess-1", role="assistant", content="鐎规瓕灏欓弫鎾诲箣?濞戞搩浜滈ˇ鍙夌▕閻樿鲸宕查柛?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_summary_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闁活潿鍔嶉崺娑㈠蓟閵壯勭畽濞存粌妫欏﹢浼村川閵娧€鏁勯梻鍌氬级濡炲倿姊绘潏鍓х閻庣懓顦扮敮鎾寸閸℃稓褰柡浣规緲椤﹀弶绋婇悩渚悁闁告帗甯槐?濞戞搩浜欓幑銏ゅ礉閳藉懐绀?,
                "actions": ["闁哄被鍎撮妤冪矚濞差亝锛濋柡鍐ㄧ埣濡?, "闁汇垻鍠愰崹姘殗濡粯娈跺璺虹С缁″嫮鎷嬮垾鍐茬亰"],
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
        assert "濡ゅ倹蓱閺嗙喐寰勫鍕槑" in summary.summary


@pytest.mark.asyncio
async def test_end_session_extracts_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-2", username="sesstest2", hashed_password="x")
        db.add(user)

        msgs = [
            ConversationMessage(session_id="sess-2", role="user", content="闁瑰瓨鍨甸弸鈺佲枎閵忊剝锛嶅☉鎾筹工椤﹀弶绋婇悩鍨€炵紒澶嬪煀缁辨繈寮插顐ょ憪闁活亜顑嗛弸鍐矓?),
            ConversationMessage(session_id="sess-2", role="assistant", content="濠靛倻鏅▓鎴︽晬鐏炴儳鐏夐悹渚€顣︾紞鍥ㄧ?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闁活潿鍔嶉崺娑氭偘閵娿劍褰уù婊冩椤掔喐绋婇悩铏槯闂傚倹娼欐禍鍛婄附?,
                "actions": [],
                "memories": [
                    {"category": "preference", "content": "闁哥姵绮嶉浠嬪籍閳衡偓缁楀倹寰勫鍕槑闁荤偛妫涢～鏍晬鐏炵偓鐝撳☉鎾筹功濠€鍛村棘閸モ晩娼?},
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
        assert "闁荤偛妫涢～? in memories[0].content
        assert memories[0].source_session_id == "sess-2"


@pytest.mark.asyncio
async def test_end_session_empty_conversation(setup_db):
    """No messages 闁?no summary, no crash."""
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
Expected: FAIL 闁?`ModuleNotFoundError: No module named 'app.agent.session_lifecycle'`

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

_EXTRACT_PROMPT = """闁告帒妫欓悗鑺ョ閵夈倗鐟撻悗鐢殿攰閻︿粙鏁嶅畝鍐炕闁?JSON闁挎稑鐗呯粭澶屾啺娴ｇ晫缈婚柛鎴濇惈閸欑偓绂掗弽褍鏁堕悗鍦缁辨岸鏁?
{
  "summary": "濞戞挴鍋撻柛娆嶅劥閻︿粙骞€閼姐倗娉㈤弶鈺傜懄椤愯偐鈧數顢婇惁浠嬪磻濮橆偆鍟婂ù鐘亾濞?,
  "actions": ["闁圭瑳鍡╂斀闁汇劌瀚幖閿嬫媴濠婂啫鐏欓悶?],
  "memories": [
    {"category": "preference|habit|decision|knowledge", "content": "闁稿﹦鍘х欢閬嶆⒐閹稿孩鍩傞悹渚€顣︾紞鍥儍閸曨亙绻嗛柟?}
  ]
}

閻熸瑥瀚崹顖炴晬?- summary 閻熸洑鑳堕悾婵喢烘笟濠勭濞戞挴鍋撳☉鎾卞€曡ぐ鐐垫嫚?- memories 闁告瑯浜濊ぐ渚€宕ｉ弽顐ｆ殢闁规挳鏀卞Σ鎴犳兜椤旇￥鈧啯娼忛崜褎鐣遍柛瀣箰閵堜粙濡存担椋庣槑闁诡垼鍨遍崹銊╂煂瀹ュ牜娲ｉ柛鎰－閻?- 濞戞挸绉烽々锕傚箳閵婏附鐒介柨娑樼墢閺併倝骞嬮悿顖ｅ殯"闁瑰瓨鍨堕弳鐔衡偓娑崇細缁楀绺?闁愁偅甯熼鍥亹閺囶亞骞㈤柣顫妽閸╂盯鎳撻崘褏鍟?0闁告帒妫岄崯瀣▔瀹ュ棗鑵归柡鍌ゅ弿缁?- 濞戞挸鐡ㄥ鍌炲箑瑜屾穱濠囧箒椤栨瑧鐟濋悹浣稿簻缁?濞寸姴锕ら妵澶嬬▔瀹ュ棗鍘掗悗娑崇細缁?闁?- 濠碘€冲€归悘澶娾柦閳╁啯绠掗柛濠勫帶缁惰京鎷嬫０浣虹Ф闁汇劌瀚穱濠囧箒椤栥倗绀塵emories 濞戞捁娅ｉ埞鏍极閹殿喚鐭?""


async def end_session(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    llm_client: AsyncOpenAI,
) -> None:
    """Process session end: generate summary and extract memories.

    This is called when the WebSocket disconnects or times out.
    Failures are logged but never raised 闁?session end must not crash.
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
    session_timeout_minutes: int = 120  # 2 hours inactivity 闁?new session
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
                            user_answer = user_response.get("answer", "缁绢収鍠涢?)
                            event = await generator.asend(user_answer)
                        elif event["type"] == "done":
                            break
                        else:
                            event = await generator.__anext__()
                except StopAsyncIteration:
                    pass
    except WebSocketDisconnect:
        # Session ended 闁?generate summary and extract memories
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

### Task 8: Update Agent.md 闁?Memory Tool Rules

Add behavior rules for the memory tools to Agent.md.

**Files:**
- Modify: `student-planner/Agent.md`

- [ ] **Step 1: Add memory tool usage rules**

Add the following under the `### 鐎规悶鍎遍崣鎸庢媴鐠恒劍鏆廯 section in `Agent.md`:

```markdown
- recall_memory闁挎稒鑹剧紞瀣閳ь剛鎲版担鍛婄闊洤妫涢弫銈夊箣閾氬倻顓洪柛鎾崇Ф濞堟垿宕戣箛鎾卞仺闁靛棔妞掔弧鍕箚椤栨稑鐏楅柛鎰－閻°儵寮張闈涒枏闁活潿鍔婇埀顒€鍊风粭澶屾啺娴ｅ湱妲ㄦ繛鍡忊偓鎰佸殸閻犲洦绻堥崗妯兼嫬閸愵亝鏆忛柨娑樿嫰瑜把囧捶閵娧€鈧鈧湱鍋ゅ〒鍓佹啺娴ｇ鍧婇柛娆掑紦娣囧﹪骞侀娑欘槯濞达綀娉曢弫?- save_memory闁挎稒鑹捐ぐ褎绌卞┑鍡欐憼闁活潿鍔嶉崺娑㈠及鎼达絺鈧鎮伴妸銊﹀涧闁汇劌瀚穱濠囧箒椤栥倗绀夊☉鎾崇Х椤╋箓骞掗妸锔界劷闁靛棗鍊风换姘扁偓娑櫭晶鐘虹疀閸涙番鈧繘宕楅崼銏℃殢 ask_user 缁绢収鍠涢濠氭晬?闁瑰瓨鍨奸鍥ㄦ媴韫囧海鍟婇柨娑欑摕闁告劕鎳庨鎬鹃柕鍡楀€搁顕€宕ュΔ瀣惞"
  - preference闁挎稒姘ㄩ弫銈夊箣瀹勯鐒婂┑鍌涙灮缁?闁瑰瓨鍨甸弸鈺佲枎閵忊剝锛嶅☉鎾筹工椤﹀弶绋婇悩铏閻?闁?  - habit闁挎稒鑹鹃鐔哥▕閻樿京鐦庨柟顖ｅ灲缁?闁瑰瓨鍨崇粩鏉戔枎閳╁啯浠樺鑸靛哺濞夛附绋?閻忓繐绻戝?闁?  - decision闁挎稒宀搁崳鍝ユ啺娴ｇ鏋€缂佹稒鐗槐?濡ゅ倹蓱閺嗙喖鎮介妸銉ョ€荤紒鏃傚Ь婵☆厾绮甸弽顐ｆ"闁?  - knowledge闁挎稒淇洪宕囩矙鐎ｎ収鍚囬柣顓滃劵缁?闁活潿鍔嶉崺娑氭喆婢跺﹦绻佹慨鎺戝€诲鑲╂媼閻戞ɑ浠橀梻?闁?- 濞戞挸绉烽々锔界┍濠靛棛鎽犲☉鎾崇摠濡炲倿骞€瑜屾穱濠囧箒椤栥倗绀?濞寸姴锕ら妵澶嬬▔瀹ュ棗鍘掗悗娑崇細缁?闁?- 濞戞挸绉烽々锔界┍濠靛棛鎽犵€规瓕灏欑划锟犲捶閵婏附娈堕柟璇″枛缁ㄨ鲸绋夐鐘崇暠濞ｅ洠鍓濇导鍛存晬閸綆鍤︾紒瀣儍閳ь兛妞掗幑銏ゅ礉鎺抽埀顑挎祰閳ь剙鍟抽惁顖炴晬?- 鐟滅増鎸鹃弫銈夊箣閻ゎ垼鍤?闊洦蓱鐢偓xxx"闁哄啳顔愮槐婵嬫偨?recall_memory 闁瑰灚鍎抽崺宀€鈧數鎳撶花鑼媼閺夎法绠撻柨娑樼灱閸斞囧触鎼粹剝鍟為柣顓滃劤閺併倝骞嬪畡鏉垮殥闁告帞濞€濞?```

- [ ] **Step 2: Add few-shot example for memory**

Add the following as a new example after existing examples in `Agent.md`:

```markdown
### 缂佲偓鏉炴壆浼?闁挎稒淇洪鍥疀閸℃瑯鍚€闁?
闁活潿鍔嶉崺? "闁瑰瓨鍨佃ぐ鍌炴偝閻楀牊鐝撳☉鎾筹工椤﹀弶绋婇悩铏珡闁绘粌娲﹀ú鎸庮殗濮楀牏绀夊ù鐘劚閹鏁钘夌亯闁硅泛锕らˇ鍙夌▕閻樿鍘撮悗鐟邦槹鐢捇宕烽妸锔界彄濞戞挸锕ら幆?

闁?save_memory(category="preference", content="闁哄懏鐭粭鍌涘緞瀹ュ嫮鐦庨柡浣哥墢瀹稿ジ寮撮幘顔惧蒋闁挎稑鑻禍鍛婄附閼恒儲鐝撻梻鍌涙綑閻ｃ劑骞掗幒鎴Щ濞?)
闁?濞达絽妫楅崢娑氭兜椤旀鍚囬柨娑欑摣sk_user(type="confirm", question="闁瑰瓨鍨奸鍥ㄦ媴韫囧海鍟婇柨娑欑煯缂嶆﹢寮插顐ょ憪濠㈣泛绉崇弧鍕极閸垹鑺抽柡鍥ㄦ尦閻濐噣鏁嶇仦闂寸鞍闁告艾绨肩槐顓㈠礂閸繄鏆旈柟鐑樺笚濞呭嫰姊婚弶鎴Щ濞戞梻濮伴埀顒€鍊搁顕€宕ュΔ瀣惞")
闁?闁活潿鍔嶉崺娑氭兜椤旀鍚?闁?save_memory
闁?闁搞儳鍋涢ˇ? "濠靛倻鏅▓鎴︽晬鐏炶棄鍤掗悹渚€顣︾紞鍥Υ閸屾瑤绨伴柛姘捣閺佹捇骞嬮幇顒夋Щ濞戞梻濮鹃鎼佸礆閹烘挻顦уù鍏肩煯缁鳖參宕楅崼婵堟殧闁圭儤甯楀▍鍕⒒鐎涙ɑ顦ф繛鍫㈠仯閳?

闁活潿鍔嶉崺? "闊洦蓱鐢偓濞戞柨顑呮晶鐘垫嫚鐎靛憡鐣遍柡鍐ｆ櫃缁楀倹寰勫鍕槑闁轰焦婢橀?

闁?recall_memory(query="闁哄啠鏅欑粭鍌涘緞瀹ュ嫮鐦庨柡浣规緲椤?)
闁?闁瑰灚鍎抽崺宀€鎷嬮弶璺ㄧ畵 闁?闁告帞濞€濞?闁?闁搞儳鍋涢ˇ? "鐎瑰憡褰冮崹褰掓⒔閵堝牏绠归柡澹溿値鍞堕煫鍥ф閳?
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
        {"role": "user", "content": "濞达絿濮撮妶?},
        {"role": "assistant", "content": "濞达絿濮撮妶浠嬫晬娴ｈ绠掑ù鐘亾濞戞柨鐗嗚ぐ鍙夌閵夈儱绨诲ù锝囧Х濞堟垿鏁?},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    """Long conversations should have older messages compressed."""
    messages = [{"role": "system", "content": "System prompt"}]
    # Add 20 user/assistant pairs
    for i in range(20):
        messages.append({"role": "user", "content": f"闁活潿鍔嶉崺娑樷槈閸喍绱?{i}"})
        messages.append({"role": "assistant", "content": f"闁告柡鏅滄晶婊堝炊閻愬樊妲?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "濞戞柨顑呮晶鐘绘儍閸曨偒鍤犻悹鍥ㄧ箑閼垫垿鏁嶅畝鈧弫銈夊箣瀹勬澘绲洪梺顐℃缁?0闁哄鍓濈粔鐑藉箒椤栥倗绀夐柛鏂烘櫆婢ф粓鏌堥挊澶夌驳濞存粌妫楀ú鏍ㄥ緞瀹ュ啠鍋?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # System prompt should be preserved
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"

    # Should have a summary message
    assert any("濞戞柨顑呮晶鐘绘儍閸曨偒鍤犻悹? in m.get("content", "") for m in result)

    # Recent messages should be preserved (last 12 non-system messages = 6 pairs)
    assert len(result) <= 14  # system + summary + 12 recent


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    """The most recent messages should be kept intact."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(20):
        messages.append({"role": "user", "content": f"婵炴垵鐗婃导?{i}"})
        messages.append({"role": "assistant", "content": f"闁搞儳鍋涢ˇ?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "闁哄啠鏅滃﹢锛勨偓鐢殿攰閻︿粙骞楀Ο娆炬矗",
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # Last message should be the most recent assistant reply
    assert result[-1]["content"] == "闁搞儳鍋涢ˇ?19"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: FAIL 闁?`ImportError: cannot import name 'compress_conversation_history'`

- [ ] **Step 3: Add compress_conversation_history to context_compressor.py**

Append to `app/services/context_compressor.py`:

```python
from app.agent.llm_client import chat_completion as _chat_completion

_SUMMARIZE_PROMPT = """閻犲洭顥撻弫?-3闁告瑣鍎撮惁浠嬪箑閼姐倗娉㈠ù鐘劙缁楀懐鈧數顢婇惁浠嬪礃閸涱収鍟囬柕鍡楀€块崳鎼佹倷闁稓绠介柣锝嗙懕缁变即鎮介妸锕€鐓曢柛瀣煯缁ㄢ剝绂掗埀顒佺▕閸喐鎯欏ù锝嗗殠閳ь兛鑳堕垾妯兼媼閵堝嫮鍟婂ù鐘亾濞戞柨鐗勯埀顑挎祰閵嗗啯娼忛崣銉у晩濞寸姭鍋撳☉鏂跨墕娴滃憡绺芥慨鎰ㄥ亾?""


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
        summary = response.get("content", "闁挎稑鐗婂Λ顓㈠嫉閻斿鍤犻悹鍥ㄧ箖閹插磭鎲版担椋庣憹闁告瑯鍨抽弫銈夋晬?)
    except Exception:
        summary = "闁挎稑鐗婂Λ顓㈠嫉閻斿鍤犻悹鍥ㄧ箖閹插磭鎲版担鐑樻櫢闁瑰瓨鍔曢妵鎴犳嫻閵夘垳绀?

    summary_msg = {
        "role": "user",
        "content": f"[濞戞柨顑呮晶鐘绘儍閸曨偒鍤犻悹鍥ㄧ箖閹插磭鎲版稊?{summary}",
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

### Task 10: Update AGENTS.md 闁?Mark Plan 4 Progress

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Update progress in AGENTS.md**

Update the Plan 4 line and current status:

```markdown
- [ ] Plan 4: Memory + 濞戞挸锕ｇ粭鍛村棘閸モ晩鍚€闁荤偛妫寸槐?0 濞?task闁?```

Update "鐟滅増鎸告晶鐘差潰閿濆懏韬柟绗涘棭鏀? to reflect Plan 4 completion.

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with Plan 4 completion status"
```
