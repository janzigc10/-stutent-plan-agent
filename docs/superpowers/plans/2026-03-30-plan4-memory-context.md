# Plan 4: Memory 缂備緡鍨靛畷鐢靛垝?+ 婵炴垶鎸搁敃锝囩箔閸涙潙妫橀柛銉㈡櫓閸氣偓闂?
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer memory system (working/short-term/long-term) and context window management to keep conversations coherent across sessions without blowing up the context window.

**Architecture:** Memory CRUD service handles persistence. Two new agent tools (`recall_memory`, `save_memory`) give the LLM on-demand access. Tool result compression summarizes verbose outputs inline. Session lifecycle hooks generate summaries and extract memories at session end. The system prompt builder loads hot/warm memories at session start.

**Tech Stack:** SQLAlchemy async (existing), OpenAI-compatible LLM for summarization, existing agent tool system

**Depends on:** Plan 1 (Memory, SessionSummary, ConversationMessage models), Plan 2 (agent loop, tool_executor, llm_client)

---

## File Structure

```
student-planner/
闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?app/
闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?services/
闂?  闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?memory_service.py          # Memory CRUD: create, query, update, delete, staleness
闂?  闂?  闂佸疇顫夐弻锟犲绩閵忋倕鐓橀柍?context_compressor.py      # Tool result summarization + conversation compression
闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?agent/
闂?  闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?tools.py                   # (modify: add recall_memory, save_memory definitions)
闂?  闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?tool_executor.py           # (modify: add recall_memory, save_memory handlers)
闂?  闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?loop.py                    # (modify: add tool result compression after each tool call)
闂?  闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?context.py                 # (modify: add hot/warm memory loading)
闂?  闂?  闂佸疇顫夐弻锟犲绩閵忋倕鐓橀柍?session_lifecycle.py       # Session end: generate summary + extract memories
闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?routers/
闂?  闂?  闂佸疇顫夐弻锟犲绩閵忋倕鐓橀柍?chat.py                    # (modify: call session lifecycle on disconnect/timeout)
闂?  闂佸疇顫夐弻锟犲绩閵忋倕鐓橀柍?config.py                      # (modify: add context window thresholds)
闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?tests/
闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?test_memory_service.py         # Memory CRUD unit tests
闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?test_context_compressor.py     # Compression logic tests
闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?test_memory_tools.py           # recall_memory / save_memory tool tests
闂?  闂佸疇顫夋竟鏇㈠绩閵忋倕鐓橀柍?test_session_lifecycle.py      # Session end flow tests
闂?  闂佸疇顫夐弻锟犲绩閵忋倕鐓橀柍?test_context_loading.py        # Hot/warm memory in system prompt tests
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
            content="闂佸摜濮电划宥夘敃娴犲绫嶉柍琛″亾缂佹鍊瑰鍕吋閸曨厾妲戦梺杞扮劍濠㈡﹢顢?,
            source_session_id="session-abc",
        )
        assert mem.id is not None
        assert mem.category == "preference"
        assert mem.content == "闂佸摜濮电划宥夘敃娴犲绫嶉柍琛″亾缂佹鍊瑰鍕吋閸曨厾妲戦梺杞扮劍濠㈡﹢顢?
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

        await create_memory(db, "mem-user-2", "preference", "闂佸搫鍟犻弲娆戠箔閸屾稑绶炵€广儱瀚惁搴ㄦ煛娴ｈ绶叉い?)
        await create_memory(db, "mem-user-2", "habit", "婵炴垶鎸撮崑鎾寸箾閸″繐澧叉繛鎾瑰煐瀵?闁诲繐绻愮换鎴濐渻?)
        await create_memory(db, "mem-user-2", "decision", "婵°倕鍊硅摫闁哄棛鍠栭幃浠嬪Ω閵夈儳鈧崵绱掗弮鍌毿┑鈽嗗幘缁敻寮介锝嗩吅")

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
        await create_memory(db, "mem-user-3", "decision", "婵°倕鍊硅摫闁哄棛鍠栭幃浠嬪Ω閵夈儳鈧崵绱掗弮鍌毿┑鈽嗗幘缁敻寮介锝嗩吅")

        # Old memory (simulate 30 days ago)
        old_mem = Memory(
            user_id="mem-user-3",
            category="decision",
            content="缂備焦鍎抽妵姗€宕鍕仺闁靛鍎遍悡鏇炍涢悧鍫劷闁宦板劦閹?,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_mem)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)
        assert len(warm) == 1
        assert warm[0].content == "婵°倕鍊硅摫闁哄棛鍠栭幃浠嬪Ω閵夈儳鈧崵绱掗弮鍌毿┑鈽嗗幘缁敻寮介锝嗩吅"


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "婵°倕鍊硅摫闁哄棛鍠栭幃浠嬪Ω閵夈儳鈧崵绱掗弮鍌毿┑鈽嗗幘缁敻寮介锝嗩吅闂佹寧绋戦張顒勫疾閵夆晛鍑犳繝濞惧亾缂佹顦甸弻?)
        await create_memory(db, "mem-user-4", "preference", "闂佸摜濮电划宥夘敃娴犲绫嶉柍琛″亾缂佹鍊瑰鍕吋閸曨厾妲?)
        await create_memory(db, "mem-user-4", "knowledge", "濠殿喗甯掗崐璇差啅閼测晜濯奸柣鎴炆戞禒姗€姊?)

        results = await recall_memories(db, "mem-user-4", query="婵°倕鍊硅摫闁?)
        assert len(results) >= 1
        assert any("婵°倕鍊硅摫闁? in m.content for m in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-5", "decision", "婵°倕鍊硅摫闁哄棛鍠栭幃浠嬪Ω閵夈儳鈧崵绱掗弮鍌毿┑鈽嗗幘缁敻寮介锝嗩吅")
        original_accessed = mem.last_accessed

        # Small delay to ensure timestamp differs
        results = await recall_memories(db, "mem-user-5", query="婵°倕鍊硅摫闁?)
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

        mem = await create_memory(db, "mem-user-6", "preference", "闂佸搫鍟犻弲娆戠箔閸屾稑绶炵€广儱瀚惁?)
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

        mem = await create_memory(db, "mem-user-7", "preference", "闂佸搫鍟犻弲娆戠箔閸屾稑绶炵€广儱瀚惁?)
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
            content="闂佸搫鍞查崨顔炬殸闂佸憡鍔曠壕顓㈡偤?,
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
                "weekday": "闂佸憡绋忛崝瀣箔?,
                "free_periods": [
                    {"start": "08:00", "end": "10:00", "duration_minutes": 120},
                    {"start": "14:00", "end": "16:00", "duration_minutes": 120},
                ],
                "occupied": [
                    {"start": "10:00", "end": "12:00", "type": "course", "name": "婵°倕鍊硅摫闁?},
                ],
            },
            {
                "date": "2026-04-02",
                "weekday": "闂佸憡绋忛崝灞矫?,
                "free_periods": [
                    {"start": "09:00", "end": "11:00", "duration_minutes": 120},
                ],
                "occupied": [],
            },
        ],
        "summary": "2026-04-01 闂?2026-04-02 闂?3 婵炴垶鎼╂禍鐐哄煘閺嶎厽鈷掗柛娆忣樈閸炰粙鏌ㄥ☉妯绘拱闁逞屽墯濡叉帡顢?6 闁诲繐绻愮换鎴濐渻?0 闂佸憡甯掑Λ婵嬪箰?,
    }
    compressed = compress_tool_result("get_free_slots", result)
    # Should use the existing summary field
    assert "3 婵炴垶鎼╂禍鐐哄煘閺嶎厽鈷掗柛娆忣樈閸? in compressed
    assert "6 闁诲繐绻愮换鎴濐渻? in compressed
    # Should NOT contain the full slot details
    assert "free_periods" not in compressed


def test_compress_list_courses():
    result = {
        "courses": [
            {"id": "1", "name": "婵°倕鍊硅摫闁?, "teacher": "閻?, "weekday": 1, "start_time": "08:00", "end_time": "09:40"},
            {"id": "2", "name": "缂備焦鍎抽妵姗€宕?, "teacher": "闂?, "weekday": 3, "start_time": "10:00", "end_time": "11:40"},
            {"id": "3", "name": "闂佸吋妲掔划楣冾敋?, "teacher": "闂?, "weekday": 2, "start_time": "08:00", "end_time": "09:40"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_courses", result)
    assert "3" in compressed
    assert "婵°倕鍊硅摫闁? in compressed


def test_compress_list_tasks():
    result = {
        "tasks": [
            {"id": "1", "title": "婵犮垼娉涚粔宕囧姬閸曨剦娈楁俊顖滅帛濞堝墎绱掑Δ濠傚幐缂佹柨顕划?, "status": "completed"},
            {"id": "2", "title": "婵犮垼娉涚粔宕囧姬閸曨剦娈楁俊顖滅帛濞堝墎绱掑Δ濠傚幐缂併劉鏅濈划?, "status": "pending"},
            {"id": "3", "title": "婵犮垼娉涚粔宕囧姬閸曨厾妫鍓侇焾閺?, "status": "pending"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_tasks", result)
    assert "3" in compressed
    assert "1" in compressed  # completed count


def test_compress_create_study_plan():
    result = {
        "tasks": [
            {"title": "婵犮垼娉涚粔宕囧姬閸曨剦娈楁俊顖滅帛濞堝墎绱掑Δ濠傚幐缂佹柨顕划?, "date": "2026-04-01"},
            {"title": "婵犮垼娉涚粔宕囧姬閸曨剦娈楁俊顖滅帛濞堝墎绱掑Δ濠傚幐缂併劉鏅濈划?, "date": "2026-04-02"},
            {"title": "婵犮垼娉涚粔宕囧姬閸曨厾妫鍓侇焾閺?, "date": "2026-04-03"},
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
        return f"[缂備礁鏈钘壩涙禒瀣睄闁煎憡顔栭崬浠嬫煛鐏炶鍔ユい鏇燁殘缁辨帡骞樼€甸晲鍑絔 {summary}"
    slots = result.get("slots", [])
    total = sum(len(d.get("free_periods", [])) for d in slots)
    return f"[缂備礁鏈钘壩涙禒瀣睄闁煎憡顔栭崬浠嬫煛鐏炶鍔ユい鏇燁殘缁辨帡骞樼€甸晲鍑絔 {len(slots)} 婵犮垹鐏堥弲顏嗘濠靛绀?{total} 婵炴垶鎼╂禍鐐哄煘閺嶎厽鈷掗柛娆忣樈閸?


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = [c["name"] for c in courses[:5]]
    names_str = "闂?.join(names)
    if count > 5:
        names_str += f" 缂?{count} 闂?
    return f"[闁荤姴娲ゆ晶浠嬪煝婵傜绀嗘俊銈呭閳ь剙鍎?闂?{count} 闂傚倸鍊堕崝蹇涱敋閹惰姤鏅慨婵堜刊ames_str}"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    pending = count - completed
    return f"[婵炲濮鹃褎鎱ㄩ悢鐓庣婵°倕瀚ㄩ埀顒€鍎?闂?{count} 婵炴垶鎼╂禍娆撳箲閵忋倕绀夐柍钘夋噽缁€澧坈ompleted} 婵炴垶鎼╂禍婊堝礄閿涘嫧鍋撻悷鐗堟拱闁搞劍宀搁弫宥団偓闈涚崼ending} 婵炴垶鎼╂禍婊呮閻旇　鍋撻悷鐗堟拱闁?


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    return f"[婵犮垼娉涚粔宕囧姬閸曨厽濯奸柍銉ュ暱閻忓キ 閻庤鐡曠亸娆撳极閹捐绠?{count} 婵炴垶鎼╂禍婊埶囬崣澶屸枙闁绘椴稿畷鏌ユ煕?


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
            "description": "婵炲濮村ù鐑藉极閵堝绠ｅ瀣閻ｉ亶姊婚埀顒勫箰鎼淬垹鐒搁柣鐘辩劍濠㈡鎹㈤崒娑氣枖妞ゆ挾鍣ュ鍓х磼娓氬灝鐏繛鏉戭樀瀹曟宕楅崨顒傜畾闂佽鍙庨崹顒勫焵椤掆偓閸婂摜绱炵€ｎ喗顥嗛柍褜鍓涢幉鐗堟媴閸涘﹦顦ラ棅顐㈡搐濡盯寮妶澶婄闁炬艾鍊婚娲煕閹惧磭肖婵炲牊鍨垮畷鎴ｇ疀閹惧崬浠洪梺闈涙濡炴帞寮ч崟顖氱畾妞ゆ牗绋戦悘妤呮煕閹邦剛锛嶉柣掳鍎靛顕€寮甸棃娑掓瀼闂佹椿娼块崝濠囧焵椤掆偓閸婄晫鎹㈤幋锕€鐐婇柣鎰絻閻栭亶姊洪弶璺ㄐゆ繛鍫熷灩閹峰寮剁捄銊х暤闂佸憡甯楅〃澶愬Υ閸愵喖违?,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "闂佺懓鍚嬬划搴ㄥ磼閵娾晛绀傞柟鎯板Г閺嗘盯鎮归崶褏鈻岀紒杈ㄧ箖娣?闂佽桨鐒﹀姗€顢楅悢绋跨窞鐎广儱瀚惁搴ｇ磼濞戞瑧澧遍柡?闂?闁诲孩鍐荤紓姘卞姬閸曨剛鈻曢柣妯哄暱閸?",
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
            "description": "婵烇絽娲︾换鍌炴偤閵婏妇鈻旈柍褜鍓熷鍫曟晬閸曨剚娈㈤梺瑙勬尦椤ユ挸鈻撻幋锔解拹闁圭瀛╅崺鍌炴偣娴ｈ绶茬紒璇插€挎俊鎾磼濮橆剚閿繛锝呮处缁诲倿鎮洪妸鈺傚仺闁靛绠戦悡鏇㈡煛閸曨偅鎹ｉ柍銉︻焽閹即濡搁妸锕€娑ч梺姹囧妼鐎氼剚绂嶉崨濠勯檮濠殿喗鍔忛崑鎾存媴妞嬪海妲戦梺璇″灱閸ㄩ亶宕归妸鈺傜厒鐎广儱鐗滃ú锝夋煕閹邦剛锛嶉柣掳鍎甸弫宥囦沪閼测晝鎲归柣鐔告磻閻掞妇鏁ぐ鎺戞妞ゆ挻澹曢崑鎾诲磼濞嗘垹顔旈柣搴㈢⊕閿氬褏濮剧粻娑㈠川濞ｎ兘鍋撹箛娑樼闁割偁鍨洪弳?ask_user 缂佺虎鍙庨崰娑㈩敇婵犳艾违?,
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["preference", "habit", "decision", "knowledge"],
                        "description": "闁荤姳鐒﹀妯兼崲閸屾粎灏甸悹鍥ㄥ絻閻掑ジ鏌ㄥ☉娆樺姃reference=闂佺顑呯换鎰板Χ? habit=婵炴垶姊绘慨鐢稿磿? decision=闂佸憡鍔曠壕顓㈡偤? knowledge=闁荤姳闄嶉崐妤呮偂?,
                    },
                    "content": {
                        "type": "string",
                        "description": "闁荤姳鐒﹀妯兼崲閸岀偛绀冮柛娑卞弾閸熷洭鏌ㄥ☉妯肩劮闁搞倖绮撻幃鐐哄箚闁箑娈ч柣鐔风殱閸嬫捇鏌熺拠鑼闁?,
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
            "description": "闂佸憡甯炴繛鈧繛鍛缁嬪鍩€椤掑嫬绾ч柨娑樺閺嗗繘鏌熼幘顕呮婵炲牊鍨垮褰掑箰鎼淬垹鐒搁柣鐘辩劍濠㈡鎹㈤崒鐐参ラ柛灞炬皑缁夊ジ鏌ｉ～顒€濡介柛鈺傜〒閹?闂婎偄娲﹁摫閻㈩垪鍋搙xx'闂佸搫鍟抽鎰濠靛绀傞柛顐犲灪閺?recall_memory 闂佺懓鐏氶崕鎶藉春瀹€鈧埀顒傛暩閹虫挾鑺遍懠顒佸闁哄娉曠粻鎾绘煟?ID闂佹寧绋戦懟顖炲疮閳ь剟鎮圭€ｎ亜鏆熼柡浣靛€曢～銏ゅΧ閸涱剛鐭楅梺绋跨箰閸㈡煡宕硅ぐ鎺撯挃闁靛牆鍟犻崑?,
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "闁荤喐娲戠粈渚€宕硅ぐ鎺撯挃闁靛牆娲﹂悾閬嶆偣娴ｈ绶茬紒?ID闂佹寧绋戦悧鍛垝?recall_memory 缂傚倷鐒﹂幐濠氭倶婢跺鈻旀い鎾偓宕囶唵闂佸憡鐟﹂悧顓犳?,
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
            content="闂佸摜濮电划宥夘敃娴犲绫嶉柍琛″亾缂佹鍊瑰鍕吋閸曨厾妲戦梺杞扮劍濠㈡﹢顢?,
        )
        db.add(mem)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "闂佽桨鐒﹀姗€顢?},
            db=db,
            user_id="tool-mem-1",
        )
        assert "memories" in result
        assert len(result["memories"]) >= 1
        assert "闂佽桨鐒﹀姗€顢? in result["memories"][0]["content"]


@pytest.mark.asyncio
async def test_recall_memory_empty_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-2", username="toolmem2", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "婵炴垶鎸哥粔鎾偤閵娾晛鎹堕柕濞у嫮鏆犻梺鍛婂姇閹冲酣顢?},
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
            {"category": "preference", "content": "闂佸摜濮电划宥夘敃娴犲鐤炬慨姗嗗亞閻熸劕顭跨捄铏剐＄紒鈥冲瀵剟宕堕埡濠冪稑"},
            db=db,
            user_id="tool-mem-3",
        )
        assert result["status"] == "saved"

        mems = await db.execute(
            select(Memory).where(Memory.user_id == "tool-mem-3")
        )
        saved = mems.scalars().all()
        assert len(saved) == 1
        assert saved[0].content == "闂佸摜濮电划宥夘敃娴犲鐤炬慨姗嗗亞閻熸劕顭跨捄铏剐＄紒鈥冲瀵剟宕堕埡濠冪稑"
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
        "message": f"閻庤鐡曠亸顏堫敊閸ャ劍濯撮煫鍥ュ劤缁愭⒋content}",
    }


async def _delete_memory_handler(
    db: AsyncSession, user_id: str, memory_id: str, **kwargs
) -> dict[str, Any]:
    """Delete a long-term memory by ID."""
    deleted = await delete_memory(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "閻庣懓鎲¤ぐ鍐垂瑜版帗鈷旈柕鍫濈墱閸ゅ鎮规担瑙勭凡缂?}
    return {"error": "闁荤姳鐒﹀妯兼崲閸屾稓鈻旂€广儱鎳愰幗鐘绘煕閿斿搫濡介柛銊ｅ姂瀵噣鎮╅搹顐ょК闂佸憡甯炴繛鈧繛?}
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
            "slots": [{"date": f"2026-04-{i:02d}", "weekday": "闂佸憡绋忛崝瀣博?, "free_periods": [{"start": "08:00", "end": "22:00", "duration_minutes": 840}], "occupied": []} for i in range(1, 8)],
            "summary": "2026-04-01 闂?2026-04-07 闂?7 婵炴垶鎼╂禍鐐哄煘閺嶎厽鈷掗柛娆忣樈閸炰粙鏌ㄥ☉妯绘拱闁逞屽墯濡叉帡顢?98 闁诲繐绻愮换鎴濐渻?0 闂佸憡甯掑Λ婵嬪箰?,
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
                assert "7 婵炴垶鎼╂禍鐐哄煘閺嶎厽鈷掗柛娆忣樈閸? in content
                return {"role": "assistant", "content": "婵炶揪绲挎慨鍓ф崲閺嶎厼宸濋柕濠忛檮缁犳帞鈧灚婢橀悧鍡浰囩捄銊х煔婵炲樊浜濋敍婵嬫煛閸愩劎鍩ｆ俊顐㈡健閺?}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                gen = run_agent_loop("闂佸搫琚崕鍐诧耿閸涱垳鐭氭繛宸簼閿涙繈鏌￠崘銊у煟婵?, user, "test-session", db, AsyncMock())
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
        pref = Memory(user_id="ctx-user-1", category="preference", content="闂佸摜濮电划宥夘敃娴犲绫嶉柍琛″亾缂佹鍊瑰鍕吋閸曨厾妲戦梺杞扮劍濠㈡﹢顢?)
        habit = Memory(user_id="ctx-user-1", category="habit", content="婵炴垶鎸撮崑鎾寸箾閸″繐澧叉繛鎾瑰煐瀵板嫬顫濋懜浣冨亖婵?闁诲繐绻愮换鎴濐渻?)
        db.add_all([pref, habit])
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂佸摜濮电划宥夘敃娴犲绫嶉柍琛″亾缂佹鍊瑰鍕吋閸曨厾妲戦梺杞扮劍濠㈡﹢顢? in context
        assert "婵炴垶鎸撮崑鎾寸箾閸″繐澧叉繛鎾瑰煐瀵板嫬顫濋懜浣冨亖婵?闁诲繐绻愮换鎴濐渻? in context


@pytest.mark.asyncio
async def test_warm_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-2", username="ctxtest2", hashed_password="x")
        db.add(user)
        decision = Memory(user_id="ctx-user-2", category="decision", content="婵°倕鍊硅摫闁哄棛鍠栭幃浠嬪Ω閵夈儳鈧崵绱掗弮鍌毿┑鈽嗗幘缁敻寮介锝嗩吅")
        db.add(decision)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "婵°倕鍊硅摫闁哄棛鍠栭幃浠嬪Ω閵夈儳鈧崵绱掗弮鍌毿┑鈽嗗幘缁敻寮介锝嗩吅" in context


@pytest.mark.asyncio
async def test_no_memories_still_works(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-3", username="ctxtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        context = await build_dynamic_context(user, db)
        # Should still have time info, just no memory section
        assert "閻熸粎澧楅幐鍛婃櫠閻樿绫嶉柛顐ｆ礃閿? in context


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
            summary="婵炴垶鎸搁敃銉╊敃閼测斁鍋撻悽娈挎敯闁伙缚绮欓弫宥咁潩鏉堛劍娈㈤梺瑙勬綑閸㈡煡顢氶柆宥呯闁靛鍊楅崯濠囨偣閸ャ劌绀冮柕鍡楀暣閺佸秴鐣濋崘鎯ф櫗缂傚倸鍠氶崰鏇犺姳?闂傚倸鍊堕崝蹇涘焵椤掆偓閸熸娊鎯侀鐐村剭闁告洦鍋掑Σ璇测槈閺冨倸鞋妞ゆ挻鎮傚畷?,
        )
        db.add(summary)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闁诲海鏁搁崢褔宕ｉ崱妯碱洸闁糕剝鍑归崵锕傛偠? in context
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_context_loading.py -v`
Expected: FAIL 闂?memories not appearing in context output

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

WEEKDAY_NAMES = ["闂佸憡绋忛崝瀣博?, "闂佸憡绋忛崝瀣姳?, "闂佸憡绋忛崝瀣箔?, "闂佸憡绋忛崝灞矫?, "闂佸憡绋忛崝瀣姳?, "闂佸憡绋忛崝宀勫矗?, "闂佸憡绋忛崝宥呂?]


async def build_dynamic_context(user: User, db: AsyncSession) -> str:
    """Build the dynamic portion of the system prompt."""
    now = datetime.now(timezone.utc)
    today = now.date()
    weekday = today.isoweekday()

    parts: list[str] = []
    parts.append(f"閻熸粎澧楅幐鍛婃櫠閻樿绫嶉柛顐ｆ礃閿涚喖鏌ㄥ☉娆樺姱now.strftime('%Y-%m-%d %H:%M')}闂佹寧绋戝鏈〦EKDAY_NAMES[weekday - 1]}闂?)

    if user.current_semester_start:
        delta = (today - user.current_semester_start).days
        week_num = delta // 7 + 1
        parts.append(f"閻熸粎澧楅幐鍛婃櫠閻樼鍋撳☉鎶芥婵犫偓閿熺姵鏅慨姗€纭搁崕鎲憌eek_num}闂?)

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

    parts.append("\n婵炲濮撮敃銈夊Φ婢舵劖鍎嶉柛鏇ㄥ墯閿涘绱掔€ｎ亶鍎滅紒?)
    if not courses and not tasks:
        parts.append("- 闂佸搫鍟版慨鎾偩閵娾晛绠?)
    else:
        for course in courses:
            location = f" @ {course.location}" if course.location else ""
            parts.append(f"- {course.start_time}-{course.end_time} {course.name}{location}闂佹寧绋戦悧鎰邦敋瀹曞洨鐭欓悗锝呭缁€?)
        for task in tasks:
            status_mark = "闂? if task.status == "completed" else "闂?
            parts.append(f"- {task.start_time}-{task.end_time} {task.title}闂佹寧绋戝鏉漷atus_mark}闂?)

    # User preferences
    preferences = user.preferences or {}
    if preferences:
        parts.append("\n闂佹椿娼块崝宥夊春濞戙垹纾婚煫鍥ㄦ尪閸嬨劑鏌?)
        if "earliest_study" in preferences:
            parts.append(f"- 闂佸搫鐗冮崑鎾绘煛閸愶絾娅呮い鎺斿枑缁嬪﹪鎮╅搹顐Н闂傚倸鍊介幓顏嗘閻ㄦⅰreferences['earliest_study']}")
        if "latest_study" in preferences:
            parts.append(f"- 闂佸搫鐗冮崑鎾绘煛閸涱喛澹樻い鎺斿枑缁嬪﹪鎮╅搹顐Н闂傚倸鍊介幓顏嗘閻ㄦⅰreferences['latest_study']}")
        if "lunch_break" in preferences:
            parts.append(f"- 闂佸憡顨呴悧鍛閵堝鏅慨婵堟枾references['lunch_break']}")
        if "min_slot_minutes" in preferences:
            parts.append(f"- 闂佸搫鐗冮崑鎾绘煟椤撗冨箺婵犫偓娓氣偓瀵偊宕奸悢鍓叉Н濠电偛鐗忛。顔炬閻ㄦⅰreferences['min_slot_minutes']}闂佸憡甯掑Λ婵嬪箰?)
        if "school_schedule" in preferences:
            parts.append("- 閻庣懓鎲￠悡锟犲储閵堝洨纾炬い鏃囧吹缁嬪﹪鏌熼褍鐏℃俊鐐插€垮鑽ゅ鐎ｃ劉鍋?)

    # Hot memories (preferences + habits) 闂?always loaded
    hot_memories = await get_hot_memories(db, user.id)
    if hot_memories:
        parts.append("\n闂傚倵鍋撻柟绋垮閸╁倿鎮规担瑙勭凡缂佽鍊块弫宥夊醇濠靛懐鍓ㄦ繝闈涘€归崹婵堢箔鐏炲墽鈻曢柣妯哄暱閸旂敻鏌ㄥ☉姗嗘缂?)
        for mem in hot_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Warm memories (recent decisions/knowledge) 闂?loaded at session start
    warm_memories = await get_warm_memories(db, user.id, days=7)
    if warm_memories:
        parts.append("\n闁哄鏅滈崹璺猴耿閿涘嫭濯奸柡澶庢硶缁犳捇鏌ㄥ☉妯煎婵炴捁鍩栧?婵犮垹鐏堥弲顏嗘濮樿埖鏅?)
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
        parts.append(f"\n婵炴垶鎸搁敃銉╊敃閼测斁鍋撻悽娈挎敯闁伙缚绮欓獮妤€螣濞嗙偓鐭楅梺鎸庣⊕椤掔珮ast_summary.summary}")

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
            ConversationMessage(session_id="sess-1", role="user", content="闁汇埄鍨奸崰妤呭垂濠婂牊鍎戦悗锝庡墯缁犳瑩寮堕埡鍌滄噧闁瑰啿妫濋幆鍐礋椤撴稒鏅為梻鍌氬€稿璺侯渻閸岀偞鈷?),
            ConversationMessage(session_id="sess-1", role="assistant", content="婵炶揪绲挎慨鍓ф崲閺嶎厼宸濋柕濠忛檮缁?2婵炴垶鎼╂禍鐐哄煘閺嶎厽鈷掗柛娆忣槹椤ρ勭箾?),
            ConversationMessage(session_id="sess-1", role="user", content="闁汇埄鍨奸崰妤呭垂濠婂應鍋撻悷閭︽Ч閻㈩垱鎸婚〃鍥熺紒妯活啀婵犮垼娉涚粔宕囧姬?),
            ConversationMessage(session_id="sess-1", role="assistant", content="閻庤鐡曠亸娆撳极閹捐绠?婵炴垶鎼╂禍婊埶囬崣澶屸枙闁绘椴稿畷鏌ユ煕?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_summary_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂佹椿娼块崝宥夊春濞戙垹钃熼柕澹嫮鐣芥繛瀛樼矊濡瑥锕㈡导鏉戝窛闁靛ě鈧弫鍕⒒閸屾艾绾ф俊鐐插€垮缁樻綇閸撗咁槷闁诲海鎳撻ˇ鎵暜閹惧顩查柛鈩冪〒瑜邦垶鏌℃担瑙勭凡妞わ箑寮剁粙濠囨偐娓氼垰鎮侀梺鍛婂笚鐢亞妲?婵炴垶鎼╂禍娆撳箲閵忋倕绀夐柍钘夋噽缁€?,
                "actions": ["闂佸搫琚崕鎾敋濡ゅ啰鐭氭繛宸簼閿涙繈鏌￠崘銊у煟婵?, "闂佹眹鍨婚崰鎰板垂濮橆収娈楁俊顖滅帛濞堣泛顭跨捄铏剐＄紒鈥冲閹峰鍨鹃崘鑼喊"],
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
        assert "婵°倕鍊硅摫闁哄棛鍠愬鍕吋閸曨厾妲? in summary.summary


@pytest.mark.asyncio
async def test_end_session_extracts_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-2", username="sesstest2", hashed_password="x")
        db.add(user)

        msgs = [
            ConversationMessage(session_id="sess-2", role="user", content="闂佺懓鐡ㄩ崹鐢稿几閳轰讲鏋庨柕蹇婂墲閿涘秴鈽夐幘绛瑰伐妞わ箑寮剁粙濠囨偐閸偄鈧偟绱掓径瀣厐缂佽鲸绻堝鎻掝潩椤愩倗鎲梺娲讳簻椤戝棝寮搁崘顏嗙煋?),
            ConversationMessage(session_id="sess-2", role="assistant", content="婵犻潧鍊婚弲顐⑩枔閹达附鏅悘鐐村劤閻忓鎮规笟鈧。锔剧礊閸ャ劎顩?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂佹椿娼块崝宥夊春濞戞碍鍋橀柕濞垮妽瑜把兠瑰鍐╊棞妞ゆ帞鍠愮粙濠囨偐閾忣偒妲梻鍌氬€瑰娆愮閸涘﹦闄?,
                "actions": [],
                "memories": [
                    {"category": "preference", "content": "闂佸摜濮电划宥夘敃娴犲绫嶉柍琛″亾缂佹鍊瑰鍕吋閸曨厾妲戦梺鑽ゅ仜濡盯锝為弽顓熸櫖閻忕偟鍋撻悵鎾斥槈閹剧鍔熸繝鈧崨鏉戞闁搞儮鏅╁?},
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
        assert "闂佽崵鍋涘Λ娑綖? in memories[0].content
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

_EXTRACT_PROMPT = """闂佸憡甯掑Λ娆撴倵閼恒儳顩烽柕澶堝€楅悷鎾绘倵閻㈡鏀伴柣锔跨矙閺佸秴鐣濋崘顏嗙倳闂?JSON闂佹寧绋戦悧鍛箔婢跺本鍟哄ù锝囨櫕缂堝鏌涢幋婵囨儓闁告瑧鍋撶粋鎺楀冀瑜嶉弫鍫曟倵閸︻厽顏熺紒杈ㄥ哺閺?
{
  "summary": "婵炴垶鎸撮崑鎾绘煕濞嗗秴鍔ラ柣锔跨矙楠炩偓闁煎鍊楀▔銏ゅ级閳哄倻鎳勬い鎰亹閳ь剛鏁搁、濠囨儊娴犲纾绘慨姗嗗亞閸熷﹤霉閻橆偄浜炬繛?,
  "actions": ["闂佸湱鐟抽崱鈺傛杸闂佹眹鍔岀€氼參骞栭柨瀣婵犲﹤鍟悘娆撴偠?],
  "memories": [
    {"category": "preference|habit|decision|knowledge", "content": "闂佺锕﹂崢褏娆㈤柆宥嗏拹闁圭瀛╅崺鍌炴偣娓氣偓椤ｏ妇绱為崶顒佸剭闁告洦浜欑换鍡涙煙?}
  ]
}

闁荤喐鐟ョ€氼剟宕归鐐存櫖?- summary 闁荤喐娲戦懗鍫曟偩濠靛枹鐑樼瑹婵犲嫮顦繛鎴炴尨閸嬫挸鈽夐幘鍗炩偓鏇°亹閻愬灚瀚?- memories 闂佸憡鐟禍婵娿亹娓氣偓瀹曪綁寮介锝嗘闂佽鎸抽弨鍗炍ｉ幋鐘冲厹妞ゆ棁锟ラ埀顒€鍟蹇涘礈瑜庨悾閬嶆煕鐎ｎ亞绠伴柕鍫滅矙婵″瓨鎷呮搴ｆ闂佽鍨奸崹閬嶅垂閵娾晜鐓傜€广儱鐗滃ú锝夋煕閹邦剛锛嶉柣?- 婵炴垶鎸哥粔鐑姐€呴敃鍌氱闁靛闄勯悞浠嬫煥濞戞澧㈤柡浣靛€濋獮瀣偪椤栵絽娈?闂佺懓鐡ㄩ崹鍫曞汲閻旇　鍋撳☉宕囩窗缂佹顦扮缓?闂佹剚鍋呯敮鐔碱敊閸ヮ亗浜归柡鍥朵簽楠炪垽鏌ｉ～顒€濡介柛鈺傜洴閹虫捇宕樿閸?0闂佸憡甯掑Λ宀勫疮鐎ｎ偆鈻旂€广儱妫楅懙褰掓煛閸屻倕寮跨紒?- 婵炴垶鎸搁悺銊ヮ渻閸岀偛绠戠憸灞剧┍婵犲洤绠掓い鏍ㄧ懅閻熸繈鎮规担绋跨盎缂?婵炲濮撮敃銈夊Φ婢跺鈻旂€广儱妫楅崢鎺楁倵濞戝磭绱扮紒?闂?- 婵犵鈧啿鈧綊鎮樻径濞炬煢闁斥晛鍟粻鎺楁煕婵犲嫬甯剁紒鎯颁含閹峰锛愭担铏剐ら梺姹囧妼鐎氼亝绌辨繝鍥х畳妞ゆ牓鍊楃粈濉礶mories 婵炴垶鎹佸▍锝夊煘閺嶎厼鏋侀柟娈垮枤閻?""


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
                            user_answer = user_response.get("answer", "缂佺虎鍙庨崰娑㈩敇?)
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

Add the following under the `### 閻庤鎮堕崕閬嶅矗閹稿孩濯撮悹鎭掑妽閺嗗化 section in `Agent.md`:

```markdown
- recall_memory闂佹寧绋掗懝鍓х礊鐎ｎ喗顥嗛柍褜鍓涢幉鐗堟媴閸涘﹦顦ラ棅顐㈡搐濡盯寮妶澶婄闁炬艾鍊婚娲煕閹惧磭肖婵炲牊鍨垮畷鎴ｇ疀閹惧崬浠洪梺闈涙濡炴帞寮ч崟顖氱畾妞ゆ牗绋戦悘妤呮煕閹邦剛锛嶉柣掳鍎靛顕€寮甸棃娑掓瀼闂佹椿娼块崝濠囧焵椤掆偓閸婇绮径灞惧暫濞达絽婀卞Σ銊︾箾閸″繆鍋撻幇浣告闁荤姴娲︾换鍫ュ礂濡吋瀚柛鎰典簼閺嗗繘鏌ㄥ☉妯垮鐟滄妸鍥ф嵍闁靛ě鈧埀顒侇焽閳ь剙婀遍崑銈呫€掗崜浣瑰暫濞达絿顭堥崸濠囨煕濞嗘帒绱﹀ǎ鍥э躬楠炰線顢涘☉娆樻Н婵炶揪缍€濞夋洟寮?- save_memory闂佹寧绋掗懝鎹愩亹瑜庣粚鍗炩攽閸℃瑦鎲奸梺娲绘娇閸斿秹宕哄☉銏犲強閹艰揪绲洪埀顒侇焽閹即濡搁妸锕€娑ч梺姹囧妼鐎氼亝绌辨繝鍥х畳妞ゆ牓鍊楃粈澶娾槈閹惧磭啸妞も晪绠撻獮鎺楀Ω閿旂晫鍔烽梺闈涙閸婇鎹㈠鎵佸亾濞戞顏呮櫠閻樿櫣鐤€闁告稒鐣埀顒€绻樺畷妤呭醇閵忊剝娈?ask_user 缂佺虎鍙庨崰娑㈩敇婵犳碍鏅?闂佺懓鐡ㄩ崹濂割敊閸ャ劍濯撮煫鍥ф捣閸熷﹪鏌ㄥ☉娆戞憰闂佸憡鍔曢幊搴敊閹箖鏌曢崱妤€鈧悂顢氶鈧畷銉ノ旂€ｎ剙鎯?
  - preference闂佹寧绋掑銊╁极閵堝绠ｇ€瑰嫰顣﹂悞濠傗攽閸屾稒鐏紒?闂佺懓鐡ㄩ崹鐢稿几閳轰讲鏋庨柕蹇婂墲閿涘秴鈽夐幘绛瑰伐妞わ箑寮剁粙濠囨偐閾忣偅顔嶉柣?闂?  - habit闂佹寧绋掗懝楣冾敆閻斿摜鈻曢柣妯夸含閻﹀酣鏌熼锝呯伈缂?闂佺懓鐡ㄩ崹宕囩博閺夋垟鏋庨柍鈺佸暞娴犳ê顭块懜闈涘摵婵炲闄勭粙?闁诲繐绻愮换鎴濐渻?闂?  - decision闂佹寧绋掑畝鎼佸闯閸濄儲鍟哄ù锝囶焾閺嬧偓缂備焦绋掗悧顓犳?婵°倕鍊硅摫闁哄棛鍠栭幃浠嬪Ω閵夈儳鈧崵绱掗弮鍌毿┑鈽嗗幘缁敻寮介锝嗩吅"闂?  - knowledge闂佹寧绋掓穱娲敋瀹曞洨鐭欓悗锝庡弾閸氬洭鏌ｉ婊冨姷缂?闂佹椿娼块崝宥夊春濞戞碍鍠嗗璺猴功缁讳焦鎱ㄩ幒鎴濃偓璇差啅閼测晜濯奸柣鎴炆戞禒姗€姊?闂?- 婵炴垶鎸哥粔鐑姐€呴敂鐣屸攳婵犻潧妫涢幗鐘测槈閹惧磭鎽犳俊鐐插€块獮鈧憸灞剧┍婵犲洤绠掓い鏍ュ€楃粈?婵炲濮撮敃銈夊Φ婢跺鈻旂€广儱妫楅崢鎺楁倵濞戝磭绱扮紒?闂?- 婵炴垶鎸哥粔鐑姐€呴敂鐣屸攳婵犻潧妫涢幗鐘碘偓瑙勭摃鐏忔瑧鍒掗敓鐘叉嵍闁靛闄勫▓鍫曟煙鐠団€虫灈缂併劏椴哥粙澶愵敇閻樺磭鏆犳繛锝呮礌閸撴繃瀵奸崨瀛樻櫖闁割偓缍嗛崵锔剧磼鐎ｎ亶鍎嶉柍褜鍏涘鎺楀箲閵忋倕绀夐幒鎶藉焵椤戞寧绁伴柍褜鍓欓崯鎶芥儊椤栫偞鏅?- 閻熸粎澧楅幐楣冨极閵堝绠ｉ柣銈庡灱閸?闂婎偄娲﹁摫閻㈩垪鍋搙xx"闂佸搫鍟抽鎰濠靛鍋?recall_memory 闂佺懓鐏氶崕鎶藉春瀹€鈧埀顒傛暩閹虫挾鑺遍懠顒佸闁哄娉曠粻鎾绘煥濞戞鐏遍柛鏂炲洤瑙﹂幖绮瑰墲閸熺偤鏌ｉ婊冨姢闁轰降鍊濋獮瀣暋閺夊灝娈ラ梺鍛婂笧婵炩偓婵?```

- [ ] **Step 2: Add few-shot example for memory**

Add the following as a new example after existing examples in `Agent.md`:

```markdown
### 缂備讲鍋撻弶鐐村娴?闂佹寧绋掓穱娲敊閸ヮ亞鐤€闁糕剝鐟崥鈧梺?
闂佹椿娼块崝宥夊春? "闂佺懓鐡ㄩ崹浣冦亹閸岀偞鍋濋柣妤€鐗婇悵鎾斥槈閹剧宸ユい锕€寮剁粙濠囨偐閾忣偅鐝￠梺缁樼矊濞诧箑煤閹稿寒娈楁慨妤€鐗忕粈澶娒归悩顔煎姎闁诡喗顨堥弫顕€顢欓挊澶屼函闂佺娉涢敃銈壦囬崣澶屸枙闁绘顕ч崢鎾倵閻熼偊妲归悽顖涙崌瀹曠兘濡搁敂鐣屽絼婵炴垶鎸搁敃銈夊箚?

闂?save_memory(category="preference", content="闂佸搫鎳忛惌顔剧箔閸屾稑绶炵€广儱瀚惁搴ㄦ煛娴ｅ摜澧㈢€圭銈稿鎾箻椤旀儳钂嬮梺鎸庣☉閼活垱绂嶉崨濠勯檮闁兼亽鍎查悵鎾绘⒒閸屾稒缍戦柣锝冨姂楠炴帡骞掗幋顓熜╂繛?)
闂?婵炶揪绲藉Λ妤呭储濞戞碍鍏滄い鏃€顑欓崥鍥煥濞戞瑧鎽k_user(type="confirm", question="闂佺懓鐡ㄩ崹濂割敊閸ャ劍濯撮煫鍥ф捣閸熷﹪鏌ㄥ☉娆戠叝缂傚秵锕㈠鎻掝潩椤愩倗鎲繝銏ｆ硾缁夊磭寮ч崟顖氭瀬闁割偁鍨归懞鎶芥煛閸ャ劍灏﹂柣婵愬櫍閺佸秶浠﹂梻瀵搁瀺闂佸憡鑹剧花鑲╂椤撱垹绀傞柛顐ｇ箘閺嗘棃鏌熼悜妯虹瑲婵炲懎瀚板濠氬级閹搭厽些婵炴垶姊绘慨浼村焵椤掆偓閸婃悂顢氶鈧畷銉ノ旂€ｎ剙鎯?)
闂?闂佹椿娼块崝宥夊春濞戞碍鍏滄い鏃€顑欓崥?闂?save_memory
闂?闂佹悶鍎抽崑娑⑺? "婵犻潧鍊婚弲顐⑩枔閹达附鏅悘鐐舵閸ゆ帡鎮规笟鈧。锔剧礊閸ヮ剙违闁稿本鐟ょ花浼存煕濮橆剚鎹ｉ柡浣规崌楠炲骞囬澶嬓╂繛鎴炴⒒婵箖顢橀幖浣哥闁圭儤鎸婚ˇ褍霉閸忚偐鐓紒槌栧弮瀹曟宕煎┑鍫熸闂佸湱鍎ょ敮妤€鈻嶉崟顖涒拻閻庢稒蓱椤ρ勭箾閸垹浠柍?

闂佹椿娼块崝宥夊春? "闂婎偄娲﹁摫閻㈩垪鍋撴繛鎴炴煥椤戝懏鏅堕悩鍨珰閻庨潧鎲￠悾閬嶆煛閸愶絾娅冪紒妤€鍊瑰鍕吋閸曨厾妲戦梺杞扮劍濠㈡﹢顢?

闂?recall_memory(query="闂佸搫鍟犻弲娆戠箔閸屾稑绶炵€广儱瀚惁搴ㄦ煛娴ｈ绶叉い?)
闂?闂佺懓鐏氶崕鎶藉春瀹€鈧幏瀣级鐠恒劎鐣?闂?闂佸憡甯炴繛鈧繛?闂?闂佹悶鍎抽崑娑⑺? "閻庣懓鎲¤ぐ鍐垂瑜版帗鈷旈柕鍫濈墢缁犲綊鏌℃竟婧垮€ら崬鍫曠叓閸パ勵棑闁?
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
        {"role": "user", "content": "婵炶揪绲挎慨鎾Χ?},
        {"role": "assistant", "content": "婵炶揪绲挎慨鎾Χ娴犲鏅ù锝堫潐缁犳帒霉閻橆偄浜炬繛鎴炴煥閻楀棜銇愰崣澶岊浄闁靛鍎辩花璇裁归敐鍥ユ繛鍫熷灴閺?},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    """Long conversations should have older messages compressed."""
    messages = [{"role": "system", "content": "System prompt"}]
    # Add 20 user/assistant pairs
    for i in range(20):
        messages.append({"role": "user", "content": f"闂佹椿娼块崝宥夊春濞戞ǚ妲堥柛顐ゅ枍缁?{i}"})
        messages.append({"role": "assistant", "content": f"闂佸憡鏌￠弲婊勬櫠濠婂牆鐐婇柣鎰▕濡?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "婵炴垶鏌ㄩ鍛櫠閻樼粯鍎嶉柛鏇ㄥ亽閸ょ娀鎮归崶銊х畱闁煎灚鍨块弫宥呯暆閳ь剟寮妶澶婄鐎瑰嫭婢樼徊娲⒑椤愨剝顦风紒?0闂佸搫顦崜婵堢矓閻戣棄绠掓い鏍ュ€楃粈澶愭煕閺傜儤娅嗗褎绮撻弻鍫ユ寠婢跺椹虫繛瀛樼矊濡煤閺嶃劌绶炵€广儱鍟犻崑?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # System prompt should be preserved
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"

    # Should have a summary message
    assert any("婵炴垶鏌ㄩ鍛櫠閻樼粯鍎嶉柛鏇ㄥ亽閸ょ娀鎮? in m.get("content", "") for m in result)

    # Recent messages should be preserved (last 12 non-system messages = 6 pairs)
    assert len(result) <= 14  # system + summary + 12 recent


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    """The most recent messages should be kept intact."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(20):
        messages.append({"role": "user", "content": f"濠电偞鍨甸悧濠冨?{i}"})
        messages.append({"role": "assistant", "content": f"闂佹悶鍎抽崑娑⑺?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "闂佸搫鍟犻弲婊冿耿閿涘嫧鍋撻悽娈挎敯闁伙缚绮欓獮妤€螣濞嗙偓鐭?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # Last message should be the most recent assistant reply
    assert result[-1]["content"] == "闂佹悶鍎抽崑娑⑺?19"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: FAIL 闂?`ImportError: cannot import name 'compress_conversation_history'`

- [ ] **Step 3: Add compress_conversation_history to context_compressor.py**

Append to `app/services/context_compressor.py`:

```python
from app.agent.llm_client import chat_completion as _chat_completion

_SUMMARIZE_PROMPT = """闁荤姴娲ˉ鎾诲极?-3闂佸憡鐟ｉ崕鎾儊娴犲绠戦柤濮愬€楀▔銏犆归悩顔煎姍缂佹鎳愰埀顒傛暩椤㈠﹪鎯佹禒瀣闁告侗鍙庨崯鍥煏閸℃鈧潡宕抽幖浣瑰€烽梺顐ｇ〒缁犱粙鏌ｉ敐鍡欐嚂缂佸彉鍗抽幃浠嬪Ω閿曗偓閻撴洟鏌涚€ｎ偆鐓紒銊㈠墲缁傛帡鍩€椤掍胶鈻曢柛顐ゅ枑閹瑥霉閿濆棗娈犻柍褜鍏涢懗鍫曞灳濡吋濯奸柕鍫濆閸熷﹤霉閻橆偄浜炬繛鎴炴煥閻楀嫰鍩€椤戞寧绁伴柕鍡楀暞濞煎繘宕ｉ妷褍鏅╂繛瀵稿Л閸嬫挸鈽夐弬璺ㄥ濞存粌鎲＄缓鑺ユ叏閹般劌浜?""


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
        summary = response.get("content", "闂佹寧绋戦悧濠偽涢銏犲珘闁绘柨顨庨崵鐘绘偣閸ャ劎绠栭柟鎻掔－閹茬増鎷呮搴ｆ喒闂佸憡鐟崹鎶藉极閵堝鏅?)
    except Exception:
        summary = "闂佹寧绋戦悧濠偽涢銏犲珘闁绘柨顨庨崵鐘绘偣閸ャ劎绠栭柟鎻掔－閹茬増鎷呴悜妯绘闂佺懓鐡ㄩ崝鏇㈠Φ閹寸姵瀚婚柕澶樺灣缁€?

    summary_msg = {
        "role": "user",
        "content": f"[婵炴垶鏌ㄩ鍛櫠閻樼粯鍎嶉柛鏇ㄥ亽閸ょ娀鎮归崶銊х畺闁规彃纾幉鐗堢▕?{summary}",
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
- [ ] Plan 4: Memory + 婵炴垶鎸搁敃锝囩箔閸涙潙妫橀柛銉㈡櫓閸氣偓闂佽崵鍋涘Λ瀵告?0 婵?task闂?```

Update "閻熸粎澧楅幐鍛婃櫠閻樺樊娼伴柨婵嗘噺闊剟鏌熺粭娑樻－閺€? to reflect Plan 4 completion.

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with Plan 4 completion status"
```
