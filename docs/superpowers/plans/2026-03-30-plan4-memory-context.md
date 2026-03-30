# Plan 4: Memory 缂傚倸鍊搁崐椋庢閿熺姴鍨傞梻鍫熺〒閺嗭箓鏌ｉ姀銈嗘锭闁?+ 濠电姷鏁搁崑鐐哄垂閸洖绠伴柟闂寸劍閺呮繈鏌ㄥ┑鍡樺窛缂佺姵妫冮弻娑樷槈濞嗘劗绋囧┑鈽嗗亝閿曘垽寮诲☉銏犖ㄩ柕蹇婂墲閻濓箓姊洪崨濠傜劰闁稿鎹囧?
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer memory system (working/short-term/long-term) and context window management to keep conversations coherent across sessions without blowing up the context window.

**Architecture:** Memory CRUD service handles persistence. Two new agent tools (`recall_memory`, `save_memory`) give the LLM on-demand access. Tool result compression summarizes verbose outputs inline. Session lifecycle hooks generate summaries and extract memories at session end. The system prompt builder loads hot/warm memories at session start.

**Tech Stack:** SQLAlchemy async (existing), OpenAI-compatible LLM for summarization, existing agent tool system

**Depends on:** Plan 1 (Memory, SessionSummary, ConversationMessage models), Plan 2 (agent loop, tool_executor, llm_client)

---

## File Structure

```
student-planner/
闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?app/
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?services/
闂?  闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?memory_service.py          # Memory CRUD: create, query, update, delete, staleness
闂?  闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣埖鍔曢拑鐔兼煥閻斿搫孝缂備讲鏅犻弻鏇＄疀鐎ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?context_compressor.py      # Tool result summarization + conversation compression
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?agent/
闂?  闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?tools.py                   # (modify: add recall_memory, save_memory definitions)
闂?  闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?tool_executor.py           # (modify: add recall_memory, save_memory handlers)
闂?  闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?loop.py                    # (modify: add tool result compression after each tool call)
闂?  闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?context.py                 # (modify: add hot/warm memory loading)
闂?  闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣埖鍔曢拑鐔兼煥閻斿搫孝缂備讲鏅犻弻鏇＄疀鐎ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?session_lifecycle.py       # Session end: generate summary + extract memories
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?routers/
闂?  闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣埖鍔曢拑鐔兼煥閻斿搫孝缂備讲鏅犻弻鏇＄疀鐎ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?chat.py                    # (modify: call session lifecycle on disconnect/timeout)
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣埖鍔曢拑鐔兼煥閻斿搫孝缂備讲鏅犻弻鏇＄疀鐎ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?config.py                      # (modify: add context window thresholds)
闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?tests/
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?test_memory_service.py         # Memory CRUD unit tests
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?test_context_compressor.py     # Compression logic tests
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?test_memory_tools.py           # recall_memory / save_memory tool tests
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣泛顑囬悵鍫曟煛閸ャ儱鐏╃紓浣叉櫊閺屾洝绠涚€ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?test_session_lifecycle.py      # Session end flow tests
闂?  闂傚倸鍊风粈渚€鎮块崶顒婄稏濠㈣埖鍔曢拑鐔兼煥閻斿搫孝缂備讲鏅犻弻鏇＄疀鐎ｎ亖鍋撻弴銏″亗婵せ鍋撻柡?test_context_loading.py        # Hot/warm memory in system prompt tests
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
            content="闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈缂備緡鍋勭粔褰掑蓟瀹ュ洦鍋橀柍銉ュ帠婢规洜绱撻崒娆戝妽妞ゃ劌鎳樺畷鎰版偡闁箑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇婇崣澶婄伌婵﹦鍎ゅ顏堝箥椤旂厧顬夋繝鐢靛О閸ㄦ椽鏁冮姀銈冣偓?,
            source_session_id="session-abc",
        )
        assert mem.id is not None
        assert mem.category == "preference"
        assert mem.content == "闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈缂備緡鍋勭粔褰掑蓟瀹ュ洦鍋橀柍銉ュ帠婢规洜绱撻崒娆戝妽妞ゃ劌鎳樺畷鎰版偡闁箑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇婇崣澶婄伌婵﹦鍎ゅ顏堝箥椤旂厧顬夋繝鐢靛О閸ㄦ椽鏁冮姀銈冣偓?
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

        await create_memory(db, "mem-user-2", "preference", "闂傚倸鍊风粈渚€骞栭锕€鐤柣妯款嚙閻ょ偓绻涢崱妯虹仼缂佺姵妫冮弻娑氫沪閸撗€妲堢紓浣稿閸嬬喖鍩€椤掆偓缁犲秹宕曟潏鈹惧亾濮樼厧娅嶉柟顖欑劍閹棃濡搁敂鎯у箰濠电偠鎻紞鈧い顐㈩槺濞嗐垽宕ｆ径鍫滅盎?)
        await create_memory(db, "mem-user-2", "habit", "濠电姷鏁搁崑鐐哄垂閸洖绠伴柟缁㈠枛绾惧鏌熼幆褜鍤熺紒鐘荤畺閺屾盯鍨惧畷鍥╊唶婵犫拃鍐ㄧ骇缂佺粯鐩獮姗€鎮烽幍顔煎缚闁?闂傚倷娴囬褏鎹㈤幇顔藉床闁归偊鍠楀畷鏌ユ煙鐎涙绠ユ繛?)
        await create_memory(db, "mem-user-2", "decision", "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村冀椤撶偟鐣烘繛瀵稿Т椤戝懏鍎梻渚€娼чˇ顓㈠磿閹惰棄鐒垫い鎺戝暙閸氬湱绱掓潏銊ユ诞鐎殿噮鍣ｅ畷鎺懶掑▎鎯у闁宠鍨块崺銉╁幢濡も偓缁犺崵绱撴笟鍥ф灓闁轰浇顕ч锝嗙鐎ｅ灚鏅濋梺鎸庣箓濡參宕?)

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
        await create_memory(db, "mem-user-3", "decision", "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村冀椤撶偟鐣烘繛瀵稿Т椤戝懏鍎梻渚€娼чˇ顓㈠磿閹惰棄鐒垫い鎺戝暙閸氬湱绱掓潏銊ユ诞鐎殿噮鍣ｅ畷鎺懶掑▎鎯у闁宠鍨块崺銉╁幢濡も偓缁犺崵绱撴笟鍥ф灓闁轰浇顕ч锝嗙鐎ｅ灚鏅濋梺鎸庣箓濡參宕?)

        # Old memory (simulate 30 days ago)
        old_mem = Memory(
            user_id="mem-user-3",
            category="decision",
            content="缂傚倸鍊搁崐鐑芥倿閿曞倸纾块柟鎯版妗呭┑顔姐仜閸嬫挾鈧娲﹂崜鐔笺€佸Δ鍛妞ゆ巻鍋撳ù鐘虫そ濮婃椽妫冨☉杈╁姼闂佺閰ｆ禍鍫曞箖閿熺姴鍗抽柣鎰У閻╊垶骞冭瀹曞ジ顢曢妶鍛ㄩ梻鍌欑椤撲粙寮堕崹顔夹曢梻?,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_mem)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)
        assert len(warm) == 1
        assert warm[0].content == "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村冀椤撶偟鐣烘繛瀵稿Т椤戝懏鍎梻渚€娼чˇ顓㈠磿閹惰棄鐒垫い鎺戝暙閸氬湱绱掓潏銊ユ诞鐎殿噮鍣ｅ畷鎺懶掑▎鎯у闁宠鍨块崺銉╁幢濡も偓缁犺崵绱撴笟鍥ф灓闁轰浇顕ч锝嗙鐎ｅ灚鏅濋梺鎸庣箓濡參宕?


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村冀椤撶偟鐣烘繛瀵稿Т椤戝懏鍎梻渚€娼чˇ顓㈠磿閹惰棄鐒垫い鎺戝暙閸氬湱绱掓潏銊ユ诞鐎殿噮鍣ｅ畷鎺懶掑▎鎯у闁宠鍨块崺銉╁幢濡も偓缁犺崵绱撴笟鍥ф灓闁轰浇顕ч锝嗙鐎ｅ灚鏅濋梺鎸庣箓濡參宕ラ崨瀛樷拻濞达絿鎳撻婊呯磼鐎ｎ偄鐏寸€殿喚鏁婚、妤呭礋椤愩倖鐓ｉ梻渚€娼чˇ顐﹀疾濞戙垹绀勯柣妯虹－缁♀偓婵犵數鍋為崕铏閸撗呯＝濞达綀顕栧▓鏃€銇勯敂鐐毈鐎?)
        await create_memory(db, "mem-user-4", "preference", "闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈缂備緡鍋勭粔褰掑蓟瀹ュ洦鍋橀柍銉ュ帠婢规洜绱撻崒娆戝妽妞ゃ劌鎳樺畷鎰版偡闁箑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇?)
        await create_memory(db, "mem-user-4", "knowledge", "婵犵數濮甸鏍窗濡ゅ啯鏆滈柟鐑橆殔绾惧綊鎮归崶褎鈻曢柛鐔锋嚇閺屻倕霉鐎ｎ偅鐝曟繝娈垮灠閵堟悂寮婚敐澶婄闁绘劕妫欓崹鍓佺矉閹烘埈娼ㄩ柍褜鍓欓～?)

        results = await recall_memories(db, "mem-user-4", query="濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊?)
        assert len(results) >= 1
        assert any("濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊? in m.content for m in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-5", "decision", "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村冀椤撶偟鐣烘繛瀵稿Т椤戝懏鍎梻渚€娼чˇ顓㈠磿閹惰棄鐒垫い鎺戝暙閸氬湱绱掓潏銊ユ诞鐎殿噮鍣ｅ畷鎺懶掑▎鎯у闁宠鍨块崺銉╁幢濡も偓缁犺崵绱撴笟鍥ф灓闁轰浇顕ч锝嗙鐎ｅ灚鏅濋梺鎸庣箓濡參宕?)
        original_accessed = mem.last_accessed

        # Small delay to ensure timestamp differs
        results = await recall_memories(db, "mem-user-5", query="濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊?)
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

        mem = await create_memory(db, "mem-user-6", "preference", "闂傚倸鍊风粈渚€骞栭锕€鐤柣妯款嚙閻ょ偓绻涢崱妯虹仼缂佺姵妫冮弻娑氫沪閸撗€妲堢紓浣稿閸嬬喖鍩€椤掆偓缁犲秹宕曟潏鈹惧亾濮樼厧娅嶉柟?)
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

        mem = await create_memory(db, "mem-user-7", "preference", "闂傚倸鍊风粈渚€骞栭锕€鐤柣妯款嚙閻ょ偓绻涢崱妯虹仼缂佺姵妫冮弻娑氫沪閸撗€妲堢紓浣稿閸嬬喖鍩€椤掆偓缁犲秹宕曟潏鈹惧亾濮樼厧娅嶉柟?)
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
            content="闂傚倸鍊风粈渚€骞栭锕€鑸归柡灞诲劚瀹告繃銇勯弮鍌氫壕婵炲牊鎮傚缁樻媴閸涘﹤鏆堥梺鍛婃⒐濞叉粍绔熼弴銏╂晣闁靛繆鈧厖妲?,
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
                "weekday": "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶愭倵閿濆骸澧扮紒?,
                "free_periods": [
                    {"start": "08:00", "end": "10:00", "duration_minutes": 120},
                    {"start": "14:00", "end": "16:00", "duration_minutes": 120},
                ],
                "occupied": [
                    {"start": "10:00", "end": "12:00", "type": "course", "name": "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊?},
                ],
            },
            {
                "date": "2026-04-02",
                "weekday": "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶愭倶閻愮數鍙?,
                "free_periods": [
                    {"start": "09:00", "end": "11:00", "duration_minutes": 120},
                ],
                "occupied": [],
            },
        ],
        "summary": "2026-04-01 闂?2026-04-02 闂?3 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鏌ユ煟閹邦剚鎯堥柣鎾达耿閺屸€愁吋鎼粹€崇闂佹娊鏀辩敮锟犲蓟濞戞ǚ鏋庨煫鍥风稻閳绘捇姊洪崫銉ヤ粧缂侇喗鐟╁濠氬Ω閵夈垺顫嶅┑鈽嗗灣缁垶骞忛柆宥嗏拺闂侇偆鍋涢懟顖涙櫠椤栨稐绻嗛柛娆忣槸濞搭喗銇?6 闂傚倷娴囬褏鎹㈤幇顔藉床闁归偊鍠楀畷鏌ユ煙鐎涙绠ユ繛?0 闂傚倸鍊风粈渚€骞夐敍鍕殰闁圭儤鍤﹀☉妯锋斀閻庯綆浜為?,
    }
    compressed = compress_tool_result("get_free_slots", result)
    # Should use the existing summary field
    assert "3 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鏌ユ煟閹邦剚鎯堥柣鎾达耿閺屸€愁吋鎼粹€崇闂佹娊鏀辩敮锟犲蓟濞戞ǚ鏋庨煫鍥风稻閳绘捇姊? in compressed
    assert "6 闂傚倷娴囬褏鎹㈤幇顔藉床闁归偊鍠楀畷鏌ユ煙鐎涙绠ユ繛? in compressed
    # Should NOT contain the full slot details
    assert "free_periods" not in compressed


def test_compress_list_courses():
    result = {
        "courses": [
            {"id": "1", "name": "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊?, "teacher": "闂?, "weekday": 1, "start_time": "08:00", "end_time": "09:40"},
            {"id": "2", "name": "缂傚倸鍊搁崐鐑芥倿閿曞倸纾块柟鎯版妗呭┑顔姐仜閸嬫挾鈧?, "teacher": "闂?, "weekday": 3, "start_time": "10:00", "end_time": "11:40"},
            {"id": "3", "name": "闂傚倸鍊风粈渚€宕ョ€ｎ€綁骞掗弬鍨亰婵°倧绲介崰姘跺极?, "teacher": "闂?, "weekday": 2, "start_time": "08:00", "end_time": "09:40"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_courses", result)
    assert "3" in compressed
    assert "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊? in compressed


def test_compress_list_tasks():
    result = {
        "tasks": [
            {"id": "1", "title": "濠电姷鏁告慨浼村垂閻撳簶鏋栨繛鎴炴皑閻挾鈧娲栧ú銈嗘叏椤掑嫭鐓曢柡鍥ュ妼婢х粯绻涢崼鐕佹畷濞ｅ洤锕、娑橆煥閸涱厾顐兼繝鐢靛仜閻楀棙鏅舵惔锝嗩潟闁圭儤鍤﹂弮鈧换婵嬪磼濮橆剛顔囩紓鍌氬€烽悞锕傚蓟閵娾晩鏁嬫い鎾跺Т閸?, "status": "completed"},
            {"id": "2", "title": "濠电姷鏁告慨浼村垂閻撳簶鏋栨繛鎴炴皑閻挾鈧娲栧ú銈嗘叏椤掑嫭鐓曢柡鍥ュ妼婢х粯绻涢崼鐕佹畷濞ｅ洤锕、娑橆煥閸涱厾顐兼繝鐢靛仜閻楀棙鏅舵惔锝嗩潟闁圭儤鍤﹂弮鈧换婵嬪磼濮橆剛顔囩紓鍌氬€烽梽宥夊礉婢舵劕鐤炬繝闈涚墕閸?, "status": "pending"},
            {"id": "3", "title": "濠电姷鏁告慨浼村垂閻撳簶鏋栨繛鎴炴皑閻挾鈧娲栧ú銈嗘叏椤掑嫭鐓曢柡鍥ュ妼楠炴ɑ淇婇顐㈢仩妞ゎ厼娼″畷婊勭瑹閸モ晛濮奸梻?, "status": "pending"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_tasks", result)
    assert "3" in compressed
    assert "1" in compressed  # completed count


def test_compress_create_study_plan():
    result = {
        "tasks": [
            {"title": "濠电姷鏁告慨浼村垂閻撳簶鏋栨繛鎴炴皑閻挾鈧娲栧ú銈嗘叏椤掑嫭鐓曢柡鍥ュ妼婢х粯绻涢崼鐕佹畷濞ｅ洤锕、娑橆煥閸涱厾顐兼繝鐢靛仜閻楀棙鏅舵惔锝嗩潟闁圭儤鍤﹂弮鈧换婵嬪磼濮橆剛顔囩紓鍌氬€烽悞锕傚蓟閵娾晩鏁嬫い鎾跺Т閸?, "date": "2026-04-01"},
            {"title": "濠电姷鏁告慨浼村垂閻撳簶鏋栨繛鎴炴皑閻挾鈧娲栧ú銈嗘叏椤掑嫭鐓曢柡鍥ュ妼婢х粯绻涢崼鐕佹畷濞ｅ洤锕、娑橆煥閸涱厾顐兼繝鐢靛仜閻楀棙鏅舵惔锝嗩潟闁圭儤鍤﹂弮鈧换婵嬪磼濮橆剛顔囩紓鍌氬€烽梽宥夊礉婢舵劕鐤炬繝闈涚墕閸?, "date": "2026-04-02"},
            {"title": "濠电姷鏁告慨浼村垂閻撳簶鏋栨繛鎴炴皑閻挾鈧娲栧ú銈嗘叏椤掑嫭鐓曢柡鍥ュ妼楠炴ɑ淇婇顐㈢仩妞ゎ厼娼″畷婊勭瑹閸モ晛濮奸梻?, "date": "2026-04-03"},
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
        return f"[缂傚倸鍊搁崐椋庣矆娓氣偓瀵敻顢楅埀顒勨€旈崘顔藉癄濠㈠厜鏅滅粙鎺旂矉閹烘柡鍋撻敐搴濈敖闁活偄瀚板娲偂鎼淬垹鏆堝銈嗘⒐閻楃姴鐣烽浣侯浄閻庯綆鍋嗛崢鎼佹煟韫囨洖浠╂い鏇嗗洤绀夐柕澶涜礋娴滄粓鏌￠崶鈺佹珡婵炲牊顭囩槐鎺撴綇閵娿儲璇炲Δ鐘靛仦椤洭鍩€椤掑倹鏆柡鍛叀瀹曟瑧寰?{summary}"
    slots = result.get("slots", [])
    total = sum(len(d.get("free_periods", [])) for d in slots)
    return f"[缂傚倸鍊搁崐椋庣矆娓氣偓瀵敻顢楅埀顒勨€旈崘顔藉癄濠㈠厜鏅滅粙鎺旂矉閹烘柡鍋撻敐搴濈敖闁活偄瀚板娲偂鎼淬垹鏆堝銈嗘⒐閻楃姴鐣烽浣侯浄閻庯綆鍋嗛崢鎼佹煟韫囨洖浠╂い鏇嗗洤绀夐柕澶涜礋娴滄粓鏌￠崶鈺佹珡婵炲牊顭囩槐鎺撴綇閵娿儲璇炲Δ鐘靛仦椤洭鍩€椤掑倹鏆柡鍛叀瀹曟瑧寰?{len(slots)} 濠电姷鏁告慨浼村垂瑜版帗鍊堕柛顐犲劚閻ょ偓銇勮箛鎾搭棡妞ゎ偅娲樼换婵嬫濞戝崬鍓扮紓浣插亾?{total} 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鏌ユ煟閹邦剚鎯堥柣鎾达耿閺屸€愁吋鎼粹€崇闂佹娊鏀辩敮锟犲蓟濞戞ǚ鏋庨煫鍥风稻閳绘捇姊?


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = [c["name"] for c in courses[:5]]
    names_str = "闂?.join(names)
    if count > 5:
        names_str += f" 缂?{count} 闂?
    return f"[闂傚倷娴囧畷鍨叏閺夋嚚娲Χ閸℃ɑ鐝锋繛瀵稿Т椤戝懘鎮″┑鍡忔斀闁稿本绮犻悞鍓х磼閳ь剟宕卞Ο鍦畾闂侀潧鐗嗛幊搴敂閵夆晜鐓冪憸婊堝礈濞嗘挸纾?闂?{count} 闂傚倸鍊搁崐鎼佸磹閹间礁纾归柛顐ｆ礀缁€澶愮叓閸ャ劋绶遍柡浣割儔閺岀喖骞嗛弶鍟冩捇鏌￠崪浣稿闁逛究鍔岄埞鎴﹀醇濠婂啫鐏乤mes_str}"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    pending = count - completed
    return f"[濠电姷鏁搁崑娑㈩敋椤撶喐鍙忓Δ锝呭枤閺佸鎲告惔銊ョ疄闁靛ň鏅滈崑鍕煟閹捐櫕鎹ｆい锔诲亜閳规垶骞婇柛濠冩礈閳ь剚鍝庨崝鎴﹀春閳ь剚銇勯幒鍡椾壕闂?闂?{count} 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鍙夌箾閸℃ɑ灏紒鐘崇叀閺屾洝绠涚€ｎ亖鍋撻弴鐘电焼濠㈣埖鍔栭悡鍐煢濡警妲归柛锝囨櫕缁辨帡鍩€椤掍焦娅犻柛褍娼祄pleted} 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鍙夌節婵犲倻澧曠紒鈧崟顖涚叆婵炴垶锚椤忋倝鏌涚€ｎ偅宕岄柟顔惧厴閹囧醇閻旂顏伴梻鍌欑劍閹爼宕濆鍛殕闁归棿绀侀弸浣衡偓骞垮劚濞茬娀宕戦幘缁橆棃婵炴垶鑹鹃柋鍣€nding} 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鍙夌節婵犲倹鍣烘い鎰矙閺岋綁寮崶銉㈠亾閳ь剟鏌涚€ｎ偅宕岄柟顔惧厴閹囧醇閻旂顏伴梻?


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    return f"[濠电姷鏁告慨浼村垂閻撳簶鏋栨繛鎴炴皑閻挾鈧娲栧ú銈嗘叏椤掑嫭鐓曢柡鍥ュ妼楠炴鈹戦姘ュ仮闁哄苯绉规俊鐑藉Ψ閵夛附鐦ｉ梻浣筋嚙缁绘劙濡?闂備浇顕у锕傦綖婢舵劖鍋ら柡鍥╁С閻掑﹥绻涢崱妯诲碍闁哄绶氶弻鐔煎箲閹伴潧娈紓?{count} 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鍙夌節婵犲倻鍚囬柛銉墮閻顭跨捄鍝勵槵闁哄鐟╁铏圭磼濮楀棛鍔告俊鐐差嚟椤牓鎮鹃悜钘夎摕闁靛濡囬崢?


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
            "description": "濠电姷鏁搁崑娑㈩敋椤撶喐鍙忛柡澶嬪殮瑜版帗鍊婚柦妯侯槹閻庮剟姊洪棃娑氬妞わ富鍨崇划濠氭晲閸滀焦瀵岄柣搴秵娴滄粓顢楅姀銈嗙厽闁挎繂顦幉鐐叏婵犲偆鐓奸柛鈹惧亾濡炪倖甯掔€氼剛绮绘导鏉戠婵烇綆鍓欓悘鈺呮煟閹烘挻鍊愰柡宀嬬秮閹晜娼忛埡浣割瀴婵犵數濮伴崹娲€﹂崶顒€绠查柕蹇嬪€曠壕鍏肩箾閹寸偛鐒归柡瀣墪椤啴濡堕崱妯烘殫闂侀潻绲婚崕閬嶏綖韫囨稑绀堢憸蹇曞閻撳簺鈧帒顫濋鍌欒檸闂佽娴氶崰妤冩崲濞戙垹绾ч柟鎼幗閳诲牓鎮楃憴鍕妞ゃ劌锕ら悾宄拔旈崨顓炵獩濡炪倖甯掗崐濠氭偩妤ｅ啯鈷掑ù锝囩摂閸ゅ啴鏌涘▎蹇涘弰鐎规洖缍婇、妤呭礋椤愩倕濮︽俊鐐€栧濠氬磻閹剧粯鐓曞┑鐘插€归幉鍝ョ磼鏉堚晛浠ч柍褜鍓ㄧ紞鍡涘窗濡ゅ惤澶愬幢濞戞瑧鍘撻悷婊勭矒瀹曟粌鈽夐姀鐘电枀闂佺粯顨呴悧濠冨垔閹绢喗鐓曟繛鎴烇公閸旂喐銇勯敂鍝勫姦婵☆偄鎳橀、鏇㈠閳╁啯鍊锋繝纰樻閸嬪懘鎯勯姘煎殨妞ゆ劧绠戝洿婵犮垼娉涢敃锕傤敇濞差亝鈷戦柣鎰靛墲婢规﹢鏌涙繝鍌ょ吋妞ゃ垺锚鐓ゆい蹇撴噽閸橀亶姊虹憴鍕姢缁剧虎鍙€閸婂瓨绻濋悽闈涗粶闁绘锕畷褰掑垂椤旂偓娈鹃梺纭呮彧缁插潡鎮块埀顒勬⒑鐟欏嫬鍔ょ€规洦鍓氱粋鎺懨洪鍛嫼闂傚倸鐗婄粙鎺椝夊▎鎰箚闁绘劖娼欑粭褏鈧鍟崶褏顦板銈嗙墬濮樸劑鎮鹃幆褜娓婚柕鍫濇婢ь剛绱掔€ｎ偄鐏撮柟顔矫灃闁告侗鍠氶崢閬嶆⒑瑜版帒浜伴柛鎾寸洴閺佸秴顓兼径瀣幗闁圭儤濞婂畷鏇㈡濞戝崬娈ㄥ銈嗘磵閸嬫挾鈧鍠氶弫璇参涢崘銊㈡闁圭儤鎸鹃埀顒€銈稿缁樻媴鐟欏嫨浠у┑鐐靛帶濞尖€崇暦濠靛洨绡€闁搞儜鍛Е婵＄偑鍊栧濠氬磻閹剧粯鐓曞┑鐘插濞呮洟鏌熼獮鍨伈妤犵偛顑夐弫鍐焵椤掑嫭鍊峰┑鐘叉处閻撶喖鏌熼柇锕€骞栫紒鎻掝煼閺岋綁寮介婵囧枤濠殿喖锕ュ钘夘嚕閸撲焦宕夐柕濠冨姂閸婃牜鎹㈠☉銏犻唶闁绘棃顥撴禒濂告⒑閻熸澘妲绘い鎴濐槸椤曪綁宕滄担鐟扮／闂侀潧臎閸涱喗顔撻梻鍌氬€风粈渚€骞夐敍鍕殰婵°倕鎳岄埀顒€鍟鍕箛椤戔斂鍎甸弻娑㈠箛闂堟稒鐏堥弶?,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "闂傚倸鍊烽懗鍫曞箠閹捐瑙﹂悗锝庡墮閸ㄦ繈骞栧ǎ顒€濡肩痪鎯с偢閺屾洘绻涢悙顒佺彅缂備讲鍋撻柛宀€鍋為悡娆撴煙椤栨稒绶茬悮姘舵⒑閸濆嫭顥為柣鈺婂灦楠炲啳銇愰幒鎴犲€為悷婊冪箻閸┿垹鐣濋埀顒傛閹烘挻缍囬柕濞у懐鏆┑?闂傚倸鍊峰ù鍥ь浖閵娾晜鍊块柨鏇楀亾妞ゎ厼鐏濋～婊堝焵椤掑嫨鈧礁螖閸涱喖浜滅紓浣割儓濞夋洜绮ｉ悙鐑樺€垫鐐茬仢閸旀岸鎮楀鐓庢珝闁诡垯鐒﹂幆鏃堟晲閸モ晪绱叉繝鐢靛仦閸ㄥ爼鎮疯閺呭爼鏌嗗鍡欏幐?闂?闂傚倷娴囬褏鈧稈鏅犲畷姗€鎳￠妶鍥╋紳濠殿喗锚瀹曨剚鎱ㄩ鍕厱闁哄洢鍔屾晶浼存煃缂佹ɑ绀嬮柡宀嬬到铻ｉ柛婵嗗濮ｆ劙姊?",
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
            "description": "濠电姷鏁搁崕鎴犲緤閽樺娲晜閻愵剙搴婇梺绋跨灱閸嬬偤宕戦妶澶嬬厪濠电姴绻愰々顒勬煃缂佹ɑ顥堥柡灞界Х椤т線鏌涢幘璺烘瀻妞ゆ洩缍佸畷濂稿即閻斿憡鐝梻浣告啞濞诧箓宕滃顑芥灁闁靛繈鍊栭埛鎴︽偡濞嗗繐顏悘蹇ラ檮閵囧嫰濡烽敂钘夌闂佸磭绮幑鍥嵁鐎ｎ喗鏅滈悷娆欑稻鐎氬姊绘担鍛婅础妞ゎ厼鐗忛埀顒佺▓閺呯姴鐣峰ú顏勭＜闁绘劖娼欐禒顖涚箾鏉堝墽绉い顐㈩槺濞嗐垽鎳犻鍌滐紲闁荤姴娲﹁ぐ鍐焵椤掍礁顕滃ǎ鍥э躬楠炴﹢顢欓懖鈺嬬床婵犳鍠楅敃鈺呭礈濮樿埖鐓ユい鎾跺枔缁犻箖鏌ㄥ┑鍡樺櫤濠㈣泛瀚槐鎺旀嫚閹绘巻鍋撻崸妤€绠栨繛宸簻鎯熼梺鍐叉惈閸婂憡绂掑ú顏呪拺闂傚牊渚楅悡顓犵磼閻樺啿鐏撮柟顕嗙節瀵挳濮€閿涘嫬骞愰梻浣告啞濞诧箓宕戦崨鏉戠闁挎繂顦伴悡鍐煏婢舵稑鐦滈柣鎺嶇矙閺岀喖顢欑拠鎻掔ギ婵犵鍓濋幃鍌涗繆閹间焦鏅濋柍褜鍓欓埥澶庮樄婵﹤鎼晥闁搞儜鍐剧€抽梺璇插閸戝綊宕滃杈╃焿鐎广儱顦婵嗏攽閻樻彃顏俊缁㈠枟缁绘繂鈻撻崹顔界亶闂佸憡鏌ㄧ换妯虹暦閹达箑绠婚悗娑櫭鎾翠繆閻愬樊鍎忔繛鏉戝槻鍗遍柟杈鹃檮閳锋垿鎮归崶锝傚亾瀹曞洣绱橀梻浣规偠閸旀垶绂嶇捄铏规殾鐟滅増甯掓儫闂佸啿鎼崐濠氬储閹烘鍊垫鐐茬仢閸旀岸鏌ｅΔ浣虹煀閻撱倝鏌ㄥ┑鍡╂Ч闁绘挻娲熼弻鐔兼焽閿曗偓婢т即鏌ㄥ☉妯夹ч柡宀嬬稻楠炲﹪鏌涙惔锝嗘毈鐎殿噮鍋勯濂稿炊閿旇棄濯伴梻浣稿悑缁佹挳寮插┑瀣疅鐟滅増甯楅悡鐔兼煟閺傛寧鍟炵痪鎯ь煼閺岋綁骞掗悙宸喘闂佽桨绶￠崰娑㈠Φ閹版澘绠抽柟瀵稿剱濡喐淇婇悙顏勨偓鏍箰缂佹鐝堕柡鍥ュ灩绾惧鏌熼幑鎰靛殭缁炬儳鍚嬬换娑㈠幢濡櫣浠煎銈嗘⒐濡啴寮婚敐鍡樺劅闁靛繆鎳囨慨鍥⒑閹稿氦澹樻い顓″劵椤︽潙鈹戦鐓庘挃缂侇喛顕ч埥澶愬閻樿尙鐛╂繝鐢靛剳缂嶅棝宕楀鈧畷鎴﹀箻閸︻厾鏉稿┑鐐村灦椤洭藝瑜斿娲礈閹绘帊绨撮梺鎼炲妽濡炶棄顕?ask_user 缂傚倸鍊烽懗鍫曟惞鎼淬劌鐭楅幖娣妼缁愭绻涢幋娆忕労闁轰礁娲ら埞鎴︽偐鐎圭姴顥濋弶?,
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["preference", "habit", "decision", "knowledge"],
                        "description": "闂傚倷娴囧畷鍨叏閹惰姤鍊块柨鏇楀亾妞ゎ厼鐏濊灒闁稿繒鍘ф惔濠囨⒑缁嬫寧婀扮紒顔兼捣娴滄悂鎮介崨濠備化闂佹悶鍎崝宀€寰婃繝姘厽闁圭儤鍨崑銏ゆ煛鐏炶濡奸柍钘夘槸閳诲骸螣閸濆嫷娼弐eference=闂傚倸鍊烽懗鍫曗€﹂崼銉晞闁告侗鍨卞畷鏌ユ煙閻楀牊绶查崶? habit=濠电姷鏁搁崑鐐哄垂鐠轰警娼栫紓浣股戦崣蹇涙煟閵忋埄鐒剧痪? decision=闂傚倸鍊风粈渚€骞夐敓鐘茬闁哄洨濮撮ˉ姘亜閹惧崬鐏柛? knowledge=闂傚倷娴囧畷鍨叏閹惰姤鈷旂€广儱顦壕瑙勪繆閵堝懏鍣洪柛?,
                    },
                    "content": {
                        "type": "string",
                        "description": "闂傚倷娴囧畷鍨叏閹惰姤鍊块柨鏇楀亾妞ゎ厼鐏濊灒闁稿繒鍘ф惔濠囨⒑缁嬭法鐏遍柛瀣〒缁牓宕橀鐣屽幈濠电偞鍨靛畷顒€顕ｆィ鍐╃厱闁绘棃鏀遍崰姗€鏌＄仦璇插闁宠棄顦灒闁兼祴鏅涙慨浼存⒒娴ｈ鍋犻柛濠冪墱閸掓帡骞樼拠鑼暫闂佺粯鍔曢幖顐ょ不濮樿埖鈷戞い鎾卞妿閻ｈ鲸绻涢崼浣告处閻撶喖鏌ｉ弮鍫婵炲牓浜堕弻娑氣偓锝庡亝瀹曞矂鏌″畝鈧崰鎾诲箯閻樼粯鍤戞い鎺戝亞閸熷牓姊?,
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
            "description": "闂傚倸鍊风粈渚€骞夐敍鍕殰闁绘劕顕粻楣冩煃瑜滈崜姘辨崲濞戙垹宸濇い鎾跺剱閸斿绱撴担鍓插剰妞わ妇鏁诲畷娲焵椤掍降浜滈柟鐑樺灥椤忊晝绱掗悪娆忔处閻撱儲绻涢幋鐏活亪顢旈鍫熺厸闁糕剝顨堢粻濠氭煛瀹€鈧崰鏍嵁濮椻偓椤㈡岸宕ㄩ鍛棝濠电姷鏁搁崑娑㈡偋婵犲洤鍨傞柛顭戝櫘濞兼牜鎲搁悧鍫濈瑨缂佺姳鍗抽獮鏍庨鈧悘鈺呮煟閹烘挻鍊愰柡宀嬬秮閹晜娼忛埡浣割瀴婵犵數濮伴崹娲€﹂崶顒€绠查柕蹇嬪€曠壕濂告煟閹邦剙妫橀柕澶嗘櫆閻撴洟鎮橀悙闈涗壕闁汇劍鍨圭槐鎺撳緞婵炲灝浠梺鍝勭焿缂嶄線鏁愰悙渚晢闁逞屽墯娣囧﹥绂掔€ｎ偆鍘遍梺鍐叉惈閸婂濡撮幒妤佺厵?闂傚倸鍊搁…顒勫磻閸曨個娲晝娴ｈ鍣烽梻浣圭湽閸╁嫰宕归鍫濈；闁瑰吋鐛皒'闂傚倸鍊风粈渚€骞栭锕€鐤柟鍓佺摂閺佸﹪鏌熼柇锕€鏋熸い顐ｆ礃缁绘繈妫冨☉鍗炲壈缂備讲鍋撻柛宀€鍋為悡鏇熴亜閹邦喖孝闁诲浚浜弻?recall_memory 闂傚倸鍊烽懗鍫曞箠閹剧粯鍊舵慨妯挎硾绾惧潡鏌熼幆鐗堫棄闁哄嫨鍎抽埀顒€鍘滈崑鎾绘煃瑜滈崜鐔煎春閳ь剚銇勯幒鎴濃偓褰掑汲閳哄懏鐓欓柧蹇ｅ亝鐏忕敻鏌ゅú顏冩喚闁瑰磭濞€椤㈡鎷呴崜娴嬪亾濞戙垺鈷戦柛婵嗗濡插吋绻涙径瀣缂侇喖顭烽獮妯肩磼濡厧骞?ID闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟杈鹃檮閸ゆ劖銇勯弽顐粶闁汇値鍣ｉ弻宥堫檨闁告挾鍠栭獮鍐捶椤撴稑浜鹃柨婵嗙凹缁ㄥ鏌￠崱娆忔灈闁哄备鍓濋幏鍛存濞戞帒浜鹃柡鍥舵緛缂嶆牠鏌曡箛瀣偓鏇炴纯闂備礁鎲℃笟妤呭礈濞戙垺鍎楁俊銈呮噺閳锋垹绱掔€ｎ厽纭剁紒鐘卞嵆閺屾盯濮€閿涘嫬寮ㄩ悗瑙勬礈椤㈠﹪濡甸幇鏉跨闁圭虎鍨辩€垫牠姊绘笟鈧褔鎮ч崱娑樼柈闁绘顕х壕?,
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "闂傚倷娴囧畷鐢稿窗閹邦優娲箣閻樼數鐒兼繛鎾村焹閸嬫挾鈧娲滈、濠囧Φ閹版澘绠抽柟缁㈠灡鐎垫牠姊绘笟鈧褔鎮ч崱妞曟椽鏁冮崒娑樹患闂備緡鍓欑粔鐢稿磻閿濆悿褰掓晲閸偅缍堢紓浣瑰劶鐏忔瑧妲?ID闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟杈鹃檮閸嬪鏌涘☉鍗炵仩闁?recall_memory 缂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€哥粻鏉库攽閻樺磭顣查柛濠呮硾椤法鎹勬笟顖氬壋闂佸磭绮褰掑Φ閸曨垰绠绘い鏍殔娴滃墽鈧娲栧ù鍌炲船閻㈠憡鈷掑ù锝呮啞閸熺偤鏌ｉ悤鍌滅暤闁诡啫鍥舵晣闁绘ɑ鍓氬?,
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
            content="闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈缂備緡鍋勭粔褰掑蓟瀹ュ洦鍋橀柍銉ュ帠婢规洜绱撻崒娆戝妽妞ゃ劌鎳樺畷鎰版偡闁箑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇婇崣澶婄伌婵﹦鍎ゅ顏堝箥椤旂厧顬夋繝鐢靛О閸ㄦ椽鏁冮姀銈冣偓?,
        )
        db.add(mem)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "闂傚倸鍊峰ù鍥ь浖閵娾晜鍊块柨鏇楀亾妞ゎ厼鐏濋～婊堝焵椤掑嫨鈧?},
            db=db,
            user_id="tool-mem-1",
        )
        assert "memories" in result
        assert len(result["memories"]) >= 1
        assert "闂傚倸鍊峰ù鍥ь浖閵娾晜鍊块柨鏇楀亾妞ゎ厼鐏濋～婊堝焵椤掑嫨鈧? in result["memories"][0]["content"]


@pytest.mark.asyncio
async def test_recall_memory_empty_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-2", username="toolmem2", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "濠电姷鏁搁崑鐐哄垂閸洖绠伴柛婵勫劤閻捇鏌熺紒銏犳灍闁稿鍊濋弻鏇熺箾閻愵剚鐝旈梺鍦嚀閻栧ジ寮婚弴鐔虹鐟滃秶鈧凹鍣ｅ鎶芥偐缂佹ǚ鎷洪梺鍛婄☉閿曘倖鎱ㄩ崶顒佺厵闁告劖鐓￠崣鍕亜?},
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
            {"category": "preference", "content": "闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈闂佹眹鍊楅崑鎾诲箞閵娿儺娼ㄩ柛鈩冦仦缁ㄤ粙姊洪懡銈呮瀾闁告梹娲熼垾锔炬崉閵婏箑纾梺鎯х箰婢э綁鏁嶉崟顓狅紲闂佺偨鍎遍崯鍧楊敂椤撶姭鍋撳▓鍨珮闁告挾鍠庨悾鐑藉醇閺囩偟鍘告繝鐢靛Т閸熸壆绮?},
            db=db,
            user_id="tool-mem-3",
        )
        assert result["status"] == "saved"

        mems = await db.execute(
            select(Memory).where(Memory.user_id == "tool-mem-3")
        )
        saved = mems.scalars().all()
        assert len(saved) == 1
        assert saved[0].content == "闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈闂佹眹鍊楅崑鎾诲箞閵娿儺娼ㄩ柛鈩冦仦缁ㄤ粙姊洪懡銈呮瀾闁告梹娲熼垾锔炬崉閵婏箑纾梺鎯х箰婢э綁鏁嶉崟顓狅紲闂佺偨鍎遍崯鍧楊敂椤撶姭鍋撳▓鍨珮闁告挾鍠庨悾鐑藉醇閺囩偟鍘告繝鐢靛Т閸熸壆绮?
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
        "message": f"闂備浇顕у锕傦綖婢舵劖鍋ら柡鍥╁С閻掑﹥銇勮箛鎾跺⒈闁轰礁锕弻娑㈠Ψ閿濆懎顬夋繝娈垮灡閹告娊鎮￠锕€鐐婇柕澶堝劚婵垻绱撴担鐟板闁冲嘲鐛歰ntent}",
    }


async def _delete_memory_handler(
    db: AsyncSession, user_id: str, memory_id: str, **kwargs
) -> dict[str, Any]:
    """Delete a long-term memory by ID."""
    deleted = await delete_memory(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "闂備浇顕уù鐑藉箠閹捐绠熼梽鍥Φ閹版澘绀冩い鏃傚帶閻庮參鎮峰鍛暭閻㈩垱顨婇崺娑㈠籍閸喓鍘梺鍓插亝缁诲嫭鏅堕柆宥嗙厱闁靛牆鎷嬪Ο鈧梺璇″枦椤骞忛崨顖涘枂闁告洦鍘奸崵鎺旂磽?}
    return {"error": "闂傚倷娴囧畷鍨叏閹惰姤鍊块柨鏇楀亾妞ゎ厼鐏濊灒闁稿繒鍘ф惔濠囨⒑缁嬫寧婀扮紒瀣崌閸┿垽寮崒妤€浜炬鐐茬仢閸旀岸鏌熼搹顐㈠妤犵偞顨婇幃鈺冪磼濡厧骞堥梻浣瑰閺屻劑骞栭锝勭箚濞寸姴顑嗛悡鏇㈡煏婵犲繒鍒板┑顔煎€婚埀顒侇問閸ｎ噣宕抽敐澶婄畺闁冲搫鎳忛幆鐐淬亜閹扳晛鈧鈪查梻鍌氬€风粈渚€骞夐敍鍕殰闁绘劕顕粻楣冩煃瑜滈崜姘辨崲?}
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
            "slots": [{"date": f"2026-04-{i:02d}", "weekday": "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶愭倵閿濆骸澧伴柛?, "free_periods": [{"start": "08:00", "end": "22:00", "duration_minutes": 840}], "occupied": []} for i in range(1, 8)],
            "summary": "2026-04-01 闂?2026-04-07 闂?7 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鏌ユ煟閹邦剚鎯堥柣鎾达耿閺屸€愁吋鎼粹€崇闂佹娊鏀辩敮锟犲蓟濞戞ǚ鏋庨煫鍥风稻閳绘捇姊洪崫銉ヤ粧缂侇喗鐟╁濠氬Ω閵夈垺顫嶅┑鈽嗗灣缁垶骞忛柆宥嗏拺闂侇偆鍋涢懟顖涙櫠椤栨稐绻嗛柛娆忣槸濞搭喗銇?98 闂傚倷娴囬褏鎹㈤幇顔藉床闁归偊鍠楀畷鏌ユ煙鐎涙绠ユ繛?0 闂傚倸鍊风粈渚€骞夐敍鍕殰闁圭儤鍤﹀☉妯锋斀閻庯綆浜為?,
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
                assert "7 濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鏌ユ煟閹邦剚鎯堥柣鎾达耿閺屸€愁吋鎼粹€崇闂佹娊鏀辩敮锟犲蓟濞戞ǚ鏋庨煫鍥风稻閳绘捇姊? in content
                return {"role": "assistant", "content": "濠电姷鏁搁崑鐘诲箵椤忓棗绶ら柟绋垮閸欏繘鏌涢幘妤€瀚惔濠囨⒑閸濆嫮鈻夐柛妯煎帶椤斿繐鈹戠€ｎ偆鍘繝鐢靛Т缁绘ê顬婇鍓х＜闁绘ê鍟跨粭褔鏌嶈閸撴瑩鎮樺顒夌唵婵せ鍋撻柟顔ㄥ洤骞㈡繛瀛樻緲濞层劑骞戦崟顖毼╃憸蹇涙偂閺傚簱鏀介柣鎰级閳绘洖霉濠婂嫮绠為柡浣哥Т閳规垹鈧綆鍋嗛崢鎼佹⒑閸涘﹤濮傞柛鏂块叄瀹曟椽鏁愰崱鏇犵畾濡炪倖鍔戦崹娲磻閵夆晜鐓?}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                gen = run_agent_loop("闂傚倸鍊风粈渚€骞栭銈嗗仏妞ゆ劧绠戠壕鍧楁煕閹邦垼鍤嬮柤鏉挎健閺屾稑鈽夐崡鐐典化闂佹椿鍘界喊宥囨崲濞戞﹩鍟呮い鏃囧吹閸戝綊姊洪幐搴ｂ姇缂佽鐗撳濠氭晸閻樿尙顦ㄩ梺闈浤涢崘顏勫箺濠?, user, "test-session", db, AsyncMock())
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
        pref = Memory(user_id="ctx-user-1", category="preference", content="闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈缂備緡鍋勭粔褰掑蓟瀹ュ洦鍋橀柍銉ュ帠婢规洜绱撻崒娆戝妽妞ゃ劌鎳樺畷鎰版偡闁箑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇婇崣澶婄伌婵﹦鍎ゅ顏堝箥椤旂厧顬夋繝鐢靛О閸ㄦ椽鏁冮姀銈冣偓?)
        habit = Memory(user_id="ctx-user-1", category="habit", content="濠电姷鏁搁崑鐐哄垂閸洖绠伴柟缁㈠枛绾惧鏌熼幆褜鍤熺紒鐘荤畺閺屾盯鍨惧畷鍥╊唶婵犫拃鍐ㄧ骇缂佺粯鐩獮姗€鎮烽幍顔煎缚闁诲骸鐏氬妯尖偓姘煎墴閿濈偛鈹戠€ｎ偄娈濇繛杈剧到閸燁偅绂嶉弽褉鏀?闂傚倷娴囬褏鎹㈤幇顔藉床闁归偊鍠楀畷鏌ユ煙鐎涙绠ユ繛?)
        db.add_all([pref, habit])
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈缂備緡鍋勭粔褰掑蓟瀹ュ洦鍋橀柍銉ュ帠婢规洜绱撻崒娆戝妽妞ゃ劌鎳樺畷鎰版偡闁箑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇婇崣澶婄伌婵﹦鍎ゅ顏堝箥椤旂厧顬夋繝鐢靛О閸ㄦ椽鏁冮姀銈冣偓? in context
        assert "濠电姷鏁搁崑鐐哄垂閸洖绠伴柟缁㈠枛绾惧鏌熼幆褜鍤熺紒鐘荤畺閺屾盯鍨惧畷鍥╊唶婵犫拃鍐ㄧ骇缂佺粯鐩獮姗€鎮烽幍顔煎缚闁诲骸鐏氬妯尖偓姘煎墴閿濈偛鈹戠€ｎ偄娈濇繛杈剧到閸燁偅绂嶉弽褉鏀?闂傚倷娴囬褏鎹㈤幇顔藉床闁归偊鍠楀畷鏌ユ煙鐎涙绠ユ繛? in context


@pytest.mark.asyncio
async def test_warm_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-2", username="ctxtest2", hashed_password="x")
        db.add(user)
        decision = Memory(user_id="ctx-user-2", category="decision", content="濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村冀椤撶偟鐣烘繛瀵稿Т椤戝懏鍎梻渚€娼чˇ顓㈠磿閹惰棄鐒垫い鎺戝暙閸氬湱绱掓潏銊ユ诞鐎殿噮鍣ｅ畷鎺懶掑▎鎯у闁宠鍨块崺銉╁幢濡も偓缁犺崵绱撴笟鍥ф灓闁轰浇顕ч锝嗙鐎ｅ灚鏅濋梺鎸庣箓濡參宕?)
        db.add(decision)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村冀椤撶偟鐣烘繛瀵稿Т椤戝懏鍎梻渚€娼чˇ顓㈠磿閹惰棄鐒垫い鎺戝暙閸氬湱绱掓潏銊ユ诞鐎殿噮鍣ｅ畷鎺懶掑▎鎯у闁宠鍨块崺銉╁幢濡も偓缁犺崵绱撴笟鍥ф灓闁轰浇顕ч锝嗙鐎ｅ灚鏅濋梺鎸庣箓濡參宕? in context


@pytest.mark.asyncio
async def test_no_memories_still_works(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-3", username="ctxtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        context = await build_dynamic_context(user, db)
        # Should still have time info, just no memory section
        assert "闂備浇宕甸崰鎰垝鎼淬垺娅犳俊銈呮噹缁犱即鏌涘☉姗堟敾婵炲懐濞€閺岋絽螣濞嗘儳娈紓渚囧亜缁夊綊寮诲☉銏╂晝闁挎繂妫涢ˇ銊╂⒑? in context


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
            summary="濠电姷鏁搁崑鐐哄垂閸洖绠伴柟闂寸劍閺呮繈鏌曟径鍡樻珦闁轰礁鍟撮弻銈吤圭€ｎ偅婢掗梺绋款儐閹瑰洭骞冮挊澶嗘灁闁圭瀛╅弳鐐烘⒒娴ｉ涓茬紓鍌涙皑閸掓帒鈻庨幘铏€悗骞垮劚閹峰顭囬埡鍛骇闁割偅绋戞俊鑺ョ箾閸稑鐏叉慨濠呮閹叉挳宕熼鍌溾枏闂備焦鎮堕崹娲偂閿熺姰鈧礁顫濋懜鐢靛姸閻庡箍鍎遍幊鎰八囪濮婃椽妫冨☉杈ㄐら梺绋匡攻椤ㄥ﹤鐣烽娑氱瘈闁搞儯鍔屾禒顖炴⒑閹肩偛鍔橀柛鏂跨灱缁牓宕橀鐣屽帾闂佺硶鍓濋〃鍛村汲閿濆鐓涘ù锝呮憸瀛濋梺浼欑稻缁诲牆鐣峰鈧獮鍡氼槼婵炲懏顨堢槐鎾诲磼濮橆兘鍋撻幖浣哥獥婵娉涚粣妤呮煛閸モ晛鞋濠?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柛顐ｆ礀缁€澶愮叓閸ャ劎鈽夐柣鎺戠仛閵囧嫰骞掗崱妞惧闂備礁鎽滈崰鎰箾婵犲洤绠氬〒姘ｅ亾妞ゃ垺鐩幃娆撳级閹存繂顥夐梻鍌欑閹测€趁洪敃鍌氱；闁圭儤鍤﹂敐鍥ㄥ珰婵炴潙顑嗛～宥夋⒑閸濆嫬鏆欓柛濠冩倐閻庨攱淇婇悙顏勨偓鏍箰婵犳艾绠栭柛灞炬皑閺?,
        )
        db.add(summary)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂傚倷娴囬褍霉閻戣棄鏋侀柟闂寸閸屻劎鎲搁弬璺ㄦ殾闁挎繂顦獮銏′繆椤栨壕鎷℃繛鍙夋倐濮婅櫣鍖栭弴鐐测拤闂佸憡鍨电紞濠傜暦閻㈠憡鏅濋柛灞剧☉娴? in context
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

WEEKDAY_NAMES = ["闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶愭倵閿濆骸澧伴柛?, "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶愭倵閿濆骸澧插┑?, "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶愭倵閿濆骸澧扮紒?, "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶愭倶閻愮數鍙?, "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶愭倵閿濆骸澧插┑?, "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶屸偓鍏夊亾闁告洦鍋嗛悡?, "闂傚倸鍊风粈渚€骞夐敍鍕煓闊洦绋戠粈澶屸偓骞垮劚閹?]


async def build_dynamic_context(user: User, db: AsyncSession) -> str:
    """Build the dynamic portion of the system prompt."""
    now = datetime.now(timezone.utc)
    today = now.date()
    weekday = today.isoweekday()

    parts: list[str] = []
    parts.append(f"闂備浇宕甸崰鎰垝鎼淬垺娅犳俊銈呮噹缁犱即鏌涘☉姗堟敾婵炲懐濞€閺岋絽螣濞嗘儳娈紓渚囧亜缁夊綊寮诲☉銏╂晝闁挎繂妫涢ˇ銊╂⒑閹稿海銆掗柛鐘崇墵瀵濡搁妷銏☆潔濠电偛妫欓敋濠殿喚婀弌w.strftime('%Y-%m-%d %H:%M')}闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟瀛樼箥閻斿棝鏌￠崼娑掑亾椤ㄧ嵔DAY_NAMES[weekday - 1]}闂?)

    if user.current_semester_start:
        delta = (today - user.current_semester_start).days
        week_num = delta // 7 + 1
        parts.append(f"闂備浇宕甸崰鎰垝鎼淬垺娅犳俊銈呮噹缁犱即鏌涘☉姗堟敾婵炲懐濞€閺岋絽螣绾拌鲸姣岄梺绋款儐閹告悂鍩ユ径鎰闁兼亽鍎洪埀顒€绉撮埞鎴︽偐椤愵澀澹曢梻浣芥硶閸犳挻鎱ㄩ悽绋跨柧妞ゆ帊鐒﹂崣蹇旀叏濡炶浜剧紒缁㈠幗閹倸鐣烽弴銏犵疅闁规彃鐣秂k_num}闂?)

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

    parts.append("\n濠电姷鏁搁崑娑㈩敋椤撶喐鍙忛柟缁㈠枟閺呮繈鏌曢崼婵愭Ц濡楀懏绻濋姀锝呯厫闁告梹鐗犲畷鏇烆吋婢跺鍘遍梺鍝勬储閸斿本鏅堕鐐寸叆婵炴垶锕╁Σ铏圭磼鏉堛劌绗ч柍褜鍓ㄧ紞鍡樼閸洖纾挎繝濠傛噽绾?)
    if not courses and not tasks:
        parts.append("- 闂傚倸鍊风粈渚€骞栭锕€鐤柣妤€鐗婇崣蹇涙煙缂併垹鏋熼柛瀣ф櫊閺屾洘绻涢悙顒佺彅缂?)
    else:
        for course in courses:
            location = f" @ {course.location}" if course.location else ""
            parts.append(f"- {course.start_time}-{course.end_time} {course.name}{location}闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟杈鹃檮閸嬪鏌熸导鏉戜喊闁轰礁顑囬埀顒冾潐濞叉牕煤閵娾晜鍎楁繛鍡樻尰閸婄敻鏌ㄥ┑鍡樺櫣妞わ絽纾槐鎺楀焵?)
        for task in tasks:
            status_mark = "闂? if task.status == "completed" else "闂?
            parts.append(f"- {task.start_time}-{task.end_time} {task.title}闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟瀛樼箥閻斿棝鏌℃径瀣皨atus_mark}闂?)

    # User preferences
    preferences = user.preferences or {}
    if preferences:
        parts.append("\n闂傚倸鍊烽悞锕€顪冮崹顕呯劷闁秆勵殔缁€澶屸偓骞垮劚椤︻垶寮伴妷锔剧闁瑰瓨鐟ラ悘鈺冪棯閹岀吋闁绘搩鍋婂畷鍫曞Ω閿曗偓閽勫ジ姊虹粙娆惧剭闁告梹鍨垮?)
        if "earliest_study" in preferences:
            parts.append(f"- 闂傚倸鍊风粈渚€骞栭锔藉亱闁告劦鍠栫壕濠氭煙閸撗呭笡闁绘挻鐩弻娑㈠箛閸撲胶蓱濠电偛鎳庨幊蹇涘Φ閸曨垰绠抽柡鍌涘閻庡墽绱撴担鍓插剰闁挎洦浜獮鍐煛閸涱喗鍎銈嗗姦閸嬪懓鈪堕梻鍌氬€搁崐鎼佸磹閹间礁纾瑰ù鐘差儏缁犲灚銇勮箛鎾搭棡妞ゎ偅娲熼弻锝夊Ω閿旂懓褰弐eferences['earliest_study']}")
        if "latest_study" in preferences:
            parts.append(f"- 闂傚倸鍊风粈渚€骞栭锔藉亱闁告劦鍠栫壕濠氭煙閸撗呭笡闁绘挻鐩弻娑樷槈閸楃偞鐏曟繝銏ｎ潐钃遍柕鍥у楠炴帡寮幐搴ｂ偓鍓х磽娴ｅ壊鍎忛柨鏇ㄤ邯楠炲啴鍩￠崨顔藉劒濡炪倖鍔﹂崑鍛扳叾闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰ù鐘差儏缁犲灚銇勮箛鎾搭棡妞ゎ偅娲熼弻锝夊Ω閿旂懓褰弐eferences['latest_study']}")
        if "lunch_break" in preferences:
            parts.append(f"- 闂傚倸鍊风粈渚€骞夐敓鐘偓鍐川鐎涙ê浜遍梺鍛婁緱閸ㄩ亶锝為弴銏＄厪闁割偅绻嶅Σ褰掓煛閸滀礁澧柟渚垮妼閳规垿宕奸悢鍝ヤ紜references['lunch_break']}")
        if "min_slot_minutes" in preferences:
            parts.append(f"- 闂傚倸鍊风粈渚€骞栭锔藉亱闁告劦鍠栫壕濠氭煙閸撗呭笡闁绘挾鍠愰妵鍕箻濡も偓閸燁偆绮婚崫鍕ㄦ斀闁绘﹩鍋勬禍鐐箾閹炬潙鐒归柛瀣尵閳ь剚顔栭崳顕€宕戞繝鍌滄殾濠靛倸鎲￠崑鍕煕閹惧啿绾х悮褍鈹戦悩鍨毄闁稿鐩幃褑绠涘☉鏍ゅ亾閸岀儐鏁婇柣鎰靛墻濞肩喖姊哄Ч鍥у闁愁亞娈檈ferences['min_slot_minutes']}闂傚倸鍊风粈渚€骞夐敍鍕殰闁圭儤鍤﹀☉妯锋斀閻庯綆浜為?)
        if "school_schedule" in preferences:
            parts.append("- 闂備浇顕уù鐑藉箠閹捐绠熼柨鐔哄У閸嬪倿鏌ㄩ悢鍝勑㈤柛灞诲姂閺屾洟宕煎┑鍥х獩缂佹儳澧介崑鎾诲Φ閸曨垰绫嶉柛銉戝啯鍎紓鍌欑椤戝懘鏁冮鍫濊摕闁绘梻鈷堥弫鍥╂喐瀹ュ鍊堕柍鈺佸暕缁诲棝鏌ｉ幇顓炵祷闁逞屽墮閻忔繈锝炶箛娑欏殥闁靛牆鎷嬪Λ婊堟煟鎼搭垳绁烽柛鏂款樀瀹?)

    # Hot memories (preferences + habits) 闂?always loaded
    hot_memories = await get_hot_memories(db, user.id)
    if hot_memories:
        parts.append("\n闂傚倸鍊搁崐鎼佸磹閻㈢纾婚柟鍓х帛閻撴瑧绱掔€ｎ亞浠㈡い鎺嬪灲閺屾盯鍩℃担绯曞亾閸ф绠栭悷娆忓婵挳鎮峰▎蹇擃伀闁告埊绱曠槐鎾存媴缁涘娈梺绋匡工濞尖€愁嚕椤愩埄鍚嬪璺猴躬閸炶泛鈹戦悩缁樻锭闁硅櫕鍔欏畷婊堝Ω閿斿墽鐦堥梻鍌氱墛缁嬫垿鍩€椤掆偓缂嶅﹤鐣烽悷鎵虫斀闁割偁鍨婚悾鍫曟煟韫囨洖浠滃褌绮欓崺銏ゅ即閵忥紕鍘藉┑鈽嗗灠閹碱偊寮抽柆宥嗙厱闁哄啫鍊归弳顒勬煛鐏炶濡奸柍钘夘槸椤粓宕卞鍡忓亾閸℃瑧纾?)
        for mem in hot_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Warm memories (recent decisions/knowledge) 闂?loaded at session start
    warm_memories = await get_warm_memories(db, user.id, days=7)
    if warm_memories:
        parts.append("\n闂傚倷绀侀幖顐λ囬锕€鐤炬繝濠傜墕閸ㄥ倿鎮归搹鐟扮殤闁兼澘娼￠弻銊モ槈濡警浠炬繝娈垮灠閵堟悂寮婚埄鍐ㄧ窞閹兼番鍨婚妴濠勭磽娴ｅ搫校闁圭懓娲濠氬Ω閵夈垺顫嶅┑鈽嗗灣閸樠嚶烽埀顒佺節閻㈤潧浠﹂柟閫涚窔瀹曟椽寮借閻?濠电姷鏁告慨浼村垂瑜版帗鍊堕柛顐犲劚閻ょ偓銇勮箛鎾搭棡妞ゎ偅娲橀幈銊ノ熼崹顔惧帿闂?)
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
        parts.append(f"\n濠电姷鏁搁崑鐐哄垂閸洖绠伴柟闂寸劍閺呮繈鏌曟径鍡樻珦闁轰礁鍟撮弻銈吤圭€ｎ偅婢掗梺绋款儐閹瑰洭骞冮挊澶嗘灁闁圭瀛╅弳鐐烘⒒娴ｉ涓茬紓鍌涙皑閸掓帒鈻庨幘璺虹ウ濠德板€愰崑鎾绘懚閿濆棛绠鹃柛鈩冪懃娴滈箖鏌ｉ鐕佹疁婵﹥妞介獮鎰償閿濆倸顫屾俊鐐€栫敮鐐烘偟閻㈩暀t_summary.summary}")

    return "\n".join(parts)
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_context_loading.py -v`
Expected: All 4 tests PASS

- [x] **Step 5: Run existing context tests to verify no regression**

Run: `cd student-planner && python -m pytest tests/ -v -k "context"`
Expected: All PASS

- [x] **Step 6: Commit**

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

- [x] **Step 1: Write the failing tests**

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
            ConversationMessage(session_id="sess-1", role="user", content="闂傚倷鐒﹂惇褰掑春閸曨垰鍨傚┑鍌滎焾缁愭淇婇妶鍛櫣闁搞劌鍊圭换婵囩節閸屾粌顤€闂佺瀛╅崹鍧楀箖濡ゅ懏鏅查幖绮光偓鎰佹浇缂傚倷鑳舵慨鐢告偡閳轰緡鍤曢柛顐ｆ礀閻撴盯鏌涚仦鍓х煁闁革急鍥ㄢ拺闁荤喐婢橀弳杈ㄤ繆椤愶絿绠炴鐐叉瀹曟﹢顢欓懖鈺婃Ч婵＄偑鍊栭幐鑽ょ矙閹烘鐤鹃柣鎰劋閳锋帡鏌涚仦鎹愬闁逞屽墰椤牓顢氶敐鍥ㄥ磯濞撴凹鍨辩€靛矂姊虹粙璺ㄧ伇闁稿鍋ら崺?),
            ConversationMessage(session_id="sess-1", role="assistant", content="濠电姷鏁搁崑鐘诲箵椤忓棗绶ら柟绋垮閸欏繘鏌涢幘妤€瀚惔濠囨⒑閸濆嫮鈻夐柛妯煎帶椤斿繐鈹戠€ｎ偆鍘繝鐢靛Т缁绘ê顬婇鍓х＜?2濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鏌ユ煟閹邦剚鎯堥柣鎾达耿閺屸€愁吋鎼粹€崇闂佹娊鏀辩敮锟犲蓟濞戞ǚ鏋庨煫鍥风稻鏁堟俊鐐紖娴ｇ顏紒?),
            ConversationMessage(session_id="sess-1", role="user", content="闂傚倷鐒﹂惇褰掑春閸曨垰鍨傚┑鍌滎焾缁愭淇婇妶鍛櫣闁搞劌鍊圭换婵囩節閸屾稑娅濋梺绋款儐閹瑰洭骞冮悜鑺ョ劷闁挎柨褰ㄨ閺岋綁濮€閳轰胶浠梺鍦焾椤兘濡撮崘顔肩倞妞ゎ剦鍓涢崰鎾舵閹烘嚦鐔访虹拠鍙夋珒濠电姷鏁告慨浼村垂閻撳簶鏋栨繛鎴炴皑閻挾鈧娲栧ú銈嗘叏?),
            ConversationMessage(session_id="sess-1", role="assistant", content="闂備浇顕у锕傦綖婢舵劖鍋ら柡鍥╁С閻掑﹥绻涢崱妯诲碍闁哄绶氶弻鐔煎箲閹伴潧娈紓?濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鍙夌節婵犲倻鍚囬柛銉墮閻顭跨捄鍝勵槵闁哄鐟╁铏圭磼濮楀棛鍔告俊鐐差嚟椤牓鎮鹃悜钘夎摕闁靛濡囬崢?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_summary_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂傚倸鍊烽悞锕€顪冮崹顕呯劷闁秆勵殔缁€澶屸偓骞垮劚椤︻垶寮伴妷锔剧闁瑰瓨鐟ラ悘鈺呮煢閸愵亜鏋涢柡灞炬礃缁旂喖顢涘顒変紑闂佷紮缍€婵倗鎹㈠☉姘ｅ亾濞戞瑯鐒介柣顓烇攻娣囧﹪顢曢敐鍥ㄥ櫑闂佹寧娲忛崹铏光偓闈涖偢瀵爼骞嬪┑鍫㈠春闂傚倷绶氬褑鍣归梺閫炲苯澧寸€殿噮鍋婂畷鐔碱敍濞戞帗瀚介梻浣侯焾閺堫剟鎳濋崜褏妫憸搴㈢┍婵犲洦鍊烽柟缁樺坊閸嬫捇宕归鍛稁缂傚倷鐒﹁摫缂傚秴娲弻娑㈠箻濡も偓閹峰危閻戣姤鈷戦悹鍥у级閹癸綁鏌熼搹顐ｅ磳閽樻繈鏌熷▓鍨灍闁哄棙绮撻弻鐔煎箚瑜滈崵鐔搞亜閳哄倻鍙€闁哄本鐩崺鍕礃椤忓倵鍋撻幒鏃€鍠愰梺顓ㄧ畱閻忥箓鏌＄仦绋垮⒉闁瑰嘲鎳愰幉鎾礋椤撶偛娈ュ┑锛勫亼閸娧呯不閹存繍鍤曢柛鎾茶兌閻瑥鈹戦悩鍙夊闁稿鍔曢妴鎺戭潩閻撳海浠╅梺璇″枙缁舵艾顫忓ú顏勫窛濠电姴鍊婚悷鏌ユ煟閵忊晛鐏卞ù婊呭仜鍗?濠电姷鏁搁崑鐐哄垂閸洖绠归柍鍝勫€婚々鍙夌箾閸℃ɑ灏紒鐘崇叀閺屾洝绠涚€ｎ亖鍋撻弴鐘电焼濠㈣埖鍔栭悡鍐煢濡警妲归柛锝囨櫕缁辨帡鍩€?,
                "actions": ["闂傚倸鍊风粈渚€骞栭銈嗗仏妞ゆ劧绠戠壕鍧楁煙缂併垹娅橀柡浣割儐娣囧﹪濡堕崨顓熸闂佹椿鍘界喊宥囨崲濞戞﹩鍟呮い鏃囧吹閸戝綊姊洪幐搴ｂ姇缂佽鐗撳濠氭晸閻樿尙顦ㄩ梺闈浤涢崘顏勫箺濠?, "闂傚倸鍊烽悞锕傛儑瑜版帒鍨傚┑鐘宠壘缁愭鏌熼悧鍫熺凡闁搞劌鍊归幈銊ヮ潨閸℃瀛ｅ┑鐐茬墛椤ㄥ棙绌辨繝鍥舵晬婵犲﹤鎳庣粭鈥斥攽閻愯尙澧ｆ繛澶嬬洴閳ワ妇鎹勯妸锕€纾梺鎯х箰婢э綁鏁嶉崟顓狅紲闂佺偨鍎遍崯鍧楊敂椤愶附鐓欑€瑰嫰鍋婇崕鏃堟煕閵娾晝鐣虹€规洘锕㈤幊鐘活敄閸喗鐎?],
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
        assert "濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村箛椤掑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇? in summary.summary


@pytest.mark.asyncio
async def test_end_session_extracts_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-2", username="sesstest2", hashed_password="x")
        db.add(user)

        msgs = [
            ConversationMessage(session_id="sess-2", role="user", content="闂傚倸鍊烽懗鍫曞箠閹剧粯鍋ら柕濞炬櫅閸ㄥ倿鏌ｉ姀銏╃劸闁告垹濞€閺屽秵娼幏宀婂敼闂佸搫顑呴柊锝夊蓟閺囷紕鐤€濠电姴鍊搁埛澶愭⒑閹稿海鈽夌紒澶嬫尦閸┿儲寰勯幇顒傤啋缂備焦绋撻幊鎾村閹邦剦娓婚柕鍫濈箳閻ｈ京鈧鍠栨晶搴ｅ垝濞嗘劗绡€闁搞儯鍔屾禍褰掓⒑閸撹尙鍘涢柛瀣閸┾偓妞ゆ帒鍊告禒褏绱掓潏銊ョ瑲鐎垫澘瀚埀顒婄秵娴滅偤宕㈤幇顔剧＝濞达絼绮欓崫铏圭磼鐠囪尙澧曟い鏇秮楠炴捇骞掑┑鍥у厞婵＄偑鍊栭崝鎴﹀磹濡ゅ懎绠熸い蹇撶墛閳锋垶绻涢懠棰濆敽缂併劎绮妵鍕箣濠靛浂妫﹂悗娈垮枟閹倸鐣峰鈧、鏃堝幢濞嗘垵甯?),
            ConversationMessage(session_id="sess-2", role="assistant", content="濠电姷鏁告繛鈧繛浣冲洤纾瑰┑鐘宠壘閻ょ偓銇勯幇銊﹀櫚闁哄妫冮弻鐔告綇妤ｅ啯顎嶉梺鍝勬媼閸撶喖骞冨鈧幃娆撳级閹存繂袘闂備浇顕х换鎰八囬悽绋跨畺閻熸瑥瀚悷褰掓煃瑜滈崜鐔煎Υ閸岀偞鏅滈柛鎾楀拋妲搁梻浣规偠閸庮垶宕濇惔銊ｂ偓?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂傚倸鍊烽悞锕€顪冮崹顕呯劷闁秆勵殔缁€澶屸偓骞垮劚椤︻垶寮伴妷锔剧闁瑰鍋熼。鏌ユ煕鐎ｎ偓鑰块柡灞炬礃缁绘盯宕归纰辩€撮柣鐔哥矋婵℃悂宕楅悩鍨殌妞ゎ厹鍔戝畷姗€鍩℃繝鍐炬＇濠碉紕鍋戦崐鏍暜閻愬搫绐楅柟閭﹀枤閻瑥鈹戦悩鍙夊闁稿鍔欓弻褑绠涢敐鍛埅濠碘€虫▕閸ㄨ泛顫忔繝姘＜婵﹩鍏橀崑鎾绘偡闁妇鍔峰┑鐐叉閸旀銆呴弻銉︾厱婵炴垶锕崝鐔兼⒒?,
                "actions": [],
                "memories": [
                    {"category": "preference", "content": "闂傚倸鍊风粈渚€骞楀鍕弿闁汇垽娼ч崹婵堚偓骞垮劚椤︿粙寮崘顭嬪綊鎮╁顔煎壈缂備緡鍋勭粔褰掑蓟瀹ュ洦鍋橀柍銉ュ帠婢规洜绱撻崒娆戝妽妞ゃ劌鎳樺畷鎰版偡闁箑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇婇崣澶婄伌婵﹥妞介幊锟犲Χ閸涱剛鎹曟繝纰樻閸嬪懘鎯勯鐐存櫜闁绘劕鎼崘鈧銈嗘尵閸犳劕鈻嶉弽顓熺厽闊洦娲栨禒褔鏌涚€ｎ偅宕岄柟顔炬暬楠炴﹢寮妷锔绘綌闂備胶鎳撴晶浠嬵敆閺屻儱绀夐柣鏂挎憸缁♀偓闂侀€炲苯澧寸€规洏鍔戝鍫曞箣閻戝棙顥ら梻鍌欑劍閹爼宕曢鈧鏌ュ煛娓氬洨鍔?},
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
        assert "闂傚倸鍊峰ù鍥х暦閻㈢纾绘繛鎴烆焸濞戞ǚ妲堟い顐枤缁? in memories[0].content
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

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_session_lifecycle.py -v`
Expected: FAIL 闂?`ModuleNotFoundError: No module named 'app.agent.session_lifecycle'`

- [x] **Step 3: Implement session_lifecycle.py**

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

_EXTRACT_PROMPT = """闂傚倸鍊风粈渚€骞夐敍鍕殰闁圭儤鍤﹀☉妯锋瀻闁圭偓娼欓埀顒傛暬閺屻倝骞侀幒鎴濆Б濡炪倐鏅濋崗姗€寮婚弴鐔风窞闁割偅绺鹃崑鎾澄旈崨顔间画闂佺懓澧界划顖炲磹閻㈠憡鐓熼柕蹇婃閸熷繘鏌￠埀顒佸鐎涙鍘介梺鎸庢濞夋洟鎯屽▎鎾寸厸濞达絽鎽滃瓭闂佷紮绲剧换鍫濈暦濮椻偓椤㈡棃宕卞▎蹇婂亾閹惰姤鈷?JSON闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟杈鹃檮閸嬪鏌涘☉鍗炵仯缂佺姵鏌ㄩ…璺ㄦ崉閻戞ɑ鎷遍梺鍝ュ枎閹碱偊婀侀梺鎸庣箓濞诧箑鈻嶉弴鐘电＝闁割偅绻嶉悡濂告煛鐏炲墽娲存鐐差儏閳规垿宕堕妸銉ュ闂傚倷绀侀幉锟犳偡瑜斿畷鎴﹀箻閸撲胶鐒块梺鍦劋椤ㄥ懘宕橀埀顒勬偡濠婂啰效鐎殿噮鍋婂畷濂稿即閻斿皝鍋撻悽鍛婄厱闁挎棁顕ч獮妤併亜韫囨洖鏋旂紒杈ㄥ笚濞煎繘濡搁妷銉︽嚈闂?
{
  "summary": "濠电姷鏁搁崑鐐哄垂閸洖绠伴柟缁㈠枛绾惧鏌熼崜褏甯涢柣鎾存礃缁绘盯宕卞Δ鍐冦垽鏌涢弬璇插姦闁哄矉缍侀弫鍌滄崉閵娧呭幆婵°倗濮烽崑鎰板磻閹剧粯鈷戦柣鎾冲瘨濞肩喖鏌涙繝鍐炬當闁崇粯妫冩慨鈧柕鍫濇噽妤犲洭姊洪崘鍙夋儓闁稿﹤顭烽獮濠囧礋椤戝彞绨婚梺褰掑亰閸ㄧ増绂嶈ぐ鎺撶厓鐟滄粓宕滃☉銏犳瀬闁归棿闄嶉埀顑跨劍缁绘繈宕堕妸銉ュ⒕濠电偛顕慨鎾敄閸涱垰顥氱紓浣股戦崣蹇旀叏濡も偓濡绂嶉悙鐑樼厱闁绘柨鍤栧銉╂婢舵劖鐓熸慨妤€妫楁禍婊兠瑰鍛壕缂?,
  "actions": ["闂傚倸鍊风粈浣革耿闁秵鍋￠柟鎯版楠炪垽鏌嶉崫鍕偓褰掑级閹间焦鈷掑ù锝呮贡濠€浠嬫煕閺傝法鐏遍柍褜鍓氶崙褰掑矗閸愵喚宓侀柡宥庡幗閻撱儵鎮楅敐搴′簻妞ゅ孩鎸搁埞鎴︽偐鐠囇冧紣闂佸摜鍣ラ崑濠囧箖濡　鏋庨柟鐐綑娴?],
  "memories": [
    {"category": "preference|habit|decision|knowledge", "content": "闂傚倸鍊烽懗鍫曗€﹂崼銉︽櫇闁挎洖鍊搁崒銊ф喐韫囨挴鏋庨柕蹇嬪€栭悞鑲┾偓骞垮劚濡矂骞忚ぐ鎺撯拺闁革富鍙庨悞楣冩倵濞戞帗娅婄€规洘妞藉畷鎺楁倷閺夋垳鍖栧┑鐐存尰閸╁啴宕戦幘娣簻闁挎繂绻愰々顒傜磼鏉堚晛浠辩€规洖鐖奸、妤佹媴缁嬪灝顥夐梻鍌欑閹测€趁洪敂鐣岊洸婵炲棙鍨跺畷鏌ユ煕閳╁啰鈯曢柣?}
  ]
}

闂傚倷娴囧畷鐢稿窗閹扮増鍋￠柕澹偓閸嬫挸顫濋悡搴♀拫閻庤娲栫紞濠囥€佸☉銏″€烽悗娑櫳戦悵?- summary 闂傚倷娴囧畷鐢稿窗閹邦優娲箣閿旇棄娈戦梺鍓插亝濞叉﹢宕戦埡鍌滅瘈闂傚牊绋掗悘鈺呮煟閹寸儐鐒介柣鐔烘嚀閳规垿鎮╅幓鎺濅紑濡炪倧瀵岄崰妤冩崲濞戙垹绠ｉ柣鎰綑閻ㄦ垿姊虹粙娆惧剱闁瑰憡鎮傞崺銉﹀緞閹邦剛顔掗梺鍛婎殘閸嬫劙宕戦幘璇插嵆閹鸿櫕绂嶈ぐ鎺撶厽闁归偊鍓涙禒娑㈡倵?- memories 闂傚倸鍊风粈渚€骞夐敓鐘冲仭妞ゆ牗绋撻々鍙夌節闂堟侗鐒惧ù婊呮嚀閵嗘帒顫濋敐鍛闁诲氦顫夊ú鈺冪礊娴ｅ壊鍤曞ù鐘差儛閺佸啴鏌ㄥ┑鍡橆棡妞ゆ挸缍婂缁樻媴缁涘缍堥梺鐟版啞婵炲﹤顕ｉ妸鈺佺闁绘劕绋勭紞渚€鐛€ｎ喗鍋愰柛鎰絻楠炴垶淇婇悙顏勨偓鏍涙笟鈧弫鎾诲Ψ閳轰胶鍔﹀銈嗗坊閸嬫捇鏌涢悤浣哥仩妞ゎ厼娲╃粻娑樷槈濡⒈妲堕柣鐔哥矊闁帮綁骞冩ィ鍐╃劶鐎广儱妫涢崢閬嶆煟鎼搭垳绉靛ù婊呭仧缁粯瀵肩€涙鍘梺鍓插亝缁酣鎯屽▎蹇婃斀闁炽儱纾幗鐘绘煙瀹勭増鍣烘い锔惧閹棃鏁愰崱鈺傜稑闂傚倸鍊峰ù鍥敋閺嶎厼鍨傚┑鍌滎焾閸ㄥ倿姊洪鈧粔鎾垂閸岀偞鐓忓┑鐐靛亾濞呭棝鏌ｉ幘鍐测偓濠氬焵椤掆偓缁犲秹宕曢柆宥嗗亱婵犲﹤鍘惧ú顏呮櫜濠㈣泛顑囬崢閬嶆⒑瑜版帒浜伴柛鎾寸洴閺佸秴顓兼径瀣幗?- 濠电姷鏁搁崑鐐哄垂閸洖绠伴柛婵勫劤閻捇鏌ｉ幋婵愭綗闁逞屽墮閹虫﹢寮崘顔肩＜婵﹢纭搁崬娲⒒娓氣偓濞佳団€﹂銏♀挃闁告洦鍨遍崐鍨归悩宸剱闁绘挶鍎茬换娑㈠箣閻戝棛鍔锋繝鈷€浣哥伈闁哄备鍓濋幏鍛存濞戞帒浜炬繝闈涱儑瀹撲線鎮楅敐搴℃灍闁稿浜濋妵鍕冀閻㈤潧鍩屽┑?闂傚倸鍊烽懗鍫曞箠閹剧粯鍋ら柕濞炬櫅閸ㄥ倿鏌涢锝嗙婵鐓￠弻锝夊籍閸ャ儮鍋撻埀顒勬煕鐎ｎ偅灏柍钘夘槸閻ｇ兘宕堕埡鍐炊缂傚倸鍊烽悞锕傘€冮崨姝ゅ洭骞嶉鍓у?闂傚倸鍊烽悞锕傚礈濮樿泛纾婚柛娑卞灡閺嗘粓鏌ｉ弮鍌楁嫛闁轰礁锕弻娑㈠Ψ椤旇崵鏆楁繛瀛樼矊缂嶅﹪寮婚敓鐘茬倞闁哄牏鏁搁弫鏍旈悩闈涗杭闁搞劋绮欏濠氭晲婢舵稓绋忓銈嗗坊閸嬫挸鈹戦垾鑼煓闁哄本鐩崺锟犲磼濠婂嫬鍨遍梻浣侯攰濞呮洟骞戦崶褏鏆︽俊顖涱儥濡查箖姊?0闂傚倸鍊风粈渚€骞夐敍鍕殰闁圭儤鍤﹀☉妯兼殕闁告洦鍋嗛弻鍫ユ煟鎼搭垳绉甸柛瀣閸┿垽寮崒妤€浜炬鐐茬仢閸旀碍淇婇锝庢疁闁硅櫕鐟ㄩ妵鎰板箳閹捐泛骞愰梻浣侯焾鐞氼偊宕愰弴鐑嗗殨閻犳亽鍔庣壕?- 濠电姷鏁搁崑鐐哄垂閸洖绠伴柟闂寸劍閸嬨倝鏌曟繛鍨姶婵炴挸顭烽弻娑樼暆閳ь剟宕戝☉姘变笉闁瑰濮甸崰鎰版倶閻愭彃鈷旈柍鐟扮Т閳规垿鎮╅崣澶嬫倷缂備胶濮电敮妤呭Φ閸曨垰鍐€闁靛ě鍕珮闂備浇宕甸崰鎰崲閸儱绠栭悷娆忓婵绱掔€ｎ厽纭堕柣鈺佹捣缁?濠电姷鏁搁崑娑㈩敋椤撶喐鍙忛柟缁㈠枟閺呮繈鏌曢崼婵愭Ц濡楀懏绻濋姀锝嗙【妞ゆ垵娲崺銏ゅ籍閸屾浜炬鐐茬仢閸旀碍淇婇锝庢疁鐎规洏鍨介獮鎺懳旀担绯曞亾閸偆绠鹃柟瀛樼箘閿涘秶绱掓潏銊ヮ棆缂?闂?- 濠电姷鏁告慨鐑姐€傛禒瀣劦妞ゆ巻鍋撻柛鐔锋健閸┾偓妞ゆ巻鍋撶紓宥咃躬楠炲啫螣鐠囪尙绐炴繝鐢靛仧閸嬫捇鎮￠姀銈嗏拺闁哄倶鍎插▍鍛存煕閻曚礁鐏ｇ紒顔碱煼楠炴帒螖娴ｅ搫骞堝┑鐘垫暩婵鈧凹鍓涢弫顕€宕滄担铏癸紲闂佽鍨堕。锕傚触椤愶附鐓欑€瑰嫰鍋婇崕鎰版煥濞戞瑥濮堥柟宄版嚇閹煎綊宕滈幇鈺佲偓婵嗩潖閸濆嫅褔宕惰椤牓鏌ｆ惔銏犲毈濞存粍绻勭划姘綇閵娧呯槇闂佹悶鍎滈崨顖涙濠碉紕鍋戦崐鏍偋閹捐纾规俊銈呭暟閻棗鈹戞径灞讳粡mories 濠电姷鏁搁崑鐐哄垂閸洖绠插ù锝囩《閺嬪秹鏌ㄥ┑鍡╂Ц闁绘挻锕㈤弻鈥愁吋鎼粹€崇闂佸搫顑勭欢姘跺蓟閻斿皝鏋旈柛顭戝枟閻忔捇姊?""


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

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_session_lifecycle.py -v`
Expected: All 4 tests PASS

- [x] **Step 5: Commit**

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

- [x] **Step 1: Add session timeout config**

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

- [x] **Step 2: Modify chat.py to call end_session on disconnect**

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
                            user_answer = user_response.get("answer", "缂傚倸鍊烽懗鍫曟惞鎼淬劌鐭楅幖娣妼缁愭绻涢幋娆忕労闁?)
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

Add the following under the `### 闂備浇顕у锕傦綖婢舵劕绠栭柛顐ｆ礀绾惧潡姊洪鈧粔鎾儗濡ゅ懏鐓欑紒瀣仢椤掋垹鈹戦娑欏唉闁诡喖缍婇獮渚€骞掗幋婵愮€撮梻浣告惈濡宕?section in `Agent.md`:

```markdown
- recall_memory闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟鐑橆殕閸ゅ矂鏌涢幘妤€鎳愰ˇ顖炴煟鎼搭垳绉甸柛鐘愁殜钘熼柛鈩冪⊕閻撳啰鎲稿鍫濈婵炴垯鍨圭粻鐔兼煟濡も偓閻楀﹥鍒婇幘顔界厱婵炴垶锕崝鐔搞亜閿斿搫鍔︽俊顐㈡嚇椤㈡洟濮€閳╁啯鍊锋繝纰樻閸嬪懘鎯勯姘煎殨妞ゆ劧绠戝洿婵犮垼娉涢敃锕傤敇濞差亝鈷戦柣鎰靛墲婢规﹢鏌涙繝鍌ょ吋妞ゃ垺锚鐓ゆい蹇撴噽閸橀亶姊虹憴鍕姢缁剧虎鍙€閸婂瓨绻濋悽闈涗粶闁绘锕畷褰掑垂椤旂偓娈鹃梺纭呮彧缁插潡鎮块埀顒勬⒑鐟欏嫬鍔ょ€规洦鍓氱粋鎺懨洪鍛嫼闂傚倸鐗婄粙鎺椝夊▎鎰箚闁绘劖娼欑粭褏鈧鍟崶褏顦板銈嗙墬濮樸劑鎮鹃幆褜娓婚柕鍫濇婢ь剛绱掔€ｎ偄鐏撮柟顔矫灃闁告侗鍠氶崢閬嶆⒑瑜版帒浜伴柛鎾寸洴閺佸秴顓兼径瀣幗闁圭儤濞婂畷鏇㈡濞戝崬娈ㄥ銈嗘磵閸嬫挾鈧鍠氶弫璇参涢崘銊㈡闁圭儤鎸鹃埀顒€銈稿缁樻媴鐟欏嫨浠у┑鐐靛帶濞尖€崇暦濠靛洨绡€闁搞儜鍛Е婵＄偑鍊栧濠氬磻閹剧粯鐓曞┑鐘叉祩濡垹绱掗鍛箺鐎垫澘瀚禒锕傚箚瑜庡В鍥р攽閻愯埖褰х紒鑼舵閿曘垽宕￠悙宥忕秮婵℃悂鏁傞崜褜鍟庨梻浣虹《閳ь剙纾粻姘舵煕鐎ｎ偅宕屾鐐叉处閹峰懘宕ㄦ繝搴℃櫊闂傚倷娴囧畷鍨叏閺夋嚚娲晜閻愵剙搴婇梺鍓插亖閸庤京绮堥崒娑楃箚妞ゆ牗鑹鹃幃鎴︽倵濮樼厧澧撮柡灞剧洴楠炲洭宕楅崫銉ュ毈闂備礁鎼Λ妤冩崲濮椻偓瀵濡搁妷銏☆潔濠碘槅鍨伴悘婵嬵敂椤撱垺鍋℃繝濠傚鎯熼梺鎼炲劀閸曨偆銈堕梻鍌欑窔濞佳嗗櫣闂侀€炲苯澧撮柛鈹惧亾濡炪倖甯婄欢锟犳倿娴犲鐓冪憸婊堝礈濞嗗骏鑰块梺顒€绉寸壕濠氭煏閸繃鍣烽柍褜鍓氱敮鈥崇暦濠婂嫭濯撮柣鐔哄濮ｅ洤鈹戦悙鑸靛涧缂佹彃娼￠垾锕傚醇閵夈儵鏁滄繝鐢靛Т濞诧箓鎮￠弴鐔虹闁糕剝锚缁楁帞绱掗幉瀣暠閼挎劙鏌涢妷鎴濈Х閸氼偄螖閻橀潧浠掔紒鑸靛哺閵嗕礁鈽夊Ο閿嬵潔濠电偛妫欒摫鐞氀勭節閻㈤潧浠╅柟娲讳簽缁辩偤鍩€椤掍胶绠惧璺侯儐缁€瀣偓?- save_memory闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟鐑橆殕閸ゅ矂鏌熺憴鍕濞存粌婀遍幉鍛婃償閿濆洨鐓旈梺鍛婎殘閸嬫劙寮ㄦ禒瀣厱闁斥晛鍟伴幊鍕煙閹绘帇鍋㈡慨濠傛惈鐓ょ紓浣姑埢蹇涙⒑閸涘﹥鐓ョ紒澶屾嚀閻ｇ兘宕崟銊︻潔闂侀潧绻掓慨鏉戭嚕閻戣姤鐓欓柤鍦瑜把呯磼閸欏銇濋柛鈹惧亾濡炪倖甯婄欢锟犳倿娴犲鐓欐い鏃囶嚙瀹撳棗鈹戦埄鍐╁€愬┑鈩冩倐閺佸啴鍩€椤掆偓閳藉顦规慨濠傛惈鏁堥柛銉戝喚鐎抽梺璇插閸戣绂嶅┑鍫㈢煔閺夊牄鍔庣弧鈧梺鎼炲劀閸涱垱娈哄┑锛勫亼閸婃牠鎮ч幘璇茬９婵°倕鍟伴惌鍡楊熆鐠哄彿鍫澪ｉ崼銉︾厵闁诡垎鍜冪礊闁哥喓顭堥—鍐Χ閸屾稒鐝ㄧ紓浣哄У閹瑰洭鎮伴鈧獮鎺懳旈埀顒佸劔闂備焦瀵у濠氬疾椤愶箑绀夐柣鎴ｅГ閳锋垿姊婚崼鐔衡姇妞ゃ儲绮撻弻娑欑節閸ヨ埖顥栭梺鐟扮畭閸ㄥ綊锝炲┑瀣濞达綁鏅叉竟鏇炩攽閻愭潙鐏︽い蹇ｄ邯椤㈡棃宕ㄩ鐣屽娇闂備胶绮…鍫濃枍閿濆鍋柍褜鍓熷娲川婵犲嫧濮囬梺浼欑秵娴滎亪宕洪埀顒併亜閹哄棗浜剧紓浣虹帛閿氶柣锝呭槻铻栭柛娑卞弮閸炲爼姊洪棃娑氱畾闁告挻绻傞埢?ask_user 缂傚倸鍊烽懗鍫曟惞鎼淬劌鐭楅幖娣妼缁愭绻涢幋娆忕労闁轰礁娲ら埞鎴︽偐瀹曞浂鏆￠梺?闂傚倸鍊烽懗鍫曞箠閹剧粯鍋ら柕濞炬櫅閸ㄥ倸鈹戦崒姘棌闁轰礁锕弻娑㈠Ψ閿濆懎顬夋繝娈垮灡閹告娊鎮￠锕€鐐婄憸搴ㄥ箲閿濆鐓曢柣鏂垮殩闊剟鏌＄仦璇插闁宠棄顦埢搴ㄥ箣閻愭潙鏆梻鍌氬€风粈渚€骞夐敓鐘茬闁哄洢鍨圭粻鐘诲箹閹碱厾鍘涢柡浣革躬閺岀喖顢楅崟顓犳毇闂佸搫鏈ú鐔风暦閸楃倣鏃堝焵椤掑嫬鐒垫い鎺嶇劍閸婃劖銇勯姀鈥冲摵妞ゃ垺宀搁崺鈧い鎺嗗亾闁伙絿鍏樻俊鐑藉Ψ鎼淬垺鈷掗柍褜鍓ㄧ紞鍡涘礈濞嗘挸绠?
  - preference闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟鐑樺焾濞尖晠鏌曟繛鐐珔闁哄绶氶弻鏇㈠醇濠垫劖笑缂備胶濯寸徊鍧楀焵椤掑倹鍤€閻庢矮鍗抽妴鍌炴晝閸屾稑鈧灝鈹戦悩鎻掆偓鐢稿绩娴犲鐓曢悘鐐插⒔閳洟鏌ｈ箛锝呮灓缂?闂傚倸鍊烽懗鍫曞箠閹剧粯鍋ら柕濞炬櫅閸ㄥ倿鏌ｉ姀銏╃劸闁告垹濞€閺屽秵娼幏宀婂敼闂佸搫顑呴柊锝夊蓟閺囷紕鐤€濠电姴鍊搁埛澶愭⒑閹稿海鈽夌紒澶嬫尦閸┿儲寰勯幇顒傤啋缂備焦绋撻幊鎾村閹邦剦娓婚柕鍫濈箳閻ｈ京鈧鍠栨晶搴ｅ垝濞嗘劗绡€闁搞儯鍔屾禍褰掓⒑閹勭闁稿鎳橀、娆忣吋婢跺鍘?闂?  - habit闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟鐑橆殕閸ゅ苯螖閿濆懎鏋ら柡浣告閺岋綁寮幐搴㈠枑闂佸磭绮ú鐔煎蓟閿濆憘鐔稿緞缁嬫寧鍎撻梻浣风串缁犳垿鏌婇敐澶婅摕闁绘梻鈷堥弫宥夋煥濠靛棙鍣藉ù鐓庣墢缁?闂傚倸鍊烽懗鍫曞箠閹剧粯鍋ら柕濞炬櫅閸ㄥ倻鈧娲栧ú銊╁础濮樿埖鐓涘璺侯儏閻忓秹鏌＄€ｎ亪鍙勯柡灞界Ч閸┾剝鎷呴崨濠冾唹濠电偛顕慨鐢告晪濡炪値鍘煎锟犲箠濠婂牊顥堟繛鎴炆戦幊娆愮節閻㈤潧浠滄い褉鍋撻梻鍌氬鐎氼喚鍒?闂傚倷娴囬褏鎹㈤幇顔藉床闁归偊鍠楀畷鏌ユ煙鐎涙绠ユ繛?闂?  - decision闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟鐑樺灩閺嗗棝鏌熼梻瀵割槮闂傚偆鍨堕弻娑樷攽閸曨偄濮曢梺鍝ュ枎閹碱偊婀侀梺鎸庣箓濞村倿鎮炴ィ鍐╃厸閻庯急鍐у缂傚倸鍊搁崐鐑芥倿閿斿墽鐭欓柟鐑橆殕閸嬪銇勯幘璺盒ｆい?濠电姴鐥夐弶搴撳亾閺囥垹纾圭痪顓炴噺閹冲矂姊绘担鍛婃儓婵☆偅鐩畷浼村冀椤撶偟鐣烘繛瀵稿Т椤戝懏鍎梻渚€娼чˇ顓㈠磿閹惰棄鐒垫い鎺戝暙閸氬湱绱掓潏銊ユ诞鐎殿噮鍣ｅ畷鎺懶掑▎鎯у闁宠鍨块崺銉╁幢濡も偓缁犺崵绱撴笟鍥ф灓闁轰浇顕ч锝嗙鐎ｅ灚鏅濋梺鎸庣箓濡參宕?闂?  - knowledge闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟鐑樻尵閳瑰秵绻涘顔绘喚闁轰礁顑囬埀顒冾潐濞叉牕煤閵娾晜鍎楁繛鍡樻尰閸婄敻鏌ㄥ┑鍡涱€楃€殿噣绠栭弻娑橆潩椤掍礁鏋犻梺鍝勭焿缂嶄線銆佸Ο渚叆闁告劑鍔屽暩缂?闂傚倸鍊烽悞锕€顪冮崹顕呯劷闁秆勵殔缁€澶屸偓骞垮劚椤︻垶寮伴妷锔剧闁瑰鍋熼。鏌ユ煕閻樺弶顥滄い顓℃硶閹瑰嫰鎮弶鎴濐潬缂傚倷娴囬濠囨倿閿曞倸绠為柕濞炬櫅缁犳娊鏌熺€涙濡囬柛瀣尵閹风姴顔忛鍏兼珚闂備礁鍚嬬粊鎾疾濠婂嫬鍨斿┑鍌氭啞閻撶喖鏌熺€电鈧牠骞嬮悙娈挎祫濠殿喗銇涢崑鎾存叏?闂?- 濠电姷鏁搁崑鐐哄垂閸洖绠伴柛婵勫劤閻捇鏌ｉ幋婵愭綗闁逞屽墮閹虫﹢寮崒鐐村仼閻忕偛鎲￠弫鍨節閻㈤潧鈻堟繛浣冲吘娑樷槈閵忕姷顔戦梺缁樕戠粊鏉懳ｉ崼銉︾厵闁诡垎鍜冪礊闂佸湱鏅慨鍨┍婵犲洦鍊烽柟缁樺坊閸嬫捇宕稿Δ鍐ㄧウ闂侀€炲苯澧伴柟鎻掓憸娴狅箓宕滆閺€铏節閻㈤潧孝婵炲眰鍊楃划濠氬箳閹惧彉绨婚梺鍝勭Р閸庨亶鍩€椤掍緡娈樼紒?濠电姷鏁搁崑娑㈩敋椤撶喐鍙忛柟缁㈠枟閺呮繈鏌曢崼婵愭Ц濡楀懏绻濋姀锝嗙【妞ゆ垵娲崺銏ゅ籍閸屾浜炬鐐茬仢閸旀碍淇婇锝庢疁鐎规洏鍨介獮鎺懳旀担绯曞亾閸偆绠鹃柟瀛樼箘閿涘秶绱掓潏銊ヮ棆缂?闂?- 濠电姷鏁搁崑鐐哄垂閸洖绠伴柛婵勫劤閻捇鏌ｉ幋婵愭綗闁逞屽墮閹虫﹢寮崒鐐村仼閻忕偛鎲￠弫鍨節閻㈤潧鈻堟繛浣冲吘娑樷槈閵忕姷顔戦梺缁橆焽椤ｄ粙宕戦幘鑸靛枂闁告洦鍘介幉娆撴煟韫囨挾绠查柣鐔濆洤绀嗛柟鐑橆殕閺呮悂鏌ｅΟ鍝勭骇鐎规挸绉瑰娲濞戣京鍙氶梻鍌氬鐎氼剟鍩㈤幘璇查唶闁哄洨鍠撻崢鐢告煟閻樺弶绀岄柍褜鍓濆▍鏇㈡倶閸垻纾藉ù锝夋涧婵偓婵＄偞娼欓幗婊呭垝濞嗘劕绶為柟鏉跨仛閺咃綁姊虹紒妯忣亞澹曢銏犳辈闁绘ê纾粻楣冩煥濠靛棙鍣虹紒鈧畝鍕厱闁规儳顕粻鏍倵闂堟稏鍋㈢€规洏鍔庨埀顒佺⊕钃辨繛鍛墵濮婃椽宕滈幓鎺嶅缂傚倸绉村Λ婵嗙暦閻㈠憡鏅滈柛鎾楀拑绱查梺璇插嚱缂嶅棙绂嶉崼鏇炵？鐎广儱顦伴悡鍐喐濠婂牆绀傛繛鎴烇供濞撳鏌熼悜姗嗘當缂佺姵鐓￠弻鏇＄疀鐎ｎ亖鍋撻弴鐘电焼濠㈣埖鍔曠粻鎶芥煙閹増顥夐柣鎺戠仛閵囧嫰骞嬮悙宸殝缂備椒妞掗崡鎶藉蓟瀹ュ牜妾ㄩ梺鍛婃尰閻熲晛鐣烽鐐茬闁兼亽鍎遍崜銊ヮ渻閵堝棛澧遍柛瀣仱瀵?- 闂備浇宕甸崰鎰垝鎼淬垺娅犳俊銈呮噹缁犳澘螖閿濆懎鏆欓柡瀣╃窔閺屾洟宕煎┑鎰︾紓浣哄缂嶄線寮婚敐澶娢ч幖杈剧磿娴煎洭姊?闂傚倸鍊搁…顒勫磻閸曨個娲晝娴ｈ鍣烽梻浣圭湽閸╁嫰宕归鍫濈；闁瑰吋鐛皒"闂傚倸鍊风粈渚€骞栭锕€鐤柟鍓佺摂閺佸﹪鏌熼柇锕€鏋熸い顐ｆ礃缁绘繈妫冨☉鍗炲壉闂?recall_memory 闂傚倸鍊烽懗鍫曞箠閹剧粯鍊舵慨妯挎硾绾惧潡鏌熼幆鐗堫棄闁哄嫨鍎抽埀顒€鍘滈崑鎾绘煃瑜滈崜鐔煎春閳ь剚銇勯幒鎴濃偓褰掑汲閳哄懏鐓欓柧蹇ｅ亝鐏忕敻鏌ゅú顏冩喚闁瑰磭濞€椤㈡鎷呴崜娴嬪亾濞戙垺鈷戦柛婵嗗濡插吋绻涙径瀣缂侇喖顭烽獮妯肩磼濡厧寮虫繝鐢靛仦閸ㄥ爼鈥﹂崶顒佸€堕梺顒€绉甸悡鏇㈡煛閸屾粌浠滄繛灞傚€楅幉鎾晝閸屾氨顔愮紓渚囧枤閹虫挻鏅堕弻銉︾厱闁绘柨鎼禒閬嶆煛瀹€瀣М妞ゃ垺锚椤劑宕橀妸銉愭垿姊绘担鑺ャ€冮梻鍕Ч瀹曟劕鈹戠€ｎ剙绁﹂柣搴秵娴滅偤寮崇€ｎ喗鐓涘璺猴功娴犮垺绻涢崼娑樺姦婵﹥妞藉畷銊︾節閸屾粠鍎屽┑鐘垫暩閸嬫劙宕戦幘鏂ユ斀?```

- [ ] **Step 2: Add few-shot example for memory**

Add the following as a new example after existing examples in `Agent.md`:

```markdown
### 缂傚倸鍊搁崐椋庢媼閺屻儱纾婚柟鎹愵嚙缁狙囨煟閹邦厽缍戞い銉ヮ儏闇?闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟鐑樻尵閳瑰秵绻涘顔绘喚闁轰礁锕弻娑㈠Ψ椤旇崵鏁栭梺姹囧€愰崑鎾绘⒒娴ｈ櫣銆婇柛鎾寸箞閹兘顢涢悙鑼缎曢梺閫炲苯澧存慨?
闂傚倸鍊烽悞锕€顪冮崹顕呯劷闁秆勵殔缁€澶屸偓骞垮劚椤︻垶寮? "闂傚倸鍊烽懗鍫曞箠閹剧粯鍋ら柕濞炬櫅閸ㄥ倸霉閿濆懎鏆斿ù婊冪秺閺屾稑鐣濋埀顒勫磻閻愬搫纾绘繝闈涱儐閻撶喐淇婇妶鍌氫壕闂佺粯顨呴敃顏堝箖閻㈢绠婚柡鍌樺劜椤秹姊洪悷鏉库挃妞ゆ帗褰冮蹇涘Ψ閿旇桨绨婚梺鎸庢磵閸嬫挾鈧鍠栨晶搴ｅ垝濞嗘劗绡€闁搞儯鍔屾禍褰掓⒑閹勭闁稿鎳橀幃鐢告晸閻樻枼鎷虹紓鍌欑劍椤洭鎯屾繝鍐閻犲泧鍛殸闁绘挶鍊濋弻鐔虹矙閸喚妲板┑鐐茬墛椤ㄥ棝骞堥妸銉庢棃鍩€椤掑嫭鍋嬮煫鍥ㄦ礈閻棗顭跨捄琛″鐟滅増甯楅崑鎰亜閺冨倸甯跺┑顔奸叄濮婅櫣鎷犻垾铏亶濡炪們鍔岄悧鎾愁嚕椤愶富鏁嬮柍褜鍓熼妴浣糕枎閹炬潙鐧勬繝銏ｆ硾婵傛棃宕欐禒瀣拻濞达絼璀﹂弨鐗堢箾婢跺娲撮柡浣稿暣婵¤埖绔熼敃鈧ú顓炵暦閿濆棗绶為悘鐐叉啞閻忓棝姊绘担铏瑰笡妞ゎ厼鐗撻、姘愁樄鐎规洏鍨介獮姗€顢欓挊澶嗗亾閻㈠憡鐓熼柣鏃傚帶娴滅増淇婇幓鎺旂Ш闁诡喕绮欓、娑樷槈濞嗗繒锛撻柣搴ゎ潐濞叉粓宕楀Ο璁崇箚闁归棿鐒﹂弲婊堟煟閿濆懓瀚扮紒鑼帶閳规垿鎮欓弶鎴犱桓闂佺懓鎲￠幃鍌炲极閸愵喖围濠㈣泛锕﹂悾?

闂?save_memory(category="preference", content="闂傚倸鍊风粈渚€骞栭锕€绠犻煫鍥ㄧ⊕閸庢銇勯弬鍨挃缂佺姵妫冮弻娑氫沪閸撗€妲堢紓浣稿閸嬬喖鍩€椤掆偓缁犲秹宕曟潏鈹惧亾濮樼厧娅嶉柟顖欑劍閹棃濡搁敂鎯у箰濠电偠鎻徊浠嬪箺濠婂嫭娅犻柕蹇婃噰閸嬫捇宕烽褏鍔搁梺闈涚墢椤牓顢氶敐澶婄妞ゆ棁鍋愰鎺戭渻閵堝棙鈷愰柛搴㈠▕閹峰繒鈧綆鍠楅埛鎴︽煙缁嬫寧鎹ｉ柍钘夘樀閺屻倕煤鐠囪尙浠紓浣稿€哥粔鐟扮暦閵婏妇绡€闁告洦鍨遍宥夋⒒娴ｇ鎮戝ù婊€绮欏畷鏇㈠蓟閵夛箑浠ч梺鐟板⒔缁垶鍩涢幒妤佺厱閻忕偛澧介埊鏇犵磽瀹ュ棗鐏撮柡宀嬬秮閺佹劙宕橀妸銉綆婵°倗濮烽崑鐐垫暜閿熺姷宓侀柟鐑橆殔缁狅絾銇勯幘璺烘櫩闁冲搫鍊荤粻?)
闂?濠电姷鏁搁崑鐘诲箵椤忓棗绶ら柦妯猴級濞戞鏃堝川椤撶偛浜舵繝鐢靛仦閸ㄥ墎鍠婂澶婄婵犲﹤瀚ㄦ禍婊堟煛閸愶絽浜惧銈嗗灦閻熲晛鐣烽妷鈺佺倞妞ゆ帊鑳堕崣鍡椻攽閻愭潙鐏﹂柣鐔濆洤绠烘い銈囶劖_user(type="confirm", question="闂傚倸鍊烽懗鍫曞箠閹剧粯鍋ら柕濞炬櫅閸ㄥ倸鈹戦崒姘棌闁轰礁锕弻娑㈠Ψ閿濆懎顬夋繝娈垮灡閹告娊鎮￠锕€鐐婄憸搴ㄥ箲閿濆鐓曢柣鏂垮殩闊剟鏌＄仦璇插闁宠棄顦埢搴ㄥ箣閻樻彃缍嗙紓鍌氬€搁崐鍝ョ矓閻㈠憡鏅濋柕蹇曞閸ゆ洟鏌熺紒妯轰刊婵炲皷鏅滈妵鍕箛閳轰讲鍋撳Δ鍛疅妞ゅ繐鎳愮弧鈧梺闈涢獜缁插墽娑甸崜褏纾煎璺猴功閿涘秶鈧鍟崶褏顦板銈嗙墬绾板秹鎮楅鍕拺闁告挻褰冩禍鏍煕閵娿儳绉洪柟宕囧仱楠炲酣鎳為妷褍骞愰梻浣规偠閸庮垶宕濆鍥︾剨闁挎洖鍊归悡鐔哥節閸偄濮囨繛鍛Ч閺屸剝鎷呴崫銉愩倕霉閻欏懐鐣垫慨濠呭吹閳ь剙鐏氶幃鍌炴倵濞差亝鈷掑ù锝呮啞閸熺偤鏌ら悷鏉库挃闁兼椽浜堕幊鏍煛閸屻倖缍楁俊鐐€栭幐鍫曞垂閸︻厾鐭嗛柛宀€鍋為悡鏇熴亜閹板墎鎮肩紒鐘筹耿閺岋繝宕卞Ο娲绘闂佸搫鐬奸崰鏍箖濠婂吘鐔兼惞閸︻厽鍤冨┑鐘垫暩閸嬫盯骞婃惔锝傚亾濮橆厽绶叉い顐㈢箲缁绘繂顫濋鍌炵崜闂備浇顫夐幆宀勫储閹存帞鏄傚┑鐘垫暩閸嬬偤宕圭捄渚綎缂備焦蓱閸欏繐霉閸忓吋缍戦柣鎺戠仛閵囧嫰骞掗崱妞惧闂備胶顭堥敃銉╁箖閸岀偑鈧礁顫濇０婵囨櫔闂侀€炲苯澧柣锝囧厴婵＄兘濡锋惔銏♀拻闁逞屽墾缂嶅棝宕滃▎鎾崇畾?)
闂?闂傚倸鍊烽悞锕€顪冮崹顕呯劷闁秆勵殔缁€澶屸偓骞垮劚椤︻垶寮伴妷锔剧闁瑰鍋熼。鏌ユ煕韫囨梻鐭嬮柕鍥у瀵噣鍩€椤掑嫷鏁勬繛鍡樻尭鐟?闂?save_memory
闂?闂傚倸鍊烽悞锕傚箖閸洖纾块柟鎯版绾剧粯绻涢幋鏃€鍤? "濠电姷鏁告繛鈧繛浣冲洤纾瑰┑鐘宠壘閻ょ偓銇勯幇銊﹀櫚闁哄妫冮弻鐔告綇妤ｅ啯顎嶉梺鍝勬媼閸撶喖骞冨鈧幃娆撴嚋濞堟寧顥夐梻浣规偠閸婃牜鏁敓鐘茬畺閻熸瑥瀚悷褰掓煃瑜滈崜鐔煎Υ閸岀偞鏅滈柛鎾楀拋妲搁梻浣规偠閸庢椽宕滃▎鎺旂闂傚倷鑳堕…鍫ュ嫉椤掑嫭鍋￠柕鍫濇穿婵啿霉閻撳海鎽犻柣鎾存礃閹便劌顫滈崱妤€顫梺鍦缂嶄線寮婚埄鍐╁閻熸瑥瀚壕鍐参旈悩闈涗粶妞ゆ垵顦甸悰顕€宕堕澶嬫櫌婵犮垼娉涢悷鈺呭煛閸屾粎顔曢梺鐟邦嚟閸嬬偤鍩涢幒鎴旀斀妞ゆ洍鍋撶紒鐘崇墵閵嗕礁顫滈埀顒勭嵁閺嶃劍濯撮柛婵勫労濡叉挳姊绘担鍛婅础闁稿簺鍊濋獮鎰節濮ｇ娲╅ˇ鏌ユ婢舵劖鐓曢煫鍥ㄨ壘娴滃綊鏌ｉ幙鍐ㄧ仯缂佽鲸甯楅～鎴﹀冀瑜嶇猾宥夋倵鐟欏嫭绀冩い銊ワ工閻ｇ兘鎮℃惔妯绘杸闂佸壊鍋嗛崰鎰邦敇妤ｅ啯鈷掑ù锝呮啞鐠愶繝鏌涙惔娑樷偓妤呭极椤斿槈鏃堝焵椤掑嫬鐓濈€广儱顦粈瀣亜閺嶃劎鈻撻柟宄邦煼閺岋絾鎯旈姀鈶╁闁藉啳椴搁妵鍕唩闁告洦鍘鹃鏇㈡⒑閸撴彃浜栭柛銊潐缁傛帡顢涢悙瀵稿帗?

闂傚倸鍊烽悞锕€顪冮崹顕呯劷闁秆勵殔缁€澶屸偓骞垮劚椤︻垶寮? "闂傚倸鍊搁…顒勫磻閸曨個娲晝娴ｈ鍣烽梻浣圭湽閸╁嫰宕归鍫濈；闁规儳顕粻楣冩煙鐎电浠﹂柣鎾卞劜閵囧嫰骞嬪┑鍥ф闂佸搫鎳庨悥濂稿箖閳哄懎鍨傛い鎰╁灮瑜版挳姊虹拠鏌ュ弰婵炰匠鍥х疅闁跨喓濮甸崑鈺呮⒑椤掆偓缁夌敻鎮″☉銏＄厱闁规澘澧庣粙缁樼箾閸涱厼鏆熺紒杈ㄥ笒铻栭柍褜鍓熷畷鎰版偡闁箑娈梺鍛婃处閸嬫帡宕ョ€ｎ喗鐓曢柡鍥ュ妼楠炴ɑ淇婇崣澶婄伌婵﹦鍎ゅ顏堝箥椤旂厧顬夋繝鐢靛О閸ㄦ椽鏁冮姀銈冣偓?

闂?recall_memory(query="闂傚倸鍊风粈渚€骞栭锕€鐤柣妯款嚙閻ょ偓绻涢崱妯虹仼缂佺姵妫冮弻娑氫沪閸撗€妲堢紓浣稿閸嬬喖鍩€椤掆偓缁犲秹宕曟潏鈹惧亾濮樼厧娅嶉柟顖欑劍閹棃濡搁敂鎯у箰濠电偠鎻紞鈧い顐㈩槺濞嗐垽宕ｆ径鍫滅盎?)
闂?闂傚倸鍊烽懗鍫曞箠閹剧粯鍊舵慨妯挎硾绾惧潡鏌熼幆鐗堫棄闁哄嫨鍎抽埀顒€鍘滈崑鎾绘煃瑜滈崜鐔肩嵁韫囨洍鍋撻敐搴℃灈缂佺嫏鍥ㄥ仯闁诡厽甯掓俊鍧楁煟?闂?闂傚倸鍊风粈渚€骞夐敍鍕殰闁绘劕顕粻楣冩煃瑜滈崜姘辨崲?闂?闂傚倸鍊烽悞锕傚箖閸洖纾块柟鎯版绾剧粯绻涢幋鏃€鍤? "闂備浇顕уù鐑藉箠閹捐绠熼梽鍥Φ閹版澘绀冩い鏃傚帶閻庮參鎮峰鍛暭閻㈩垱顨婇崺娑㈠籍閸喓鍘梺鍓插亝缁诲嫭鏅堕姀銏㈢＜闁绘灏欑粔娲煛鐏炵澧茬紒鏃傚枎閳瑰啴宕归鐟颁壕闁靛牆顦懜褰掓煕椤愶絾绀堥柛娆愭崌閺屾盯濡烽幋婵嗩伌婵☆偅鍨垮?
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
        {"role": "user", "content": "濠电姷鏁搁崑鐘诲箵椤忓棗绶ら柟绋垮閸欏繘鏌熺紒銏犳灈閸?},
        {"role": "assistant", "content": "濠电姷鏁搁崑鐘诲箵椤忓棗绶ら柟绋垮閸欏繘鏌熺紒銏犳灈閸ュ瓨绻涚€电孝妞ゆ垵妫濆鏌ヮ敆閳ь剟婀侀梺鎸庣箓閻楁粌顭囬幇顔剧＜闁绘ê鍟跨粭鎺楁婢舵劖鐓熸慨妤€妫楁禍婊兠瑰鍛壕缂佺粯鐩獮瀣倷鐎电寮抽梻浣虹帛椤ㄥ懎螞濠婂牆桅闁圭増婢橀惌妤€顭跨捄铏圭劸婵炴潙瀚板娲濞戣鲸肖闂佺姘︽禍顒勬嚍鏉堚晜瀚氶悷浣风缂嶅﹪寮幇鏉跨倞妞ゎ剦鍠撻崕鑼崲濞戙垹閱囬柣鏃堫棑娴煎矂姊?},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    """Long conversations should have older messages compressed."""
    messages = [{"role": "system", "content": "System prompt"}]
    # Add 20 user/assistant pairs
    for i in range(20):
        messages.append({"role": "user", "content": f"闂傚倸鍊烽悞锕€顪冮崹顕呯劷闁秆勵殔缁€澶屸偓骞垮劚椤︻垶寮伴妷锔剧闁瑰鍊戝顑╋綁宕奸妷锔惧幈濡炪倖鍔戦崐鏇㈠几瀹ュ洨纾?{i}"})
        messages.append({"role": "assistant", "content": f"闂傚倸鍊风粈渚€骞夐敓鐘茶摕闁跨喓濮撮悿鐐節婵犲倸顏繛鍛У缁绘繃绻濋崒婊冾暫闂佺粯鍔曢敃顏堝蓟閿濆绠涙い鎺嶈閺嬫瑥鈹?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "濠电姷鏁搁崑鐐哄垂閸洖钃熼柕濞炬櫓閺佸嫰鏌涘☉鍗炴灍婵炲懐濞€閺岋絽螣閼测晛绗￠梺绋块缁夊綊寮诲☉銏犲嵆闁靛鍎伴懜顏堟⒑閹肩偛鈧绻涢埀顒勬煙椤旇偐绉虹€规洖鐖兼俊姝岊槾闁伙綁浜跺娲偂鎼达絼绮甸梺鎼炲妼濞尖€愁嚕椤愩埄鍚嬮柛娑卞灡濞堟洟姊洪柅鐐茶嫰婢у鈧鍣崑濠冧繆閼搁潧绶炲┑鐘插閸氬懘鏌ｆ惔锝嗗殌閻庢凹鍘奸…鍨熼悡搴ｇ瓘濠电偛妯婃禍婵嬪煕閹寸偑浜滈柟鑸妼婢у弶銇勯敃鍌ゆ缂?0闂傚倸鍊风粈渚€骞栭位鍥敃閿曗偓缁€鍫熺節闂堟稓澧㈤柣顓熸崌閺岋綁骞嬮敐鍡╂缂備胶濮电敮妤呭Φ閸曨垰鍐€闁靛鍎崑鎾澄旈崘顏嗙劶婵犮垼鍩栭崝鏍偂閺囥垺鐓涢柛灞剧矊閸斿绻涢崨顓燁棞妞ゎ叀鍎婚ˇ宕囩磼椤旇姤宕岀€殿喖顭峰畷濂稿Ψ閿曗偓閻у嫭绻濋姀锝嗙【妞わ箒椴搁妵娆撴惞椤愩倗顔曢柣搴㈢⊕椤洭鎯屾繝鍐х箚妞ゆ劧缍嗗▓鏃堟偂閵堝鐓涚€广儱鍟俊鑲╃磼閸撲礁浠ч柍褜鍓欑粻宥夊磿闁秴鐤柣妯款嚙绾?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # System prompt should be preserved
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"

    # Should have a summary message
    assert any("濠电姷鏁搁崑鐐哄垂閸洖钃熼柕濞炬櫓閺佸嫰鏌涘☉鍗炴灍婵炲懐濞€閺岋絽螣閼测晛绗￠梺绋块缁夊綊寮诲☉銏犲嵆闁靛鍎伴懜顏堟⒑閹肩偛鈧绻涢埀顒勬煙? in m.get("content", "") for m in result)

    # Recent messages should be preserved (last 12 non-system messages = 6 pairs)
    assert len(result) <= 14  # system + summary + 12 recent


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    """The most recent messages should be kept intact."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(20):
        messages.append({"role": "user", "content": f"婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柣銏犳啞閸嬪鈹戦悩鎻掓殭妞?{i}"})
        messages.append({"role": "assistant", "content": f"闂傚倸鍊烽悞锕傚箖閸洖纾块柟鎯版绾剧粯绻涢幋鏃€鍤?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "闂傚倸鍊风粈渚€骞栭锕€鐤柣妯款嚙閻ょ偓绻濇繝鍌氭灕闁兼澘娼￠弻銊モ槈濡警浠遍梺绋款儐閹瑰洭骞冮挊澶嗘灁闁圭瀛╅弳鐐烘⒒娴ｉ涓茬紓鍌涙皑閸掓帒鈻庨幘璺虹ウ濠德板€愰崑鎾绘懚閿濆棛绠鹃柛鈩冪懃娴滈箖鏌?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # Last message should be the most recent assistant reply
    assert result[-1]["content"] == "闂傚倸鍊烽悞锕傚箖閸洖纾块柟鎯版绾剧粯绻涢幋鏃€鍤?19"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: FAIL 闂?`ImportError: cannot import name 'compress_conversation_history'`

- [ ] **Step 3: Add compress_conversation_history to context_compressor.py**

Append to `app/services/context_compressor.py`:

```python
from app.agent.llm_client import chat_completion as _chat_completion

_SUMMARIZE_PROMPT = """闂傚倷娴囧畷鍨叏閺夋嚚娲敇閳跺搫顦甸獮妯兼嫚閸欏鈧?-3闂傚倸鍊风粈渚€骞夐敓鐘冲仭闁挎繂顦壕鍧楁煙缂併垹鏋熼柛搴★工闇夐柣妯烘▕閸庡繒绱掗悩鍐茬伌闁哄被鍊栭幈銊╁箛椤戣棄浜炬俊銈傚亾闁崇粯妫冩慨鈧柣妯烘缂嶅﹪骞冮埡鍜佹晩闁绘挸楠搁～鎺旂磽閸屾瑧鍔嶆い銊ユ嚇楠炲﹪骞囬弶璺ㄥ姦濡炪倖甯掗崐褰掑汲閳哄倶浜滈柕蹇曞闊剟鏌熼娆戝妽缂佸倹甯為埀顒婄秵娴滅偤藝閵娾晜鈷戦柛娑橈梗缁堕亶鏌涘▎蹇涘弰鐎规洦鍨跺畷鍫曨敆娴ｅ搫甯鹃梻浣虹《閸撴繈銆冮崨鏉戠劦妞ゆ巻鍋撴繛灏栤偓宕囨殾闁规儼妫勭粻鐟懊归敐鍥ㄥ殌闁逞屽墰閸忔ê顫忓ú顏嶆晝闁挎繂娲㈤埀顒佸笧缁辨帡鎮╂潏鈺冪厯闂佸搫鐭夌紞渚€寮幇鏉垮耿婵炲棙鍔曞▓蹇曠磽閸屾瑧顦︾憸鏉款樀瀹曪繝骞庨挊澶岀暫婵炲濮撮鍛劔闂備焦瀵уú宥夊磻閹剧粯鐓熼柟鎯х摠缁€瀣煛鐏炲墽銆掗柍褜鍓ㄧ紞鍡涘磻閸℃稒鍋傛い鏍ㄧ矌绾惧ジ鏌曟繛鍨仼濠⒀嗗皺缁辨帡宕掑☉妯昏癁闂佺硶鏂侀崑鎾愁渻閵堝棗绗傞柤鍐茬埣閸┿垽寮撮姀锛勫幈濡炪倖鍔戦崐鏇㈠几閹达附鐓欐い鏍ㄧ〒閹冲啴妫佹径鎰叆婵犻潧妫欓ˉ婊勭箾閸垹鈻堥柡灞界Х椤т線鏌涜箛鏃傛创闁硅櫕顨婂畷濂稿即閻愬吀绱滄繝纰樻閸ㄤ即宕ョ€ｎ偄鍨斿┑鍌氭啞閻撳繘鏌涢锝囩畵妞ゅ浚鍋婇弻娑㈡偄閸戙倕浼愰梻鍥ь樀閺岋絽顫滈崱妞剧盎婵炲瓨绮庨崑鎾舵崲濞戙垹绠ｉ柣鎰嚟閸欏棝姊虹紒姗嗘當閻庢矮鍗冲畷娲焵椤掍降浜滈柟瀵稿仜椤曟粎绱掓担宄板祮闁哄本娲熷畷鍗炍旈埀顒勫汲閻愬绠鹃柣鎾虫捣缁犺崵鈧娲╃紞浣逛繆閻ゎ垼妲婚梺鍝勬噳閺呮粎鎹㈠☉姘ｅ亾閻㈡鐒剧悮銉╂⒑缁嬫鍎愰柟鍛婃倐閸┿儲寰勯幇顒侇棟闁荤姵浜介崝宀勩€傞悜妯肩閻庢稒顭囬惌濠囨煙鐠囇呯？缂傚倹鎹囬幊鐐哄Ψ閿曗偓瀵潡姊虹涵鍛劷闁告柨鏈粋?""


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
        summary = response.get("content", "闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟杈鹃檮閸嬪鈹戦悩韫抗婵炴垯鍩勯弫鍥煏韫囨洖孝闁绘繃锕㈠铏圭磼濡崵鍙嗗銈冨妼闁帮絽鐣烽悽鍛婂亹缂備焦锚娴狀垶姊洪幖鐐插姌闁告柨娴风划濠氬冀椤撶喓鍘甸梺鍦帛鐢偤鏁嶅澶嬬厵闁肩⒈鍓欓。濂告煙瀹勭増鍣烘い锔惧閹棃鏁愰崱妤佺亐闂傚倸鍊风粈渚€骞夐敓鐘冲仭妞ゆ牜鍋涢崹鍌炴煙閹増顥夐柡瀣╃窔閺屾洟宕煎┑鎰ч梺?)
    except Exception:
        summary = "闂傚倸鍊烽悞锔锯偓绗涘懐鐭欓柟杈鹃檮閸嬪鈹戦悩韫抗婵炴垯鍩勯弫鍥煏韫囨洖孝闁绘繃锕㈠铏圭磼濡崵鍙嗗銈冨妼闁帮絽鐣烽悽鍛婂亹缂備焦锚娴狀垶姊洪幖鐐插姌闁告柨娴风划濠氬冀椤撶喓鍘甸梺鍦帛鐢偤鏁嶅澶嬬厵闁肩⒈鍓欓。濂告煙瀹勭増鍤囬柟顔界矊铻ｇ紓浣癸供娴犙囨⒒閸屾瑨鍏岄柟铏崌閹椽濡搁埡浣侯槷闂佸搫娲㈤崹瑙勵攰闂備胶鎳撻顓熸叏閻㈢鍋撳顒夌吋闁哄本娲樺鍕熼搹閫涘寲缂傚倷璁查崑?

    summary_msg = {
        "role": "user",
        "content": f"[濠电姷鏁搁崑鐐哄垂閸洖钃熼柕濞炬櫓閺佸嫰鏌涘☉鍗炴灍婵炲懐濞€閺岋絽螣閼测晛绗￠梺绋块缁夊綊寮诲☉銏犲嵆闁靛鍎伴懜顏堟⒑閹肩偛鈧绻涢埀顒勬煙椤旇偐绉虹€规洖鐖兼俊姝岊槾闁伙絾妞藉铏规喆閸曨偆绁风紒鍓ц檸閸欏啴鐛径鎰亱闁割偀鎳囬弸?{summary}",
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
- [ ] Plan 4: Memory + 濠电姷鏁搁崑鐐哄垂閸洖绠伴柟闂寸劍閺呮繈鏌ㄥ┑鍡樺窛缂佺姵妫冮弻娑樷槈濞嗘劗绋囧┑鈽嗗亝閿曘垽寮诲☉銏犖ㄩ柕蹇婂墲閻濓箓姊洪崨濠傜劰闁稿鎹囧缁樻媴閽樺鎯為梺绋款儐缁嬫垼鐏嬮柣搴ㄦ涧閹诧繝锝?0 濠?task闂?```

Update "闂備浇宕甸崰鎰垝鎼淬垺娅犳俊銈呮噹缁犱即鏌涘☉姗堟敾婵炲懐濞€閺岋絽螣閻戞ǚ鏋欏┑鐐烘？閸楁娊寮婚妸銉㈡斀闁糕剝锚濞呫倝姊绘繝搴″⒒闁告挾鍠栧濠氭偄閾忓湱鐣跺┑鐐村灦钃遍柨娑樼Ч閺岋繝鍩€? to reflect Plan 4 completion.

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with Plan 4 completion status"
```
