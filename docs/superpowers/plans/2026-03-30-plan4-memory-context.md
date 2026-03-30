# Plan 4: Memory 缂傚倸鍊搁崐鎼佸磹妞嬪孩顐介柨鐔哄Т閸ㄥ倿姊婚崼鐔恒€掗柡鍡畵閺岋綁濮€閵堝棙閿梺?+ 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熼梻瀵稿妽闁哄懏绻堥弻銊モ攽閸℃ê绐涚紓浣哄У濡啴寮诲☉妯锋婵炲棙鍔楃粙鍥р攽閳藉棗浜濋柨鏇樺灲瀵鈽夐姀鐘栥劑鏌曡箛濠傚⒉闁绘繐绠撳娲川婵犲倻鍔伴梺绋款儐閹瑰洤顫?
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer memory system (working/short-term/long-term) and context window management to keep conversations coherent across sessions without blowing up the context window.

**Architecture:** Memory CRUD service handles persistence. Two new agent tools (`recall_memory`, `save_memory`) give the LLM on-demand access. Tool result compression summarizes verbose outputs inline. Session lifecycle hooks generate summaries and extract memories at session end. The system prompt builder loads hot/warm memories at session start.

**Tech Stack:** SQLAlchemy async (existing), OpenAI-compatible LLM for summarization, existing agent tool system

**Depends on:** Plan 1 (Memory, SessionSummary, ConversationMessage models), Plan 2 (agent loop, tool_executor, llm_client)

---

## File Structure

```
student-planner/
闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?app/
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?services/
闂?  闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?memory_service.py          # Memory CRUD: create, query, update, delete, staleness
闂?  闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼鍩栭崝鏇㈡嫅閻斿吋鐓ラ柣鏂挎惈瀛濈紓鍌欒閺呯娀寮婚弴锛勭杸閻庯綆浜栭崑鎾诲即閵忊€充簵濠殿喗銇涢崑鎾绘煛?context_compressor.py      # Tool result summarization + conversation compression
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?agent/
闂?  闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?tools.py                   # (modify: add recall_memory, save_memory definitions)
闂?  闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?tool_executor.py           # (modify: add recall_memory, save_memory handlers)
闂?  闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?loop.py                    # (modify: add tool result compression after each tool call)
闂?  闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?context.py                 # (modify: add hot/warm memory loading)
闂?  闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼鍩栭崝鏇㈡嫅閻斿吋鐓ラ柣鏂挎惈瀛濈紓鍌欒閺呯娀寮婚弴锛勭杸閻庯綆浜栭崑鎾诲即閵忊€充簵濠殿喗銇涢崑鎾绘煛?session_lifecycle.py       # Session end: generate summary + extract memories
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?routers/
闂?  闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼鍩栭崝鏇㈡嫅閻斿吋鐓ラ柣鏂挎惈瀛濈紓鍌欒閺呯娀寮婚弴锛勭杸閻庯綆浜栭崑鎾诲即閵忊€充簵濠殿喗銇涢崑鎾绘煛?chat.py                    # (modify: call session lifecycle on disconnect/timeout)
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼鍩栭崝鏇㈡嫅閻斿吋鐓ラ柣鏂挎惈瀛濈紓鍌欒閺呯娀寮婚弴锛勭杸閻庯綆浜栭崑鎾诲即閵忊€充簵濠殿喗銇涢崑鎾绘煛?config.py                      # (modify: add context window thresholds)
闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?tests/
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?test_memory_service.py         # Memory CRUD unit tests
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?test_context_compressor.py     # Compression logic tests
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?test_memory_tools.py           # recall_memory / save_memory tool tests
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼娉涢鍥偟閸洘鐓涢柛銉ｅ劚閻忊晝绱撴担鍙夋珚闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮姀鈥充簵濠殿喗銇涢崑鎾绘煛?test_session_lifecycle.py      # Session end flow tests
闂?  闂傚倸鍊搁崐椋庣矆娓氣偓閹潡宕堕濠勭◤婵犮垼鍩栭崝鏇㈡嫅閻斿吋鐓ラ柣鏂挎惈瀛濈紓鍌欒閺呯娀寮婚弴锛勭杸閻庯綆浜栭崑鎾诲即閵忊€充簵濠殿喗銇涢崑鎾绘煛?test_context_loading.py        # Hot/warm memory in system prompt tests
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
            content="闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堢紓鍌欑贰閸嬪嫮绮旇ぐ鎺戣摕鐎广儱娲﹂崑姗€鏌嶉妷銉ュ笭濠㈣娲滅槐鎾诲磼濞嗘垵濡藉銈冨妼閹虫ê鐣烽幇鐗堝仭闂侇叏绠戝▓顐︽⒑閸涘﹥澶勯柛瀣浮瀹曘儳鈧綆鍠楅悡鏇㈡煛閸ャ儱濡兼鐐瓷戞穱濠囧矗婢跺﹦浼屽┑顔硷功閸庛倕顭囬鍫濈妞ゆ梻鍘ч‖澶嬬節閻㈤潧袨闁搞劍妞介弫鍐閵堝啠鍋?,
            source_session_id="session-abc",
        )
        assert mem.id is not None
        assert mem.category == "preference"
        assert mem.content == "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堢紓鍌欑贰閸嬪嫮绮旇ぐ鎺戣摕鐎广儱娲﹂崑姗€鏌嶉妷銉ュ笭濠㈣娲滅槐鎾诲磼濞嗘垵濡藉銈冨妼閹虫ê鐣烽幇鐗堝仭闂侇叏绠戝▓顐︽⒑閸涘﹥澶勯柛瀣浮瀹曘儳鈧綆鍠楅悡鏇㈡煛閸ャ儱濡兼鐐瓷戞穱濠囧矗婢跺﹦浼屽┑顔硷功閸庛倕顭囬鍫濈妞ゆ梻鍘ч‖澶嬬節閻㈤潧袨闁搞劍妞介弫鍐閵堝啠鍋?
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

        await create_memory(db, "mem-user-2", "preference", "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧悿顕€鏌ｅΟ娆惧殭闁汇倗鍋撶换娑㈠幢濡櫣浠肩紓浣哄У濡啴寮诲☉姘勃闁告挆鈧Σ鍫㈢磽娴ｇ顣抽柛瀣枛閸┾偓妞ゆ巻鍋撶紒鐘茬Ч瀹曟洘娼忛埞鎯т壕婵鍘у▍宥夋煙椤栨瑧鍔嶉柟顖涙婵℃悂鏁傞幆褍绠版繝鐢靛仩閹活亞绱為埀顒併亜椤愩埄妲烘繛鍡愬灲瀹曪絾寰勯崼婊呯泿?)
        await create_memory(db, "mem-user-2", "habit", "婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熺紒銏犳灈缁炬儳顭烽弻鐔煎箚瑜滈崵鐔虹磼閻樿崵鐣洪柡灞剧洴閸ㄦ儳鐣烽崶鈺婂敹濠电姭鎷冮崘銊ч獓缂備胶绮惄顖炵嵁濮椻偓閹兘骞嶉鐓庣細闂?闂傚倸鍊峰ù鍥敋瑜忛幑銏ゅ箛椤旇棄搴婇梺褰掑亰閸犳鐣烽弻銉︾厵閻庢稒顭囩粻銉︾箾?)
        await create_memory(db, "mem-user-2", "decision", "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戝唨妞ゆ挾鍋熼悾鐑樼箾鐎电孝妞ゆ垵鎳忛崕顐︽⒒娓氣偓濞佳囁囬銏犵？闁规儼妫勯悞鍨亜閹烘垵鏆欓柛姘贡缁辨帗娼忛妸銉﹁癁閻庢鍣崳锝呯暦閹烘嚩鎺戔枎閹冾潻闂佸疇顫夐崹鍧楀春閵夆晛骞㈡俊銈傚亾缂佺姾宕电槐鎾寸瑹閸パ勭亾闂佽桨娴囬褔顢氶敐鍡欘浄閻庯絽鐏氶弲婵嬫⒑閹稿海绠撴俊顐弮瀹?)

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
        await create_memory(db, "mem-user-3", "decision", "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戝唨妞ゆ挾鍋熼悾鐑樼箾鐎电孝妞ゆ垵鎳忛崕顐︽⒒娓氣偓濞佳囁囬銏犵？闁规儼妫勯悞鍨亜閹烘垵鏆欓柛姘贡缁辨帗娼忛妸銉﹁癁閻庢鍣崳锝呯暦閹烘嚩鎺戔枎閹冾潻闂佸疇顫夐崹鍧楀春閵夆晛骞㈡俊銈傚亾缂佺姾宕电槐鎾寸瑹閸パ勭亾闂佽桨娴囬褔顢氶敐鍡欘浄閻庯絽鐏氶弲婵嬫⒑閹稿海绠撴俊顐弮瀹?)

        # Old memory (simulate 30 days ago)
        old_mem = Memory(
            user_id="mem-user-3",
            category="decision",
            content="缂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€哥壕鍧楁煙閹増顥夊鍛攽椤斿浠滈柛瀣尵閳ь剝顫夊ú锕傚礈閻旂鈧礁螖閸涱厾顦板銈嗗坊閸嬫挸霉閻樿櫕銇濇慨濠冩そ濡啫鈽夋潏鈺佸Ъ闂備胶顭堥柊锝嗙閸洖绠栭柨鐔哄Т閸楁娊鏌ｉ幇顒傂ｉ柣鈺婂灦楠炲啳顦圭€规洖銈搁、鏇㈠Χ閸涱厜銊╂⒒閸屾瑧顦︽い鎾茬矙瀵爼宕归澶规洟姊?,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_mem)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)
        assert len(warm) == 1
        assert warm[0].content == "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戝唨妞ゆ挾鍋熼悾鐑樼箾鐎电孝妞ゆ垵鎳忛崕顐︽⒒娓氣偓濞佳囁囬銏犵？闁规儼妫勯悞鍨亜閹烘垵鏆欓柛姘贡缁辨帗娼忛妸銉﹁癁閻庢鍣崳锝呯暦閹烘嚩鎺戔枎閹冾潻闂佸疇顫夐崹鍧楀春閵夆晛骞㈡俊銈傚亾缂佺姾宕电槐鎾寸瑹閸パ勭亾闂佽桨娴囬褔顢氶敐鍡欘浄閻庯絽鐏氶弲婵嬫⒑閹稿海绠撴俊顐弮瀹?


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戝唨妞ゆ挾鍋熼悾鐑樼箾鐎电孝妞ゆ垵鎳忛崕顐︽⒒娓氣偓濞佳囁囬銏犵？闁规儼妫勯悞鍨亜閹烘垵鏆欓柛姘贡缁辨帗娼忛妸銉﹁癁閻庢鍣崳锝呯暦閹烘嚩鎺戔枎閹冾潻闂佸疇顫夐崹鍧楀春閵夆晛骞㈡俊銈傚亾缂佺姾宕电槐鎾寸瑹閸パ勭亾闂佽桨娴囬褔顢氶敐鍡欘浄閻庯絽鐏氶弲婵嬫⒑閹稿海绠撴俊顐弮瀹曘儵宕ㄧ€涙ǚ鎷绘繛杈剧悼閹虫捇顢氬鍛＜閻庯綆鍋勯悘瀵糕偓娈垮枤閺佸銆佸Δ鍛妞ゆ劑鍊栭悡锝夋⒒娓氣偓濞佳囁囬锕€鐤炬繛鎴欏灩缁€鍕煟濡櫣锛嶇紒鈾€鍋撳┑鐘垫暩閸嬬偤宕曢搹顐ゎ洸闁告挆鍛紳婵炶揪缍€椤曟牕鈻撻弮鈧妵鍕晜閻愵剚姣堥悗?)
        await create_memory(db, "mem-user-4", "preference", "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堢紓鍌欑贰閸嬪嫮绮旇ぐ鎺戣摕鐎广儱娲﹂崑姗€鏌嶉妷銉ュ笭濠㈣娲滅槐鎾诲磼濞嗘垵濡藉銈冨妼閹虫ê鐣烽幇鐗堝仭闂侇叏绠戝▓顐︽⒑閸涘﹥澶勯柛瀣浮瀹曘儳鈧綆鍠楅悡鏇㈡煛閸ャ儱濡兼鐐瓷戞穱?)
        await create_memory(db, "mem-user-4", "knowledge", "濠电姷鏁告慨鐢割敊閺嶎厼绐楁俊銈呭暞閺嗘粓鏌熼悜姗嗘當缁炬儳缍婇幃褰掑炊瑜庨埢鏇㈡煕閻旈攱鍤囬柡灞诲€曢湁閻庯綆鍋呴悵鏇熺節濞堝灝鐏犻柕鍫熸倐瀵鏁愭径濠勵吅闂佺粯鍔曞Λ娆撳垂閸撲胶鐭夐柟鐑樺焾濞笺劑鏌嶈閸撴瑩锝?)

        results = await recall_memories(db, "mem-user-4", query="婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚?)
        assert len(results) >= 1
        assert any("婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚? in m.content for m in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-5", "decision", "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戝唨妞ゆ挾鍋熼悾鐑樼箾鐎电孝妞ゆ垵鎳忛崕顐︽⒒娓氣偓濞佳囁囬銏犵？闁规儼妫勯悞鍨亜閹烘垵鏆欓柛姘贡缁辨帗娼忛妸銉﹁癁閻庢鍣崳锝呯暦閹烘嚩鎺戔枎閹冾潻闂佸疇顫夐崹鍧楀春閵夆晛骞㈡俊銈傚亾缂佺姾宕电槐鎾寸瑹閸パ勭亾闂佽桨娴囬褔顢氶敐鍡欘浄閻庯絽鐏氶弲婵嬫⒑閹稿海绠撴俊顐弮瀹?)
        original_accessed = mem.last_accessed

        # Small delay to ensure timestamp differs
        results = await recall_memories(db, "mem-user-5", query="婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚?)
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

        mem = await create_memory(db, "mem-user-6", "preference", "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧悿顕€鏌ｅΟ娆惧殭闁汇倗鍋撶换娑㈠幢濡櫣浠肩紓浣哄У濡啴寮诲☉姘勃闁告挆鈧Σ鍫㈢磽娴ｇ顣抽柛瀣枛閸┾偓妞ゆ巻鍋撶紒鐘茬Ч瀹曟洘娼忛埞鎯т壕婵鍘у▍宥夋煙?)
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

        mem = await create_memory(db, "mem-user-7", "preference", "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧悿顕€鏌ｅΟ娆惧殭闁汇倗鍋撶换娑㈠幢濡櫣浠肩紓浣哄У濡啴寮诲☉姘勃闁告挆鈧Σ鍫㈢磽娴ｇ顣抽柛瀣枛閸┾偓妞ゆ巻鍋撶紒鐘茬Ч瀹曟洘娼忛埞鎯т壕婵鍘у▍宥夋煙?)
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
            content="闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧懜褰掓煛鐏炶鍔氱€瑰憡绻冮妵鍕籍閸屾矮澹曞┑鐐茬墛閹倸顫忕紒妯诲闁告稑锕ら弳鍫ユ⒑閸涘﹥鈷愭繛鍙夌矋缁旂喖寮撮姀鈺傛櫍闂侀潧绻嗛埀顒€鍘栧Σ?,
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
                "weekday": "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢舵劖鍊甸柨婵嗛婢ф壆绱?,
                "free_periods": [
                    {"start": "08:00", "end": "10:00", "duration_minutes": 120},
                    {"start": "14:00", "end": "16:00", "duration_minutes": 120},
                ],
                "occupied": [
                    {"start": "10:00", "end": "12:00", "type": "course", "name": "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚?},
                ],
            },
            {
                "date": "2026-04-02",
                "weekday": "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢舵劖鍊堕柣鎰暩閸?,
                "free_periods": [
                    {"start": "09:00", "end": "11:00", "duration_minutes": 120},
                ],
                "occupied": [],
            },
        ],
        "summary": "2026-04-01 闂?2026-04-02 闂?3 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴弻銉︾厽闁归偊鍓氶幆鍫ユ煟閹捐揪鑰块柡灞糕偓鎰佸悑閹肩补鈧磭顔戦梻浣瑰▕閺€杈╂暜閿熺姴钃熸繛鎴炃氶弸搴ㄧ叓閸ラ绋婚柍缁樻崌濮婃椽宕妷銉ょ钵缂備緡鍠楅悷鈺侇嚕婵犳艾惟闁靛鍨洪～宥呪攽閳藉棗鐏ｇ紒顕呭灦楠炲繘鏌嗗鍡忔嫼闂備緡鍋嗛崑娑㈡嚐椤栨稒娅犳い鏍ㄧ◥缁诲棝鏌涘▎蹇ｆЦ婵炴惌鍠楅妵?6 闂傚倸鍊峰ù鍥敋瑜忛幑銏ゅ箛椤旇棄搴婇梺褰掑亰閸犳鐣烽弻銉︾厵閻庢稒顭囩粻銉︾箾?0 闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顒佹闂佸湱鍎ら崵锕€鈽夊Ο閿嬫杸闁诲函缍嗘禍鐐侯敊?,
    }
    compressed = compress_tool_result("get_free_slots", result)
    # Should use the existing summary field
    assert "3 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴弻銉︾厽闁归偊鍓氶幆鍫ユ煟閹捐揪鑰块柡灞糕偓鎰佸悑閹肩补鈧磭顔戦梻浣瑰▕閺€杈╂暜閿熺姴钃熸繛鎴炃氶弸搴ㄧ叓閸ラ绋婚柍缁樻崌濮? in compressed
    assert "6 闂傚倸鍊峰ù鍥敋瑜忛幑銏ゅ箛椤旇棄搴婇梺褰掑亰閸犳鐣烽弻銉︾厵閻庢稒顭囩粻銉︾箾? in compressed
    # Should NOT contain the full slot details
    assert "free_periods" not in compressed


def test_compress_list_courses():
    result = {
        "courses": [
            {"id": "1", "name": "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚?, "teacher": "闂?, "weekday": 1, "start_time": "08:00", "end_time": "09:40"},
            {"id": "2", "name": "缂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€哥壕鍧楁煙閹増顥夊鍛攽椤斿浠滈柛瀣尵閳?, "teacher": "闂?, "weekday": 3, "start_time": "10:00", "end_time": "11:40"},
            {"id": "3", "name": "闂傚倸鍊搁崐椋庣矆娓氣偓瀹曘儳鈧綆鈧叏缍侀獮鎺楀棘閸喚浜板┑掳鍊х徊浠嬪窗濮樿泛鏋?, "teacher": "闂?, "weekday": 2, "start_time": "08:00", "end_time": "09:40"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_courses", result)
    assert "3" in compressed
    assert "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚? in compressed


def test_compress_list_tasks():
    result = {
        "tasks": [
            {"id": "1", "title": "婵犵數濮烽弫鍛婃叏娴兼潙鍨傞柣鎾崇岸閺嬫牗绻涢幋鐐寸殤闁活厽鎸鹃埀顒冾潐濞叉牕煤閵堝棙鍙忔い鎺戝閻撴洟鏌￠崶銉ュ濠⒀呯帛缁绘盯宕奸悤浣圭暦婵烇絽娲ら敃顏堛€佸☉姗嗙叆闁告侗鍘鹃鍏肩節閻㈤潧浠滈柣妤€妫欓弲鑸垫償閿濆棭娼熼梺鍦劋閸わ箓寮埀顒傛崲濠靛纾兼慨姗嗗墰椤斿洨绱撻崒姘偓鐑芥倿閿曞倸钃熼柕濞炬櫓閺佸銇勯幘璺盒㈤柛?, "status": "completed"},
            {"id": "2", "title": "婵犵數濮烽弫鍛婃叏娴兼潙鍨傞柣鎾崇岸閺嬫牗绻涢幋鐐寸殤闁活厽鎸鹃埀顒冾潐濞叉牕煤閵堝棙鍙忔い鎺戝閻撴洟鏌￠崶銉ュ濠⒀呯帛缁绘盯宕奸悤浣圭暦婵烇絽娲ら敃顏堛€佸☉姗嗙叆闁告侗鍘鹃鍏肩節閻㈤潧浠滈柣妤€妫欓弲鑸垫償閿濆棭娼熼梺鍦劋閸わ箓寮埀顒傛崲濠靛纾兼慨姗嗗墰椤斿洨绱撻崒姘偓鐑芥⒔瀹ュ绀夊鑸靛姇閻ょ偓绻濋棃娑氬闁?, "status": "pending"},
            {"id": "3", "title": "婵犵數濮烽弫鍛婃叏娴兼潙鍨傞柣鎾崇岸閺嬫牗绻涢幋鐐寸殤闁活厽鎸鹃埀顒冾潐濞叉牕煤閵堝棙鍙忔い鎺戝閻撴洟鏌￠崶銉ュ妤犵偞蓱娣囧﹪顢曢銏哗濡炪値鍘煎鈥崇暦濠婂嫮鐟归柛銉㈡櫅婵ジ姊?, "status": "pending"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_tasks", result)
    assert "3" in compressed
    assert "1" in compressed  # completed count


def test_compress_create_study_plan():
    result = {
        "tasks": [
            {"title": "婵犵數濮烽弫鍛婃叏娴兼潙鍨傞柣鎾崇岸閺嬫牗绻涢幋鐐寸殤闁活厽鎸鹃埀顒冾潐濞叉牕煤閵堝棙鍙忔い鎺戝閻撴洟鏌￠崶銉ュ濠⒀呯帛缁绘盯宕奸悤浣圭暦婵烇絽娲ら敃顏堛€佸☉姗嗙叆闁告侗鍘鹃鍏肩節閻㈤潧浠滈柣妤€妫欓弲鑸垫償閿濆棭娼熼梺鍦劋閸わ箓寮埀顒傛崲濠靛纾兼慨姗嗗墰椤斿洨绱撻崒姘偓鐑芥倿閿曞倸钃熼柕濞炬櫓閺佸銇勯幘璺盒㈤柛?, "date": "2026-04-01"},
            {"title": "婵犵數濮烽弫鍛婃叏娴兼潙鍨傞柣鎾崇岸閺嬫牗绻涢幋鐐寸殤闁活厽鎸鹃埀顒冾潐濞叉牕煤閵堝棙鍙忔い鎺戝閻撴洟鏌￠崶銉ュ濠⒀呯帛缁绘盯宕奸悤浣圭暦婵烇絽娲ら敃顏堛€佸☉姗嗙叆闁告侗鍘鹃鍏肩節閻㈤潧浠滈柣妤€妫欓弲鑸垫償閿濆棭娼熼梺鍦劋閸わ箓寮埀顒傛崲濠靛纾兼慨姗嗗墰椤斿洨绱撻崒姘偓鐑芥⒔瀹ュ绀夊鑸靛姇閻ょ偓绻濋棃娑氬闁?, "date": "2026-04-02"},
            {"title": "婵犵數濮烽弫鍛婃叏娴兼潙鍨傞柣鎾崇岸閺嬫牗绻涢幋鐐寸殤闁活厽鎸鹃埀顒冾潐濞叉牕煤閵堝棙鍙忔い鎺戝閻撴洟鏌￠崶銉ュ妤犵偞蓱娣囧﹪顢曢銏哗濡炪値鍘煎鈥崇暦濠婂嫮鐟归柛銉㈡櫅婵ジ姊?, "date": "2026-04-03"},
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
        return f"[缂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾鐎殿喚鏁婚、妤呭焵椤掑嫧鈧棃宕橀钘夌檮婵犮垹鍘滈弲婊呯矙閹烘梻鐭夐柟鐑樻煛閸嬫捇鏁愭惔婵堟晼闂佹椿鍋勭€氭澘顫忓ú顏呭亗閹兼番鍨归弳鍫濐渻閵堝棙鈷愰柣妤冨Т閻ｇ兘顢楁担渚祫闁诲函缍嗛崑鍡涘储閹间焦鐓熼煫鍥ㄦ礀娴犫晜銇勯弴鍡楁搐缁€澶愭煏婢舵稖绀嬪ù婊勭矒閺岋繝宕堕埡浣圭彙濠电偛鐗婇…鍥╂閹烘挻缍囬柕濞垮劜鐠囩偛螖閻橀潧浠︽い顓炴喘閸┾偓妞ゆ帒鍊归弳顒勬煛閸涱喚鍙€鐎规洘鐟у?{summary}"
    slots = result.get("slots", [])
    total = sum(len(d.get("free_periods", [])) for d in slots)
    return f"[缂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾鐎殿喚鏁婚、妤呭焵椤掑嫧鈧棃宕橀钘夌檮婵犮垹鍘滈弲婊呯矙閹烘梻鐭夐柟鐑樻煛閸嬫捇鏁愭惔婵堟晼闂佹椿鍋勭€氭澘顫忓ú顏呭亗閹兼番鍨归弳鍫濐渻閵堝棙鈷愰柣妤冨Т閻ｇ兘顢楁担渚祫闁诲函缍嗛崑鍡涘储閹间焦鐓熼煫鍥ㄦ礀娴犫晜銇勯弴鍡楁搐缁€澶愭煏婢舵稖绀嬪ù婊勭矒閺岋繝宕堕埡浣圭彙濠电偛鐗婇…鍥╂閹烘挻缍囬柕濞垮劜鐠囩偛螖閻橀潧浠︽い顓炴喘閸┾偓妞ゆ帒鍊归弳顒勬煛閸涱喚鍙€鐎规洘鐟у?{len(slots)} 婵犵數濮烽弫鍛婃叏娴兼潙鍨傜憸鐗堝笚閸婂爼鏌涢鐘插姎闁汇倗鍋撻妵鍕疀閹炬惌妫″銈庡亝濞叉鎹㈠┑瀣棃婵炴垵宕崜鎵磽娴ｆ彃浜?{total} 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴弻銉︾厽闁归偊鍓氶幆鍫ユ煟閹捐揪鑰块柡灞糕偓鎰佸悑閹肩补鈧磭顔戦梻浣瑰▕閺€杈╂暜閿熺姴钃熸繛鎴炃氶弸搴ㄧ叓閸ラ绋婚柍缁樻崌濮?


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = [c["name"] for c in courses[:5]]
    names_str = "闂?.join(names)
    if count > 5:
        names_str += f" 缂?{count} 闂?
    return f"[闂傚倸鍊峰ù鍥х暦閸偅鍙忛柡澶嬪殮濞差亜围闁糕剝蓱閻濋攱绻涚€电孝妞ゆ垵鎳橀幃鈥斥攽閸″繑鏂€闂佺鏈划鐘绘倿閸撗呯＜闁逞屽墴瀹曞崬螣閸︻厾鐣鹃梻渚€娼ч悧鍡涘箠鎼搭煈鏁傞柕澶嗘櫆閻撳啰鎲稿鍫濈婵炲棙鎸哥壕?闂?{count} 闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌涢锝嗙缂佲偓婢舵劗鍙撻柛銉ｅ妺缁堕亶鏌℃担鍓插剶闁哄瞼鍠栭獮鍡涘级閸熷啯鎹囬弻锟犲椽娴ｇ顫梺閫涚┒閸斿矂鍩為幋锕€閱囨繝濠傚暙閻忎工mes_str}"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    pending = count - completed
    return f"[婵犵數濮烽弫鎼佸磻濞戙埄鏁嬫い鎾跺枑閸欏繐螖閿濆懎鏋ら柡浣割儑閹插憡鎯旈妸銉х杽闂侀潧艌閺呮粓宕戦崟顖涚厽闁规崘娅曢幑锝嗐亜閿旇浜滈柍瑙勫灦楠炲﹪鏌涙繝鍐╃闁逞屽墯閸濆酣宕濋幋锕€鏄ラ柍褜鍓氶妵鍕箳閸℃ぞ澹曢梻?闂?{count} 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴崣澶岀闁糕剝蓱鐏忣厾绱掗悩宕囧弨闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮悩鐢电劶婵犮垼鍩栭崝鏍偂閸愵喗鐓㈡俊顖欒濡插綊鏌涢敐鍥ㄦ珪缂佽鲸甯￠崺鈧い鎺嶇劍濞呯娀鏌涜濞肩pleted} 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴崣澶岀瘈濠电姴鍊绘晶鏇犵磼閳ь剟宕熼娑氬弳濠电偞鍨堕敋妞ゅ繈鍊濋弻娑氣偓锝庡亝瀹曞矂鏌熼鎯у幋闁诡啫鍥ч唶闁绘梻顭堥浼存⒒閸屾瑧鍔嶉柟顔肩埣瀹曟繂顓奸崨顖涙畷闂佸綊妫跨粈渚€寮告担琛″亾楠炲灝鍔氭繛鑼█瀹曟垿骞樼紒姗嗘濠电偞鍨堕懝楣冩煁閸ｂ偓nding} 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴崣澶岀瘈濠电姴鍊归崳鐑樸亜閹邦亞鐭欓柡宀嬬秮瀵噣宕堕妷銏犱壕闁逞屽墴閺屾稓鈧綆鍋呭畷宀勬煙椤旀儳鍘撮柟顔ㄥ洤閱囬柣鏃傤焾椤忎即姊?


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    return f"[婵犵數濮烽弫鍛婃叏娴兼潙鍨傞柣鎾崇岸閺嬫牗绻涢幋鐐寸殤闁活厽鎸鹃埀顒冾潐濞叉牕煤閵堝棙鍙忔い鎺戝閻撴洟鏌￠崶銉ュ妤犵偞顨呴埞鎴︻敍濮樸儱浠梺鍝勮嫰缁夎淇婇悜钘壩ㄩ柕澶涢檮閻︼綁姊绘担绛嬪殭缂佺粯鍔欐俊?闂傚倷娴囬褍顫濋敃鍌︾稏濠㈣埖鍔栭崑銈夋煛閸モ晛小闁绘帒锕ョ换娑㈠幢濡纰嶉梺鍝勵儎缁舵岸寮婚悢鐓庣闁逛即娼у▓顓犵磽?{count} 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴崣澶岀瘈濠电姴鍊婚崥鍥煕閵夘喖澧柣顓燁殔椤法鎹勯崫鍕垫У闂佸搫顑嗛悷鈺侇潖閾忓湱纾兼慨妤€妫涢崝鍛婁繆閻愬樊鍤熸い顓炵墦閹箖鎮滈挊澶庢憰闂侀潧顧€婵″洭宕?


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
            "description": "婵犵數濮烽弫鎼佸磻濞戙埄鏁嬫い鎾跺枑閸欏繘鏌℃径瀣鐟滅増甯楅崐濠氭煢濡警妲归柣搴墴濮婃椽妫冨☉姘暫濡炪倧瀵岄崹宕囧垝婵犳碍鏅查柛婊€鐒︾€靛矂鏌ｆ惔顖滅У濞存粍绮撻、妤呭閵堝棛鍘介梺鎸庣箓椤︻噣骞夐悙顒佸弿濠电姴鍋嗛悡濂告煕閳规儳浜炬俊鐐€栫敮鎺斺偓姘煎墰缁粯瀵奸弶鎴狀啇濠电儑缍嗛崜娆撴倶閳哄懏鐓熼柟鐑樻尰閸婃劙鏌″畝瀣М闁诡喒鏅滃蹇涘煛娴ｅ壊鐎村┑鐘垫暩婵即宕瑰ú顏佲偓锕傚炊椤掆偓缁犳煡鏌曡箛瀣偓鏇犲閸忚偐绠鹃柟瀵稿仜閻掑綊鏌＄€ｎ偆澧い顏勫暣婵″爼宕卞Ο鐑樻闂備線娼荤徊濠氬磿闁稄缍栭煫鍥ㄧ☉缁€鍫㈡喐韫囨洖顥氶柣鎾崇昂閳ь剚甯掗～婵嬵敆閸屾瑨妾搁梻浣筋嚙濞存岸宕板Δ鍐╁床婵炴垯鍨圭痪褔鏌熼幖顓炲箺闁宠鐗撻幃妤冩喆閸曨剛顦ㄥ銈冨妼閿曘倝鎮惧畡鎷旀棃宕ㄩ鐐电崺婵＄偑鍊栫敮鎺楀磹婵犳碍鍋╁Δ锝呭暞閳锋帒霉閿濆洨鎽傞柛銈呭暣閺屾稑鈻庤箛娑樺及閻庤娲栫紞濠囥€佸Δ鍛妞ゆ劑鍊曟慨锔戒繆閻愵亜鈧牕顔忔繝姘；闁瑰墽绮悡鏇炩攽閻樻彃鈧綊骞夐崫銉х＜閺夊牃鏅涙禒褔鏌嶈閸撱劎绱為崱娑樼獥婵°倕鎯ゆ径鎰耿婵炴垶鐟ч崢鎾绘偡濠婂嫮鐭掔€规洘绮岄埥澶愬閻樼數鏋€闂備胶绮〃鍛存偋婵犲啫鍨旈柟缁㈠枟閻撴洘绻涢幋鐑囧叕闁告梻鍠愰妵鍕晜閸濆嫬濮﹀┑鈽嗗亜閹虫﹢銆侀弴銏狀潊闁斥晛鍟崐閿嬬節绾版ɑ顫婇柛瀣嚇閹嫰顢涘鐓庢濡炪倖鍔х粻鎴濇纯濠电姰鍨煎▔娑㈡晝閿曞偆鏁囨繛宸簼閳锋垿鏌ｉ幇闈涘⒉濠㈣锕㈤弻娑欑節閸屻倗鍚嬪銈冨灪閿氶悡銈嗐亜韫囨挻鍣介柛姗€浜跺铏规喆閸曨偄濮㈢紒鍓ц檸閸欌偓闁稿﹤鐡ㄧ换婵嬫偨闂堟稐绮堕梺缁橆殔閿曨亜鐣疯ぐ鎺戝瀭妞ゆ梻鍋撳▓楣冩⒑绾懏褰х紒鎻掓健閹潡鍩€椤掑嫭鈷戦悷娆忓閸斻倗鈧娲﹂崜姘辩矉閹烘嚚娲敂閸涱亝瀚奸梻鍌氬€搁悧濠勭矙閹烘澶娾枎閹邦亞绠氶梺缁樺姈濞兼瑧绮閳ь剚顔栭崯顐﹀炊瑜忛ˇ鏉款渻閵堝棛澧慨妯稿姂閹箖骞嗚濞撳鏌曢崼婵囶棤濠⒀屽墰缁辨帞鈧綆鍋勯悘鎾煙椤旂煫顏囩亙闂佸憡渚楅崰姘跺储闁秵鈷戠憸鐗堝笒娴滀即鏌涢幘瀵告创闁轰礁绉撮鍏煎緞鐎ｎ剙骞楅梺鍦劋婵炲﹤鐣烽弴銏☆棃婵炴垵宕▓銊ヮ渻閵堝棙纾甸柛瀣尵閳ь剚顔栭崰姘跺极鐠囧弬娑㈠礃閵娿垺顫嶉梺鍦劋閹搁箖鍩€椤掆偓閵堢顫忕紒妯诲閻熸瑥瀚ㄦ禒褍鈹戦悙闈涘付婵炲皷鈧磭鏆︽繝闈涙川缁♀偓闂佹悶鍎滈崨顓炐曞┑锛勫亼閸婃牕顔忔繝姘；闁瑰墽绮悡鏇炩攽閻樻彃顏繛鍛礋閺岀喖鐛崹顔句紙濡ょ姷鍋涢澶愬极閸愵喖鐒垫い鎺戝閸婂嘲鈹戦悩鍙夊闁绘挾鍠栭弻鐔兼焽閿曗偓楠炴牜绱掗幓鎺濈吋闁哄矉缍佸浠嬵敇濠靛洤鏋ゆ繝娈垮枛閿曘儱顪冮挊澶樺殨闁告挷鐒﹀畷澶愭煏婵犲啫濮傞柛濠冪墱閹广垹鈽夐姀鐘诲敹闂佺粯妫冮ˉ鎾寸婵傚憡鈷戦柣鐔告緲濡茬粯銇勯幋婵愭Ц妞ゆ洩缍佸畷婊勬媴閻熸壆锛忛梻渚€娼ц噹闁告侗鍠楅鎾绘⒒閸屾艾鈧绮堟笟鈧獮澶愭晬閸曨剚娈板┑掳鍊曢幊宀勫焵椤掆偓閸燁垰顕ラ崟顖氱疀妞ゆ垟鏂傞崕鐢稿蓟濞戙垹绠涢梻鍫熺⊕閻忓牓寮?,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鎹愵嚙鐟欙箓鎮楅敐搴″闁搞劍绻堥獮鏍庨鈧俊鑲╃棯閹佸仮闁哄本娲樼换娑㈡倷椤掍胶褰呯紓鍌欒閸嬫捇鏌涘畝鈧崑鐐烘偂濞嗘挻鐓欐い鏍ㄧ⊕缁惰尙鎮鑸碘拺闁告繂瀚ˉ鐐烘煟閳哄﹤鐏︽鐐插暢閵囨劙骞掗幋鐘测偓鐐烘偡濠婂啰绠婚柛鈹垮灩閻ｆ繈鍩€椤掑倹顫曢柟鐑樻尰缂嶅洭鏌曟繛褍鎳愰弳顐⑩攽?闂傚倸鍊搁崐宄懊归崶褜娴栭柕濞炬櫆閸婂潡鏌ㄩ弴妤€浜惧銈庡幖閻忔繈锝炲鍫濈劦妞ゆ帒瀚ㄩ埀顑跨铻栭柛娑卞枛娴滄粎绱撴担鍓插創婵炲娲滅划锝夋倷閻戞ê鈧灚顨ラ悙鑼虎闁告梹宀搁幃妤€顫濋悡搴㈢彎闂佽鍨悞锕傚箚閺冨牊鏅查柛銉㈡櫔缁卞弶绻濋悽闈涗沪闁搞劌鐖奸幃鐤槼闁哄懎鐖奸弻鍡楊吋閸℃瑥骞?闂?闂傚倸鍊峰ù鍥敋瑜忛埀顒佺▓閺呯姴鐣峰鈧幊锟犲Χ閸モ晪绱虫繝娈垮枟閿氱€规洦鍓氶幈銊╊敆閸曨剛鍘遍梺鍝勬储閸斿本鏅舵导瀛樼厓缂備焦蓱缁€瀣煛瀹€瀣埌閾伙綁鏌涘┑鍡楊仾婵絾鍔欏?",
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
            "description": "婵犵數濮烽弫鎼佸磿閹寸姴绶ら柦妯侯棦濞差亝鏅滈柣鎰靛墮鎼村﹪姊虹粙璺ㄧ伇闁稿鍋ゅ畷鎴﹀Χ婢跺鍘繝鐢靛Т缁绘劙銆呴鍕厓缂備焦蓱椤ュ牓鏌＄仦鐣屝ユい褌绶氶弻娑㈠箻鐠虹儤鐎诲銈嗘穿缂嶄礁鐣锋總绋垮嵆闁绘柨鎲￠悵顐︽⒒娴ｅ憡鍟炴繛璇х畵瀹曟粌顫濋鑺ョ亖闂侀潧绻堥崐鏍煕閹达附鍋℃繛鍡楃箰椤忣亪鎮樿箛銉╂闁靛洤瀚版俊鐑芥晜閽樺顣查梻浣哥－缁垶骞戦崶顒傚祦閻庯綆鍠楅弲婊堟偡濞嗘瑧绋婚悗姘煼濮婄粯鎷呴崨濠呯濡炪値鍘奸悧蹇涘焵椤掍胶鈻撻柡鍛Т閻ｅ嘲煤椤忓嫮锛滈梺缁樺姈濞兼瑦绂掗娑氱閺夊牆澧界粔顒併亜椤愩埄妲烘繛鍡愬灲閹崇娀顢楅崒婊愮床闂佽崵濮村ú锕併亹閸愵喖鐒垫い鎺嶇椤曟粌菐閸パ嶈含妤犵偞锕㈤、娆撴嚃閳哄搴婂┑鐘愁問閸犳鏁冮埡鍛婵鍩栭悡銉︺亜閹捐泛鏋旂紒鐘荤畺閺屻劌鈹戦崱妯烘婵犮垼娉涚€氼喚妲愰幒鏃€瀚氶柟缁樺坊閸嬫捇宕稿Δ鈧粻鏍ㄧ箾瀹割喕绨婚幆鐔兼⒑閸愬弶鎯堥柛濠傛啞缁傛帒煤椤忓應鎷洪梻鍌氱墛娓氭鎮￠鐘电＜闁绘ê鍟块悘鎾煙椤曞棛绡€鐎殿喗鎸虫慨鈧柨娑樺楠炴劙姊绘担鍛婂暈婵炶绠撳畷鎴﹀川閺夋垹顔夐梺鎸庣箓椤︿即鎮￠崘顔界厪濠㈣埖绋戦惁婊堟煟閹哄秶鐭欓柡宀€鍠栭、娆戞嫚閹绘帞銈┑鐘殿暯閸撴繈骞冮崒娑楃箚闁归棿鐒﹂弲婵嬫煃瑜滈崜娆撳煡婢跺寒妯勫┑顔硷工閹碱偅鏅ラ梺鎼炲劀閸愬墽鈧娊姊虹拠鎻掝劉闁告垵缍婂畷婊冾潩鏉堚晝鐒块悗骞垮劚椤︻垰顔忓┑鍡忔斀闁绘ɑ褰冮顓熶繆缂併垹鏋熺紒缁樼箓閳绘捇宕归鐣屼憾闂備礁鎲￠弻銊ф崲濡櫣鏆﹂柟杈剧畱缁犲鎮楀☉娅亪顢撻幘缈犵箚闁绘劕妯婇崕蹇旂箾閺夋垵妲婚崡閬嶆煙鏉堥箖妾柍閿嬪灴閹綊宕堕敐鍌氫壕鐎规洖娲ｇ槐姗€姊绘担瑙勫仩闁告梹鍨剁粋宥囨崉閾忚娈鹃悷婊呭鐢帗鍎梻浣稿暱閹碱偊宕愭繝姘偍闁圭儤顨嗛崐鍨殽閻愯尙浠㈤柛鏃€宀搁弻锝呂旀担铏圭厐闁绘挶鍊濋弻銊モ攽閸♀晜效闂佺粯鎸诲ú鐔煎蓟閻斿吋鐒介柨鏇楀亾濠⒀傚嵆閺屻劌鈽夊Ο澶寡囨煛瀹€瀣ɑ妤犵偛锕弻娑欐償閿濆棙姣堥悗娈垮櫘閸嬪嫰顢樻總绋跨倞闁挎棁妫勬刊浼存⒒娴ｇ鎮戠紒浣规尦瀵彃鈹戠€ｎ亞鐤呴悷婊呭鐢鎮￠悢鍏肩厽闁哄倹瀵ч崯鐐电棯閹岀吋闁哄矉缍侀獮鎺楁倷瀹割喗鍠橀梻浣芥〃缁讹繝宕板☉銏犖﹂柟鐗堟緲缁犳娊鏌熺€电鍓辨俊顐ゅ枑娣囧﹪鎮欓鍕ㄥ亾閺嶎厼绠扮紓浣诡焽閻濆爼鏌￠崶銉ョ仼缁炬儳顭烽弻鐔煎箲閹伴潧娈紒鐐劤閸氬鎹㈠☉銏犲耿婵☆垵娅ｆ禒鐓庮渻閵堝棙鈷愭俊顐㈠暣瀵鏁愰崱妯哄妳闂侀潧绻嗛幊鍥ㄦ叏閸ヮ剚鈷戦柟绋挎唉婢规ɑ銇勯鈥冲姷妞わ附娼欓埞鎴︻敊閻撳簶鎸冪紓渚囧枦椤曆囧煡婢舵劕顫呴柣妯垮皺閻涒晜绻濋悽闈涘壋缂傚秴妫濆畷妤€顫滈埀顒€鐣烽幋锕€绠婚柛锔诲幘閺夌鈹戦悙鏉戠仸妞ゎ厼娲棟鐟滄柨顫忓ú顏勭闁圭粯甯婄花鎾⒑閹肩偛濡芥俊鐐舵椤?ask_user 缂傚倸鍊搁崐鐑芥嚄閸洘鎯為幖娣妼閻骞栧ǎ顒€濡肩紒鎰殕缁绘盯骞嬪▎蹇曞姶闂佽桨绀佸ú銈夊煘閹达附鍋愰悗鍦Т椤ユ繈寮?,
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["preference", "habit", "decision", "knowledge"],
                        "description": "闂傚倸鍊峰ù鍥х暦閸偅鍙忛柟鎯板Г閸婂潡鏌ㄩ弴妤€浜惧銈庡幖閻忔繆鐏掗梺绋跨箳閸樠勬償婵犲洦鈷戠紒瀣濠€鎵磼椤斿吋鎹ｅù婊勬倐閹粙宕ㄦ繝鍌欏寲闂備焦鎮堕崕顖炲礉瀹€鈧濠冪節濮橆厾鍘介梺鍦劋閸垶宕戦姀銈嗙厸閻忕偠顕ф俊濂告煃閽樺妲搁柍璇查铻ｉ柛婵嗗濞煎紣eference=闂傚倸鍊搁崐鐑芥嚄閸洍鈧箓宕奸妷顔芥櫈闂佸憡渚楅崹鍗炵暦閺屻儲鐓欓柣妤€鐗婄欢鏌ュ炊? habit=婵犵數濮烽弫鎼佸磻閻愬搫鍨傞悹杞拌濞兼牜绱撴担鑲℃垿宕ｈ箛娑欑厽闁靛繈鍩勯悞鍓х棯? decision=闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁撻悩鑼槷闂佸搫娲ㄦ慨鎾夊顓滀簻闁规儳宕悘顏堟煕? knowledge=闂傚倸鍊峰ù鍥х暦閸偅鍙忛柟鎯板Г閳锋梻鈧箍鍎遍ˇ顖滃鐟欏嫪绻嗛柕鍫濇噺閸ｆ椽鏌?,
                    },
                    "content": {
                        "type": "string",
                        "description": "闂傚倸鍊峰ù鍥х暦閸偅鍙忛柟鎯板Г閸婂潡鏌ㄩ弴妤€浜惧銈庡幖閻忔繆鐏掗梺绋跨箳閸樠勬償婵犲洦鈷戠紒瀣硶閻忛亶鏌涚€ｎ偆銆掔紒顔肩墦瀹曟﹢顢欓悾灞藉箞婵犵數鍋為崹闈涚暦椤掆偓椤曪絾銈ｉ崘鈺冨幈闂佺粯妫冮弨閬嶅窗濮椻偓閺岋紕浠︾拠鎻掝瀳闂佸疇妫勯ˇ顖濈亽闂佸吋绁撮弲娑欐叏娴煎瓨鈷掑ù锝堫潐閸嬬娀鏌涙繝鍐⒈闁告帗甯￠獮妯兼嫚閼碱剛鏆梻浣虹帛閸旀洟骞栭銈囦笉婵鍩栭埛鎴炪亜閹惧崬濡块柣锝堥哺缁绘盯宕兼担鍛婂闁绘挾鍠栭弻锝夊籍閸偅顥栧┑鐐茬墦娴滃爼寮诲☉姘ｅ亾閿濆骸浜濈€规洖鐭傞弻鈥崇暆閳ь剟宕伴幘璇茬闁绘绮崵鎴炪亜閹烘垵浜為柛鐔风墦濮?,
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
            "description": "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顒佹闂佺粯鍔曢顓犵不妤ｅ啯鐓冪憸婊堝礈濮樿鲸宕叉繛鎴欏灩瀹告繃銇勯幘璺哄壉闁告柨顦辩槐鎾存媴閸撴彃鍓板銈忓閺佽鐣峰ú顏勭劦妞ゆ帊闄嶆禍婊堟煙閻戞ê鐏ユい蹇婃櫇缁辨帡鎮▎蹇斿闁绘挶鍎茬换娑㈠箣閻忔椿浜、鏃堫敂閸喓鍘搁梺绯曞墲椤ㄥ牏绮绘繝姘厸鐎光偓閳ь剟宕伴弽顓犲祦婵せ鍋撴い銏″哺瀹曘劑顢氶崨顕呮婵犵數濮烽弫鎼佸磻濞戙垺鍋嬪┑鐘叉搐閸ㄥ倿鏌涢…鎴濇珮婵炲吋鐗滈幉鎼佹偋閸繄鐟ㄧ紓浣哄С閸楁娊鐛弽顬ュ酣顢楅埀顒勬倶閳哄懏鐓熼柟鐑樻尰閸婃劙鏌″畝瀣М闁诡喒鏅滃蹇涘煛娴ｅ壊鐎村┑鐘垫暩婵即宕瑰ú顏佲偓锕傚炊椤掆偓缁犳煡鏌曡箛瀣偓鏇犲婵傚憡鐓熼柟閭﹀墮濡﹢鏌曟径鍡樻珕闁绘挻娲熼幃姗€鎮欓棃娑楀闂佹眹鍔嶉崹鍦閹烘挸绶炲┑鐐茬仢娴狀噣姊洪崫鍕効缂傚秳绶氶弫鎰版倷娓氼垱鏅㈤梺閫炲苯澧ǎ鍥э攻缁傛帞鈧綆鍋嗛崢閬嶆⒑閸愬弶鎯堥柛濠傤煼婵℃挳骞掑Δ浣哄幍?闂傚倸鍊搁崐鎼佲€﹂鍕；闁告洦鍊嬪ú顏呮櫇濞达綀顫夐崳鐑芥⒒娴ｅ湱婀介柛鈺佸瀹曞綊顢旈崼婵堬紱闂佺懓鍚嬮悰鐨?闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧悿顕€鏌熼崜浣烘憘闁轰礁锕弻鐔兼焽閿曗偓閺嬬喐銇勯锝嗙缂佺粯绻堝Λ鍐ㄢ槈閸楃偛澹堢紓鍌欒閸嬫捇鏌涘畝鈧崑鐐烘偂閺囩喆浜滈柟閭﹀枛瀛濋梺璇叉禋娴滎亪寮?recall_memory 闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸婅埖鎱ㄥΟ鎸庣【缁炬儳娼￠弻鐔煎箚閻楀牜妫勯梺鍝勫閸庢娊鍩€椤掆偓閸樻粓宕戦幘缁樼厓鐟滄粓宕滈悢鐓庢槬闁逞屽墯閵囧嫰骞掗幋婵冨亾瑜版帒姹查柍鍝勬噺閻撴瑩鏌ц箛锝呬簼閻忓繒鏁婚弻銈吤洪鍐╁枤闂佺懓纾繛鈧い銏☆殕閹峰懘宕滃ù瀣壕婵炴垯鍨洪埛鎴︽煕濠靛棗顏存俊鎻掑悑缁绘稒寰勭€ｎ偆顦紓渚囧枛椤兘鐛Ο鑲╃＜婵☆垳鍘ч獮?ID闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熸潏楣冩闁搞倖鍔栭妵鍕冀椤愵澀绮堕梺姹囧€ら崳锝夊蓟瀹ュ牜妾ㄩ梺鍛婃尵閸犳牠鐛崘顔兼嵍妞ゆ挻绋戞禍楣冩煥濠靛棛鍑圭紒銊ヮ煼閺岋繝宕卞▎蹇旂亪闂佸搫澶囬崜婵嬪箯閸涘瓨顥堟繛鎴炲笒娴滈箖鏌￠崶鑸电窙缂傚秵鐗犻弻鏇＄疀鐎ｎ亖鍋撻弴鐐寸函闂傚倷绀侀幉鈩冪瑹濡ゅ懎绀堟繛鎴欏灪閸庢淇婇妶鍛櫤闁抽攱鍨圭槐鎺斺偓锝庡幗绾墎绱掗悩鍗炲祮闁哄本鐩慨鈧柨娑樺瀵劑鎮楃憴鍕妞ゃ垹锕俊鐢稿箛閺夎法顔婇梺鍦檸閸ㄨ京鈧灚鐗犲缁樼瑹閳ь剙顭囪閹囧幢濞戞鏌堥梺缁橆焾椤曆呭?,
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "闂傚倸鍊峰ù鍥х暦閻㈢绐楅柟閭﹀劒濞差亜绠ｉ柣妯兼暩閻掑吋绻涢幘鏉戠劰闁稿鎸鹃埀顒冾潐濞叉粓銆佹繝鍥﹂柟鐗堟緲缁犳娊鏌熺紒銏犵仭閻庡灚鐗犲缁樼瑹閳ь剙顭囪閹囧幢濡炴洘妞介弫鍐磼濞戞ü鎮ｉ梻鍌欑贰閸撴瑧绮旈悽绋跨；闁挎繂鎮胯ぐ鎺撴櫜闁割偒鍋呯紞鍫㈢磽娴ｇ懓鍔堕悘蹇旂懅濡?ID闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熸潏楣冩闁稿顑夐弻娑樷槈閸楃偟浠╅梺?recall_memory 缂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓鍝ョ不閺夊簱鏀介柣妯虹－椤ｆ煡鏌涙繝鍛【妞ゎ叀娉曢幑鍕瑹椤栨艾澹嬮梻浣哥－缁垰顫忚ぐ鎺懳﹂柛鏇ㄥ灠缁犵粯銇勯弽顭戞當濞存粌澧介埀顒冾潐濞叉牕霉閸岀偛鑸归柣銏犳啞閳锋帒霉閿濆懏鍟為柛鐔哄仱閺岋綁鎮ら崒婊呮殼闂佽鍟崶鑸垫櫍闂佺粯蓱閸撴艾顭?,
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
            content="闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堢紓鍌欑贰閸嬪嫮绮旇ぐ鎺戣摕鐎广儱娲﹂崑姗€鏌嶉妷銉ュ笭濠㈣娲滅槐鎾诲磼濞嗘垵濡藉銈冨妼閹虫ê鐣烽幇鐗堝仭闂侇叏绠戝▓顐︽⒑閸涘﹥澶勯柛瀣浮瀹曘儳鈧綆鍠楅悡鏇㈡煛閸ャ儱濡兼鐐瓷戞穱濠囧矗婢跺﹦浼屽┑顔硷功閸庛倕顭囬鍫濈妞ゆ梻鍘ч‖澶嬬節閻㈤潧袨闁搞劍妞介弫鍐閵堝啠鍋?,
        )
        db.add(mem)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "闂傚倸鍊搁崐宄懊归崶褜娴栭柕濞炬櫆閸婂潡鏌ㄩ弴妤€浜惧銈庡幖閻忔繈锝炲鍫濈劦妞ゆ帒瀚ㄩ埀?},
            db=db,
            user_id="tool-mem-1",
        )
        assert "memories" in result
        assert len(result["memories"]) >= 1
        assert "闂傚倸鍊搁崐宄懊归崶褜娴栭柕濞炬櫆閸婂潡鏌ㄩ弴妤€浜惧銈庡幖閻忔繈锝炲鍫濈劦妞ゆ帒瀚ㄩ埀? in result["memories"][0]["content"]


@pytest.mark.asyncio
async def test_recall_memory_empty_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-2", username="toolmem2", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌涘┑鍕姢闁活厽鎹囬弻鐔虹磼閵忕姵鐏嶉梺绋款儍閸婃繈寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閸︻厽鍤€闁绘牕銈稿濠氬即閻旇櫣顔曢悷婊冪Ф閳ь剚鍑归崳锝咁嚕閹惰姤鍋愮紓浣骨氶幏娲⒑閸涘﹦鈽夐柨鏇樺€栭幈銊╁炊椤掍胶鍘甸梺鍛婂姈閻擄繝宕ｉ崟顑句簻?},
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
            {"category": "preference", "content": "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堥梻浣圭湽閸婃宕戦幘璇茬疄闁靛鍎哄銊╂煕閳╁啨浠︾紒銊ょ矙濮婃椽鎳￠妶鍛€鹃梺鍛婃⒐濞茬喖鍨鹃敂鐐磯闁靛绠戠壕顖炴⒑閹呯濠⒀嶇秮閺佸秹宕熼鐙呯床闂備胶鍋ㄩ崕閬嶅疮閸ф鏁傛い鎾跺Л閸嬫挸鈻撻崹顔界彯闂佸憡鎸鹃崰搴ㄦ偩閻戣棄閱囬柡鍥╁仧閸樺憡绻濋悽闈浶㈤柛鐔稿缁?},
            db=db,
            user_id="tool-mem-3",
        )
        assert result["status"] == "saved"

        mems = await db.execute(
            select(Memory).where(Memory.user_id == "tool-mem-3")
        )
        saved = mems.scalars().all()
        assert len(saved) == 1
        assert saved[0].content == "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堥梻浣圭湽閸婃宕戦幘璇茬疄闁靛鍎哄銊╂煕閳╁啨浠︾紒銊ょ矙濮婃椽鎳￠妶鍛€鹃梺鍛婃⒐濞茬喖鍨鹃敂鐐磯闁靛绠戠壕顖炴⒑閹呯濠⒀嶇秮閺佸秹宕熼鐙呯床闂備胶鍋ㄩ崕閬嶅疮閸ф鏁傛い鎾跺Л閸嬫挸鈻撻崹顔界彯闂佸憡鎸鹃崰搴ㄦ偩閻戣棄閱囬柡鍥╁仧閸樺憡绻濋悽闈浶㈤柛鐔稿缁?
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
        "message": f"闂傚倷娴囬褍顫濋敃鍌︾稏濠㈣埖鍔栭崑銈夋煛閸モ晛小闁绘帒锕ラ妵鍕疀閹捐泛鈷堥梺杞扮閿曨亪寮诲☉銏犖ㄩ柨婵嗘噹椤绻濆▓鍨仭闁瑰憡濞婇幃锟狀敃閿曗偓閻愬﹪鏌曟径鍫濆姎濠殿喓鍨荤槐鎾存媴閻熸澘顫嶉梺鍐插槻閻涙ntent}",
    }


async def _delete_memory_handler(
    db: AsyncSession, user_id: str, memory_id: str, **kwargs
) -> dict[str, Any]:
    """Delete a long-term memory by ID."""
    deleted = await delete_memory(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "闂傚倷娴囬褍霉閻戣棄绠犻柟鎹愵嚙缁犵喖姊介崶顒€桅闁圭増婢樼粈鍐┿亜閺冨倸甯堕柣搴弮閹嘲顭ㄩ崨顓ф毉闁汇埄鍨遍〃濠囧春濞戙垹绫嶉柛顐ゅ枔閸橆亪姊洪崜鎻掍簼缂佽瀚弲鍫曟焼瀹ュ棛鍘遍梺闈涚墕閹峰螣閳ь剟姊虹拠鈥虫灕妞ゎ偄顦甸獮蹇涘川椤栨稑鏋傞梺鍛婃处閸樺ジ宕甸幒鏃傜＝?}
    return {"error": "闂傚倸鍊峰ù鍥х暦閸偅鍙忛柟鎯板Г閸婂潡鏌ㄩ弴妤€浜惧銈庡幖閻忔繆鐏掗梺绋跨箳閸樠勬償婵犲洦鈷戠紒瀣濠€鎵磼鐎ｎ偅宕岄柛鈹垮灲瀵噣宕掑Δ鈧禍鐐殽閻愯尙浠㈤柛鏃€宀搁弻鐔兼惞椤愩垹顫掑Δ鐘靛仦椤ㄥ﹪骞冮埡鍐＜婵☆垳鍘ч獮鍫ユ⒒娴ｇ懓顕滈柡灞诲姂楠炴牠顢曢敐鍕畾婵炲濮撮鍡涙偂閺囥垺鐓忓┑鐘茬箳閸掓澘鈹戦鐓庘偓濠氬焵椤掍緡鍟忛柛锝庡櫍瀹曟娊鏁愭径濠勭暫闂佸啿鎼幊蹇涘箚閻愭番浜滈柟鎵虫櫅閳ь剚顨夐埅鏌ユ⒒閸屾艾鈧绮堟笟鈧獮澶愭晬閸曨剚娈伴梺缁樺姇椤曨厾绮绘ィ鍐╃厓鐟滄粓宕滃杈ㄥ床?}
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
            "slots": [{"date": f"2026-04-{i:02d}", "weekday": "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢舵劖鍊甸柨婵嗛婢т即鏌?, "free_periods": [{"start": "08:00", "end": "22:00", "duration_minutes": 840}], "occupied": []} for i in range(1, 8)],
            "summary": "2026-04-01 闂?2026-04-07 闂?7 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴弻銉︾厽闁归偊鍓氶幆鍫ユ煟閹捐揪鑰块柡灞糕偓鎰佸悑閹肩补鈧磭顔戦梻浣瑰▕閺€杈╂暜閿熺姴钃熸繛鎴炃氶弸搴ㄧ叓閸ラ绋婚柍缁樻崌濮婃椽宕妷銉ょ钵缂備緡鍠楅悷鈺侇嚕婵犳艾惟闁靛鍨洪～宥呪攽閳藉棗鐏ｇ紒顕呭灦楠炲繘鏌嗗鍡忔嫼闂備緡鍋嗛崑娑㈡嚐椤栨稒娅犳い鏍ㄧ◥缁诲棝鏌涘▎蹇ｆЦ婵炴惌鍠楅妵?98 闂傚倸鍊峰ù鍥敋瑜忛幑銏ゅ箛椤旇棄搴婇梺褰掑亰閸犳鐣烽弻銉︾厵閻庢稒顭囩粻銉︾箾?0 闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顒佹闂佸湱鍎ら崵锕€鈽夊Ο閿嬫杸闁诲函缍嗘禍鐐侯敊?,
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
                assert "7 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴弻銉︾厽闁归偊鍓氶幆鍫ユ煟閹捐揪鑰块柡灞糕偓鎰佸悑閹肩补鈧磭顔戦梻浣瑰▕閺€杈╂暜閿熺姴钃熸繛鎴炃氶弸搴ㄧ叓閸ラ绋婚柍缁樻崌濮? in content
                return {"role": "assistant", "content": "婵犵數濮烽弫鎼佸磻閻樿绠垫い蹇撴缁躲倝鏌熺粙鍨劉闁告瑥绻橀弻娑㈠箻濡も偓鐎氼剚鎯旀繝鍥ㄢ拺闁告繂瀚埢澶愭煕濡厧甯舵い鏂跨箰閳规垹鈧綆鍋嗛崢顏呯節閻㈤潧孝缂佺粯锚椤﹪顢欓崜褏锛滈梺缁樏崯璺ㄧ箔瑜旈弻宥堫檨闁告挻鐟╅幃妯侯潩椤掑鍞靛┑顔姐仜閸嬫捇鏌熼銊ユ搐楠炪垺绻涚€涙ɑ绶叉繛灞傚姂楠炴垿宕熼姣尖晝鎲歌箛娑欏亗闁哄倸绨遍弨浠嬫煟閹邦剙绾ч柍缁樻礀闇夋繝濠傚缁犵偤鏌℃担鍝バ㈤柍瑙勫灩閳ь剨缍嗛崑鍡涘储閹间焦鈷戦柛娑橈工婵倿鏌涢弬鍧楀弰鐎规洘妞介弫鎰板幢閺囩姷鐣炬俊鐐€栭崝鎴﹀垂濞差亜纾婚柕澶嗘櫆閻?}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                gen = run_agent_loop("闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢妶鍡椾粡濡炪倖鍔х粻鎴犲閸ф鐓曢柟閭﹀灱閸ゅ鏌ら弶鎸庡仴闁哄本绋戦埥澶愬础閻愬吀鍖栭梻浣规た閸樼晫鍠婂鍥ㄥ床婵炴垶锕╅崯鍛亜閺冨洤鍚归柛鎴濈秺濮婃椽骞愭惔锝傚缂備浇顕ч悧鎾愁嚕婵犳碍鏅搁柣妯垮皺椤︺劑姊洪棃娴ゆ盯宕橀鍕婵?, user, "test-session", db, AsyncMock())
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
        pref = Memory(user_id="ctx-user-1", category="preference", content="闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堢紓鍌欑贰閸嬪嫮绮旇ぐ鎺戣摕鐎广儱娲﹂崑姗€鏌嶉妷銉ュ笭濠㈣娲滅槐鎾诲磼濞嗘垵濡藉銈冨妼閹虫ê鐣烽幇鐗堝仭闂侇叏绠戝▓顐︽⒑閸涘﹥澶勯柛瀣浮瀹曘儳鈧綆鍠楅悡鏇㈡煛閸ャ儱濡兼鐐瓷戞穱濠囧矗婢跺﹦浼屽┑顔硷功閸庛倕顭囬鍫濈妞ゆ梻鍘ч‖澶嬬節閻㈤潧袨闁搞劍妞介弫鍐閵堝啠鍋?)
        habit = Memory(user_id="ctx-user-1", category="habit", content="婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熺紒銏犳灈缁炬儳顭烽弻鐔煎箚瑜滈崵鐔虹磼閻樿崵鐣洪柡灞剧洴閸ㄦ儳鐣烽崶鈺婂敹濠电姭鎷冮崘銊ч獓缂備胶绮惄顖炵嵁濮椻偓閹兘骞嶉鐓庣細闂佽楠搁悘姘熆濡皷鍋撳鐓庡⒋闁挎繄鍋涢埞鎴犫偓锝庡亜濞堟繃绻涙潏鍓у埌闁哥噥鍋呯粋宥夊冀瑜夐弨?闂傚倸鍊峰ù鍥敋瑜忛幑銏ゅ箛椤旇棄搴婇梺褰掑亰閸犳鐣烽弻銉︾厵閻庢稒顭囩粻銉︾箾?)
        db.add_all([pref, habit])
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堢紓鍌欑贰閸嬪嫮绮旇ぐ鎺戣摕鐎广儱娲﹂崑姗€鏌嶉妷銉ュ笭濠㈣娲滅槐鎾诲磼濞嗘垵濡藉銈冨妼閹虫ê鐣烽幇鐗堝仭闂侇叏绠戝▓顐︽⒑閸涘﹥澶勯柛瀣浮瀹曘儳鈧綆鍠楅悡鏇㈡煛閸ャ儱濡兼鐐瓷戞穱濠囧矗婢跺﹦浼屽┑顔硷功閸庛倕顭囬鍫濈妞ゆ梻鍘ч‖澶嬬節閻㈤潧袨闁搞劍妞介弫鍐閵堝啠鍋? in context
        assert "婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熺紒銏犳灈缁炬儳顭烽弻鐔煎箚瑜滈崵鐔虹磼閻樿崵鐣洪柡灞剧洴閸ㄦ儳鐣烽崶鈺婂敹濠电姭鎷冮崘銊ч獓缂備胶绮惄顖炵嵁濮椻偓閹兘骞嶉鐓庣細闂佽楠搁悘姘熆濡皷鍋撳鐓庡⒋闁挎繄鍋涢埞鎴犫偓锝庡亜濞堟繃绻涙潏鍓у埌闁哥噥鍋呯粋宥夊冀瑜夐弨?闂傚倸鍊峰ù鍥敋瑜忛幑銏ゅ箛椤旇棄搴婇梺褰掑亰閸犳鐣烽弻銉︾厵閻庢稒顭囩粻銉︾箾? in context


@pytest.mark.asyncio
async def test_warm_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-2", username="ctxtest2", hashed_password="x")
        db.add(user)
        decision = Memory(user_id="ctx-user-2", category="decision", content="婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戝唨妞ゆ挾鍋熼悾鐑樼箾鐎电孝妞ゆ垵鎳忛崕顐︽⒒娓氣偓濞佳囁囬銏犵？闁规儼妫勯悞鍨亜閹烘垵鏆欓柛姘贡缁辨帗娼忛妸銉﹁癁閻庢鍣崳锝呯暦閹烘嚩鎺戔枎閹冾潻闂佸疇顫夐崹鍧楀春閵夆晛骞㈡俊銈傚亾缂佺姾宕电槐鎾寸瑹閸パ勭亾闂佽桨娴囬褔顢氶敐鍡欘浄閻庯絽鐏氶弲婵嬫⒑閹稿海绠撴俊顐弮瀹?)
        db.add(decision)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戝唨妞ゆ挾鍋熼悾鐑樼箾鐎电孝妞ゆ垵鎳忛崕顐︽⒒娓氣偓濞佳囁囬銏犵？闁规儼妫勯悞鍨亜閹烘垵鏆欓柛姘贡缁辨帗娼忛妸銉﹁癁閻庢鍣崳锝呯暦閹烘嚩鎺戔枎閹冾潻闂佸疇顫夐崹鍧楀春閵夆晛骞㈡俊銈傚亾缂佺姾宕电槐鎾寸瑹閸パ勭亾闂佽桨娴囬褔顢氶敐鍡欘浄閻庯絽鐏氶弲婵嬫⒑閹稿海绠撴俊顐弮瀹? in context


@pytest.mark.asyncio
async def test_no_memories_still_works(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-3", username="ctxtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        context = await build_dynamic_context(user, db)
        # Should still have time info, just no memory section
        assert "闂傚倷娴囧畷鐢稿窗閹邦喖鍨濋幖娣灪濞呯姵淇婇妶鍛櫣缂佺姳鍗抽弻娑樷槈濮楀牊鏁惧┑鐐叉噽婵炩偓闁哄矉绲借灒婵炲棙鍎冲▓顓犵磽娓氬洤浜滅紒澶婄秺瀵鈽夐姀鈺傛櫇闂佹寧绻傚Λ娑⑺囬妸鈺傗拺? in context


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
            summary="婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熼梻瀵稿妽闁哄懏绻堥弻鏇熷緞閸℃ɑ鐝﹂梺杞扮閸熸挳寮婚妶鍚ゅ湱鈧綆鍋呭鎺楁⒑缁嬫鍎愰柟鐟版喘楠炲啴鎸婃径鍡樼亖闂佸湱顭堢€涒晠寮抽悙鐑樷拻濞达綁顥撴稉鑼磽閸屾稒鐨戦柛鎺撳笒閳诲酣骞橀搹顐も偓顒勬倵楠炲灝鍔氶柟宄邦儏椤洭鍩￠崨顓犻獓闂佸壊鍋呯粙鎴炰繆閼恒儳绠鹃柛顐ｇ☉閻忓弶鎱ㄦ繝鍛仩闁瑰弶鎸冲畷鐔碱敆閸屾壕鏋忛梻鍌欑劍閹爼宕瑰ú顏呭亗闁跨喓濮伴埀顑跨椤繈鎳滈悽闈涘Ц闁诲骸绠嶉崕閬嶅箠閹板叓鍥樄婵﹥妞藉Λ鍐ㄢ槈鏉堛剱銈夋⒑缁嬪尅鏀绘い銊ワ工閻ｇ兘顢涘☉姘辩槇闂佹悶鍎崝灞剧椤栫偞鈷戦柟鑲╁仜閸旀﹢鏌涢弬璺ㄧ伇缂侇喖鐗撳畷姗€顢欓悾灞藉妇闂備胶纭堕崜婵嬨€冮崨鏉戞辈闁挎繂顦伴悡娑樏归敐鍛喐鐎涙繈姊烘导娆戠ɑ缂佽鐗嗛悾宄邦潨閳ь剟鐛崱姘兼Ъ濠电偛鎳忛〃鍫㈡閹捐纾兼慨姗嗗厴閸嬫捇骞栨担鍝ョ崶濠殿喗顭堝▔娑氱玻濡ゅ懏鐓涢柛銉㈡櫅闉嬫繝?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌涢锝嗙缂佲偓婢舵劗鍙撻柛銉ｅ妿閳藉鏌ｉ幒鎴犱粵闁靛洤瀚伴獮鎺楀幢濡炴儳顥氶梻鍌欑閹芥粓宕伴幇顓犵濠电姴娲ょ粻姘€掑锝呬壕濡炪們鍨洪惄顖炲箖濞嗘挸绾ч柟瀛樼箓椤ュ姊婚崒娆戭槮闁规祴鈧秮娲晝閸屾氨锛涢梺鍦劋閸わ箓鏁愰崶銊ョ彴濠电偞娼欓鍡涳綖瀹ュ鈷戦柛婵嗗閺嗘瑩鏌涙繝鍐╁€愰柣搴ㄦ敱娣囧﹪鎮欓鍕ㄥ亾閺嶎厼绠板┑鐘宠壘缁犳牠鏌涚仦鐐殤闁?,
        )
        db.add(summary)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂傚倸鍊峰ù鍥敋瑜嶉湁闁绘垼妫勯弸渚€鏌熼梻瀵割槮闁稿被鍔庨幉鎼佸棘鐠恒劍娈鹃梺鎸庣箓椤︻垶鐛姀鈥茬箚妞ゆ牗澹曢幏鈩冪箾閸欏鍊愭慨濠呮閸栨牠寮撮悙娴嬫嫟闂備礁鎲￠崹鐢电礊婵犲倻鏆﹂柣銏犳啞閺呮繈鏌涚仦鍓р槈濞? in context
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

WEEKDAY_NAMES = ["闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢舵劖鍊甸柨婵嗛婢т即鏌?, "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢舵劖鍊甸柨婵嗛婢ф彃鈹?, "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢舵劖鍊甸柨婵嗛婢ф壆绱?, "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢舵劖鍊堕柣鎰暩閸?, "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢舵劖鍊甸柨婵嗛婢ф彃鈹?, "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢跺备鍋撻崗澶婁壕闂佸憡娲﹂崑鍡涙偂?, "闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顓犵厯闂婎偄娲︾粙鎴犵矆婢跺备鍋撻獮鍨姎闁?]


async def build_dynamic_context(user: User, db: AsyncSession) -> str:
    """Build the dynamic portion of the system prompt."""
    now = datetime.now(timezone.utc)
    today = now.date()
    weekday = today.isoweekday()

    parts: list[str] = []
    parts.append(f"闂傚倷娴囧畷鐢稿窗閹邦喖鍨濋幖娣灪濞呯姵淇婇妶鍛櫣缂佺姳鍗抽弻娑樷槈濮楀牊鏁惧┑鐐叉噽婵炩偓闁哄矉绲借灒婵炲棙鍎冲▓顓犵磽娓氬洤浜滅紒澶婄秺瀵鈽夐姀鈺傛櫇闂佹寧绻傚Λ娑⑺囬妸鈺傗拺闁圭娴烽妴鎺楁煕閻樺磭澧电€殿喖顭锋俊鎼佸Ψ閵忊槅娼旀繝鐢靛仜濡瑩鏁嬫繝娈垮枤濠€寮寃.strftime('%Y-%m-%d %H:%M')}闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熺€涙绠ラ柣鏂挎閺岋繝宕煎☉鎺戜壕妞ゃ劎宓擠AY_NAMES[weekday - 1]}闂?)

    if user.current_semester_start:
        delta = (today - user.current_semester_start).days
        week_num = delta // 7 + 1
        parts.append(f"闂傚倷娴囧畷鐢稿窗閹邦喖鍨濋幖娣灪濞呯姵淇婇妶鍛櫣缂佺姳鍗抽弻娑樷槈濮楀牊鏁惧┑鐐叉噽婵炩偓闁哄矉绲借灒缁炬媽椴稿В宀勬⒑缁嬫鍎愰柟鍛婃倐閸┿儲寰勯幇顒傤唴闂佸吋浜介崕娲焵椤掆偓缁夋挳鍩為幋锔藉亹妞ゆ劦婢€婢规洟姊绘担鑺ョ《闁哥姵鎸婚幈銊╂偨缁嬭法鏌у銈嗗笂閻掞箓宕ｈ箛鏃€鍙忔俊鐐额嚙娴滃墽绱掔紒銏犲箺闁诡喖鍊搁悾鐑藉即閵忕姷鐤呴梺瑙勫絻閻ｇk_num}闂?)

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

    parts.append("\n婵犵數濮烽弫鎼佸磻濞戙埄鏁嬫い鎾跺枑閸欏繘鏌熺紒銏犳灍闁哄懏绻堥弻鏇㈠醇濠垫劖笑婵℃鎳忕换婵嬪閿濆懐鍘梺鍛婃⒐閻楃姴鐣烽弴鐑嗗悑濠㈣泛顑囬崢閬嶆⒑閸濆嫭鍌ㄩ柛鏂挎湰閺呭爼顢涢悙瀵稿弳濠电偞鍨堕敃鈺佄ｉ搹鍦＜閺夊牄鍔岀粭褔鏌嶈閸撱劎绱為崱妯碱洸闁割偅娲栫壕鎸庣節婵犲倹鍣界痪?)
    if not courses and not tasks:
        parts.append("- 闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧悿顕€鏌ｅΔ鈧悧濠囧矗韫囨稒鐓欑紓浣靛灩閺嬬喖鏌涚€Ｑ勬珚闁哄本娲樼换娑㈡倷椤掍胶褰呯紓?)
    else:
        for course in courses:
            location = f" @ {course.location}" if course.location else ""
            parts.append(f"- {course.start_time}-{course.end_time} {course.name}{location}闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熸潏楣冩闁稿顑夐弻鐔稿閺夋垳鍠婇梺杞扮椤戝洭鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕濞炬櫆閸庢绻涢崱妯诲鞍闁稿﹦鏁婚弻銊モ攽閸℃ê娅ｅ銈忕到绾绢厾妲愰幒妤€鐒?)
        for task in tasks:
            status_mark = "闂? if task.status == "completed" else "闂?
            parts.append(f"- {task.start_time}-{task.end_time} {task.title}闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熺€涙绠ラ柣鏂挎閺屸剝寰勭€ｎ偄鐨╝tus_mark}闂?)

    # User preferences
    preferences = user.preferences or {}
    if preferences:
        parts.append("\n闂傚倸鍊搁崐鐑芥倿閿曗偓椤啴宕归鍛姺闂佺鍕垫當缂佲偓婢跺备鍋撻獮鍨姎妞わ富鍨跺浼村Ψ閿斿墽顔曢梺鐟扮摠閻熴儵鎮橀埡鍐／闁诡垎宀€鍚嬮梺缁樻惄閸嬪﹤鐣烽崼鏇炍╅柨鏇楀亾闁藉嫬銈稿铏圭矙濞嗘儳鍓梺鍛婃⒐閸ㄥ灝顕?)
        if "earliest_study" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敂钘変罕闂佸憡鍔﹂崰鏍婵犳碍鐓欓柛鎾楀懎绗￠梺缁樻尰閻╊垶寮诲☉銏犵疀闁告挷鑳惰摫婵犵數鍋涢幊搴ㄥ箠韫囨稑桅闁告洦鍨扮粻鎶芥煛閸屾稑顕滈柣搴″⒔缁辨挻鎷呴崜鎻掑壈闂佹寧娲︽禍顏堢嵁閸愵喖鐓涢柛娑卞枟閸庮亜顪冮妶鍡楀Е闁稿鎳撻埅鍫曟⒒閸屾艾鈧悂宕愰幖浣哥９闁归棿绀佺壕鐟懊归悩宸剰缂佺姴鐏氶妵鍕疀閹炬惌妫″銈庡亝濞茬喖寮婚敐澶娢╅柨鏃傛嚀瑜板紣eferences['earliest_study']}")
        if "latest_study" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敂钘変罕闂佸憡鍔﹂崰鏍婵犳碍鐓欓柛鎾楀懎绗￠梺缁樻尰閻╊垶寮诲☉妯锋闁告鍋為悘鏇熺節閵忥綆娼愰拑閬嶆煏閸パ冾伃妤犵偞甯″顒勫箰鎼达絺鍋撻崜褏纾藉ù锝呭閸庡繘鏌ㄩ弴銊ら偗妤犵偛鍟撮崺锟犲川椤旇棄鍔掓俊鐐€栭崝锕傚磻閸涙壋鍙鹃梻鍌氬€搁崐鎼佸磹閹间礁纾归柟闂寸绾剧懓霉閻樺樊鍎忕紒鐘茬仛閵囧嫯绠涢幘鎼！濡炪値鍋呭ú鐔煎蓟閿濆惟闁挎梻鎳撹ぐ寮恊ferences['latest_study']}")
        if "lunch_break" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁撻悩顔瑰亾閸愵喖宸濋悗娑櫭禍閬嶆⒑閸涘﹣绶遍柛銊╀憾閿濈偤寮撮姀锛勫帾闂佸壊鍋呯换宥呂ｈぐ鎺撶厸闁告粈绀佹晶顖炴煙娓氬灝濡奸柍瑙勫灴瀹曞ジ鎮㈤崫銉ょ礈references['lunch_break']}")
        if "min_slot_minutes" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敂钘変罕闂佸憡鍔﹂崰鏍婵犳碍鐓欓柛鎾楀懎绗￠梺缁樻尵閸犳劙濡甸崟顖氱婵°倐鍋撻柛鐕佸亞缁宕崟銊︽杸闂佺粯锕╅崑鍕閻愵剛绠鹃柟鐐綑閻掑綊鏌涚€ｎ偅灏甸柍褜鍓氶鏍闯椤曗偓瀹曟垶绻濋崒婊勬婵犻潧鍊搁幉锟犲磻閸曨垱鐓曢柟鎯у暱缁狙呮偖瑜嶉埞鎴︽偐閸偅姣勯梺绋款儐閻╊垶骞冭缁犳稑鈽夐弽銈呬壕闁稿瞼鍎愰弫濠囨煟閹伴潧澧绘繛鑲╁枛濮婂搫效閸パ冾瀴闂佹剚浜炲▓妾坒erences['min_slot_minutes']}闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顒佹闂佸湱鍎ら崵锕€鈽夊Ο閿嬫杸闁诲函缍嗘禍鐐侯敊?)
        if "school_schedule" in preferences:
            parts.append("- 闂傚倷娴囬褍霉閻戣棄绠犻柟鎹愵嚙缁犵喖鏌ㄩ悢鍝勑ｉ柛瀣€块弻銊╂偄閸濆嫅銏ゆ煕鐏炶濮傞柡灞炬礋瀹曠厧鈹戦崶褏鐛╃紓浣瑰劤婢т粙宕戦幘璇参﹂柛鏇ㄥ灠缁秹鏌涢妷鎴濆暞閸庮亞绱撻崒娆戭槮妞ゆ垵鎳橀弫鍐敂閸繆鎽曢梺缁樻⒒閳峰牓寮崶鈺傚枑鐎广儱顦伴崐鍫曟煃閳轰礁鏆曠紒璇叉閺岋綁骞囬鐐电シ闂侀€炲苯澧柣蹇旂箞閿濈偠绠涘☉娆忔闂侀潧鐗嗛幏瀣涘鍫熺厽閹兼惌鍨崇粊鐑芥煕閺傛妯€鐎?)

    # Hot memories (preferences + habits) 闂?always loaded
    hot_memories = await get_hot_memories(db, user.id)
    if hot_memories:
        parts.append("\n闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣銏㈩焾绾惧鏌熼崜褏甯涢柣鎾寸懅缁辨帞鈧綆浜炴禒銏°亜閹哄鐏查柡灞剧洴閸┾剝鎷呯化鏇炰壕闁秆勵殔缁犳牠鎮峰▎蹇擃仾濠殿垱鎸抽幃宄扳枎韫囨搩浼€闂佸憡鍩婄槐鏇犳閹惧瓨濯寸紒娑橆儏濞堫參姊虹粙鍖″伐婵炲皷鈧剚鍤曟い鎰╁焺閸氬顭跨捄鐚磋含闁哥偠娉涢埞鎴︽偐缂佹ɑ閿梺纭呮珪閸旀瑥鐣峰鍫澪╅柨鏂垮⒔閻﹀牓姊婚崒姘卞缂佸鍨块崺鈧い鎺嗗亾缂傚秴锕ら悾鐑芥偡閹佃櫕鏂€闂佸壊鍋侀崹濠氭偩閸洘鐓熼煫鍥ㄦ礀娴犳粌顭胯缁瑩宕洪姀銈呭嵆闁靛骏绱曢崢钘夆攽閳藉棗鐏犻柟纰卞亰瀵娊鏌嗗鍡欏幈闂佸搫鍟崐褰掑汲椤掑嫭鐓涢悘鐐额嚙婵″ジ鏌嶉挊澶樻Ц妞ゎ偅绮撳畷鍗烆潨閸″繐浜鹃柛鈩冪懅绾?)
        for mem in hot_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Warm memories (recent decisions/knowledge) 闂?loaded at session start
    warm_memories = await get_warm_memories(db, user.id, days=7)
    if warm_memories:
        parts.append("\n闂傚倸鍊风粈渚€骞栭位鍥敃閿曗偓閻ょ偓绻濇繝鍌滃闁搞劌鍊块幃褰掓惞閻熸壆娈ら梺鍏兼緲濞硷繝寮婚妸銉㈡婵☆垯璀︽禒鐐節濞堝灝鐏犻柕鍫熸倐瀵鍩勯崘銊х獮闁瑰吋鐣崹濠氬Υ婵犲嫮纾藉ù锝呮惈鏍￠梺鍦嚀濞差厼顕ｆ繝姘╅柕澶堝灪椤秴鈹戦埥鍡楃仯闁告鍤剁兘鍩€椤掍胶绡€闁汇垽娼ф禒锕傛煙闁稓绐旂€规洘妞藉鍊燁檨闁?婵犵數濮烽弫鍛婃叏娴兼潙鍨傜憸鐗堝笚閸婂爼鏌涢鐘插姎闁汇倗鍋撻妵鍕疀閹炬惌妫″銈庡亝濞叉﹢骞堥妸銉庣喖宕归鎯у缚闂?)
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
        parts.append(f"\n婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熼梻瀵稿妽闁哄懏绻堥弻鏇熷緞閸℃ɑ鐝﹂梺杞扮閸熸挳寮婚妶鍚ゅ湱鈧綆鍋呭鎺楁⒑缁嬫鍎愰柟鐟版喘楠炲啴鎸婃径鍡樼亖闂佸湱顭堢€涒晠寮抽悙鐑樷拻濞达綁顥撴稉鑼磽閸屾稒鐨戦柛鎺撳笒閳诲酣骞樼捄铏广偊婵犲痉鏉库偓鎰板磻閹剧粯鎳氶柨婵嗘缁犻箖鏌涢埄鍐噧濞存粓绠栭弻锝夘敇閻曚焦鐤佸┑顔硷攻濡炰粙鐛幇顓熷劅闁挎繂鍊搁～灞句繆閻愵亜鈧牜鏁悙鐑樺仧闁汇埄鏆€t_summary.summary}")

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
            ConversationMessage(session_id="sess-1", role="user", content="闂傚倸鍊烽悞锕傛儑瑜版帒鏄ラ柛鏇ㄥ灠閸ㄥ倸鈹戦崒婊庣劸缂佹劖顨嗘穱濠囧Χ閸涱喖娅ｉ梺鎼炲妼閸婂湱鎹㈠┑鍥╃瘈闁稿本绮岄·鈧梻浣侯焾鐎涒晠宕归崸妤€绠栨俊銈呮噺閺呮煡骞栫划鍏夊亾閹颁焦娴囩紓鍌氬€烽懗鑸垫叏閻㈠憡鍋￠柍杞扮贰閸ゆ洟鏌涢锝嗙闁绘挻鐩弻娑氫沪閸撗呯厑闂侀潻鎬ラ崶銊㈡嫼闂佽崵鍠愬姗€寮虫潏銊ょ箚妞ゆ劧绲跨粻鐐搭殽閻愬弶顥㈢€规洘锕㈤、娆撴嚃閳哄﹥效濠碉紕鍋戦崐鏍箰閼姐倗鐭欓柟鐑橆殔閻ら箖鏌ｉ幇顔煎妺闁抽攱甯￠弻娑氫沪閹规劕顥濋梺閫炲苯澧版い顓炵墦椤㈡岸鏁愰崶銊ョ／婵炴挻鍑归崹杈┾偓闈涚焸濮婅櫣绮欑捄銊т紘闂佺顑囬崑銈夊春?),
            ConversationMessage(session_id="sess-1", role="assistant", content="婵犵數濮烽弫鎼佸磻閻樿绠垫い蹇撴缁躲倝鏌熺粙鍨劉闁告瑥绻橀弻娑㈠箻濡も偓鐎氼剚鎯旀繝鍥ㄢ拺闁告繂瀚埢澶愭煕濡厧甯舵い鏂跨箰閳规垹鈧綆鍋嗛崢顏呯節閻㈤潧孝缂佺粯锚椤﹪顢欓崜褏锛?2婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴弻銉︾厽闁归偊鍓氶幆鍫ユ煟閹捐揪鑰块柡灞糕偓鎰佸悑閹肩补鈧磭顔戦梻浣瑰▕閺€杈╂暜閿熺姴钃熸繛鎴炃氶弸搴ㄧ叓閸ラ绋婚弫鍫熶繆閻愵亙绱栧ù锝囶焾椤忣偆绱?),
            ConversationMessage(session_id="sess-1", role="user", content="闂傚倸鍊烽悞锕傛儑瑜版帒鏄ラ柛鏇ㄥ灠閸ㄥ倸鈹戦崒婊庣劸缂佹劖顨嗘穱濠囧Χ閸涱喖娅ｉ梺鎼炲妼閸婂湱鎹㈠┑鍥╃瘈闁稿本绋戝▍婵嬫⒑缁嬫鍎愰柟鐟版喘楠炲啴鎮滈懞銉у姺闂佹寧鏌ㄨぐ銊樄闁哄矉缍佹慨鈧柍杞拌兌娴狀參姊洪崷顓х劸妞ゎ厾鍏樻俊鎾礃椤旇偐鍊炲銈庡墻閸撴盯宕伴幘鑸殿潟闁圭儤鍤﹂悢璁胯櫣鎷犻崣澶嬬彃婵犵數濮烽弫鍛婃叏娴兼潙鍨傞柣鎾崇岸閺嬫牗绻涢幋鐐寸殤闁活厽鎸鹃埀顒冾潐濞叉牕煤閵堝棙鍙?),
            ConversationMessage(session_id="sess-1", role="assistant", content="闂傚倷娴囬褍顫濋敃鍌︾稏濠㈣埖鍔栭崑銈夋煛閸モ晛小闁绘帒锕ョ换娑㈠幢濡纰嶉梺鍝勵儎缁舵岸寮婚悢鐓庣闁逛即娼у▓顓犵磽?婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴崣澶岀瘈濠电姴鍊婚崥鍥煕閵夘喖澧柣顓燁殔椤法鎹勯崫鍕垫У闂佸搫顑嗛悷鈺侇潖閾忓湱纾兼慨妤€妫涢崝鍛婁繆閻愬樊鍤熸い顓炵墦閹箖鎮滈挊澶庢憰闂侀潧顧€婵″洭宕?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_summary_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂傚倸鍊搁崐鐑芥倿閿曗偓椤啴宕归鍛姺闂佺鍕垫當缂佲偓婢跺备鍋撻獮鍨姎妞わ富鍨跺浼村Ψ閿斿墽顔曢梺鐟扮摠閻熴儵鎮橀埡鍛參闁告劦浜滈弸娑㈡煛鐏炵偓绀冪紒鏃傚枛椤㈡稑顫濋澶夌磻闂備椒绱紞鈧┑顔哄€楅幑銏犫槈濮橈絽浜炬繛鎴炵懐閻掍粙鏌ｉ鐑囨敾濞ｅ洤锕、鏇㈡晲閸ャ劌娅戦梻浣瑰濞插繘宕归搹鍏夊亾闂堟稏鍋㈢€殿喖鐖奸獮瀣攽閸垹鏄ラ梻鍌氬€风欢姘焽瑜戦崳褰掓⒑闁偛鑻晶瀵糕偓娈垮櫘閸嬪﹤鐣烽悢纰辨晬婵炴垶甯楃€氫粙姊绘担渚劸闁哄牜鍓熼幊婵嬪礈瑜忓Λ顖滄喐鎼淬垻鈹嶅┑鐘叉处閸婄兘鏌熺紒妯哄潑闁稿鎹囧畷褰掝敋閸涱喚绋佺紓鍌氬€烽悞锕佹懌缂傚倸绉村ú顓㈠蓟濞戙垹绠绘俊銈傚亾闁瑰嘲顑呭嵄闁绘垼濮ら埛鎴︽偣閸パ冪骇闁圭櫢缍侀弻鐔兼惞椤愶絽纾抽柦妯荤箞閺岀喎鈻撻崹顔界亶闂佸搫妫欑划鎾诲蓟閻旂厧绠氱憸婊堝吹閻旀悶浜滈柍鍝勫€婚崣鈧梺鍝勬湰閻╊垶宕洪崟顖氱妞ゅ繐鍊甸崑鎾诲箳閺冣偓閸犳劙姊洪銊х暠闁诲骏绠撻弻锛勪沪缁嬪灝鈷夐梺鐟板槻閹虫劙骞夐幘顔肩妞ゆ挾鍋涘▓銉モ攽閿涘嫬浜奸柛濞у懐涓嶉柟瀛樼箥閸ゆ洟鏌涢幘鑼跺厡闁活厽鐟ラ埞鎴︽偐閸欏顦╅梺绋款儐閸旀洟濡撮幒鎴僵闁绘挸娴锋禒鈺呮⒑鐠団€虫灆缂佽埖鑹鹃～蹇撁洪鍕獩婵犵數濮撮崐濠氭偡閺屻儲鐓熼柕蹇婃櫅閻忓崬霉濠婂懎浠滈崡?婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犲綊鏌嶉崫鍕偓濠氥€呴崣澶岀闁糕剝蓱鐏忣厾绱掗悩宕囧弨闁哄本娲濈粻娑氣偓锝庝簴閸嬫捇寮撮悩鐢电劶婵犮垼鍩栭崝鏍偂閸愵喗鐓㈡俊顖欒濡插綊鏌涢敐鍥ㄦ珪缂佽鲸甯￠崺鈧?,
                "actions": ["闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢妶鍡椾粡濡炪倖鍔х粻鎴犲閸ф鐓欑紓浣靛灩濞呮﹢鏌℃担鍓插剱濞ｅ洤锕俊鍫曞川椤撶喐顔嶉梻浣规た閸樼晫鍠婂鍥ㄥ床婵炴垶锕╅崯鍛亜閺冨洤鍚归柛鎴濈秺濮婃椽骞愭惔锝傚缂備浇顕ч悧鎾愁嚕婵犳碍鏅搁柣妯垮皺椤︺劑姊洪棃娴ゆ盯宕橀鍕婵?, "闂傚倸鍊搁崐鐑芥倿閿曞倹鍎戠憸鐗堝笒閸ㄥ倸鈹戦悩瀹犲缂佹劖顨婇弻鐔兼偋閸喓鍑￠梺鎼炲妼閸婂綊骞堥妸銉建闁糕剝顨呯€涳絽鈹戦悙鑼妞ゃ劌妫欑粚杈ㄧ節閸ヨ埖鏅┑鐘诧工閹冲海绮垾鏂ユ斀闁绘劘灏欐晶锝嗙箾婢跺娲撮柍銉閹瑰嫰濡搁敃鈧壕顖炴⒑閹呯濠⒀嶇秮閺佸秹宕熼鐙呯床闂備胶鍋ㄩ崕閬嶅疮閸ф鏁傛い鎰堕檮閻撴瑧鈧懓瀚伴崑濠囧磿閺冨牊鐓曢柕濞炬櫇閻ｈ櫣鈧娲橀敃銏ゅ箠閻樻椿鏁勯柛顭戝枟閻?],
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
        assert "婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戠疀妞ゆ帒顦▓顐︽⒑閸涘﹥澶勯柛瀣浮瀹曘儳鈧綆鍠楅悡鏇㈡煛閸ャ儱濡兼鐐瓷戞穱? in summary.summary


@pytest.mark.asyncio
async def test_end_session_extracts_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-2", username="sesstest2", hashed_password="x")
        db.add(user)

        msgs = [
            ConversationMessage(session_id="sess-2", role="user", content="闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸嬨倝鏌曟繛鐐珔闁搞劌鍊块弻锝夊閵忊晝鍔搁梺鍛婂灩婵炩偓闁哄苯绉靛顏堝箯瀹€濠傛暭闂備礁鎼鍛存煀閿濆钃熼柡鍥风磿閻も偓婵犵數濮撮崐鎼佸煕婢舵劖鈷戦柟绋挎捣閳藉绱掓径瀣唉闁糕斂鍎插鍕箛椤掑偆鍟嬬紓鍌欑劍缁嬫捇骞婇幘鏉戭嚤闁归偊鍓﹀〒濠氭煏閸繄绠抽柣锝堜含閳ь剚顔栭崰鏍ㄦ櫠鎼达絽鍨濇繛鍡樺姉缁♀偓闂佹悶鍎崝灞剧瑜版帗鈷戦柛鎾瑰皺閸樻盯鏌涚€ｎ亜顏柛鈹惧亾濡炪倖甯掗崐鍛婄瑜忕槐鎺撴綇閵娿儳鐟查悗鍨緲鐎氼噣鍩€椤掑﹦绉靛ù婊呭仱瀹曘垽骞囬鍓э紳婵炶揪绲肩划娆撳传閾忓湱纾奸悹鍥皺婢ф洘銇勯弴顏嗙М妤犵偞鎹囬獮鎺戔攽閸パ冨帪濠碉紕鍋戦崐鏍礉閹达箑纾规俊銈呮噹缁犵喐銇勮箛鎾跺闁抽攱鍨剁换娑㈡嚑妫版繂鏁界紓浣靛妿缁垶濡甸崟顖氱婵犻潧娴傚Λ锕傛倵濞堝灝鏋熼柟顔煎€搁悾宄邦潨閳ь剟銆侀弮鍫濆耿婵炲棙鍨电敮?),
            ConversationMessage(session_id="sess-2", role="assistant", content="婵犵數濮烽弫鍛婄箾閳ь剚绻涙担鍐叉搐绾剧懓鈹戦悩瀹犲闁汇倗鍋撻妵鍕箛閵婏箑娅氶梺鍝勵儐濡啴寮婚悢鍛婄秶濡わ絽鍟宥夋⒑閸濆嫭濯奸柛鎾跺枛楠炲啫顫滈埀顒勫箖濞嗘挸绾ч柟瀛樼箓琚橀梻鍌欐祰椤曆呮崲閹板叓鍥偨缁嬭法鐣洪柣鐔哥懃鐎氼噣鎮疯ぐ鎺撶厓鐟滄粓宕滈悢鐓幬ラ柛宀€鍋為弲婊堟煕閹炬鎷嬪Σ鎼佹⒒娴ｈ鍋犻柛搴灦瀹曟繃鎯旈妸锝傚亾?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂傚倸鍊搁崐鐑芥倿閿曗偓椤啴宕归鍛姺闂佺鍕垫當缂佲偓婢跺备鍋撻獮鍨姎妞わ富鍨跺浼村Ψ閿斿墽顔曢梺鐟邦嚟閸嬬喖銆傞弻銉︾厱閻庯綆鍋撻懓鍧楁煛鐏炵偓绀冪紒缁樼洴瀹曞綊顢欑喊杈┾偓鎾煟閻斿摜鐭嬪┑鈩冩倐瀹曟鎮╅崹顐㈡畬濡炪値鍘归崝鎴濈暦濮椻偓閸┾剝绻濋崘鐐紘婵犵绱曢崑鎴﹀磹閺嶎偅鏆滈柣鎰惈缁愭鏌熼柇锕€鏋ら柣顓熺懃閳规垿鎮╅崣澶婎槱闂佺顑嗛崝娆撳蓟瑜戠粻娑㈡晲閸涱剝鍩呮繝纰樷偓铏枙闁搞劏娉涢～蹇旂節濮橆剛锛滃┑顔斤供閸忔﹢宕戦幘缁樺仭闂侇叏濡囬崝宄扳攽閻愬弶顥為柛鏃€顨婇妴鍛村蓟閵夛妇鍘卞┑鐐村灦閿曨偊宕濋悢鍏尖拻?,
                "actions": [],
                "memories": [
                    {"category": "preference", "content": "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴顭ㄩ崟顒€寮块梺姹囧灲濞佳囧垂濠靛牃鍋撻獮鍨姎妞わ缚绮欏顐﹀礃椤缍婇幃鈺侇啅椤旂厧澹堢紓鍌欑贰閸嬪嫮绮旇ぐ鎺戣摕鐎广儱娲﹂崑姗€鏌嶉妷銉ュ笭濠㈣娲滅槐鎾诲磼濞嗘垵濡藉銈冨妼閹虫ê鐣烽幇鐗堝仭闂侇叏绠戝▓顐︽⒑閸涘﹥澶勯柛瀣浮瀹曘儳鈧綆鍠楅悡鏇㈡煛閸ャ儱濡兼鐐瓷戞穱濠囧矗婢跺﹦浼屽┑顔硷攻濡炰粙骞婇敓鐘参ч柛娑卞墰閹规洘绻濈喊妯活潑闁稿鎳橀幆鍕敍閻愬瓨娅滈梺缁樺姇閹碱偊宕橀埀顒€顪冮妶鍡樺暗闁哥姵鍔曢埢宥夊冀椤撶喓鍘介棅顐㈡处濞叉牗绂掕閺屾稓鈧綆鍋呭畷宀勬煙椤旂偓鏆鐐达耿瀵剟濡烽敂缁樼秾闂傚倷鑳堕幊鎾存櫠娴犲鏁嗛柡灞诲劚缁€澶愭煟閺傛寧鎲哥紒鈾€鍋撻梻渚€鈧偛鑻晶瀵糕偓瑙勬磸閸旀垵顕ｉ崼鏇炵闁绘垵妫欓ˉ銈夋⒒閸屾瑧鍔嶉柟顔肩埣瀹曟洟顢氶埀顒€顕ｉ弻銉ョ厸濞撴艾娲ㄩ崝?},
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
        assert "闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾绾剧粯绻涢幋鐑嗙劯婵炴垶菤濡插牊銇勯顐㈡灓缂? in memories[0].content
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

_EXTRACT_PROMPT = """闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顒佹闂佸湱鍎ら崵锕€鈽夊Ο閿嬬€婚梺鍦亾濞兼瑩鍩€椤掑倹鏆柡灞诲€濋獮渚€骞掗幋婵喰戞俊鐐€愰弲婵嬪礂濮椻偓瀵寮撮悢椋庣獮闂佸壊鍋呯缓楣冨磻閹炬緞鏃堝川椤旈棿鐢婚梻浣烘嚀婢х晫鍒掗鐐茬９闁汇垹鎲￠悡鐔兼煏韫囧﹥顫婇柛鐔风箻閺岋繝鍩€椤掍礁顕遍悗娑欘焽閸樹粙姊洪幐搴㈩梿婵炲娲熼幆灞解枎閹惧鍘告繛杈剧到閹芥粌鐡梻浣风串缁插墽鎹㈤崼婵堟殾婵せ鍋撴い銏℃瀹曞崬鈻庤箛濠備壕闁规儼濮ら埛?JSON闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熸潏楣冩闁稿顑夐弻娑樷槈閸楃偟浠紓浣哄У閺屻劑鈥︾捄銊﹀磯闁绘垶蓱閹烽亶姊洪崫銉ユ瀻闁圭⒈鍋婂﹢渚€姊洪幐搴ｇ畵婵炶绠戦埢宥夊即閻樼數锛濋梺鍓插亝缁诲秹鎮℃總鍛婄厸閻忕偛澧藉ú瀛橆殽閻愬樊鍎忛柍瑙勫灴瀹曞爼濡搁妷銉ヮ棐闂傚倸鍊风粈渚€骞夐敓鐘冲仭鐟滄柨鐣烽幋锕€绠婚柛鎾茶兌閻掑潡姊洪崷顓炲妺妞ゃ劌鎳樺畷姗€鍩€椤掑嫭鍋℃繝濠傚暟鏁堥悗娈垮櫘閸嬪﹤鐣锋總绋垮嵆闁绘柨鐨濋崑鎾绘偨閸涘﹦鍘遍梺鎸庢椤曆囩嵁濡や降浜滈煫鍥ㄦ礀閺嬫梻绱掓潏銊ョ瑲婵炵厧绻樻俊鎼佸Ψ閵夛附鍤堥梻?
{
  "summary": "婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熺紒銏犳灈缁炬儳顭烽弻鐔煎礈瑜忕敮娑㈡煟閹惧瓨绀冪紒缁樼洴瀹曞崬螖閸愬啨鍨介弻娑㈠棘鐠囨彃濮﹂梺鍝勭焿缂嶄線寮崒婊勫磯闁靛ě鍛箚濠德板€楁慨鐑藉磻閹版澘纾婚柟鍓х帛閳锋垿鏌ｉ幘鍐茬槰婵炶偐鍠栭弻娑欑節閸愮偓鐣堕梺宕囩帛濡啯鎱ㄩ埀顒勬煏閸繃鍣藉Δ鐘叉喘濮婃椽宕橀崣澶嬪創闂佺锕ら…鐑界嵁婵犲洤绀嬫い鎴濆綖缁ㄥ姊鸿ぐ鎺戜喊闁搞劎澧楃粋宥堛亹閹烘挾鍘撻悷婊勭矒瀹曟粌鈽夐姀鐘崇€梺褰掓？闂勫秹鍩€椤戣法鍔嶇紒缁樼箞瀹曞爼濡搁妷銉モ挄婵犵數鍋涢顓熸叏閹绢噮鏁勯柛娑卞灠椤ユ氨绱撴担鑲℃垿宕ｈ箛鏃€鍙忔俊銈傚亾婵☆偅顨嗙粋宥夋倷閻戞鍘遍梺缁樻煥閸ゆ牕顔忛妷鈺傤梿濠㈣埖鍔栭悡鐔告叏濡も偓濡绂嶅鍏犵懓顭ㄩ崨顓濆缂?,
  "actions": ["闂傚倸鍊搁崐椋庣矆娴ｉ潻鑰块梺顒€绉甸崑锟犳煙閹増顥夋鐐灲閺屽秹宕崟顐熷亾瑜版帒绾ч柟闂寸劍閳锋帒霉閿濆懏璐℃繝鈧禒瀣厱闁哄倽娉曢悘閬嶆煃瑜滈崜姘跺礄瑜版帒鐭楅柛鎰靛枤瀹撲線鏌″搴″箺闁绘挶鍎甸幃妤呮晲鎼粹€茬盎濡炪倕瀛╅幐鎼佸煘閹达附鍋愰悹鍥囧啩绱ｉ梻浣告憸閸ｃ儵宕戞繝鍥х畺婵☆垵銆€閺嬪酣鏌熼悙顒佺稇濞?],
  "memories": [
    {"category": "preference|habit|decision|knowledge", "content": "闂傚倸鍊搁崐鐑芥嚄閸洍鈧箓宕奸妷锔芥珖闂佹寧娲栭崐鎼佸磼閵娧勫枑闊洦鎸撮弸搴ㄦ煏韫囧鈧牠鎮為懖鈹惧亾楠炲灝鍔氭俊顐㈢焸楠炲繗銇愰幒鎾嫼闂侀潻瀵岄崣搴ㄦ倿妤ｅ啯鍊垫繛鎴炲笚濞呭﹦鈧娲樺钘夌暦閹烘鍊烽柡澶嬪灣閸栨牕鈹戦悙瀛樺鞍闁糕晛鍟村畷鎴﹀箻濞ｎ兛绨婚梺鎸庣箓缁绘劙銆呴鍌滅＜閺夊牃鏅涙禒杈┾偓瑙勬礀閻栧ジ銆佸Δ浣瑰缂佸鐏濋ˉ澶愭⒒閸屾瑧顦﹂柟娴嬧偓瓒佹椽鏁傞悾宀婃锤濠电偛妫欓崹璺虹暦閺屻儲鐓曢柍鈺佸暟閳洟鏌?}
  ]
}

闂傚倸鍊峰ù鍥х暦閻㈢绐楅柟鎵閸嬶繝鏌曟竟顖楀亾闁稿鎸搁～婵嬫偂鎼粹檧鎷柣搴ゎ潐濞叉牜绱炴繝鍥モ偓浣糕槈閵忊€斥偓鐑芥倵濞戞鎴︽偟?- summary 闂傚倸鍊峰ù鍥х暦閻㈢绐楅柟閭﹀劒濞差亜绠ｉ柨鏃囨濞堟垿姊洪崜鎻掍簼婵炲弶锕㈠畷鎴﹀煛閸屾粎鐦堥梻鍌氱墛缁嬫帡鎮橀埡鍛厽闁瑰鍎愰悞浠嬫煟閻旂儤鍤€闁宠鍨块幃鈺呭箵閹烘繀绱戞俊鐐€х€靛矂宕板Δ鍐╁床婵炴垯鍨圭粻锝夋煟閹邦厽缍戦柣銊﹀灴濮婅櫣绮欏▎鎯у壉闂佺懓鎲￠幃鍌炲春閵夛箑绶為柟閭﹀墰椤旀帡姊洪崨濠庢畼闁稿鍔欏畷鎴﹀箻鐠囨彃宓嗛柟楦挎珪缁傚秷銇愰幒鎾跺幗闂佸綊鍋婇崜娑欑濞戙垺鍊?- memories 闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁撻悩鍐蹭画濡炪倖鐗楃粙鎾汇€呴崣澶岀瘈闂傚牊渚楅悞鎯瑰鍛殌闁靛棙甯掗～婵嬫晲閸涱剙顥氶梺璇叉唉椤煤閳哄啰绀婂ù锝呭閸ゆ洖霉閻樺樊鍎涢柡浣稿暣閺屻劌鈹戦崱姗嗘！濡炪倖鎸哥紞濠傤潖缂佹ɑ濯寸紒娑橆儐缂嶅牓姊洪悷鐗堝暈濠电偛锕ら锝夊Ω閳轰胶顢呴梺缁樺姇缁嬪嫮绱炴笟鈧悰顔锯偓锝庡枟閸嬫劙鏌涢幇顓炵祷妤犵偞鍨舵穱濠囨倷椤忓嫧鍋撻弽顬稒绗熼埀顒勫极閹捐唯闁宠桨鑳堕崝锕€顪冮妶鍡楀潑闁稿鎹囬弻娑㈡偆娴ｅ摜浠╁銈庡幖濞测晝绮诲☉妯锋婵☆垳鈷堝Σ鍫曟煟閻斿摜鐭婇梺甯秮楠炲啯銈ｉ崘鈺冨姸閻庡箍鍎卞Λ娑㈠储闁秵鐓熼幖鎼灣缁夐潧霉濠婂懎浠х紒顔剧帛鐎佃偐鈧稒顭囬崢顏堟⒑閸撴彃浜濈紒顔奸叄閹苯鈻庤箛濠冩杸闂佺偨鍎辩壕顓㈠箺閻樼粯鐓欑€瑰嫮澧楅崳鐑樸亜閿旀儳顣奸柟顖涙閺佹劙宕遍埡鍌滅☉闂傚倸鍊搁崐宄懊归崶顒夋晪闁哄稁鍘奸崹鍌氣攽閸屾粠鐒鹃柛銊ュ€垮娲敆閳ь剛绮旈幘顔煎瀭闁稿瞼鍋為悡蹇撯攽閻愰潧浜炬繛鍛閺岋綁骞橀崘娴嬪亾婵犳艾鐒垫い鎺嗗亾缂佺姴绉瑰畷鏇㈡焼瀹ュ棗浜卞┑鐘诧工閸樻儳煤椤忓懏娅滄繝銏ｆ硾椤戝洭宕㈤柆宥嗏拺鐟滅増甯掓禍浼存煕閹惧娲撮柡浣哥Т椤撳吋寰勭€ｎ剙骞?- 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌涘┑鍕姢闁活厽鎹囬弻锝夊箣濠垫劖缍楅梺閫炲苯澧柟铏耿瀵偊宕橀鑲╋紲濠殿喗锕㈢涵鎼佸船濞差亝鈷掑〒姘ｅ亾婵炰匠鍥ｂ偓锕傤敇閵忊檧鎸冮梺鍛婃处閸ㄩ亶宕愰崹顔氬綊鎮╁顔煎壉闂佺粯鎸堕崕鑼崲濞戙垹绠ｉ柣鎴濇閸旈攱绻濋埛鈧担鍝ヤ紙闂佸搫澶囬崜婵嬪箯閸涘瓨顥堟繛鎴炲笒娴滅偓绻濋棃娑卞剳鐎规挷绶氶幃妤呮晲鎼粹剝鐏嶉梺绋款儛娴滄繈濡甸崟顖氬唨闁汇垽娼ч崺灞解攽?闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸嬨倝鏌曟繛鐐珔闁搞劌鍊块弻娑㈩敃閿濆棛顦ュ┑顔款潐閻擄繝寮婚敐澶婄睄闁搞儯鍎崑鎾诲焵椤掑嫭鐓曢悗锝庡亝鐏忣參鏌嶉挊澶樻Ц闁伙絿鍏樺畷鍫曞煛閸愵亜鐐婄紓鍌氬€搁崐鐑芥倿閿曞倶鈧啴宕ㄥ銈呮喘楠炲秹顢欓崜褍顦?闂傚倸鍊搁崐鐑芥倿閿曞倸绀堟慨妯挎硾绾惧鏌涘☉鍗炵仭闁哄棙绮撻弻锝夊籍閸屾瀚涢梺杞扮閿曨亪寮诲☉銏犖ㄦい鏃囧吹閺嗘绻涚€涙鐭婄紓宥咃躬瀵鏁撻悩鑼€為梺鍝勭墢閺佹悂寮弽顬棃鎮╅棃娑楁澀闂佹悶鍔嬬划娆忣嚕婵犳碍鏅插鑸电〒缁嬪繐顪冮妶鍡楀潑闁稿鎸搁埞鎴﹀灳閼碱剛鐓撻梺鍝勬湰閻╊垶宕洪敓鐘茬＜婵犲﹤瀚崹閬嶆⒒娴ｄ警鏀版繛鍛礋楠炴垿宕惰閺嗭附淇婇娑卞劌婵℃煡绠栧?0闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顒佹闂佸湱鍎ら崵锕€鈽夊Ο鍏兼畷闂佸憡娲﹂崑鍡涘蓟閸儲鐓熼幖鎼灣缁夌敻鏌涚€ｎ亝顥㈤柛鈹垮灲瀵噣宕掑Δ鈧禍鐐殽閻愯尙浠㈤柛鏃€纰嶆穱濠囶敃閿濆孩鐤侀梺纭呮珪閻熴劑濡甸幇鏉跨闁规崘娉涢獮鎰版⒒娴ｄ警鐒鹃悶姘煎亰瀹曟劙寮撮悜鍡楁闁荤姵浜介崝搴ｅ?- 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熼梻瀵稿妽闁稿鍊濋弻鏇熺箾閸喖濮跺┑鐐存尭椤兘寮诲☉妯兼殕闁逞屽墴瀹曟垵鈽夊鍙樼瑝闂佺懓顕慨鐢稿窗閹扮増鍊堕柣鎰絻閳锋棃鏌嶉悷鎵㈤柍瑙勫灴閹晠宕ｆ径瀣€风紓鍌欒兌婵數鏁Δ鍛﹂柛鏇ㄥ灠閸愨偓闂侀潧臎閸曨偅鐝梻鍌欐祰瀹曠敻宕伴幇顔藉床闁割偁鍎辩粻鏍偡濞嗗繐顏┑顖氼嚟缁辨帞鈧綆鍘界涵鍫曟煟閳轰焦鎹ｇ紒?婵犵數濮烽弫鎼佸磻濞戙埄鏁嬫い鎾跺枑閸欏繘鏌熺紒銏犳灍闁哄懏绻堥弻鏇㈠醇濠垫劖笑婵℃鎳忕换婵嬪閿濆棛銆愬銈嗗灥濞差參宕洪姀銈呯睄闁稿本顨呮禍鐐殽閻愯尙浠㈤柛鏃€纰嶆穱濠囶敃閿濆孩鐤侀悗瑙勬磸閸ㄤ粙鐛幒鎳虫梹鎷呯化鏇炰壕闁割煈鍋嗙粻楣冩煙鐎涙绠橀柨娑樼Ф缁辨帗娼忛妸銉缂?闂?- 婵犵數濮烽弫鍛婃叏閻戝鈧倹绂掔€ｎ亞鍔﹀銈嗗坊閸嬫捇鏌涢悢閿嬪仴闁糕斁鍋撳銈嗗坊閸嬫挾绱撳鍜冭含妤犵偛鍟灒閻犲洩灏欑粣鐐寸節閻㈤潧浠ч柛瀣崌閹繝濮€閵堝棌鎷洪梺鍝勫€堕崕鎻掆枍閸涘瓨鐓曢柣鏇氱閻忥絿绱掗纰辩吋妤犵偞甯掕灃濞达絽鎼獮鍫濃攽閻樺灚鏆╁┑顔碱嚟閳ь剚鍑归崜娑㈠极椤曗偓瀹曟粍鎷呴搹鐧哥床闂備浇顕栭崹鍫曘€傞敃鍌氳Е妞ゆ劧闄勯悡娆戔偓鐟板閸嬪﹪宕曢幇鐗堢叆婵炴垶鐟ユ慨鍫ユ煙瀹勭増鍤囬柟鐓庣秺瀹曟粓骞囬埡浣插亾濠靛棭娼栭柛婵嗗珔瑜斿畷鎯邦槻妞ゎ剙鐗撻弻锝嗘償閵忕姴姣堟繛瀛樼矋缁诲嫮鍒掑顓熺秶闁靛ě鍛闂備焦鎮堕崕婊堝川椤栨稒顔戞繝纰夌磿閸嬫垿宕愰弽顓熷亱闁规崘顕х壕瑙勪繆閵堝懎鏆熼柣顓炴閳规垶寰勭仦璁崇病mories 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犳彃霉閿濆洨銆婇柡瀣Ч閺屻劌鈹戦崱鈺傂﹂梺缁樻尰閿曘垽寮婚垾鎰佸悑閹肩补鈧磭顔愰梻浣告惈椤戝嫮娆㈠璺鸿摕闁绘柨鐨濋弸鏃堟煕椤垵鏋熼柣蹇旀崌濮?""


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
                            user_answer = user_response.get("answer", "缂傚倸鍊搁崐鐑芥嚄閸洘鎯為幖娣妼閻骞栧ǎ顒€濡肩紒鎰殕缁绘盯骞嬪▎蹇曞姶闂?)
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

- [x] **Step 3: Commit**

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

- [x] **Step 1: Add memory tool usage rules**

Add the following under the `### 闂傚倷娴囬褍顫濋敃鍌︾稏濠㈣埖鍔曠粻鏍煕椤愶絾绀€缁炬儳娼″娲敆閳ь剛绮旈幘顔藉剹婵°倕鎳忛悡娆戠磼鐎ｎ亞浠㈡い鎺嬪灩閳规垿顢涘☉娆忓攭闂佽鍠栫紞濠囩嵁娓氣偓楠炴帡骞嬪┑鎰偓鎾⒒娴ｅ憡鎯堟俊顐ｎ殜瀹?section in `Agent.md`:

```markdown
- recall_memory闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熼悜姗嗘畷闁搞倕鐭傞弻娑㈠箻濡も偓閹虫劙藝椤栫偞鐓熼幖鎼灣缁夌敻鏌涢悩鎰佹疁閽樼喖鏌涢埄鍐姇闁绘挸鍟伴幉绋款煥閸繄顦┑鐐村灟閸ㄥ湱绮婚悢鍏肩厽婵°倐鍋撻柣妤€锕ラ崚濠囧箻椤旂晫鍘卞┑鐐村灦閿曨偊宕濋悢鎼炰簻闁挎柨鎼崝锔戒繆椤愩垺鍤囨い銏℃礋婵偓闁斥晛鍟崐閿嬬節绾版ɑ顫婇柛瀣嚇閹嫰顢涘鐓庢濡炪倖鍔х粻鎴濇纯濠电姰鍨煎▔娑㈡晝閿曞偆鏁囨繛宸簼閳锋垿鏌ｉ幇闈涘⒉濠㈣锕㈤弻娑欑節閸屻倗鍚嬪銈冨灪閿氶悡銈嗐亜韫囨挻鍣介柛姗€浜跺铏规喆閸曨偄濮㈢紒鍓ц檸閸欌偓闁稿﹤鐡ㄧ换婵嬫偨闂堟稐绮堕梺缁橆殔閿曨亜鐣疯ぐ鎺戝瀭妞ゆ梻鍋撳▓楣冩⒑绾懏褰х紒鎻掓健閹潡鍩€椤掑嫭鈷戦悷娆忓閸斻倗鈧娲﹂崜姘辩矉閹烘嚚娲敂閸涱亝瀚奸梻鍌氬€搁悧濠勭矙閹烘澶娾枎閹邦亞绠氶梺缁樺姈濞兼瑧绮閳ь剚顔栭崯顐﹀炊瑜忛ˇ鏉款渻閵堝棛澧慨妯稿姂閹箖骞嗚濞撳鏌曢崼婵囶棤濠⒀屽墰缁辨帞鈧綆鍋勯悘鎾煙椤旂煫顏囩亙闂佸憡渚楅崰姘跺储闁秵鈷戠憸鐗堝笒娴滀即鏌涢幘瀵告创闁轰礁绉撮鍏煎緞鐎ｎ剙骞楅梺鍦劋婵炲﹤鐣烽弴銏☆棃婵炴垵宕▓銊ヮ渻閵堝棙纾甸柛瀣尵閳ь剚顔栭崰姘跺极鐠囧弬娑㈠礃閵娿垺顫嶉梺鍦劋閹搁箖鍩€椤掆偓閵堢顫忕紒妯诲閻熸瑥瀚ㄦ禒褍鈹戦悙闈涘付婵炲皷鈧磭鏆︽繝闈涙川缁♀偓闂佹悶鍎滈崨顓炐曞┑锛勫亼閸婃牕顔忔繝姘；闁瑰墽绮悡鏇炩攽閻樺弶绁╂俊顐ｅ灩缁辨帡顢氶崨顓炵閻庡灚婢樼€氼喗绂掗敃鍌氱畾鐟滃骸袙閸パ€鏀介柣鎰煐瑜把呯磼閼艰埖顥夐柨鏇樺灲瀹曪繝鎮欏蹇曠М濠碘剝鎮傞弫鍌炲礈瑜滈崯搴ㄦ⒒娴ｈ櫣銆婇柍褜鍓欑壕顓犵不濮樿埖鐓曢悗锝庡亝瀹曞本顨ラ悙鍙夊闁瑰嘲鎳樺畷銊︾節鎼粹剝娅婇梻鍌氬€峰ù鍥х暦閸偅鍙忛柡澶嬪殮濞差亝鏅滈柣鎰靛墮鎼村﹪姊洪崜鎻掍簴闁稿氦浜划鍫ュ磼濞戞绠氬銈嗙墬閼归箖骞冮幋锔藉€垫慨妯煎帶婢ф挳鏌＄仦鍓ф创妤犵偛娲畷妤呭传閵夈儱姣堥梻鍌欑閹碱偄螞濡ゅ啯宕叉慨妞诲亾鐎殿喖顭锋俊鎼佸Ψ閵忊槅娼旀繝纰樻閸ㄤ即鎮樺┑瀣垫晜妞ゆ挶鍨洪崑鈩冪節婵犲倸顏╅幆鐔兼⒑閹肩偛鍔€闁告洦鍋嗛妶鍫曟⒒閸屾瑧绐旀繛浣冲棗娅ｉ梻渚€鈧偛鑻晶鎾煕閳规儳浜炬俊鐐€栫敮濠勬閿熺姵鍊垮ù鐘差儐閻撳啰鎲稿鍫濈婵炲棗楠忛懓鍧楁⒑椤掆偓缁夊澹曟繝姘厪闁割偅绻冮崳鐑芥煃瑜滈崜姘辨暜閳ュ磭鏆︽繝濠傚婵挳鏌ｉ悢鍝勵暭婵絽娲ら埞鎴︽倷閼搁潧娑х紓浣瑰絻濞硷繝鍨鹃敃鍌氶唶闁靛鍎甸弫婊勭節閻㈤潧孝婵炶绠撻幃锟犲即閻旇櫣顔曢梺绯曞墲閿氱紒妤佸笧缁辨帡骞夌€ｎ剛鏆犻柤鎸庡姍閺屾盯濡烽幋婵埿ラ柛姘煎亜铻栭柣姗€娼ф禒鎺旂磼閼搁潧鍝洪柕鍡曠閳藉螣闁垮娼旀繝鐢靛仜濡瑨鎽悶姘€鍕瘈闁汇垽娼ф禒鈺呮煙濞茶绨界紒杈╁仱閸┾偓妞ゆ帊鑳剁粻鎯ь熆鐠轰警鍎愮紒鈧€ｎ兘鍋?- save_memory闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熼悜姗嗘畷闁搞倕鐭傞弻鐔烘喆閸曨偄顫囨繛瀛樼矊濠€閬嶅箟閸涘﹥鍎熼柨婵嗘川閻撴棃姊洪崨濠庢畼闁稿鍔欏銊︾鐎ｎ偆鍘遍梺鏂ユ櫅閸熶即骞婇崟顖涚厵闁圭粯甯囬崑銏℃叏婵犲倹鎯堥悡銈囩磽娴ｅ顏堝煝韫囨稒鈷戦柛娑橈攻閻撱儳绱掓径灞惧殌闁伙絿鍏樺畷顐﹀礋閵婏富娼旈梻渚€娼х换鎺撴叏閺夋埈鍤曢柣鎴ｅГ閻撴瑩鏌ら崷顓烆暭鐟滄妸鍛＜闁告瑥顦伴妵婵嬫煕閳规儳浜炬俊鐐€栫敮濠勬閿熺姵鍊垮ù鐘差儐閻撴瑦銇勯弮鍥跺殭鐎规挸妫楅埞鎴﹀焺閸愨晛鈧劕鈹戦埄鍐╁€愰柡浣稿暣閸┾偓妞ゆ巻鍋撻柍钘夘槼椤﹁鎱ㄦ繝鍌涙儓閺佸牓鏌涢妷鎴濆枤閻庢娊姊虹拠鎻掝劉闁告垼顫夌粋宥呪攽閸垻鐓旈柡澶婄墑閸斿海寮ч埀顒勬⒑閹肩偛鍔€闁告侗鍨卞▓鍝勨攽閿涘嫬浜奸柛濠冪墵閹囧箻鐠囪尙锛欏┑掳鍊曢崯浼存儗閸℃鐔嗛悹鍝勫娇閸惊锝夊醇閵夛妇鍘甸梺璇″瀻閸滃啰绀婇梺鍝ュ枔椤牓鈥旈崘顔嘉ч柛灞剧⊕閻濄劎绱撴担鍝勑ｉ柟鐟版喘閹即顢氶埀顒勭嵁閹烘嚦鏃堝焵椤掍礁鍔旈梻鍌欑劍鐎笛冾潖婵犳艾鐤炬い鎰剁畱缁€澶愭煟閹达絽袚闁抽攱鍨垮濠氬醇閻旇　濮囧銈冨劜缁捇寮诲☉娆戠瘈闁搞儴鍩栭ˉ鏍⒑閻熸壆鐣柛銊ョ秺閿濈偛鈹戠€ｎ亞顓兼繛杈剧秮閺呭弶绔熼弴鐐╂斀闁绘劖娼欓悘锔姐亜韫囷絼閭い銏℃瀹曘劑顢欓悾灞藉▏闂傚倷鑳剁划顖炩€﹂崼婵冩瀺闁挎繂顦伴崑顏堟煃瑜滈崜鐔奉潖濞差亜宸濆┑鐘插婵洭姊烘导娆戠У濞存粠浜畷娲焵椤掍降浜滈柟鍝勬娴滃墽绱撴担铏瑰笡闁挎岸鏌ｉ敐鍛Щ閾绘牠鏌涘☉鍗炲籍闁哥偛鐖煎娲濞戞氨鐣鹃梺鍛婃尰缁诲倿鍩?ask_user 缂傚倸鍊搁崐鐑芥嚄閸洘鎯為幖娣妼閻骞栧ǎ顒€濡肩紒鎰殕缁绘盯骞嬪▎蹇曞姶闂佽桨绀佸ú銈夊煘閹达附鍋愮€规洖娴傞弳锟犳⒑?闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸嬨倝鏌曟繛鐐珔闁搞劌鍊搁埞鎴﹀磼濮橆剦妫岄梺杞扮閿曨亪寮诲☉銏犖ㄩ柨婵嗘噹椤绻濆▓鍨仭闁瑰憡濞婇幃锟狀敃閿曗偓閻愬﹦鎲告惔銊ョ闁挎繂顦伴悡鏇㈡煟閺傚灝娈╅棅顒夊墴閺岋紕浠︾拠鎻掝瀳闂佸疇妫勯ˇ顖炲煝鎼淬劌绠ｉ柣鎰綑閺嗩偊姊婚崒姘偓椋庣矆娓氣偓楠炲鏁撻悩鑼槷闂佸搫娲㈤崹鍦不閻樿绠归柟纰卞幘閸樻盯鏌℃担闈╄含闁哄瞼鍠栭、妤呭礋椤撶姵姣囬梻浣告惈閺堫剙煤閻旈鏆﹂柛妤冨€ｉ弮鍫濈劦妞ゆ帒瀚悞鍨亜閹哄秶鍔嶉柛濠冨姈閵囧嫰濮€閳ュ啿鎽靛銈冨灪瀹€鎼佸春閳ь剚銇勯幒鍡椾壕闂佷紮绲块崗妯讳繆閻戣棄唯閹兼番鍨洪埛鎺楁煃瑜滈崜銊х礊閸℃稑绀堟繛鍡樻尭缁?
  - preference闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熼悜妯虹劸婵炲皷鏅犻弻鏇熺箾閻愵剚鐝旈梺鍝勵儎缁舵岸寮婚弴銏犻唶婵犲灚鍔栫瑧缂傚倷鑳舵刊瀵稿緤閸ф鐒垫い鎺戝€归崵鈧柣搴㈢煯閸楁娊濡撮崒鐐存櫇闁稿本绋戦埀顒€鐏濋埞鎴︽偐閹绘巻鍋撻悽绋跨哗濞寸姴顑嗛悡鏇㈡倶閻愭彃鈷旈柍顖涙礋閺岋綀绠涢敐鍛亾缂?闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸嬨倝鏌曟繛鐐珔闁搞劌鍊块弻锝夊閵忊晝鍔搁梺鍛婂灩婵炩偓闁哄苯绉靛顏堝箯瀹€濠傛暭闂備礁鎼鍛存煀閿濆钃熼柡鍥风磿閻も偓婵犵數濮撮崐鎼佸煕婢舵劖鈷戦柟绋挎捣閳藉绱掓径瀣唉闁糕斂鍎插鍕箛椤掑偆鍟嬬紓鍌欑劍缁嬫捇骞婇幘鏉戭嚤闁归偊鍓﹀〒濠氭煏閸繄绠抽柣锝堜含閳ь剚顔栭崰鏍ㄦ櫠鎼达絽鍨濇繛鍡樺姉缁♀偓闂佹悶鍎崝灞剧瑜版帗鈷戦柟顖嗗嫮顩伴梺绋款儏閹虫﹢銆佸▎蹇ｅ悑濠㈣泛顑囬崢?闂?  - habit闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熼悜姗嗘畷闁搞倕鑻灃闁挎繂鎳庨弸銈夋煛娴ｅ憡顥㈤柡宀嬬秮瀵剟骞愭惔銏犳瀾闂備礁纾划顖毭洪悢鐓庤摕闁挎繂鎲橀悢绋跨窞缂佸瀵ч崕鎾绘⒒娴ｉ涓茬紒鐘冲灴閺屽﹪鏁愭径濠呮憰闂佺粯姊婚埛鍫ュ极瀹ュ鐓ユ繝闈涙閸ｈ棄霉閻撳海澧㈢紒?闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸嬨倝鏌曟繛鐐珔闁搞劌鍊婚埀顒冾潐濞叉牕煤閵娾晛纭€婵鍩栭悡娑橆熆鐠轰警鍎忛柣蹇撶Ч閺岋紕鈧綆浜崣鍕煛鐏炵晫效闁糕斁鍓濋幏鍛村川婵犲喚鍞规繝鐢靛仜椤曨厽鎱ㄩ悽鍛婃櫔婵＄偑鍊ら崢鐓庮焽閿熺姴绠犳繝濠傜墛椤ュ牊绻涢幋鐐嗘垿骞婂▎鎰瘈闁汇垽娼ф禒婊勩亜瑜夐崑鎾绘⒒閸屾艾顏╅悗姘煎枤閸?闂傚倸鍊峰ù鍥敋瑜忛幑銏ゅ箛椤旇棄搴婇梺褰掑亰閸犳鐣烽弻銉︾厵閻庢稒顭囩粻銉︾箾?闂?  - decision闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熼悜妯虹仼闁哄棗妫濋弻鐔兼⒒鐎靛壊妲梻鍌氬亞閸ㄥ爼寮诲☉妯锋斀闁告洦鍋勬慨鏇㈡⒑閸濄儱鏋庨柟纰卞亰濠€渚€姊洪幐搴ｇ畵婵炴潙鍊块幃鐐淬偅閸愨晝鍘搁柣搴€ラ崘褍顥氱紓鍌氬€搁崐鎼佸磹閻戣姤鍊块柨鏂垮⒔閻瑩鏌熼悜姗嗘畷闁稿顑嗛妵鍕箻鐠虹洅锝嗐亜?婵犵數濮撮惀澶愬级鎼存挸浜鹃柡鍥ュ灩绾惧湱鐥鐐村櫤闁瑰啿鐭傚缁樻媴閸涘﹥鍎撳┑鈽嗗亝閻╊垰鐣锋导鏉戝唨妞ゆ挾鍋熼悾鐑樼箾鐎电孝妞ゆ垵鎳忛崕顐︽⒒娓氣偓濞佳囁囬銏犵？闁规儼妫勯悞鍨亜閹烘垵鏆欓柛姘贡缁辨帗娼忛妸銉﹁癁閻庢鍣崳锝呯暦閹烘嚩鎺戔枎閹冾潻闂佸疇顫夐崹鍧楀春閵夆晛骞㈡俊銈傚亾缂佺姾宕电槐鎾寸瑹閸パ勭亾闂佽桨娴囬褔顢氶敐鍡欘浄閻庯絽鐏氶弲婵嬫⒑閹稿海绠撴俊顐弮瀹?闂?  - knowledge闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熼悜妯诲暗闁崇懓绉电换娑橆啅椤旂粯鍠氶梺杞扮椤戝洭鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕濞炬櫆閸庢绻涢崱妯诲鞍闁稿﹦鏁婚弻銊モ攽閸℃侗鈧鈧鍣ｇ粻鏍蓟濞戞﹩娼╂い鎺嶇閺嬬娀姊洪崫鍕効缂傚秳绶氶妴浣肝熸笟顖滃弳闂佸憡鍔戦崝灞芥毄缂?闂傚倸鍊搁崐鐑芥倿閿曗偓椤啴宕归鍛姺闂佺鍕垫當缂佲偓婢跺备鍋撻獮鍨姎妞わ富鍨跺浼村Ψ閿斿墽顔曢梺鐟邦嚟閸嬬喖銆傞弻銉︾厱闁绘ê寮堕ˉ婊勩亜椤撯剝纭堕柟鐟板閹噣寮堕幋婵愭浆缂傚倸鍊峰ù鍥敊婵犲洦鍊块柨鏇炲€哥粻鐐烘煏婵炵偓娅呯紒鐘冲▕閺岀喓鈧稒顭囨俊鍥煕鐎ｎ偅灏甸柟椋庡Т椤斿繘顢欓崗鍏肩彋闂傚倷绀侀崥瀣矈閹绢喖鐤炬繝濠傚閸ㄦ柨鈹戦崒姘暈闁绘挾鍠栭弻鐔衡偓鐢殿焾閳ь剚鐗犻獮瀣倷濞堟寧绁繝娈垮枟閵囨盯宕戦幘瀛樺弿?闂?- 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌涘┑鍕姢闁活厽鎹囬弻锝夊箣濠垫劖缍楅梺閫炲苯澧柟铏耿瀵偊宕掗悙鏉戜患闁诲繒鍋涢幉锟犲极閸偆绡€闁汇垽娼ч埢鍫熺箾娴ｅ啿鍚樺☉妯锋闁靛繒濮烽鎴︽⒑缂佹〞鎴犵矈閺夋嚦锝夊醇閵夛妇鍘甸梺璇″瀻閸滃啰绀婇梻浣告贡閺咁偅鎱ㄩ崹顐も攳濠电姴娲﹂崐鐑芥煙缂佹ê鍧婇柛瀣崌瀹曠螖閸愩劎銈﹂梻渚€鈧偛鑻晶浼存煙閹绘帗鎲稿ù鐙呯畵瀹曟粏顦柡鈧搹顐ょ瘈闁汇垽娼у瓭濠电偛鐪伴崐妤冨垝婵犳艾绠抽柟鎯у綁缁ㄥ姊洪崫鍕犻柛搴ㄤ憾閸┾偓妞ゆ帊绶″▓妯肩磼?婵犵數濮烽弫鎼佸磻濞戙埄鏁嬫い鎾跺枑閸欏繘鏌熺紒銏犳灍闁哄懏绻堥弻鏇㈠醇濠垫劖笑婵℃鎳忕换婵嬪閿濆棛銆愬銈嗗灥濞差參宕洪姀銈呯睄闁稿本顨呮禍鐐殽閻愯尙浠㈤柛鏃€纰嶆穱濠囶敃閿濆孩鐤侀悗瑙勬磸閸ㄤ粙鐛幒鎳虫梹鎷呯化鏇炰壕闁割煈鍋嗙粻楣冩煙鐎涙绠橀柨娑樼Ф缁辨帗娼忛妸銉缂?闂?- 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌涘┑鍕姢闁活厽鎹囬弻锝夊箣濠垫劖缍楅梺閫炲苯澧柟铏耿瀵偊宕掗悙鏉戜患闁诲繒鍋涢幉锟犲极閸偆绡€闁汇垽娼ч埢鍫熺箾娴ｅ啿鍚樺☉妯锋闁靛繒濮烽鎴︽⒑缂佹﹩鐒芥い锝勭矙瀹曟垿骞橀懜闈涙瀭闂佸憡娲﹂崢浠嬪箟濞嗘挻鐓熼煫鍥ㄦ尵缁犳煡鏌ｉ悢婵嗘搐缁€鍡涙煙閻戞﹩娈曢柡鍛倐閺岋絽螣閸濆嫮楠囬悗瑙勬尭缁夌懓顫忓ú顏咁棃婵炴垼浜崣姘舵⒒閸屾艾顏╅悗姘煎墴閸┿垽骞樼拠鏌ュ敹闂佸搫娲ㄩ崰鎾诲储閻㈠憡鐓熼柣妯哄级缁€宀勬煃瑜滈崜婵嗏枍閺囥垺鍊堕柛顐犲灮绾捐棄霉閿濆娑у┑顔瑰亾濠碉紕鍋炲娆撳箺濠婂懎鍨濇繛鍡樺姇缁剁偤鏌熼弶璺ㄤ粵闁哄拑缍佸铏圭磼濡浚浜炴竟鏇㈩敇閵忕姵杈堥梺缁樏壕顓犵不妤ｅ啯鐓ユ繝闈涙閸ｈ櫣绱掗埀顒€鐣濋崟顒傚幈闂佽鍎抽顓犵不閺嶎厽鍊甸梻鍫熺◤閸嬨垻鈧娲忛崝搴ㄥ焵椤掍胶鈯曢拑杈ㄧ箾閸涱喚澧垫慨濠冩そ瀹曟粓骞撻幒宥咁棜缂傚倸鍊哥粔鏉懳涘┑鍡欐殾闁汇垹鎲￠弲婊堟煕閹炬鎷戠槐鏌ユ⒑鐠囨彃鍤辩紓宥呮缁傚秹宕奸弴鐐碉紵閻庡箍鍎遍ˇ浼存偂閸愵亝鍠愭繝濠傜墕缁€鍌涚箾閹寸儑渚涙繛鎾愁煼閺岀喖鎮滃鍡樼暥缂備胶濮甸悡锟犲蓟閺囷紕鐤€閻庯綆浜栭崑鎾诲即閻樼數鐒兼繝銏ｅ煐閸旀洜绮婚幎鑺ョ厵闁诡垳澧楅ˉ澶愭煟閹烘垹浠涢柕鍥у楠炲鎮欏顔兼疂缂傚倷妞掑鎺楀础閹惰棄钃熺€广儱鐗滃銊╂⒑閸涘﹥灏伴柣鐔叉櫅閻ｇ兘顢涢悙鑼唴闂佸吋浜介崕閬嶅礈閵娿儺娓婚柕鍫濇婢ч亶鏌涚€ｎ剙浠辩€?- 闂傚倷娴囧畷鐢稿窗閹邦喖鍨濋幖娣灪濞呯姵淇婇妶鍛櫣缂佺姵婢樿灃闁挎繂鎳庨弳娆撴煛鐎ｂ晝绐旈柡灞炬礋瀹曠厧鈹戦幇顓夛妇绱撴担鍝勵€撶紓宥勭窔瀵鏁愭径濞⒀囧箹鏉堝墽纾垮ù鐓庢喘濮?闂傚倸鍊搁崐鎼佲€﹂鍕；闁告洦鍊嬪ú顏呮櫇濞达綀顫夐崳鐑芥⒒娴ｅ湱婀介柛鈺佸瀹曞綊顢旈崼婵堬紱闂佺懓鍚嬮悰鐨?闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧悿顕€鏌熼崜浣烘憘闁轰礁锕弻鐔兼焽閿曗偓閺嬬喐銇勯锝嗙缂佺粯绻堝Λ鍐ㄢ槈閸楃偛澹夐梻?recall_memory 闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸婅埖鎱ㄥΟ鎸庣【缁炬儳娼￠弻鐔煎箚閻楀牜妫勯梺鍝勫閸庢娊鍩€椤掆偓閸樻粓宕戦幘缁樼厓鐟滄粓宕滈悢鐓庢槬闁逞屽墯閵囧嫰骞掗幋婵冨亾瑜版帒姹查柍鍝勬噺閻撴瑩鏌ц箛锝呬簼閻忓繒鏁婚弻銈吤洪鍐╁枤闂佺懓纾繛鈧い銏☆殕閹峰懘宕滃ù瀣壕婵炴垯鍨洪埛鎴︽煕濠靛棗顏存俊鎻掑悑缁绘稒寰勭€ｎ偆顦紓渚囧枛椤兘鐛Ο鑲╃＜婵☆垳鍘у铏節閻㈤潧浠﹂柛銊ョ埣閳ワ箓宕堕浣糕偓鍫曟⒑椤掆偓缁夌敻鎮￠弴銏＄厸闁稿本绮屾禒婊勭箾鐏炲倸鈧骞夐幘顔芥櫇闁稿本姘ㄩ鎰磽娓氬洤鏋ら柟铏尰閺呭爼寮婚妷锔惧幈闂佺粯鏌ㄩ幖顐ｇ闁秵鐓涚€光偓鐎ｎ剛袦濡炪們鍨洪敋妞ゎ厹鍔戝畷姗€濡搁妷鎰灴濮婄粯鎷呴懞銉ｂ偓鍐⒒閸曨偆效鐎规洘鍔曢埞鎴犫偓锝庡墮缁侊箓鏌ｆ惔顖滅У濞存粎鍋ゅ宕団偓锝庡枟閻撴稑顭跨捄鐚村姛濞寸姰鍨虹换娑㈠醇濞戞ê濮﹀┑顔硷攻濡炶棄鐣烽妸锔剧瘈闁稿本绮犻崕灞解攽閻樺灚鏆╅柛瀣姍瀹曟垿骞橀弬銉︽杸?```

- [x] **Step 2: Add few-shot example for memory**

Add the following as a new example after existing examples in `Agent.md`:

```markdown
### 缂傚倸鍊搁崐鎼佸磹妞嬪孩濯奸柡灞诲劚绾惧鏌熼幑鎰靛殭缂佺嫏鍥ㄧ厽闁归偊鍘界紞鎴炪亜閵夈儺鍎忛棁?闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熼悜妯诲暗闁崇懓绉电换娑橆啅椤旂粯鍠氶梺杞扮閿曨亪寮诲☉銏犖ㄦい鏃囧吹閺佹牠姊哄Ч鍥р偓鎰板磻閹剧粯鈷掑ù锝堟閵嗗﹪鏌涢幘瀵哥疄闁诡喚鍏橀、娑㈡倷閼肩紟鏇㈡⒑闁偛鑻晶瀛樻叏?
闂傚倸鍊搁崐鐑芥倿閿曗偓椤啴宕归鍛姺闂佺鍕垫當缂佲偓婢跺备鍋撻獮鍨姎妞わ富鍨跺? "闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸嬨倝鏌曟繛鐐珔闁搞劌鍊搁湁闁挎繂鎳庨弳鏂棵瑰鍐Ш闁哄本绋戦悾婵嬪焵椤掑嫬纾婚柣鎰惈绾剧粯绻濋棃娑卞剱闁绘挾鍠愭穱濠囧Χ閸屾矮澹曢梻浣虹帛椤ㄥ懘鏁冮鍫濈畺闁汇垻顭堢粻濠氭煛閸屾ê鍔滄い顐㈢Ч濮婃椽鎮烽弶搴撴寖濡炪倖甯楄ぐ鍐敊韫囨稑唯闁挎棁妗ㄧ花濠氭⒑閹稿孩纾甸柛瀣尵閳ь剚顔栭崰鏍ㄦ櫠鎼达絽鍨濇繛鍡樺姉缁♀偓闂佹悶鍎崝灞剧瑜版帗鈷戦柟顖嗗嫮顩伴梺绋款儏閹虫﹢骞冮悽鍛婃櫢闁绘ɑ鏋奸幏铏圭磽閸屾瑧鍔嶆い顓炴喘閹本绻濋崘顏嗩啎闁荤姴娉ч崨顖涙闂佺粯鎸堕崐婵嬪蓟閻旇櫣鐭欓柛顭戝枤濡叉澘鈹戦悙鑼妞ゃ劌妫濋獮鍫ュΩ閵夊孩妫冮崺鈧い鎺戝閸嬪鐓崶銊︾闁活厼妫楅…璺ㄦ崉鐞涒€愁潓閻熸粎澧楃敮妤呭磻閹邦厹浜滈柡鍐ㄥ€哥敮璺衡攽椤斿ジ鍙勬慨濠呮閹风娀鍨鹃搹顐や憾婵＄偑鍊戦崝宀勬偋閹炬剚鍤曟い鎰跺瘜閺佸鏌嶈閸撶喖濡存担绯曟瀻闁圭偓娼欓惂鍕節閵忥絾纭惧┑鍌涙瀹曟瑦绂掔€ｎ偀鎷绘繛杈剧导鐠€锕傚绩閻楀牏绠惧璺侯儑濞叉挳鏌℃担绋挎殻濠德ゅ煐缁旂喖鏁冮埀顒€煤椤撶偟鏆﹂柨婵嗘缁剁偤鎮橀悙鍙夊暈闁诲繐妫濆缁樻媴閾忕懓绗″銈庡幖閻楁捇銆佸鎰佹▌閻庤娲忛崹浠嬬嵁濮椻偓椤㈡瑩鎸婃径鍡椾壕闁汇垹鎲￠悡鐔兼煟閺冨倸甯跺ù婊呭娣囧﹪骞撻幒鏃傂ㄩ梺璇″枙缁瑩銆佸☉妯锋婵炲棗绻掗敍鎾绘煟鎼淬値娼愭繛鍙夌矒瀹曟螣鐠佸磭绠氶梺褰掓？閻掞箓寮插鍫熺厽闁挎繂鎳撶€氭壆绱掗懠顒€甯堕柍瑙勫灴閹瑩寮堕幋鐘辨闂備胶鎳撻幉锟犲箖閸岀偛鏋侀柛鎰靛枛鍥存繝銏ｆ硾閿曪箓鎮?

闂?save_memory(category="preference", content="闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧粻鐘荤叓閸ャ劎鈯曢柛搴㈩殕閵囧嫰寮崹顔规寖缂備胶濮靛Λ鍐蓟濞戞矮娌柛鎾椻偓濡插牏绱撴担绋款暢闁稿鍠栭崺鈧い鎺嗗亾缂佺姴绉瑰畷鏇熸綇閳规儳浜炬慨妯煎帶濞呭秹鏌熼娆戝妽闁诡垱妫冩俊鎼佹晜閹冪婵犵數鍋犻幓顏嗗緤娴犲绠烘繝濠傚濞呯娀鏌曡箛濠冨櫚闁稿鎹囧畷鐑筋敇瑜忛崝鎼佹⒑闂堟稓澧㈡い顓炵墦椤㈡岸鏁愭径濠勵啋濡炪倖妫侀崑鎰邦敊閹烘埈娓婚柕鍫濇閳锋劙鏌涙惔銏犫枙闁瑰嘲绻掗埀顒婄秵閸犳鍩涢幋锔界厵缂佸瀵ч幑锝夋煃閽樺妯€闁哄被鍊曠叅閻犲洩灏欐禒顓犵磽娴ｇ鈧摜绮旈悷鎵殾闁靛濡囩弧鈧梺鍛婃处閸ㄩ亶顢撳澶嬧拻濞达絿顭堥幃鎴澝瑰鈧划娆忕暦閺囥垹钃熼柕澶涚畱娴犙囨⒑閻熸澘鈷旂紒顕呭灦閸╂盯骞掑Δ浣哄幈闁诲繒鍋涙晶浠嬪煀閺囩姷纾界€广儱妫楅悘鎾煛瀹€瀣М闁轰焦鍔欏畷姗€濡搁妷顔界秵濠德板€楁慨鐑藉磻閻愬灚鏆滈柨鐔哄Х瀹撲線鏌熼悜姗嗘當缂佺媴绲鹃妵鍕箻鐠虹儤娅╅梺鍐叉惈閸婅崵绮?)
闂?婵犵數濮烽弫鎼佸磻閻樿绠垫い蹇撴缁躲倝鏌﹀Ο鐚寸礆婵炴垶顭傞弮鍫濆窛妞ゆ挾鍋涙禍鑸电節閻㈤潧浠﹂柛銊ュ閸犲﹤顓兼径濠勵槯濠电姴锕ょ€氥劍绂嶅鍫熺厸闁告劧绲芥禍鎯ь渻閵堝棗鐏﹂柣鐔叉櫅閻ｇ兘濡烽埡浣哄€炲銈嗗笂閼冲爼宕ｉ崱妞绘斀闁绘劖娼欓悘锕傛煟閻旀繂娲ょ粻鐑樸亜閵堝浂鍔朹user(type="confirm", question="闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸嬨倝鏌曟繛鐐珔闁搞劌鍊搁埞鎴﹀磼濮橆剦妫岄梺杞扮閿曨亪寮诲☉銏犖ㄩ柨婵嗘噹椤绻濆▓鍨仭闁瑰憡濞婇幃锟狀敃閿曗偓閻愬﹦鎲告惔銊ョ闁挎繂顦伴悡鏇㈡煟閺傚灝娈╅棅顒夊墴閺岋紕浠︾拠鎻掝瀳闂佸疇妫勯ˇ顖炲煝鎼淬劌绠ｉ柣妯诲絻缂嶅棛绱撻崒姘偓鎼佸磹閸濄儳鐭撻柣銏犳啞閺呮繈鏌曡箛鏇烆€岄柛銈嗘礋閺岀喓绱掑Ο杞板垔濠电偛鐨烽弲婊堝Φ閸曨垰绠涢柍杞拌閸嬫挸螖閸涱厾鐤呭銈呯箰閹虫劗寮ч埀顒勬⒑闂堟盯鐛滅紒鎻掑⒔濞戠敻宕滆绾剧厧顭跨捄鐚村姛闁挎稑绉堕埀顒侇問閸燁偊宕惰椤︽澘顪冮妶鍡欏缁炬澘绉归幃妤咁敆閸曨兘鎷洪梺鍛婃尰瑜板啯绂嶉弽顓熺厱闁靛鍎崇粔娲煙瀹曞洤浠辨鐐查叄閹崇偤濡疯楠炴劙姊绘担瑙勫仩闁稿寒鍨跺畷婵嗩吋閸ワ妇鍓ㄩ梺鎸庢礀閸婂綊鎮￠悢鍝ョ瘈闁割煈鍋勬慨鍥ㄧ箾閸涱厾效闁哄备鍓濋幏鍛村传閵夋劑鍊曢湁闁绘瑥鎳愰悾鍨叏婵犲懎鍚归柍褜鍓欓悘姘跺箖閸岀偞鍊垫繛宸簼閳锋帒霉閿濆懏鍟為柛鐔哄仱閺屻倝鎮烽弶搴撴寖闂佸吋妞芥禍鍫曞箠閺嶎厼鐓涢柛灞诲€栫紞妤佷繆閻愵亜鈧牠骞愰崼鏇炲瀭闁革富鍘鹃惌鍡涙煕瀹€鈧崑鐐烘偂閺囩喆浜滈柟鏉垮閹偐绱掗悩绛硅€块柡宀嬬節瀹曞崬螣濞茬粯顥堥梻浣告惈閻ジ宕伴弽顓炵畺婵犲﹤鍚橀悢鍏兼優闁革富鍘介崵鍐ㄢ攽閻樺灚鏆╅柛瀣洴楠炲﹥鎯旈敐鍌氫壕婵﹩鍘界欢鍙夈亜椤愩垻绠茬紒缁樼箓椤繈顢楅崒鐐靛礈闂傚倷娴囬～澶愬箚瀹€鍕偍闁瑰瓨甯為弰鍌氣攽閻樺灚鏆╅柛瀣仱瀹曞湱鎹勬笟顖涚稁缂傚倷鐒﹁摫闁告瑥绻愰湁闁稿繐鍚嬬紞鎴︽煟閹烘垹浠涢柕鍥у楠炴帡宕卞鎯ь棜闂傚倷鑳堕…鍫ユ晝閵夆晛绠栭柛宀€鍋戦埀顑跨椤繃锛愬┑鍥ㄦ珨闂備線鈧偛鑻晶顕€鏌ｉ敐鍥у幋濠碉紕鍏樻俊閿嬫償閵忊檧鎷婚梺閫炲苯澧剧紓宥呮瀹曟粌鈻庨幘宕囩暰?)
闂?闂傚倸鍊搁崐鐑芥倿閿曗偓椤啴宕归鍛姺闂佺鍕垫當缂佲偓婢跺备鍋撻獮鍨姎妞わ富鍨跺浼村Ψ閿斿墽顔曢梺鐟邦嚟閸嬬喖銆傞弻銉︾厱闊洦姊婚惌瀣煏閸パ冾伃鐎殿噮鍣ｉ崺鈧い鎺戝閺佸嫭绻涢崱妯诲碍閻?闂?save_memory
闂?闂傚倸鍊搁崐鐑芥倿閿曞倸绠栭柛顐ｆ礀绾惧潡鏌熼幆鐗堫棄缁惧墽绮换娑㈠箣閺冣偓閸? "婵犵數濮烽弫鍛婄箾閳ь剚绻涙担鍐叉搐绾剧懓鈹戦悩瀹犲闁汇倗鍋撻妵鍕箛閵婏箑娅氶梺鍝勵儐濡啴寮婚悢鍛婄秶濡わ絽鍟宥夋⒑閸濆嫭濯奸柛鎾跺枛楠炲啫顫滈埀顒勫箖濞嗘挻鍤嬫繛鍫熷椤ュ姊绘担瑙勫仩闁稿﹥鐗滈弫顕€鏁撻悩鑼暫闁荤喐鐟ョ€氼噣鎮疯ぐ鎺撶厓鐟滄粓宕滈悢鐓幬ラ柛宀€鍋為弲婊堟煕閹炬鎷嬪Σ鎼佹⒒娴ｈ鍋犻柛搴㈡そ瀹曟粌鈻庨幒鏃傤啍闂傚倸鍊烽懗鍫曗€﹂崼銉ュ珘妞ゆ帒瀚崑锟犳煏閸繃绌垮┑顔煎暱闇夐柣鎾虫捣閹界娀鏌ｉ幘瀛樼闁逛究鍔岄～婊堝幢濡も偓椤亪姊洪崷顓燁仧缂傚秳绶氬濠氬焺閸愨晛顎撻柣鐔哥懃鐎氼剛澹曢崘鍙傛棃鎮╅棃娑楃捕濡炪倖鍨甸ˇ鐢告偘椤曗偓瀹曞爼顢楁径瀣珜濠电姰鍨煎▔娑㈡偡閳哄懎鐓涢柛灞剧矌椤旀洟姊洪悷閭﹀殶闁稿鍋ら崺娑㈠箳閹存梹鏂€濡炪倖娲嶉崑鎾剁磼閻樺磭澧甸柕鍡曠椤粓鍩€椤掑嫮宓侀柡宥冨妽婵挳鏌涘┑鍕姶婵″弶鎸冲缁樻媴閸涘﹨纭€闂佺绨洪崐婵嬬嵁閹邦厾绡€婵絿顭堝ú鈺吽囬弻銉︻梿濠㈣埖鍔栭悡鏇㈢叓閸ャ劏澹樺ù婊冪秺閺岋綁骞欓崘銊т化缂備浇椴哥敮妤咃綖閹达箑鍐€鐟滃秶鐚惧澶嬪€甸悷娆忓缁€鍐┿亜閵娿儻宸ラ柣锝囧厴閹剝鎯斿Ο缁樻澑闂備礁澹婇崑鍡涘窗閹伴偊鏁囧Δ锝呭暞閳锋帒霉閿濆懏鍟為悹鎰剁節閺屾稒鎯斿☉妯峰亾濡ゅ懎鏋佹い鏂挎閺冨牆鐒垫い鎺戝閻撴繄鈧箍鍎遍ˇ顖滅矆鐎ｎ偁浜滈柡宥冨妿閳绘捇鏌熷畡閭︾吋闁哄矉绲鹃幆鏃堝閳垛晛顫岄梺钘夊暢妞存悂濡甸崟顔惧敥闂佸憡娲﹂崢楣冾敊閺囥垺鈷戦柛鎾村絻娴滄牠鏌涢妸顭戞綈缂佸倹甯￠、娑㈡倷鐎电甯?

闂傚倸鍊搁崐鐑芥倿閿曗偓椤啴宕归鍛姺闂佺鍕垫當缂佲偓婢跺备鍋撻獮鍨姎妞わ富鍨跺? "闂傚倸鍊搁崐鎼佲€﹂鍕；闁告洦鍊嬪ú顏呮櫇濞达綀顫夐崳鐑芥⒒娴ｅ湱婀介柛鈺佸瀹曞綊顢旈崼婵堬紱闂佽鍎抽顓犵不妤ｅ啯鐓欓悗鐢殿焾娴狅箓鏌ｉ幘鍗炲姕闁靛洤瀚伴獮瀣攽閸パ勵仭闂備礁鎼幊搴ㄦ偉婵傜绠栭柍鍝勬噹閸ㄥ倹銇勯幇鈺佺伄鐟滅増鎸冲铏规嫚閺屻儱寮板┑鐐板尃閸パ呯枀闂佽法鍠撴慨鐢稿磻閳哄懏鈷戞い鎺嗗亾缂佸鏁婚幃鈥斥槈閵忥紕鍘遍梺瑙勬緲婢у海绮欑紒妯肩闁告侗鍘奸弳鐔虹磼鏉堛劌绗掗摶鏍煃瑜滈崜鐔风暦閹扮増鍋￠梺顓ㄧ畱濞堫偊姊洪崨濠冨闁稿甯″畷銉р偓锝庡枟閻撴洟鏌￠崶銉ュ妤犵偞蓱娣囧﹪宕ｆ径濠勪紝濠殿喖锕﹂崕銈咁焽椤忓牆绠ユい鏃傚帶椤绻濋悽闈浶為柛銊︽そ閺佸啴濮€閵堝啠鍋?

闂?recall_memory(query="闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧悿顕€鏌ｅΟ娆惧殭闁汇倗鍋撶换娑㈠幢濡櫣浠肩紓浣哄У濡啴寮诲☉姘勃闁告挆鈧Σ鍫㈢磽娴ｇ顣抽柛瀣枛閸┾偓妞ゆ巻鍋撶紒鐘茬Ч瀹曟洘娼忛埞鎯т壕婵鍘у▍宥夋煙椤栨瑧鍔嶉柟顖涙婵℃悂鏁傞幆褍绠版繝鐢靛仩閹活亞绱為埀顒併亜椤愩埄妲烘繛鍡愬灲瀹曪絾寰勯崼婊呯泿?)
闂?闂傚倸鍊搁崐鐑芥嚄閸洖绠犻柟鍓х帛閸婅埖鎱ㄥΟ鎸庣【缁炬儳娼￠弻鐔煎箚閻楀牜妫勯梺鍝勫閸庢娊鍩€椤掆偓閸樻粓宕戦幘缁樼厓鐟滄粓宕滈悢鑲╁祦闊洦娲嶉崑鎾绘晲鎼粹剝鐏堢紓浣哄珡閸ャ劌浠梺璇″幗鐢帗淇婇崸妤佺厽?闂?闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁嶉崟顒佹闂佺粯鍔曢顓犵不妤ｅ啯鐓冪憸婊堝礈濮樿鲸宕?闂?闂傚倸鍊搁崐鐑芥倿閿曞倸绠栭柛顐ｆ礀绾惧潡鏌熼幆鐗堫棄缁惧墽绮换娑㈠箣閺冣偓閸? "闂傚倷娴囬褍霉閻戣棄绠犻柟鎹愵嚙缁犵喖姊介崶顒€桅闁圭増婢樼粈鍐┿亜閺冨倸甯堕柣搴弮閹嘲顭ㄩ崨顓ф毉闁汇埄鍨遍〃濠囧春濞戙垹绫嶉柛顐ゅ枔閸橆亪姊洪崜鎻掍簼缂佽瀚弲鍫曞閵忋垻锛滈梺缁橆焾鐏忔瑧绮斿ú顏呯厸閻忕偟顭堟晶鑼磼閺冨倸鏋庨柍鐟板暣瀹曞綊顢欓悷棰佸闂侀潧鐗嗛ˇ顖炴嚋瑜版帗鐓曟い鎰剁稻缁€鍫ユ煕濞嗘劖宕岄柡灞剧洴婵＄兘骞嬪┑鍡╀紝濠碘槅鍋呴崹鍨潖?
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
        {"role": "user", "content": "婵犵數濮烽弫鎼佸磻閻樿绠垫い蹇撴缁躲倝鏌熺粙鍨劉闁告瑥绻橀弻鐔虹磼閵忕姵鐏堥柛?},
        {"role": "assistant", "content": "婵犵數濮烽弫鎼佸磻閻樿绠垫い蹇撴缁躲倝鏌熺粙鍨劉闁告瑥绻橀弻鐔虹磼閵忕姵鐏堥柛銉ョ摠缁绘稓鈧數顭堝瓭濡炪倖鍨靛Λ婵嗩嚕閺屻儺鏁嗛柍褜鍓熷﹢渚€姊洪幐搴ｇ畵闁绘绮岄…鍥箛椤斿墽锛滈梺缁樏崯璺ㄧ箔閹烘顥嗗鑸靛姈閻撶喐鎱ㄥΔ鈧Λ妤佺濠婂厾鐟邦煥閸涱厺澹曠紓浣虹帛閻╊垶鐛€ｎ喗鍊烽悗鐢殿焾瀵娊姊绘担铏瑰笡妞ゃ劌鎳庤灋婵犲﹤鐗嗘闂佸湱澧楀姗€鎯屽Δ鈧…璺ㄦ崉閾忓湱鍔稿┑鐐存綑鐎氭澘顫忓ú顏咁棃婵炴垼椴歌倴闂備胶顭堝锔界椤掑嫭鍤嶉弶鍫氭櫆鐎氭岸鎮锋担椋庮槮缂傚秴锕顐﹀箛閺夎法鍊炲銈庡墻閸犳捇宕曢懠顒佸床婵炴垯鍨归柋鍥煟閺冨牜妫戝ù鐓庣焸濮?},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    """Long conversations should have older messages compressed."""
    messages = [{"role": "system", "content": "System prompt"}]
    # Add 20 user/assistant pairs
    for i in range(20):
        messages.append({"role": "user", "content": f"闂傚倸鍊搁崐鐑芥倿閿曗偓椤啴宕归鍛姺闂佺鍕垫當缂佲偓婢跺备鍋撻獮鍨姎妞わ富鍨跺浼村Ψ閿斿墽顔曢梺鐟邦嚟閸婃垵顫濋鈺嬬秮瀹曞ジ濡烽敂鎯у箞婵＄偑鍊栭崝鎴﹀磹閺囥垹鍑犵€广儱娲ㄧ壕?{i}"})
        messages.append({"role": "assistant", "content": f"闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁撻悩鑼舵憰闂佽法鍠撴慨鎾偪閻愵剛绡€濠电姴鍊搁顏呯箾閸涱垰校缂佺粯绻冪换婵嬪磼濠婂喚鏆梻浣虹帛閸旀洟鏁冮鍫濊摕闁挎繂顦粻娑欍亜閹哄秷顔夐柡瀣懃閳?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀閽冪喖鏌曟繛鐐珦闁轰礁瀚伴弻娑樷槈閸楃偞鐏嶅┑鐐叉噽婵炩偓闁哄矉绲借灒闁兼祴鏅涚粭锟犳⒑缁嬪潡顎楃紒澶婄秺瀵鈽夐姀鐘插祮闂侀潧顭堥崕浼存嚋椤忓牊鈷戦柟鑲╁仜閳ь剚顨嗙换娑㈠焵椤掑嫭鐓欐い鏃囧亹缁夎櫣鈧娲栭悥鍏间繆濮濆矈妲鹃梺浼欑秮娴滆泛顫忓ú顏呭亗閹艰揪绲肩划鐢告⒑閹肩偛濡兼繛灏栤偓鎰佸殨妞ゆ劑鍩勯崥瀣煕濞戝崬鐏℃繛鍫熸礋濮婃椽鏌呴悙鑼跺濠⒀冾嚟閳ь剚顔栭崳顕€宕戞繝鍐х箚闁兼悂娼х欢鐐测攽閻樻彃顏撮柛姘嚇閺岋絾鎯旈敐鍡楁畬闁诲孩鍑归崢濂糕€﹂崹顔ョ喖鎮℃惔锝囩摌婵犵數鍋涘Ο濠冪濠靛鐓曢柟瀵稿亼娴滄粓鏌熼懜顒€濡煎褍寮堕妵鍕晝閸屻倖顥栫紓?0闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曚綅閸ヮ剦鏁冮柨鏇楀亾缂佲偓閸喓绡€闂傚牊绋撴晶銏ゆ煟椤撶喐宕岄柡宀嬬秮楠炲鏁愰崱鈺傤棄缂傚倷鑳舵慨鐢垫暜濡ゅ懎桅闁告洦鍨伴崘鈧梺闈涱槶閸庮噣宕戦幘婢勬棃宕橀鍡欏姸濠电姰鍨奸崺鏍礉閺嶎厽鍋傞柡鍥ュ灪閻撴盯鏌涚仦鍓х煀闁告柨顑嗙换娑㈠川椤撶噥妫炲銈庡弨閸庡藝瀹曞洨纾兼い鏃囧Г瀹曞瞼鈧鍠栭…宄扮暦婵傜唯闁挎洍鍋撻柣褍瀚换婵嬪閿濆棛銆愬銈忕畳妞存悂濡靛▎鎾存優妞ゆ劑鍊楅鏇㈡煟鎼淬垻鈯曟い顓炴喘閹本绻濋崘褏绠氬銈嗗姧缂嶅棗鈻撻弮鍫熷亗闁靛牆顦伴悡娑氣偓骞垮劚閸燁偅淇婇懖鈺冪＜闁告挷绀佹禒褔鏌嶈閸撴瑧绮诲澶婄？闂侇剙绉撮悿顕€鏌ｅΟ娆惧殭缁?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # System prompt should be preserved
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"

    # Should have a summary message
    assert any("婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀閽冪喖鏌曟繛鐐珦闁轰礁瀚伴弻娑樷槈閸楃偞鐏嶅┑鐐叉噽婵炩偓闁哄矉绲借灒闁兼祴鏅涚粭锟犳⒑缁嬪潡顎楃紒澶婄秺瀵鈽夐姀鐘插祮闂侀潧顭堥崕浼存嚋椤忓牊鈷戦柟鑲╁仜閳ь剚顨嗙换娑㈠焵椤掑嫭鐓? in m.get("content", "") for m in result)

    # Recent messages should be preserved (last 12 non-system messages = 6 pairs)
    assert len(result) <= 14  # system + summary + 12 recent


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    """The most recent messages should be kept intact."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(20):
        messages.append({"role": "user", "content": f"濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌ｉ姀鐘冲暈闁稿顑呴埞鎴︽偐閹绘帗娈?{i}"})
        messages.append({"role": "assistant", "content": f"闂傚倸鍊搁崐鐑芥倿閿曞倸绠栭柛顐ｆ礀绾惧潡鏌熼幆鐗堫棄缁惧墽绮换娑㈠箣閺冣偓閸?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曢敃鈧悿顕€鏌ｅΟ娆惧殭闁汇倗鍋撶换婵囩節閸屾碍鐏曢梺鍏兼緲濞硷繝寮婚妸銉㈡婵☆垯璀︽禒閬嶆⒑缁嬫鍎愰柟鐟版喘楠炲啴鎸婃径鍡樼亖闂佸湱顭堢€涒晠寮抽悙鐑樷拻濞达綁顥撴稉鑼磽閸屾稒鐨戦柛鎺撳笒閳诲酣骞樼捄铏广偊婵犲痉鏉库偓鎰板磻閹剧粯鎳氶柨婵嗘缁犻箖鏌涢埄鍐噧濞存粓绠栭弻?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # Last message should be the most recent assistant reply
    assert result[-1]["content"] == "闂傚倸鍊搁崐鐑芥倿閿曞倸绠栭柛顐ｆ礀绾惧潡鏌熼幆鐗堫棄缁惧墽绮换娑㈠箣閺冣偓閸?19"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: FAIL 闂?`ImportError: cannot import name 'compress_conversation_history'`

- [ ] **Step 3: Add compress_conversation_history to context_compressor.py**

Append to `app/services/context_compressor.py`:

```python
from app.agent.llm_client import chat_completion as _chat_completion

_SUMMARIZE_PROMPT = """闂傚倸鍊峰ù鍥х暦閸偅鍙忛柡澶嬪殮濞差亶鏁囬柍璺烘惈椤︾敻鐛Ο鍏煎珰闁告瑥顦遍埀?-3闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁撻悩鍐蹭画闂佹寧绻傞ˇ顖滃閸ф鐓欑紓浣靛灩閺嬬喖鏌涙惔鈽呭伐闂囧鏌ｅΟ鐑樷枙闁稿骸绻掔槐鎺楁偐閸愯尙浼岄梺鍝勮閸婃牠骞堥妸鈺佺疀妞ゆ垼妫勬禍鐐繆閵堝倸浜鹃梺宕囩帛濡啯鎱ㄩ埀顒勬煟濡儤顥滅紓宥咃躬楠炲啴鍩￠崪浣规櫓闂佺粯鎸告鎼侊綖閹烘梻纾介柛灞剧懅閸斿秵銇勯妸銉﹀殗妤犵偛锕獮鍥级鐠恒劌濮︽俊鐐€栫敮鎺楀磹瑜版帒姹查柍鍝勫€舵禍婊堟煏韫囨洖顎撻棅顒夊墴閺岀喖顢涘▎鎴濆缂備礁鍊圭敮鐐哄焵椤掑﹦绉靛ù婊呭仱钘濋柕濞炬櫆閳锋垿鏌涘☉姗堟缂佸爼浜堕弻娑樷枎韫囨稑寮伴悗瑙勬处閸ㄨ泛鐣烽崼鏇ㄦ晢濞达絽鎼敮楣冩⒒娴ｈ櫣銆婇柛鎾寸箞閵嗗啴宕ㄩ弶鎴犲姦濡炪倖宸婚崑鎾寸箾鐏忔牑鍋撳畷鍥ㄦ闂佽鍎煎Λ鍕不閻熸噴褰掓晲閸ャ劌娈岄梺閫炲苯澧伴柛蹇斆～蹇撁洪宥嗘櫇闂佹寧绻傚ú銏ゅ焵椤掍礁绗х紒杈ㄥ浮閹晜娼忛埡鍐幆闂備礁鎼惌澶岀礊娓氣偓瀵偊骞囬弶鍨€垮┑鐐叉閸旀洖鈻撹箛鏇犵＝闁稿本鐟чˇ锔炬喐閺夋妯€鐎规洩绻濋獮搴ㄦ寠婢跺瞼鏆┑鐐差嚟婵挳顢栭崨顔煎姅闂傚倷鐒︾€笛兠哄澶婄；闁瑰墽绮悡鐔兼煙閹呮憼缂佲偓鐎ｎ喗鐓涢悘鐐插⒔閵嗘帡鏌嶈閸撱劎绱為崱娑樼；闁糕剝绋掗崑鍌涖亜閺嶃劎鐭岀痪鎯с偢閺屾洘绻涢崹顔句患婵犫拃鍡楃毢缂佽鲸甯″畷鎺戔槈濡槒鐧侀梻浣虹《閺備線宕戦幘鎰佹富闁靛牆妫楃粭鍌炴煠閸愯尙鍩ｉ柛鈹垮灲瀵挳濮€閿涘嫬骞堟俊鐐€栭崝鎴﹀磹閺囥垹鍑犻柟杈鹃檮閻撴瑦銇勯弽銊с€掗柟鍐插暣濡焦寰勯幇顓犲弳濠电娀娼уΛ娆撍夊鍕闁割偁鍨归埢鍫ユ煛鐏炵晫啸妞ぱ傜窔閺屾稖绠涢弮鍌涘垱闂佺娅曢〃濠傜暦婵傜鍗抽柣鎰悁缁辨粍绻濈喊妯活潑闁搞劋鍗冲畷銉р偓锝庡亜閸ㄦ柨鈹戦崒姘暈闁绘挸绻橀弻娑㈩敃閿濆洨鐣靛銈呮禋閸嬪﹪寮诲☉銏″亜闁告垯鍊曟导鎰版⒒閸パ屾█闁哄矉绲介～婊堝幢濡炲墽鐩庡┑鐐茬摠缁酣宕戦幘鑸靛床婵炴垯鍨圭粻锝夋煟閹邦剦鍤熼柛娆忔濮婅櫣绱掑鍡樼暥闁诲孩鐭崡鍐茬暦濞差亜鐒垫い鎺嶉檷娴滄粓鏌熺€电浠滄い鏇熺矌缁辨帗鎷呭畡鏉跨ギ闂佸搫鏈ú鐔风暦閸楃倣鏃堝焵椤掑嫬姹查柣鎰嚟缁犻箖鏌ｉ幘铏崳缂佺姾宕甸埀顒冾潐濞测晝绱炴担閫涚箚闁汇値鍨煎Σ濠氭⒑閸濆嫭鍣抽柡鍛矌閹广垹鈽夊锝呬壕闁汇垺顔栭悞鍓ф偖閵夆晜鈷戠紒瀣儥閸庢劙鏌熼崨濠冨€愰柛鈹垮劜瀵板嫰骞囬渚囨闂佽崵濮垫禍浠嬪礉瀹€鍕┾偓鍌炴倻濡偐顔曢柣搴㈢⊕椤洭鎯屾繝鍥ㄧ厵閻犲泧鍛紵缂傚倸鍊归幑鍥箠閻愬搫唯闁挎洍鍋撶€殿喖娼″铏规兜閸涱厾鍔烽梺鍛婃煥閺堫剛绮?""


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
        summary = response.get("content", "闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熸潏楣冩闁稿顑呴埞鎴︽偐闊叀鎶楀┑鐐村灟閸╁嫰寮崶顒佺厪闊洦娲栧瓭闂佺粯绻冮敃銏狀潖閾忓湱纾兼俊顖濆吹閸欏棗顪冮妶鍐ㄥ闂佸府绲介悾鐑芥偨閸涘﹤浜圭紓鍌欑劍閿氬ù鐙€鍨跺娲箹閻愭彃濮岄梺鍛婃煥濞撮鍒掓繝姘唨妞ゆ挾鍠撻崢鐢告⒑閸︻厾甯涢悽顖滃仱閺佸秴顓兼径瀣幍闂佽偐鈷堥崜娆撱€傛總鍛婄厵鐎瑰嫮澧楅崳鐑樸亜閿旀儳顣奸柟顖涙閺佹劙宕卞Δ浣轰簮闂傚倸鍊搁崐椋庣矆娓氣偓楠炲鏁撻悩鍐蹭画濡炪倖鐗滈崑娑㈠垂閸岀偞鐓欓柟顖滃椤ュ鏌＄€ｂ晝绐旈柡灞炬礋瀹曠厧鈹戦幇顓壯囨⒑?)
    except Exception:
        summary = "闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樻噽閻瑩鏌熸潏楣冩闁稿顑呴埞鎴︽偐闊叀鎶楀┑鐐村灟閸╁嫰寮崶顒佺厪闊洦娲栧瓭闂佺粯绻冮敃銏狀潖閾忓湱纾兼俊顖濆吹閸欏棗顪冮妶鍐ㄥ闂佸府绲介悾鐑芥偨閸涘﹤浜圭紓鍌欑劍閿氬ù鐙€鍨跺娲箹閻愭彃濮岄梺鍛婃煥濞撮鍒掓繝姘唨妞ゆ挾鍠撻崢鐢告⒑閸︻厾甯涢悽顖滃仱閺佸秴顓兼径瀣幍闂佽偐鈷堥崜娆撱€傛總鍛婄厵鐎瑰嫮澧楅崵鍥煙椤旂晫鐭婇摶锝囩磽娴ｇ櫢渚涘ù鐘欏洦鈷掗柛灞剧懆閸忓矂鏌熼搹顐ｅ磳闁诡喗妞芥俊鎼佸煛娴ｄ警妲烽梻浣告惈濞层垽宕圭憴鍕垫敯闂傚倷鑳堕幊鎾活敋椤撶喐鍙忛柣銏㈩暯閸嬫挸顫濋澶屽悑闂佸搫鏈ú妯侯嚗閸曨倠鐔兼惞闁稑瀵茬紓鍌氬€风拋鏌ュ磻?

    summary_msg = {
        "role": "user",
        "content": f"[婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀閽冪喖鏌曟繛鐐珦闁轰礁瀚伴弻娑樷槈閸楃偞鐏嶅┑鐐叉噽婵炩偓闁哄矉绲借灒闁兼祴鏅涚粭锟犳⒑缁嬪潡顎楃紒澶婄秺瀵鈽夐姀鐘插祮闂侀潧顭堥崕浼存嚋椤忓牊鈷戦柟鑲╁仜閳ь剚顨嗙换娑㈠焵椤掑嫭鐓欐い鏃囧亹缁夎櫣鈧娲栭悥鍏间繆濮濆矈妲鹃梺浼欑稻濡炶棄顫忛搹瑙勫枂闁告洦鍋嗙粊椋庣磼閸撗嗘闁告瑥鍟撮悰顔藉緞閹邦厼浜遍梺鍓插亐閹冲洭寮?{summary}",
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
- [ ] Plan 4: Memory + 婵犵數濮烽弫鎼佸磻閻愬搫鍨傞柛顐ｆ礀缁犱即鏌熼梻瀵稿妽闁哄懏绻堥弻銊モ攽閸℃ê绐涚紓浣哄У濡啴寮诲☉妯锋婵炲棙鍔楃粙鍥р攽閳藉棗浜濋柨鏇樺灲瀵鈽夐姀鐘栥劑鏌曡箛濠傚⒉闁绘繐绠撳娲川婵犲倻鍔伴梺绋款儐閹瑰洤顫忕紒妯诲闁芥ê顦幆鐐烘⒑缁嬫鍎愮紒瀣灱閻忓鏌ｆ惔銊︽锭闁硅绻濋敐?0 婵?task闂?```

Update "闂傚倷娴囧畷鐢稿窗閹邦喖鍨濋幖娣灪濞呯姵淇婇妶鍛櫣缂佺姳鍗抽弻娑樷槈濮楀牊鏁惧┑鐐叉噽婵炩偓闁哄矉绲借灒闁绘垶菤閺嬫瑥鈹戦悙鐑橈紵闁告濞婂濠氬Ω閵夈垺鏂€闂佺硶鍓濋敋婵炲懌鍊濆缁樼節鎼粹€斥拻闂佸憡鎸鹃崰鏍ь嚕婵犳碍鍋勯柧蹇撴贡閻ｈ泛鈹戦悙鏉戠仸閽冮亶鏌ㄥ☉妯夹ч柡宀嬬節閸┾偓? to reflect Plan 4 completion.

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with Plan 4 completion status"
```
