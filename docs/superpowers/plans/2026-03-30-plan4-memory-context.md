# Plan 4: Memory 系统 + 上下文管理

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer memory system (working/short-term/long-term) and context window management to keep conversations coherent across sessions without blowing up the context window.

**Architecture:** Memory CRUD service handles persistence. Two new agent tools (`recall_memory`, `save_memory`) give the LLM on-demand access. Tool result compression summarizes verbose outputs inline. Session lifecycle hooks generate summaries and extract memories at session end. The system prompt builder loads hot/warm memories at session start.

**Tech Stack:** SQLAlchemy async (existing), OpenAI-compatible LLM for summarization, existing agent tool system

**Depends on:** Plan 1 (Memory, SessionSummary, ConversationMessage models), Plan 2 (agent loop, tool_executor, llm_client)

---

## File Structure

```
student-planner/
├── app/
│   ├── services/
│   │   ├── memory_service.py          # Memory CRUD: create, query, update, delete, staleness
│   │   └── context_compressor.py      # Tool result summarization + conversation compression
│   ├── agent/
│   │   ├── tools.py                   # (modify: add recall_memory, save_memory definitions)
│   │   ├── tool_executor.py           # (modify: add recall_memory, save_memory handlers)
│   │   ├── loop.py                    # (modify: add tool result compression after each tool call)
│   │   ├── context.py                 # (modify: add hot/warm memory loading)
│   │   └── session_lifecycle.py       # Session end: generate summary + extract memories
│   ├── routers/
│   │   └── chat.py                    # (modify: call session lifecycle on disconnect/timeout)
│   └── config.py                      # (modify: add context window thresholds)
├── tests/
│   ├── test_memory_service.py         # Memory CRUD unit tests
│   ├── test_context_compressor.py     # Compression logic tests
│   ├── test_memory_tools.py           # recall_memory / save_memory tool tests
│   ├── test_session_lifecycle.py      # Session end flow tests
│   └── test_context_loading.py        # Hot/warm memory in system prompt tests
```

---

### Task 1: Memory CRUD Service

Pure data layer — no LLM calls. Handles create, query by category, query by relevance, update `last_accessed`, and staleness marking.

**Files:**
- Create: `student-planner/app/services/memory_service.py`
- Create: `student-planner/tests/test_memory_service.py`

- [ ] **Step 1: Write the failing tests**

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
            content="喜欢早上复习数学",
            source_session_id="session-abc",
        )
        assert mem.id is not None
        assert mem.category == "preference"
        assert mem.content == "喜欢早上复习数学"
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

        await create_memory(db, "mem-user-2", "preference", "早上复习数学")
        await create_memory(db, "mem-user-2", "habit", "一次最多2小时")
        await create_memory(db, "mem-user-2", "decision", "高数用分章节策略")

        hot = await get_hot_memories(db, "mem-user-2")
        categories = {m.category for m in hot}
        assert "preference" in categories
        assert "habit" in categories
        # decision is NOT hot — it's cold (on-demand)
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
        await create_memory(db, "mem-user-3", "decision", "高数用分章节策略")

        # Old memory (simulate 30 days ago)
        old_mem = Memory(
            user_id="mem-user-3",
            category="decision",
            content="线代用刷题策略",
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_mem)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)
        assert len(warm) == 1
        assert warm[0].content == "高数用分章节策略"


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "高数用分章节策略，效果不错")
        await create_memory(db, "mem-user-4", "preference", "喜欢早上复习")
        await create_memory(db, "mem-user-4", "knowledge", "概率论最难")

        results = await recall_memories(db, "mem-user-4", query="高数")
        assert len(results) >= 1
        assert any("高数" in m.content for m in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-5", "decision", "高数用分章节策略")
        original_accessed = mem.last_accessed

        # Small delay to ensure timestamp differs
        results = await recall_memories(db, "mem-user-5", query="高数")
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

        mem = await create_memory(db, "mem-user-6", "preference", "早上复习")
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

        mem = await create_memory(db, "mem-user-7", "preference", "早上复习")
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
            content="旧的决策",
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

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_memory_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.memory_service'`

- [ ] **Step 3: Implement memory_service.py**

```python
# app/services/memory_service.py
"""CRUD operations for the Memory table."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory

# Hot memory categories — always loaded into system prompt
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

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_memory_service.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

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

- [ ] **Step 1: Write the failing tests**

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
                "weekday": "周三",
                "free_periods": [
                    {"start": "08:00", "end": "10:00", "duration_minutes": 120},
                    {"start": "14:00", "end": "16:00", "duration_minutes": 120},
                ],
                "occupied": [
                    {"start": "10:00", "end": "12:00", "type": "course", "name": "高数"},
                ],
            },
            {
                "date": "2026-04-02",
                "weekday": "周四",
                "free_periods": [
                    {"start": "09:00", "end": "11:00", "duration_minutes": 120},
                ],
                "occupied": [],
            },
        ],
        "summary": "2026-04-01 至 2026-04-02 共 3 个空闲段，总计 6 小时 0 分钟",
    }
    compressed = compress_tool_result("get_free_slots", result)
    # Should use the existing summary field
    assert "3 个空闲段" in compressed
    assert "6 小时" in compressed
    # Should NOT contain the full slot details
    assert "free_periods" not in compressed


def test_compress_list_courses():
    result = {
        "courses": [
            {"id": "1", "name": "高数", "teacher": "张", "weekday": 1, "start_time": "08:00", "end_time": "09:40"},
            {"id": "2", "name": "线代", "teacher": "李", "weekday": 3, "start_time": "10:00", "end_time": "11:40"},
            {"id": "3", "name": "英语", "teacher": "王", "weekday": 2, "start_time": "08:00", "end_time": "09:40"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_courses", result)
    assert "3" in compressed
    assert "高数" in compressed


def test_compress_list_tasks():
    result = {
        "tasks": [
            {"id": "1", "title": "复习高数第一章", "status": "completed"},
            {"id": "2", "title": "复习高数第二章", "status": "pending"},
            {"id": "3", "title": "复习线代", "status": "pending"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_tasks", result)
    assert "3" in compressed
    assert "1" in compressed  # completed count


def test_compress_create_study_plan():
    result = {
        "tasks": [
            {"title": "复习高数第一章", "date": "2026-04-01"},
            {"title": "复习高数第二章", "date": "2026-04-02"},
            {"title": "复习线代", "date": "2026-04-03"},
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

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_context_compressor.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.context_compressor'`

- [ ] **Step 3: Implement context_compressor.py**

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
        return f"[空闲时段查询结果] {summary}"
    slots = result.get("slots", [])
    total = sum(len(d.get("free_periods", [])) for d in slots)
    return f"[空闲时段查询结果] {len(slots)} 天，共 {total} 个空闲段"


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = [c["name"] for c in courses[:5]]
    names_str = "、".join(names)
    if count > 5:
        names_str += f" 等 {count} 门"
    return f"[课程列表] 共 {count} 门课：{names_str}"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    pending = count - completed
    return f"[任务列表] 共 {count} 个任务，{completed} 个已完成，{pending} 个待完成"


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    return f"[复习计划] 已生成 {count} 个复习任务"


_COMPRESSORS = {
    "get_free_slots": _compress_get_free_slots,
    "list_courses": _compress_list_courses,
    "list_tasks": _compress_list_tasks,
    "create_study_plan": _compress_create_study_plan,
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_context_compressor.py -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
cd student-planner
git add app/services/context_compressor.py tests/test_context_compressor.py
git commit -m "feat: add tool result compressor for context window management"
```

---

### Task 3: Agent Tools — recall_memory + save_memory

Two new tools for the LLM to interact with the memory system. `recall_memory` does keyword search (cold memory). `save_memory` creates a new memory with ask_user confirmation baked into the flow.

**Files:**
- Modify: `student-planner/app/agent/tools.py` (add 2 tool definitions)
- Modify: `student-planner/app/agent/tool_executor.py` (add 2 handlers)
- Create: `student-planner/tests/test_memory_tools.py`

- [ ] **Step 1: Add tool definitions to tools.py**

Append these two entries to the `TOOL_DEFINITIONS` list in `app/agent/tools.py`:

```python
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": "从用户的长期记忆中检索相关信息。当需要回忆用户之前的偏好、习惯或决策时使用。返回匹配的记忆列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，如'数学复习策略'或'学习习惯'",
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
            "description": "保存一条用户的长期记忆。只保存用户明确表达的偏好、习惯或重要决策，不要推断。保存前必须先用 ask_user 确认。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["preference", "habit", "decision", "knowledge"],
                        "description": "记忆类别：preference=偏好, habit=习惯, decision=决策, knowledge=认知",
                    },
                    "content": {
                        "type": "string",
                        "description": "记忆内容，自然语言描述",
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
            "description": "删除一条用户的长期记忆。当用户说'忘掉xxx'时，先用 recall_memory 找到对应记忆的 ID，再调用此工具删除。",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "要删除的记忆 ID（从 recall_memory 结果中获取）",
                    },
                },
                "required": ["memory_id"],
            },
        },
    },
```

- [ ] **Step 2: Write the failing tests**

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
            content="喜欢早上复习数学",
        )
        db.add(mem)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "数学"},
            db=db,
            user_id="tool-mem-1",
        )
        assert "memories" in result
        assert len(result["memories"]) >= 1
        assert "数学" in result["memories"][0]["content"]


@pytest.mark.asyncio
async def test_recall_memory_empty_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-2", username="toolmem2", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "不存在的内容"},
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
            {"category": "preference", "content": "喜欢晚上复习文科"},
            db=db,
            user_id="tool-mem-3",
        )
        assert result["status"] == "saved"

        mems = await db.execute(
            select(Memory).where(Memory.user_id == "tool-mem-3")
        )
        saved = mems.scalars().all()
        assert len(saved) == 1
        assert saved[0].content == "喜欢晚上复习文科"
        assert saved[0].category == "preference"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_memory_tools.py -v`
Expected: FAIL — `recall_memory` not found in TOOL_DEFINITIONS

- [ ] **Step 4: Add handlers to tool_executor.py**

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
        "message": f"已记住：{content}",
    }


async def _delete_memory_handler(
    db: AsyncSession, user_id: str, memory_id: str, **kwargs
) -> dict[str, Any]:
    """Delete a long-term memory by ID."""
    deleted = await delete_memory(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "已删除该记忆"}
    return {"error": "记忆不存在或无权删除"}
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

- [ ] **Step 5: Run tests to verify they pass**

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
            "slots": [{"date": f"2026-04-{i:02d}", "weekday": "周一", "free_periods": [{"start": "08:00", "end": "22:00", "duration_minutes": 840}], "occupied": []} for i in range(1, 8)],
            "summary": "2026-04-01 至 2026-04-07 共 7 个空闲段，总计 98 小时 0 分钟",
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
                assert "7 个空闲段" in content
                return {"role": "assistant", "content": "你这周有很多空闲时间！"}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                gen = run_agent_loop("查看空闲时间", user, "test-session", db, AsyncMock())
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
Expected: FAIL — assertion `"free_periods" not in content` fails (no compression yet)

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
        pref = Memory(user_id="ctx-user-1", category="preference", content="喜欢早上复习数学")
        habit = Memory(user_id="ctx-user-1", category="habit", content="一次最多集中2小时")
        db.add_all([pref, habit])
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "喜欢早上复习数学" in context
        assert "一次最多集中2小时" in context


@pytest.mark.asyncio
async def test_warm_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-2", username="ctxtest2", hashed_password="x")
        db.add(user)
        decision = Memory(user_id="ctx-user-2", category="decision", content="高数用分章节策略")
        db.add(decision)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "高数用分章节策略" in context


@pytest.mark.asyncio
async def test_no_memories_still_works(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-3", username="ctxtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        context = await build_dynamic_context(user, db)
        # Should still have time info, just no memory section
        assert "当前时间" in context


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
            summary="上次对话：用户导入了课表，设置了3门考试的复习计划",
        )
        db.add(summary)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "导入了课表" in context
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_context_loading.py -v`
Expected: FAIL — memories not appearing in context output

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

WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


async def build_dynamic_context(user: User, db: AsyncSession) -> str:
    """Build the dynamic portion of the system prompt."""
    now = datetime.now(timezone.utc)
    today = now.date()
    weekday = today.isoweekday()

    parts: list[str] = []
    parts.append(f"当前时间：{now.strftime('%Y-%m-%d %H:%M')}（{WEEKDAY_NAMES[weekday - 1]}）")

    if user.current_semester_start:
        delta = (today - user.current_semester_start).days
        week_num = delta // 7 + 1
        parts.append(f"当前学期：第{week_num}周")

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

    parts.append("\n今天的日程：")
    if not courses and not tasks:
        parts.append("- 无安排")
    else:
        for course in courses:
            location = f" @ {course.location}" if course.location else ""
            parts.append(f"- {course.start_time}-{course.end_time} {course.name}{location}（课程）")
        for task in tasks:
            status_mark = "✓" if task.status == "completed" else "○"
            parts.append(f"- {task.start_time}-{task.end_time} {task.title}（{status_mark}）")

    # User preferences
    preferences = user.preferences or {}
    if preferences:
        parts.append("\n用户偏好：")
        if "earliest_study" in preferences:
            parts.append(f"- 最早学习时间：{preferences['earliest_study']}")
        if "latest_study" in preferences:
            parts.append(f"- 最晚学习时间：{preferences['latest_study']}")
        if "lunch_break" in preferences:
            parts.append(f"- 午休：{preferences['lunch_break']}")
        if "min_slot_minutes" in preferences:
            parts.append(f"- 最短有效时段：{preferences['min_slot_minutes']}分钟")
        if "school_schedule" in preferences:
            parts.append("- 已配置作息时间表")

    # Hot memories (preferences + habits) — always loaded
    hot_memories = await get_hot_memories(db, user.id)
    if hot_memories:
        parts.append("\n长期记忆（偏好与习惯）：")
        for mem in hot_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Warm memories (recent decisions/knowledge) — loaded at session start
    warm_memories = await get_warm_memories(db, user.id, days=7)
    if warm_memories:
        parts.append("\n近期记忆（最近7天）：")
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
        parts.append(f"\n上次对话摘要：{last_summary.summary}")

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

### Task 6: Session Lifecycle — Summary + Memory Extraction

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
            ConversationMessage(session_id="sess-1", role="user", content="帮我看看这周的空闲时间"),
            ConversationMessage(session_id="sess-1", role="assistant", content="你这周有12个空闲时段"),
            ConversationMessage(session_id="sess-1", role="user", content="帮我安排高数复习"),
            ConversationMessage(session_id="sess-1", role="assistant", content="已生成5个复习任务"),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_summary_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "用户查看了本周空闲时间，安排了高数复习计划（5个任务）",
                "actions": ["查询空闲时间", "生成高数复习计划"],
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
        assert "高数复习" in summary.summary


@pytest.mark.asyncio
async def test_end_session_extracts_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-2", username="sesstest2", hashed_password="x")
        db.add(user)

        msgs = [
            ConversationMessage(session_id="sess-2", role="user", content="我喜欢早上复习理科，晚上看文科"),
            ConversationMessage(session_id="sess-2", role="assistant", content="好的，我记住了"),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "用户表达了学习时间偏好",
                "actions": [],
                "memories": [
                    {"category": "preference", "content": "喜欢早上复习理科，晚上看文科"},
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
        assert "理科" in memories[0].content
        assert memories[0].source_session_id == "sess-2"


@pytest.mark.asyncio
async def test_end_session_empty_conversation(setup_db):
    """No messages → no summary, no crash."""
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
Expected: FAIL — `ModuleNotFoundError: No module named 'app.agent.session_lifecycle'`

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

_EXTRACT_PROMPT = """分析以下对话，输出 JSON（不要输出其他内容）：

{
  "summary": "一句话总结这次对话做了什么",
  "actions": ["执行的操作列表"],
  "memories": [
    {"category": "preference|habit|decision|knowledge", "content": "值得长期记住的信息"}
  ]
}

规则：
- summary 要简洁，一两句话
- memories 只提取用户明确表达的偏好、习惯或重要决策
- 不要推断（用户说"我数学不好"→记录；用户考了60分→不推断）
- 临时性信息不记（"今天不想学习"）
- 如果没有值得记住的信息，memories 为空数组"""


async def end_session(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    llm_client: AsyncOpenAI,
) -> None:
    """Process session end: generate summary and extract memories.

    This is called when the WebSocket disconnects or times out.
    Failures are logged but never raised — session end must not crash.
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
    session_timeout_minutes: int = 120  # 2 hours inactivity → new session
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
                            user_answer = user_response.get("answer", "确认")
                            event = await generator.asend(user_answer)
                        elif event["type"] == "done":
                            break
                        else:
                            event = await generator.__anext__()
                except StopAsyncIteration:
                    pass
    except WebSocketDisconnect:
        # Session ended — generate summary and extract memories
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

### Task 8: Update Agent.md — Memory Tool Rules

Add behavior rules for the memory tools to Agent.md.

**Files:**
- Modify: `student-planner/Agent.md`

- [ ] **Step 1: Add memory tool usage rules**

Add the following under the `### 工具使用` section in `Agent.md`:

```markdown
- recall_memory：当需要回忆用户之前的偏好、习惯或决策时使用。不要每次对话都调用，只在确实需要历史信息时使用
- save_memory：只保存用户明确表达的信息，不要推断。保存前必须先用 ask_user 确认："我记住了：[内容]。对吗？"
  - preference：用户偏好（"我喜欢早上复习数学"）
  - habit：学习习惯（"我一次最多集中2小时"）
  - decision：重要决策（"高数用分章节策略"）
  - knowledge：课程认知（"用户觉得概率论最难"）
- 不要保存临时性信息（"今天不想学习"）
- 不要保存已经在数据库中的信息（课程、任务、考试）
- 当用户说"忘掉xxx"时，用 recall_memory 找到对应记忆，然后告知用户已删除
```

- [ ] **Step 2: Add few-shot example for memory**

Add the following as a new example after existing examples in `Agent.md`:

```markdown
### 示例4：记忆管理

用户: "我发现晚上复习效率更高，以后帮我把复习都安排在晚上吧"

→ save_memory(category="preference", content="晚上复习效率更高，偏好晚间安排复习")
→ 但先确认：ask_user(type="confirm", question="我记住了：你晚上复习效率更高，以后优先安排晚间复习。对吗？")
→ 用户确认 → save_memory
→ 回复: "好的，已记住。以后生成复习计划时会优先安排晚间时段。"

用户: "忘掉之前说的早上复习数学"

→ recall_memory(query="早上复习数学")
→ 找到记忆 → 删除
→ 回复: "已删除这条记忆。"
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
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮你的？"},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    """Long conversations should have older messages compressed."""
    messages = [{"role": "system", "content": "System prompt"}]
    # Add 20 user/assistant pairs
    for i in range(20):
        messages.append({"role": "user", "content": f"用户消息 {i}"})
        messages.append({"role": "assistant", "content": f"助手回复 {i}"})

    mock_response = {
        "role": "assistant",
        "content": "之前的对话中，用户发送了20条消息，助手都做了回复。",
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # System prompt should be preserved
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"

    # Should have a summary message
    assert any("之前的对话" in m.get("content", "") for m in result)

    # Recent messages should be preserved (last 12 non-system messages = 6 pairs)
    assert len(result) <= 14  # system + summary + 12 recent


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    """The most recent messages should be kept intact."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(20):
        messages.append({"role": "user", "content": f"消息 {i}"})
        messages.append({"role": "assistant", "content": f"回复 {i}"})

    mock_response = {
        "role": "assistant",
        "content": "早期对话摘要",
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # Last message should be the most recent assistant reply
    assert result[-1]["content"] == "回复 19"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: FAIL — `ImportError: cannot import name 'compress_conversation_history'`

- [ ] **Step 3: Add compress_conversation_history to context_compressor.py**

Append to `app/services/context_compressor.py`:

```python
from app.agent.llm_client import chat_completion as _chat_completion

_SUMMARIZE_PROMPT = """请用1-3句话总结以下对话内容。重点保留：用户做了什么操作、确认了什么、表达了什么偏好。"""


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
        summary = response.get("content", "（早期对话摘要不可用）")
    except Exception:
        summary = "（早期对话摘要生成失败）"

    summary_msg = {
        "role": "user",
        "content": f"[之前的对话摘要] {summary}",
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

### Task 10: Update AGENTS.md — Mark Plan 4 Progress

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Update progress in AGENTS.md**

Update the Plan 4 line and current status:

```markdown
- [ ] Plan 4: Memory + 上下文管理（10 个 task）
```

Update "当前正在执行" to reflect Plan 4 completion.

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with Plan 4 completion status"
```
