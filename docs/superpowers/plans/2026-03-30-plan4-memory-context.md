# Plan 4: Memory 缂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣椤愪粙鏌ㄩ悢鍝勑㈤柛銊ュ€垮濠氬醇閻旀亽鈧帡鏌￠崱顓犵暤闁哄矉缍佹慨鈧柕鍫濇闁款參姊?+ 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔兼⒒鐎电濡介梺鍝勬噺缁诲牓寮婚妸銉㈡斀闁糕剝锚缁愭稓绱撴担鍝勑ｆ俊顐㈠暣瀵鈽夊Ο閿嬵潔濠电偛妫欓崝妤冪矙閸パ€鏀介柍钘夋娴滄繈鏌ㄩ弴妯虹伈鐎殿喛顕ч埥澶愬閻樻牓鍔戦弻鏇＄疀婵犲倸鈷夐梺缁樼箰缁犳挸顫忓ú顏勫窛濠电姴鍊婚崝浼存⒑缁嬫鍎愰柟鐟版搐椤?
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer memory system (working/short-term/long-term) and context window management to keep conversations coherent across sessions without blowing up the context window.

**Architecture:** Memory CRUD service handles persistence. Two new agent tools (`recall_memory`, `save_memory`) give the LLM on-demand access. Tool result compression summarizes verbose outputs inline. Session lifecycle hooks generate summaries and extract memories at session end. The system prompt builder loads hot/warm memories at session start.

**Tech Stack:** SQLAlchemy async (existing), OpenAI-compatible LLM for summarization, existing agent tool system

**Depends on:** Plan 1 (Memory, SessionSummary, ConversationMessage models), Plan 2 (agent loop, tool_executor, llm_client)

---

## File Structure

```
student-planner/
闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?app/
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?services/
闂?  闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?memory_service.py          # Memory CRUD: create, query, update, delete, staleness
闂?  闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱閸╂牠宕濋弴銏″珔闁绘柨鍚嬮悡銉╂煟閺傛寧鎯堢€涙繄绱撻崒娆掝唹闁哄懐濞€瀵寮撮敍鍕澑闁诲函缍嗘禍鏍磻閹捐鍗抽柕蹇娾偓鍏呯暗婵犳鍠楅妵娑㈠磻閹剧粯鐓?context_compressor.py      # Tool result summarization + conversation compression
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?agent/
闂?  闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?tools.py                   # (modify: add recall_memory, save_memory definitions)
闂?  闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?tool_executor.py           # (modify: add recall_memory, save_memory handlers)
闂?  闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?loop.py                    # (modify: add tool result compression after each tool call)
闂?  闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?context.py                 # (modify: add hot/warm memory loading)
闂?  闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱閸╂牠宕濋弴銏″珔闁绘柨鍚嬮悡銉╂煟閺傛寧鎯堢€涙繄绱撻崒娆掝唹闁哄懐濞€瀵寮撮敍鍕澑闁诲函缍嗘禍鏍磻閹捐鍗抽柕蹇娾偓鍏呯暗婵犳鍠楅妵娑㈠磻閹剧粯鐓?session_lifecycle.py       # Session end: generate summary + extract memories
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?routers/
闂?  闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱閸╂牠宕濋弴銏″珔闁绘柨鍚嬮悡銉╂煟閺傛寧鎯堢€涙繄绱撻崒娆掝唹闁哄懐濞€瀵寮撮敍鍕澑闁诲函缍嗘禍鏍磻閹捐鍗抽柕蹇娾偓鍏呯暗婵犳鍠楅妵娑㈠磻閹剧粯鐓?chat.py                    # (modify: call session lifecycle on disconnect/timeout)
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱閸╂牠宕濋弴銏″珔闁绘柨鍚嬮悡銉╂煟閺傛寧鎯堢€涙繄绱撻崒娆掝唹闁哄懐濞€瀵寮撮敍鍕澑闁诲函缍嗘禍鏍磻閹捐鍗抽柕蹇娾偓鍏呯暗婵犳鍠楅妵娑㈠磻閹剧粯鐓?config.py                      # (modify: add context window thresholds)
闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?tests/
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?test_memory_service.py         # Memory CRUD unit tests
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?test_context_compressor.py     # Compression logic tests
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?test_memory_tools.py           # recall_memory / save_memory tool tests
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱濞夋盯顢栭崶顒佸仧闁割偅娲橀悡娑㈡煕閵夛絽鍔氶柣蹇婃櫇缁辨挻鎷呴崣澶嬬彋闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾閳ュ厖绨垫繝娈垮枟閵囨盯宕戦幘缁樼厸?test_session_lifecycle.py      # Session end flow tests
闂?  闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾闁诡喖娼″畷鍫曨敆婵犲嫮鈼ゅ┑鐘灱閸╂牠宕濋弴銏″珔闁绘柨鍚嬮悡銉╂煟閺傛寧鎯堢€涙繄绱撻崒娆掝唹闁哄懐濞€瀵寮撮敍鍕澑闁诲函缍嗘禍鏍磻閹捐鍗抽柕蹇娾偓鍏呯暗婵犳鍠楅妵娑㈠磻閹剧粯鐓?test_context_loading.py        # Hot/warm memory in system prompt tests
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
            content="闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫㈢磽閸屾瑧璐伴柛瀣缁棁銇愰幒鎴ｆ憰閻庡箍鍎卞ú锕傚磻濮椻偓閺屽秹濡烽妷銉ョ婵犮垼顫夊ú婊呮閹捐纾兼繛鍡樺灥婵¤棄顪冮妶鍐ㄥ闁硅櫕锚閻ｇ兘骞囬悧鍫濅画闂備緡鍙忕粻鎴濃枔椤愶附鈷戦柛娑橈攻婢跺嫰鏌涚€ｎ偄娴€规洏鍎抽埀顒婄秵閸犳鎮￠弴銏＄厸闁搞儯鍎辨俊鍏碱殽閻愮摲鎴炵┍婵犲洤鐭楀璺猴功娴煎苯鈹戦纭峰姛闁稿簺鍊曢…鍥敂閸繄顓煎銈嗘⒒閸樠団€栨径瀣瘈闁汇垽娼цⅷ闂佹悶鍔嶅浠嬪极閸愵喖顫呴柕鍫濆暊閸?,
            source_session_id="session-abc",
        )
        assert mem.id is not None
        assert mem.category == "preference"
        assert mem.content == "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫㈢磽閸屾瑧璐伴柛瀣缁棁銇愰幒鎴ｆ憰閻庡箍鍎卞ú锕傚磻濮椻偓閺屽秹濡烽妷銉ョ婵犮垼顫夊ú婊呮閹捐纾兼繛鍡樺灥婵¤棄顪冮妶鍐ㄥ闁硅櫕锚閻ｇ兘骞囬悧鍫濅画闂備緡鍙忕粻鎴濃枔椤愶附鈷戦柛娑橈攻婢跺嫰鏌涚€ｎ偄娴€规洏鍎抽埀顒婄秵閸犳鎮￠弴銏＄厸闁搞儯鍎辨俊鍏碱殽閻愮摲鎴炵┍婵犲洤鐭楀璺猴功娴煎苯鈹戦纭峰姛闁稿簺鍊曢…鍥敂閸繄顓煎銈嗘⒒閸樠団€栨径瀣瘈闁汇垽娼цⅷ闂佹悶鍔嶅浠嬪极閸愵喖顫呴柕鍫濆暊閸?
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

        await create_memory(db, "mem-user-2", "preference", "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎮块鈧弻锝呂熷▎鎯ф闂佹眹鍊楅崑鎾舵崲濞戙垹骞㈡俊顖濇娴犺偐绱撴担鍝勑ｆ俊顐㈠暣瀵鈽夊顐ｅ媰闂佸憡鎸嗛埀顒€危閸垻纾藉ù锝囶焾椤ｆ娊鏌涚€ｎ剙鏋涢柛鈹惧亾濡炪倖宸婚崑鎾剁磼閻樿尙效鐎规洘娲樺蹇涘煘閹傚濠殿喗顭囬崢褍鈻嶅澶嬬厵妞ゆ牗鐟ч崝宥夋煙椤栨稒顥堝┑鈩冩倐閺佸倿骞嗚缁犵増绻濋悽闈涗哗闁规椿浜炵槐鐐哄焵椤掍降浜滄い鎰╁焺濡茬儤绻涢崱鎰伈鐎规洩绲惧鍕醇濠婂懐娉?)
        await create_memory(db, "mem-user-2", "habit", "濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔虹磼閵忕姵鐏堢紒鐐劤椤兘寮婚悢鐓庣畾鐟滄粓宕甸悢铏圭＜闁绘宕甸悾娲煛鐏炲墽娲撮柛銊﹀劤閻ｇ兘宕堕埡濠傛暪婵犵數濮幏鍐礃閵娧囩崜缂傚倷鑳剁划顖炴儎椤栫偟宓佹慨妞诲亾闁诡喚鍏橀獮宥夘敊閻撳海绱伴梻?闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃繘骞戦姀銈呯疀妞ゆ棁妫勬惔濠囨⒑瑜版帒浜伴柛鐘愁殔閻ｇ兘寮婚妷锔惧幍闁诲孩绋掗…鍥╃不閵夛妇绠?)
        await create_memory(db, "mem-user-2", "decision", "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴濆敤濡炪倖鎸鹃崑鐔兼偩閻戞绠鹃悗鐢殿焾瀛濆銈嗗灥閹冲繘宕曢锔解拻濞撴埃鍋撴繛浣冲泚鍥敇閵忕姷锛熼梺瑙勫劶濡嫰鎮為崹顐犱簻闁圭儤鍨甸弳娆撴煕濮橆剚璐＄紒杈ㄥ笚濞煎繘濡搁妷锕佺檨闁诲孩顔栭崳顕€宕抽敐鍛殾闁圭儤鍤╅幒鎴旀瀻闁诡垎鍐炬交闂備礁鐤囬～澶愬垂閸ф鏄ラ柕澶嗘櫅楠炪垺淇婇妶鍌氫壕缂備胶濮惧畷鐢垫閹惧鐟归柛銉戝嫮浜鹃梻浣芥〃濞村洭顢氳椤㈡岸鏁愰崱娆樻祫闁诲函绲介悘姘跺疾濠靛鈷戦柟绋挎捣缁犳挻淇婇顐㈠籍鐎?)

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
        await create_memory(db, "mem-user-3", "decision", "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴濆敤濡炪倖鎸鹃崑鐔兼偩閻戞绠鹃悗鐢殿焾瀛濆銈嗗灥閹冲繘宕曢锔解拻濞撴埃鍋撴繛浣冲泚鍥敇閵忕姷锛熼梺瑙勫劶濡嫰鎮為崹顐犱簻闁圭儤鍨甸弳娆撴煕濮橆剚璐＄紒杈ㄥ笚濞煎繘濡搁妷锕佺檨闁诲孩顔栭崳顕€宕抽敐鍛殾闁圭儤鍤╅幒鎴旀瀻闁诡垎鍐炬交闂備礁鐤囬～澶愬垂閸ф鏄ラ柕澶嗘櫅楠炪垺淇婇妶鍌氫壕缂備胶濮惧畷鐢垫閹惧鐟归柛銉戝嫮浜鹃梻浣芥〃濞村洭顢氳椤㈡岸鏁愰崱娆樻祫闁诲函绲介悘姘跺疾濠靛鈷戦柟绋挎捣缁犳挻淇婇顐㈠籍鐎?)

        # Old memory (simulate 30 days ago)
        old_mem = Memory(
            user_id="mem-user-3",
            category="decision",
            content="缂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓鍝ュ閸ф鐓欓柟顖滃椤ュ顩奸崨顓涙斀妞ゆ柨顫曟禒婊堟煕鐎ｎ偅灏甸柍褜鍓濋～澶娒洪敃鍌氱闁绘梻顑曢埀顑跨铻栭柛娑卞幘椤︽澘顪冮妶鍡楀潑闁稿鎸搁湁闁绘娅曢妵婵囨叏婵犲啯銇濇俊顐㈠暙閳藉娼忛埡浣感梻鍌欒兌椤牓鏌婇敐鍡欘洸闁割偅娲栫粻鏍煥閻斿搫孝闁告濞婇弻锝夊箛椤掑倐锝夋煟閳哄﹤鐏︽鐐插暢椤﹀湱鈧娲栭妶鎼併€侀弴銏犖ч柛娑卞帨閵娾晜鈷掗柛灞剧懅椤︼附銇勯幘鑼煓鐎殿喖鐖煎畷褰掝敊婢惰娲熷?,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_mem)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)
        assert len(warm) == 1
        assert warm[0].content == "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴濆敤濡炪倖鎸鹃崑鐔兼偩閻戞绠鹃悗鐢殿焾瀛濆銈嗗灥閹冲繘宕曢锔解拻濞撴埃鍋撴繛浣冲泚鍥敇閵忕姷锛熼梺瑙勫劶濡嫰鎮為崹顐犱簻闁圭儤鍨甸弳娆撴煕濮橆剚璐＄紒杈ㄥ笚濞煎繘濡搁妷锕佺檨闁诲孩顔栭崳顕€宕抽敐鍛殾闁圭儤鍤╅幒鎴旀瀻闁诡垎鍐炬交闂備礁鐤囬～澶愬垂閸ф鏄ラ柕澶嗘櫅楠炪垺淇婇妶鍌氫壕缂備胶濮惧畷鐢垫閹惧鐟归柛銉戝嫮浜鹃梻浣芥〃濞村洭顢氳椤㈡岸鏁愰崱娆樻祫闁诲函绲介悘姘跺疾濠靛鈷戦柟绋挎捣缁犳挻淇婇顐㈠籍鐎?


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴濆敤濡炪倖鎸鹃崑鐔兼偩閻戞绠鹃悗鐢殿焾瀛濆銈嗗灥閹冲繘宕曢锔解拻濞撴埃鍋撴繛浣冲泚鍥敇閵忕姷锛熼梺瑙勫劶濡嫰鎮為崹顐犱簻闁圭儤鍨甸弳娆撴煕濮橆剚璐＄紒杈ㄥ笚濞煎繘濡搁妷锕佺檨闁诲孩顔栭崳顕€宕抽敐鍛殾闁圭儤鍤╅幒鎴旀瀻闁诡垎鍐炬交闂備礁鐤囬～澶愬垂閸ф鏄ラ柕澶嗘櫅楠炪垺淇婇妶鍌氫壕缂備胶濮惧畷鐢垫閹惧鐟归柛銉戝嫮浜鹃梻浣芥〃濞村洭顢氳椤㈡岸鏁愰崱娆樻祫闁诲函绲介悘姘跺疾濠靛鈷戦柟绋挎捣缁犳挻淇婇顐㈠籍鐎规洏鍎靛畷銊р偓娑櫱氶幏缁樼箾鏉堝墽鎮奸柟铏崌椤㈡艾顭ㄩ崨顖滐紲闁诲函缍嗛崑鍕倶鐎电硶鍋撳▓鍨灓闁轰礁顭烽妴浣肝旈崨顓狀槹濡炪倖鍔戦崐鏍偂閿濆鈷掑〒姘ｅ亾婵炰匠鍥佸洭顢曢敃鈧悿鐐箾閹存瑥鐏╃紒鈧崟顖涚厽婵☆垵娅ｉ敍宥囩磼閳锯偓閸嬫挸鈹戦悩鍨毄闁稿鍋ゅ畷鏇㈡惞椤愩値娲搁梺鍛婃寙閸涱垽绱冲┑鐐舵彧缂嶁偓妞ゆ洘鐗曢埢鎾诲籍閳ь剟濡甸崟顖涙櫆闁绘劦鍓氬В鍫ユ倵?)
        await create_memory(db, "mem-user-4", "preference", "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫㈢磽閸屾瑧璐伴柛瀣缁棁銇愰幒鎴ｆ憰閻庡箍鍎卞ú锕傚磻濮椻偓閺屽秹濡烽妷銉ョ婵犮垼顫夊ú婊呮閹捐纾兼繛鍡樺灥婵¤棄顪冮妶鍐ㄥ闁硅櫕锚閻ｇ兘骞囬悧鍫濅画闂備緡鍙忕粻鎴濃枔椤愶附鈷戦柛娑橈攻婢跺嫰鏌涚€ｎ偄娴€规洏鍎抽埀顒婄秵閸犳鎮￠弴銏＄厸闁搞儯鍎辨俊鍏碱殽閻愮摲鎴炵┍?)
        await create_memory(db, "mem-user-4", "knowledge", "婵犵數濮烽弫鍛婃叏閻㈠壊鏁婇柡宥庡幖缁愭淇婇妶鍛殲闁哄棙绮撻弻鐔兼倻濮楀棙鐣剁紒鐐劤缂嶅﹪骞冭ぐ鎺戠倞鐟滃酣鍩㈤弴銏＄厱闁绘棃鏀遍崵鍥煛鐏炶鈧洟婀侀柣搴秵閸嬪懘鎮甸弴鐔虹瘈婵炲牆鐏濋悘鐘绘煏閸喐鍊愮€殿喖顭烽弫鎰緞婵犲嫷鍚呴梻浣虹帛閸旀洖螞濞嗘挸鍨傞柛鎾茶兌閻鏌熼悜妯虹劸婵炵鍔戦弻宥堫檨闁告挻鐟╅敐?)

        results = await recall_memories(db, "mem-user-4", query="濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫?)
        assert len(results) >= 1
        assert any("濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫? in m.content for m in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-5", "decision", "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴濆敤濡炪倖鎸鹃崑鐔兼偩閻戞绠鹃悗鐢殿焾瀛濆銈嗗灥閹冲繘宕曢锔解拻濞撴埃鍋撴繛浣冲泚鍥敇閵忕姷锛熼梺瑙勫劶濡嫰鎮為崹顐犱簻闁圭儤鍨甸弳娆撴煕濮橆剚璐＄紒杈ㄥ笚濞煎繘濡搁妷锕佺檨闁诲孩顔栭崳顕€宕抽敐鍛殾闁圭儤鍤╅幒鎴旀瀻闁诡垎鍐炬交闂備礁鐤囬～澶愬垂閸ф鏄ラ柕澶嗘櫅楠炪垺淇婇妶鍌氫壕缂備胶濮惧畷鐢垫閹惧鐟归柛銉戝嫮浜鹃梻浣芥〃濞村洭顢氳椤㈡岸鏁愰崱娆樻祫闁诲函绲介悘姘跺疾濠靛鈷戦柟绋挎捣缁犳挻淇婇顐㈠籍鐎?)
        original_accessed = mem.last_accessed

        # Small delay to ensure timestamp differs
        results = await recall_memories(db, "mem-user-5", query="濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫?)
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

        mem = await create_memory(db, "mem-user-6", "preference", "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎮块鈧弻锝呂熷▎鎯ф闂佹眹鍊楅崑鎾舵崲濞戙垹骞㈡俊顖濇娴犺偐绱撴担鍝勑ｆ俊顐㈠暣瀵鈽夊顐ｅ媰闂佸憡鎸嗛埀顒€危閸垻纾藉ù锝囶焾椤ｆ娊鏌涚€ｎ剙鏋涢柛鈹惧亾濡炪倖宸婚崑鎾剁磼閻樿尙效鐎规洘娲樺蹇涘煘閹傚濠殿喗顭囬崢褍鈻嶅澶嬬厵?)
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

        mem = await create_memory(db, "mem-user-7", "preference", "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎮块鈧弻锝呂熷▎鎯ф闂佹眹鍊楅崑鎾舵崲濞戙垹骞㈡俊顖濇娴犺偐绱撴担鍝勑ｆ俊顐㈠暣瀵鈽夊顐ｅ媰闂佸憡鎸嗛埀顒€危閸垻纾藉ù锝囶焾椤ｆ娊鏌涚€ｎ剙鏋涢柛鈹惧亾濡炪倖宸婚崑鎾剁磼閻樿尙效鐎规洘娲樺蹇涘煘閹傚濠殿喗顭囬崢褍鈻嶅澶嬬厵?)
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
            content="闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎳滆ぐ鎺撶厸閻忕偠顕ч崝姘扁偓鐟版啞缁诲啴濡甸崟顖氱睄闁稿本鐭竟鏇炩攽閻愯尙澧涢柟顔煎€搁～蹇曠磼濡顎撻梺鍛婄☉閿曘倝寮抽崼銉︹拺闁告稑锕ラ埛鎰箾閸欏鐭嬬紒鏃傚枛瀵挳濮€閳哄倹娅嶉梻渚€娼х换鍡涘焵椤掆偓閸樻牕危?,
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
                "weekday": "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣埖鍔栭崐鐢告煥濠靛棝顎楀褎澹嗙槐?,
                "free_periods": [
                    {"start": "08:00", "end": "10:00", "duration_minutes": 120},
                    {"start": "14:00", "end": "16:00", "duration_minutes": 120},
                ],
                "occupied": [
                    {"start": "10:00", "end": "12:00", "type": "course", "name": "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫?},
                ],
            },
            {
                "date": "2026-04-02",
                "weekday": "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣埖鍔栭崐鍫曟煟閹邦喗鏆╅柛?,
                "free_periods": [
                    {"start": "09:00", "end": "11:00", "duration_minutes": 120},
                ],
                "occupied": [],
            },
        ],
        "summary": "2026-04-01 闂?2026-04-02 闂?3 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村蓟閵夛妇鍘介梺褰掑亰閸撴岸骞嗛崼銉︾厽闁规崘鎻懓鍧楁煛鐏炵硶鍋撻幇浣告倯闁硅偐琛ラ埀顒€纾鎴︽⒒娴ｇ懓鈻曢柡鈧潏鈺傛殰闁跨喓濮撮拑鐔哥箾閹寸們姘跺几鎼淬劎鍙撻柛銉╊棑缁嬪鏌嶇紒妯诲磳婵﹥妞藉畷顐﹀Ψ閵夈倗閽电紓鍌欑贰閸犳鎮烽埡渚囧殨濠电姵鑹炬儫闂侀潧顦崹娲綖瀹ュ應鏀介柍钘夋閻忥絿绱掗鍛仸妤犵偛绻橀弻鍡楊吋閸″繑瀚奸梻鍌欑贰閸嬪棝宕戝☉銏″殣妞ゆ牗绋掑▍鐘炽亜閺嶃劎鈼ョ紒璇叉閺屾稑鈻庤箛锝喰﹀┑鐐存儗閸犳濡?6 闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃繘骞戦姀銈呯疀妞ゆ棁妫勬惔濠囨⒑瑜版帒浜伴柛鐘愁殔閻ｇ兘寮婚妷锔惧幍闁诲孩绋掗…鍥╃不閵夛妇绠?0 闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤掍焦顔囬梻浣告贡閸庛倝宕甸敃鈧埥澶娢熼柨瀣澑闂佽鍑界紞鍡樼閻愪警鏁?,
    }
    compressed = compress_tool_result("get_free_slots", result)
    # Should use the existing summary field
    assert "3 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村蓟閵夛妇鍘介梺褰掑亰閸撴岸骞嗛崼銉︾厽闁规崘鎻懓鍧楁煛鐏炵硶鍋撻幇浣告倯闁硅偐琛ラ埀顒€纾鎴︽⒒娴ｇ懓鈻曢柡鈧潏鈺傛殰闁跨喓濮撮拑鐔哥箾閹寸們姘跺几鎼淬劎鍙撻柛銉╊棑缁嬪鏌嶇紒妯诲磳婵? in compressed
    assert "6 闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃繘骞戦姀銈呯疀妞ゆ棁妫勬惔濠囨⒑瑜版帒浜伴柛鐘愁殔閻ｇ兘寮婚妷锔惧幍闁诲孩绋掗…鍥╃不閵夛妇绠? in compressed
    # Should NOT contain the full slot details
    assert "free_periods" not in compressed


def test_compress_list_courses():
    result = {
        "courses": [
            {"id": "1", "name": "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫?, "teacher": "闂?, "weekday": 1, "start_time": "08:00", "end_time": "09:40"},
            {"id": "2", "name": "缂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓鍝ュ閸ф鐓欓柟顖滃椤ュ顩奸崨顓涙斀妞ゆ柨顫曟禒婊堟煕鐎ｎ偅灏甸柍?, "teacher": "闂?, "weekday": 3, "start_time": "10:00", "end_time": "11:40"},
            {"id": "3", "name": "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾鐎规洏鍎抽埀顒婄秵閳ь剦鍙忕紞渚€鐛幒妤€妫橀柛顭戝枤娴滄澘鈹戞幊閸娧呭緤娴犲绐楁慨妯挎硾閺?, "teacher": "闂?, "weekday": 2, "start_time": "08:00", "end_time": "09:40"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_courses", result)
    assert "3" in compressed
    assert "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫? in compressed


def test_compress_list_tasks():
    result = {
        "tasks": [
            {"id": "1", "title": "濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倿鏌ｉ幘宕囧哺闁哄鐗楃换娑㈠箣閻愬娈ら梺娲诲幗閹搁箖鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕鍫濇閸欏繑銇勯幒鎴濐仾闁绘挻娲熼弻锟犲炊閵夈儱顬堟繝鈷€鍛笡缂佺粯鐩畷濂告偆娴ｅ湱鏆﹀┑鐑囩到濞层倝鏁冮鍫涒偓浣糕槈濮楀棛鍙嗛梺鍛婁緱閸橀箖顢曢崗鑲╃瘈闁汇垽娼ф禒婊堟煟濡も偓濡瑩寮查懜鍨劅闁挎繂妫鐔兼⒑閸︻厼鍔嬮柛銈忕畵瀵噣鍩€椤掑倹宕叉繝闈涱儏绾惧吋鎱ㄥ鍡楀妞ゆ柨娲ㄧ槐鎾诲磼濮橆兘鍋撻悜鑺ュ€块柨鏇炲€搁拑鐔兼煏婵炵偓娅撻柡浣割儐閵囧嫰骞樼捄鐩掋垽鏌?, "status": "completed"},
            {"id": "2", "title": "濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倿鏌ｉ幘宕囧哺闁哄鐗楃换娑㈠箣閻愬娈ら梺娲诲幗閹搁箖鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕鍫濇閸欏繑銇勯幒鎴濐仾闁绘挻娲熼弻锟犲炊閵夈儱顬堟繝鈷€鍛笡缂佺粯鐩畷濂告偆娴ｅ湱鏆﹀┑鐑囩到濞层倝鏁冮鍫涒偓浣糕槈濮楀棛鍙嗛梺鍛婁緱閸橀箖顢曢崗鑲╃瘈闁汇垽娼ф禒婊堟煟濡も偓濡瑩寮查懜鍨劅闁挎繂妫鐔兼⒑閸︻厼鍔嬮柛銈忕畵瀵噣鍩€椤掑倹宕叉繝闈涱儏绾惧吋鎱ㄥ鍡楀妞ゆ柨娲ㄧ槐鎾诲磼濮橆兘鍋撻悜鑺モ挃鐎广儱顦粈澶婎熆閼搁潧濮囬柣銈囧亾缁绘繈妫冨☉姘暫闂?, "status": "pending"},
            {"id": "3", "title": "濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倿鏌ｉ幘宕囧哺闁哄鐗楃换娑㈠箣閻愬娈ら梺娲诲幗閹搁箖鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕鍫濇閸欏繑銇勯幒鎴濐仾闁绘挻娲熼弻锟犲炊閵夈儱顬堝Δ鐘靛仦钃卞ǎ鍥э躬椤㈡洟顢曢姀顫摋婵＄偑鍊ら崢鐓庮焽閳ュ磭鏆︽繝濠傚閻熷綊鏌涢妷銏℃珔濠殿喖銈稿?, "status": "pending"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_tasks", result)
    assert "3" in compressed
    assert "1" in compressed  # completed count


def test_compress_create_study_plan():
    result = {
        "tasks": [
            {"title": "濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倿鏌ｉ幘宕囧哺闁哄鐗楃换娑㈠箣閻愬娈ら梺娲诲幗閹搁箖鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕鍫濇閸欏繑銇勯幒鎴濐仾闁绘挻娲熼弻锟犲炊閵夈儱顬堟繝鈷€鍛笡缂佺粯鐩畷濂告偆娴ｅ湱鏆﹀┑鐑囩到濞层倝鏁冮鍫涒偓浣糕槈濮楀棛鍙嗛梺鍛婁緱閸橀箖顢曢崗鑲╃瘈闁汇垽娼ф禒婊堟煟濡も偓濡瑩寮查懜鍨劅闁挎繂妫鐔兼⒑閸︻厼鍔嬮柛銈忕畵瀵噣鍩€椤掑倹宕叉繝闈涱儏绾惧吋鎱ㄥ鍡楀妞ゆ柨娲ㄧ槐鎾诲磼濮橆兘鍋撻悜鑺ュ€块柨鏇炲€搁拑鐔兼煏婵炵偓娅撻柡浣割儐閵囧嫰骞樼捄鐩掋垽鏌?, "date": "2026-04-01"},
            {"title": "濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倿鏌ｉ幘宕囧哺闁哄鐗楃换娑㈠箣閻愬娈ら梺娲诲幗閹搁箖鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕鍫濇閸欏繑銇勯幒鎴濐仾闁绘挻娲熼弻锟犲炊閵夈儱顬堟繝鈷€鍛笡缂佺粯鐩畷濂告偆娴ｅ湱鏆﹀┑鐑囩到濞层倝鏁冮鍫涒偓浣糕槈濮楀棛鍙嗛梺鍛婁緱閸橀箖顢曢崗鑲╃瘈闁汇垽娼ф禒婊堟煟濡も偓濡瑩寮查懜鍨劅闁挎繂妫鐔兼⒑閸︻厼鍔嬮柛銈忕畵瀵噣鍩€椤掑倹宕叉繝闈涱儏绾惧吋鎱ㄥ鍡楀妞ゆ柨娲ㄧ槐鎾诲磼濮橆兘鍋撻悜鑺モ挃鐎广儱顦粈澶婎熆閼搁潧濮囬柣銈囧亾缁绘繈妫冨☉姘暫闂?, "date": "2026-04-02"},
            {"title": "濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倿鏌ｉ幘宕囧哺闁哄鐗楃换娑㈠箣閻愬娈ら梺娲诲幗閹搁箖鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕鍫濇閸欏繑銇勯幒鎴濐仾闁绘挻娲熼弻锟犲炊閵夈儱顬堝Δ鐘靛仦钃卞ǎ鍥э躬椤㈡洟顢曢姀顫摋婵＄偑鍊ら崢鐓庮焽閳ュ磭鏆︽繝濠傚閻熷綊鏌涢妷銏℃珔濠殿喖銈稿?, "date": "2026-04-03"},
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
        return f"[缂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕閻庢鍠氶弫濠氥€佸Δ鍛劦妞ゆ帒瀚ч埀顒佹瀹曟﹢顢欓挊澶屾濠电姰鍨归崢婊堝疾濠婂懐鐭欓柟鐑樻⒒閻鏌熼悜妯荤厸闁稿鎹囬弫鎰償濠靛牊鏅奸梻浣规た閸嬪嫮鈧碍婢橀～蹇撁洪鍛簵闁瑰吋鐣崹褰掑汲閸繍娓婚柕鍫濇閳锋劙鏌ｅΔ鍐ㄐ㈤柣锝囧厴椤㈡鎷呮笟顖涚カ闂佽鍑界紞鍡涘磻閸℃稑鍌ㄩ柟闂寸劍閻撶喖鐓崶銊︾濞寸姭鏅滈妵鍕即閸℃鎼愮紒鈧径鎰厪濠㈣埖绋栫粈瀣瑰鍕煉闁哄矉绻濆畷鍫曞煛娴ｅ湱褰欐繝鐢靛仜閻楀﹪鈥﹂崶鈺傤潟闁圭儤鎸荤紞鍥煏婵炲灝鍔滈悹鍥╁仜铻栭柣姗€娼ф禒锔姐亜椤撶偞鍠橀柛鈹惧亾濡炪倖甯掗崐褰掑汲椤掑嫭鐓涢柛娑卞枤閸欌偓閻庤娲橀悷褍顕?{summary}"
    slots = result.get("slots", [])
    total = sum(len(d.get("free_periods", [])) for d in slots)
    return f"[缂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕閻庢鍠氶弫濠氥€佸Δ鍛劦妞ゆ帒瀚ч埀顒佹瀹曟﹢顢欓挊澶屾濠电姰鍨归崢婊堝疾濠婂懐鐭欓柟鐑樻⒒閻鏌熼悜妯荤厸闁稿鎹囬弫鎰償濠靛牊鏅奸梻浣规た閸嬪嫮鈧碍婢橀～蹇撁洪鍛簵闁瑰吋鐣崹褰掑汲閸繍娓婚柕鍫濇閳锋劙鏌ｅΔ鍐ㄐ㈤柣锝囧厴椤㈡鎷呮笟顖涚カ闂佽鍑界紞鍡涘磻閸℃稑鍌ㄩ柟闂寸劍閻撶喖鐓崶銊︾濞寸姭鏅滈妵鍕即閸℃鎼愮紒鈧径鎰厪濠㈣埖绋栫粈瀣瑰鍕煉闁哄矉绻濆畷鍫曞煛娴ｅ湱褰欐繝鐢靛仜閻楀﹪鈥﹂崶鈺傤潟闁圭儤鎸荤紞鍥煏婵炲灝鍔滈悹鍥╁仜铻栭柣姗€娼ф禒锔姐亜椤撶偞鍠橀柛鈹惧亾濡炪倖甯掗崐褰掑汲椤掑嫭鐓涢柛娑卞枤閸欌偓閻庤娲橀悷褍顕?{len(slots)} 濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倻鎲搁悧鍫濈瑲闁稿﹤鐖奸弻娑㈩敃閻樻彃濮庨梺姹囧€楅崑鎾诲Φ閸曨喚鐤€闁圭偓鎯屽Λ鈥愁渻閵堝骸浜濇繛鍙夘焽閹广垹鈹戠€ｎ偒妫冨┑鐐村灥瀹曨剟宕滈幍顔剧＝濞达絾褰冩禍?{total} 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村蓟閵夛妇鍘介梺褰掑亰閸撴岸骞嗛崼銉︾厽闁规崘鎻懓鍧楁煛鐏炵硶鍋撻幇浣告倯闁硅偐琛ラ埀顒€纾鎴︽⒒娴ｇ懓鈻曢柡鈧潏鈺傛殰闁跨喓濮撮拑鐔哥箾閹寸們姘跺几鎼淬劎鍙撻柛銉╊棑缁嬪鏌嶇紒妯诲磳婵?


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = [c["name"] for c in courses[:5]]
    names_str = "闂?.join(names)
    if count > 5:
        names_str += f" 缂?{count} 闂?
    return f"[闂傚倸鍊搁崐宄懊归崶褏鏆﹂柛顭戝亝閸欏繘鏌℃径瀣婵炲樊浜滃洿闂佺硶鍓濊摫闁绘繈鏀辩换娑氣偓鐢殿焾瀛濆銈嗗灥閹虫﹢骞冮垾鏂ユ斀闁糕€崇箲閺傗偓闂備胶顭堥張顒傚垝閻樼粯鍊块柛鎾楀懐锛滈梺閫炲苯澧寸€规洖宕灒闁革富鍘鹃悾楣冩⒒娓氣偓濞佳囨偋閸℃稑绠犻幖鎼厛閺佸倿鏌曟径鍡樻珕闁绘挸鍟伴幉绋款煥閸繄顦┑鐐叉閹稿摜澹?闂?{count} 闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌熼梻瀵割槮缁炬儳缍婇弻娑㈩敃閿濆棛顦ョ紓浣插亾濠㈣埖鍔楅崣鎾绘煕閵夛絽濡虹紒鍫曚憾閺屸剝鎷呴崜鎻掑壎闂佸搫鐬奸崰鏍嵁閸℃稑绾ч柛鐔峰暞閹瑰洭寮婚敓鐘叉そ濞达絿顭堥～顏堟⒑闁稓鈹掗柛鏂跨焸閸╃偤骞嬮敃鈧柋鍥ㄧ節婵犲倸鏆欓柣蹇庡伐mes_str}"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    pending = count - completed
    return f"[濠电姷鏁告慨鐑藉极閹间礁纾绘繛鎴欏焺閺佸銇勯幘璺烘瀾闁告瑥绻愯灃闁挎繂鎳庨弸銈夋煛娴ｅ壊鍎戦柟鎻掓啞閹棃濡搁妷褏鏉介梻渚€娼ц墝闁哄懏绮撳畷鎴﹀礋椤栨稓鍘介梺瑙勫礃濞呮洟骞戦敐鍡愪簻闁挎棁顕ф禍婊堟煃鐟欏嫬鐏︽鐐诧躬閺屾稒绻濋崘鈺冾槶闂侀€炲苯澧柛婵嗛叄瀹曟繈骞嬮敃鈧弰銉╂煃瑜滈崜姘跺Φ閸曨垰绠抽柛鈩冦仦婢规洟姊?闂?{count} 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村矗婢跺瞼顔曢梺绯曞墲钃遍悘蹇ｅ幘缁辨帡鎮╁畷鍥у绩闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾偐閻㈢數鍔跺┑鐘灱閸╂牠宕濋弽顓熷亗闁告劦鍠楅悡銏′繆椤栨瑨顒熸俊鎻掔秺閺屾盯鏁愰崶銊︾彧缂備浇椴哥敮锟犲春閳ь剚銇勯幒宥囧妽婵炲懐濞€閺屾稖顦叉繛鑲╊殙pleted} 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村矗婢跺瞼鐦堟繝鐢靛Т閸婄粯鏅堕弴鐘电＜闁逞屽墴瀹曠喖顢涘☉姘汲婵犵數鍋為崹鍫曟晪濡炪倕绻堥崐婵嬪蓟濞戞埃鍋撻敐搴′簼鐎规洖鐭傞弻鐔碱敊閹冨箣闂佽鍟崶褔鍞堕梺缁樻⒒椤牓顢旀导瀛樷拻闁稿本鐟ч崝宥夋煙椤旇偐鍩ｇ€规洘绻傞濂稿川椤栨稒鐣烽梻浣哥秺濡法绮堟笟鈧鍛婃媴鐞涒€充壕妤犵偛鐏濋崝姘箾閼碱剙鈻堢€规洘鍨块獮妯肩磼濮楀棙顥堟繝鐢靛仦閸ㄥ爼鎳濇ィ鍐╃厑闁革絺鍋搉ding} 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村矗婢跺瞼鐦堟繝鐢靛Т閸婂綊宕抽悜妯镐簻闁归偊浜為惌娆撴煛瀹€瀣М鐎殿噮鍣ｅ畷鍫曞Ψ閵忕姳澹曢梺閫炲苯澧撮柡灞剧〒閳ь剨缍嗛崑鍛暦瀹€鍕厵妞ゆ梹鍎抽崢鎾煙椤斻劌娲ら柋鍥煟閺冨偆鐒炬い蹇庡嵆濮?


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    return f"[濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倿鏌ｉ幘宕囧哺闁哄鐗楃换娑㈠箣閻愬娈ら梺娲诲幗閹搁箖鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕鍫濇閸欏繑銇勯幒鎴濐仾闁绘挻娲熼弻锟犲炊閵夈儱顬堝Δ鐘靛仦椤ㄥ懘鍩為幋锔绘晬婵ǜ鍎辨禒顕€姊洪崫鍕缂佸顫夋穱濠囨倻閽樺）銊╂煏婢舵盯妾柣锔肩秮濮婄粯鎷呯粵瀣缂備胶绮崝娆愪繆?闂傚倸鍊峰ù鍥敋瑜嶉～婵嬫晝閸岋妇绋忔繝銏ｅ煐閸旀牠宕戦妶澶嬬厸闁搞儮鏅涘皬闂佺粯甯掗敃銉ф崲濞戙垹骞㈡俊顖濐嚙绾板秹姊洪崫鍕靛剮缂佽埖宀稿濠氭偄閻撳海顔夐梺閫涘嵆濞佳冣枔椤撶姷纾?{count} 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村矗婢跺瞼鐦堟繝鐢靛Т閸婂宕ラ崶顒佺厱闁靛鍠栨晶顕€鏌ｉ鐕佹當妞ゎ叀娉曢幑鍕传閸曞灚校闂備礁鎼鍡涙偡閳轰緡娼栭柧蹇撴贡绾惧吋鎱ㄥΔ鈧Λ娑㈠礉閸涘﹣绻嗛柣鎰▕閸ょ喐銇勯鐐靛ⅵ闁诡噣绠栭幃婊堟寠婢跺孩鎲伴梻渚€娼ч¨鈧┑鈥虫喘瀹?


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
            "description": "濠电姷鏁告慨鐑藉极閹间礁纾绘繛鎴欏焺閺佸銇勯幘璺烘瀾闁告瑥绻橀弻鈩冨緞鐎ｎ亝顔呴悷婊呭鐢宕愭繝姘參婵☆垯璀﹀Σ褰掓煟鎼搭喖澧存慨濠冩そ濡啫鈽夊顒夋毇婵＄偑鍊х€靛矂宕瑰畷鍥у灊濠电姵纰嶉弲鏌ユ煕濠娾偓閻掞妇鈧潧鐭傞弻锝嗘償椤栨粎校婵炲瓨绮嶇划鎾汇€佸Δ鍛潊闁靛牆妫涢崢浠嬫⒑閹稿海绠撴い锔诲櫍楠炲鎮欓浣稿伎婵犵數濮撮崑鍡涙偂婵傚憡鐓曢柍瑙勫劤娴滅偓淇婇悙顏勨偓鏍暜閹烘柡鍋撳鐓庡缂侇喚绮€靛ジ寮堕幋鐙€鍟囨繝鐢靛剳缂嶅棝宕滃▎鎾村€堕柍鍝勬噺閻撶喖鏌熼悜妯诲鞍闁稿﹥鍔欓弻鈥崇暆鐎ｎ剛袦闂佽鍠掗弲婊冾焽韫囨稑鐓涘ù锝呭閻庢潙鈹戦悩鍨毄濠殿喕鍗冲畷鐟懊洪浣插亾閿曞倸鐐婃い鎺嗗亾缂佺姵鐓￠弻鏇＄疀鐎ｎ亖鍋撻弴鐘差棜闁稿繗鍋愮粻楣冩煙鐎电浠滈柣鎺戠秺閺岋紕鈧綆鍋嗘晶顏呫亜椤忓嫬鏆ｅ┑鈥崇埣瀹曞崬螣閻戞ɑ顔傞梻鍌欑窔濞艰崵寰婃繝姘？闂侇剙绋勭紞鏍叓閸ャ劎鈽夌紒鈧崼銏″枑闊洦娲栭ˉ姘舵煟閹惧磭鏄傞柍褜鍓氱敮鎺楋綖濠靛鏁嗛柛灞剧懆濡炬悂姊绘担绛嬪殭婵炲瓨宀稿畷鏉课旈崘鈺佸簥濠电偞鍨崹鍦棯瑜旈弻鐔煎箹椤撶偛绠洪梺瀹狀嚙閻楁捇骞冨Δ鍐╁枂闁告洦鍓涢ˇ銊ヮ渻閵堝啫濡奸柨鏇樺€濋幃鎯х暋閹锋梹妫冨畷銊╊敇閻愮數宕哄┑锛勫亼閸婃牜鏁幒妤€纾瑰┑鐘崇閸嬧晛螖閿濆懎鏆為柍閿嬪笒闇夐柨婵嗘川閹藉倿鏌涢妶鍛殻闁哄本绋戦埢搴ょ疀濞戞ê鍙婇柣搴ゎ潐濞叉牜绱炴繝鍥モ偓浣肝旈崨顓狀槹濡炪倖鍔戦崐鏇熸叏閿旀垝绻嗛柣鎰典簻閳ь剚鐗曢蹇旂節濮橆剛锛涢梺鐟板⒔缁垶鎮￠弴鐐╂斀闁绘ɑ褰冮埀顒€缍婇獮澶愬传閵壯咃紲闁哄鐗冮弲娑欑瑜旈弻宥堫檨闁告挶鍔庣槐鐐哄幢濞戞鐛ュ┑掳鍊曢幆銈嗗緞閹邦剙鑰垮┑鐐村灦閻熝囧储閹剧粯鍋℃繝濠傚閻帞鈧娲樼划宀勫煡婢舵劕顫呴柣妯兼暩閺嬧偓闂傚倷鑳剁划顖炪€冮崨瀛樺亱濠电姴鍟崹鏃堟煙缂併垹鏋熼柣鎾存礃缁绘盯骞嬮悜鍥у彆闂佸憡姊婚崰鎰板Φ閸曨垱鏅滈柛婵嗗婵箑鈹戦埥鍡椾簻闁硅櫕锕㈤妴渚€寮撮姀鐙€娼婇梺鏂ユ櫅閸燁垶宕愰柨瀣瘈缁剧増蓱椤﹪鏌涚€ｎ亝鍤囬柟顖氬椤㈡稑顫濋悡搴㈩吙婵＄偑鍊栭崝褏绮婚幋婵囩函婵犵數濮伴崹鐓庘枖濞戙垺鏅濋柨鏇炲亞閺佸洦绻涘顔荤凹闁抽攱鍨块弻锝夊箛闂堟稑鈷夋繝銏ｎ潐閿曘垽寮诲☉娆戠瘈闁稿被鍊楅崥瀣渻閵堝啫鐏柨姘舵偂閵堝棎浜滈煫鍥ㄦ尰閸ｄ粙鏌涘鈧禍璺侯潖閾忚鍠嗛柛鏇ㄥ亜婵垻绱掗崜褑妾搁柛娆屽亾闂佺锕ら悺銊ф崲濠靛鍋ㄩ梻鍫熺◥缁爼姊虹紒姗嗘當闁挎洦浜滈悾鐤亹閹烘垵鐎銈嗘⒒閸嬫挸鈻撴ィ鍐┾拺缁绢厼鎳忚ぐ褏绱掗幓鎺撳仴闁诡喖娼￠崺鈧い鎺戝閳锋垿鎮峰▎蹇擃仼闁告柣鍊楅埀顒冾潐濞诧箓宕滃杈╃焿闁圭儤鍤氬ú顏嶆晜闁告侗浜濈€氬ジ姊婚崒姘偓鎼佹偋婵犲嫮鐭欓柟鐑橆檪婢跺ň鏋庨柟閭︿簽缁犳岸姊虹紒妯哄婵炲吋鐟х划顓☆槾闁逞屽墯椤旀牠宕锕€鐐婄憸蹇浰囬弶娆炬富闁靛牆妫涙晶顒佹叏濡濮傞柟顕€绠栭獮鍡氼檨婵炴挸顭烽弻鏇㈠醇濠靛浂妫ゆ繝鈷€灞藉缂佽鲸甯為埀顒婄秵閸嬪嫰鎮橀幘顔界厵妞ゆ梻鐓鍥╀簷闂備礁鎲℃笟妤呭窗濮樿泛鍌ㄩ梺顒€绉甸埛鎴犳喐閻楀牆绗掑ù婊€鍗抽弻娑㈠箻鐎靛憡鍒涢梺杞扮缁夋挳顢橀崗鐓庣窞閻庯綆鍓欓獮妤呮⒑閸︻厼鍔嬪┑鐐诧工閻ｇ兘寮撮姀鈽嗘濠电偞鍨靛畷顒€鈻撻妸銉富闁靛牆妫欑壕鐢告煕鐎ｎ偅灏甸柍褜鍓氶鏍窗濮樿泛鏋侀悹鍥у棘濞戙垹绀冮柕濞垮灪椤秹姊洪崷顓炲妺闁规悂绠栭崺鈧い鎺嗗亾闁靛牏顭堥～蹇曠磼濡顎撻柣鐔哥懃鐎氥劍绂掕閳规垿鎮欓棃娑樹粯濠电偛鐨烽埀顒€纾弳锔界節闂堟稒宸濈紒鈾€鍋撻梻浣规偠閸庢粓宕ㄩ鐐愭洖鈹戦敍鍕杭闁稿﹥鐗曢蹇旂節濮橆剛锛涢梺鐟板⒔缁垶鎮￠弴鐐╂斀闁绘ɑ褰冮顏呯箾閸涱喗绀嬮柡宀€鍠栭悰顕€宕归鍙ョ礄婵°倗濮烽崑娑㈩敄婢舵劕鏋侀柛鎰靛枛閻掑灚銇勯幒鎴濐仾闁稿﹤鍢查埞鎴︽偐閸欏顦╅梺缁樻尵閸犳牠寮婚悢鍏肩劷闁挎洍鍋撴鐐寸墱缁辨帡骞撻幒婵堝悑闂佸搫鐭夌紞浣割嚕娴犲鏁囨繝闈涙搐閺嬨倖绻濆▓鍨灈闁挎洏鍎遍—鍐寠婢舵ê娈ㄩ梺鍛婃尫閻掞箑鐣锋径鎰厪濠电姴鍟慨鍌炴煕婵犲啰澧遍柟骞垮灩閳藉濮€閻樿鏁归梻浣虹帛濡啴藟閹惧顩峰┑鍌氭啞閳锋垿鏌ｉ悢鍛婄凡婵¤尙绮妵鍕箣濠垫劖笑濡炪倖娲╃紞浣哥暦濠婂嫭濯撮柣鐔稿閿涘繘姊绘笟鈧褑鍣归梺鍛婁緱閸犳顢欓幘缁樷拻闁稿本鑹鹃埀顒勵棑缁牊绗熼埀顒勭嵁婢舵劖鏅柛鏇ㄥ墯濞堟澘鈹戞幊閸婃洟骞婂畝鍕劦妞ゆ巻鍋撻柛鐕佸灠椤曘儵宕熼姘辩杸濡炪倖鍨熼弬鍌炲磿閻㈢钃熸繛鎴欏灩缁犳盯姊婚崼鐔衡姇闁诲繐鐗撳?,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼幑鎰靛殭閻熸瑱绠撻幃妤呮晲鎼粹€愁潻闂佹悶鍔嶇换鍫ョ嵁閺嶎灔搴敆閳ь剚淇婇懖鈺冩／闁诡垎浣镐划闂佸搫鏈ú妯兼崲濞戙垺鍊锋い鎺嶈兌瑜板懐绱撻崒娆掝唹闁稿鎹囬弻娑樼暆閳ь剟宕戦悙鐑樺亗婵炲棙鎸婚悡娆愩亜閺嶃劎鈯曠紒鎯板皺閹喖顫濋懜纰樻嫼闂佸憡绻傜€氼參藟閻愮儤鐓熼柍鍝勶工閻忥附顨ラ悙鎻掓殺闁靛洦鍔欓獮鎺楀箣閻樻祴鍋撻悙鐑樺仭婵犲﹤鍟扮粻濠氭煕閳瑰灝鐏╅柣锝嗙箞閸┾偓妞ゆ帒鍊归～鏇㈡煙閻戞ɑ灏扮紓宥呮喘閺屾洘绻涜閹虫劙寮抽鈶╂斀?闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜滃ù鏍煏婵炵偓娅嗛柛濠傛健閺屻劑寮村Δ鈧禍鎯ь渻閵堝骸骞栭柣蹇旂箞閿濈偛顭ㄩ崼婵堝姦濡炪倖甯掔€氥劑鍩€椤戣法顦﹂摶鏍煕濞戝崬鏋涘ù婊勭矌缁辨挻鎷呴崜鎻掑壍濠电偛顦板ú婊呭垝閿濆鍊烽柣鎴灻埀顒€鐏氶〃銉╂倷閼碱兛铏庨梺鍛婃⒐瀹€鎼佸箖濡も偓椤繈鎮℃惔銏㈠綆闂備浇顕栭崹顖炴倿閿曞倸绠氶柡鍐ㄧ墛閺呮煡鏌涢妷銏℃珨缂佸崬寮剁换婵嬫偨闂堟稐娌梺鎼炲妼閻栧ジ骞冮悿顖ｆЪ闂佸搫鎳庨悥濂稿蓟閸℃鍚嬮柛鈩冪懃楠?闂?闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃繘鍩€椤掍胶鈻撻柡鍛Т閻ｅ嘲顫滈埀顒勫箠閿熺姴围闁搞儮鏅槐铏節濞堝灝鏋熼柨姘扁偓瑙勬处閸撴岸骞堥妸鈺婃晢闁告洦鍓涢崢閬嶆⒑閸濆嫭鍌ㄩ柛鏂挎湰閺呰埖瀵肩€涙鍘撶紓鍌欑劍钃辩紒鈧€ｎ喗鐓涚€光偓鐎ｎ剙鍩岄柧浼欑秮閺屾稑鈹戦崱妤婁痪濠殿噯绲鹃崝娆忣潖?",
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
            "description": "濠电姷鏁告慨鐑藉极閹间礁纾块柟瀵稿Т缁躲倝鏌﹀Ο渚＆婵炲樊浜濋弲婊堟煟閹伴潧澧幖鏉戯躬濮婅櫣绮欑捄銊т紘闂佺顑囬崑銈呯暦閹达箑围濠㈣泛顑囬崢顏呯節閻㈤潧孝缂佺粯鍔欓妴鍛搭敆閸曨剛鍘撶紓鍌欑劍钃辨い銉ョ墦閺岋紕浠﹂悾灞濄儲銇勮缁舵岸寮诲☉銏犵閻犺櫣鍎ら悗璇差渻閵堝棙绌跨紓宥勭閻ｉ攱绺界粙鍨祮闂佺粯鏌ㄩ幉锟犳偟椤愶附鈷掑ù锝呮啞閸熺偞绻涚拠褏鐣电€规洘绮岄～婵嬵敄閼恒儳浜栭梻渚€娼х换鍫ュ磹閺嶎厼鐓曢柟杈鹃檮閸嬧剝绻涢崱妤冪妞ゅ浚浜幃妯跨疀閵夆晜顎嶉梺闈涙搐鐎氱増淇婇悜鑺ユ櫆闁芥ê顦遍。鏌ユ⒒娴ｅ摜锛嶇紒顕呭灦楠炴垿宕堕鍌氱ウ闁诲函缍嗛崰妤呭疾濠婂牊鍋℃繛鍡樼懅缁嬪鎮楀顒夌吋婵﹦绮幏鍛村川婵犲懐顢呮俊鐐€ら崢濂告偋韫囨稑鐒垫い鎺嶈兌閳绘捇鏌￠崨顖毿㈤柣锝呭槻鐓ゆい蹇撳閿涙粓姊虹紒妯哄婵炲吋鐟︾粋鎺楊敍濞戞氨顔曢柡澶婄墕婢х晫绮旈浣典簻妞ゆ劑鍩勫Σ鐑樼箾閸℃劕鐏查柟宕囧█椤㈡宕掑鎰簥闂備浇宕垫慨鏉懨洪敃浣典汗闁告劦鍠栭悞鍨亜閹哄秶顦︽い鏇熺矊鑿愰柛銉戝秷鍚Δ鐘靛仦閿曘垽銆佸▎鎾村殐闁冲搫顑囨惔濠傗攽閻樻剚鍟忛柛鐘愁殜閺佸啴鍩￠崨顓狀槶濠殿喗顭堥崺鏍偂閵夛负浜滈柟鎹愭硾閺嬫梻绱掗悩鑽ょ暫闁哄被鍔岄埞鎴﹀幢濡儤顏″┑鐘灱濞夋稓鈧凹鍠氬Σ鎰板箳閺冣偓鐎氭岸鏌熺紒妯哄潑闁稿鎹囧畷绋课旈埀顒傜不閺嶃劎绠剧€瑰壊鍠曠花濠氬箚閻斿吋鈷戦柛鎰级閹牓鏌涙繝鍌涘暈缂佸倹甯掔叅妞ゅ繐鎳夐幏娲⒒閸屾氨澧涘〒姘殜閹繝顢橀悩鐢碉紲闂佺粯锚閸熷潡鎮橀幘顔界厵妞ゆ洖妫涚弧鈧悗娈垮枟閹歌櫕鎱ㄩ埀顒勬煥濞戞ê顏╂鐐村姍濮婄粯鎷呴崨濠傛殘濠电偠顕滅粻鎾崇暦閹达箑宸濋柡澶嬪灩椤斿姊洪幐搴ｇ畵妞わ缚鍗抽幃锟犲礃椤旂晫鍘繝銏ｅ煐缁嬫垿鎯佸鍫熺厽闁瑰搫绉堕惌娆撴煛瀹€鈧崰鏍€佸▎鎴炲珰闁圭粯甯為妶顔尖攽閻樻鏆柛鎾寸箞楠炲啴宕掑☉妤冪畾闂佸綊妫块悞锕傚疾濠靛鐓冪憸婊堝礈濞嗘挸鐓″璺哄瘨濡嫬鈹戦纭峰伐闁圭⒈鍋呴弲銉╂⒑閹肩偛鍔€闁告劕澧介埀顒佸▕濮婅櫣鎷犻幓鎺濆妷闂佸憡鍨电紞濠傜暦濠婂喚娼╅弶鍫氭櫇閻掑潡鎮楅獮鍨姎妞わ富鍨伴蹇撯攽閸″繑鏂€闂佺粯蓱瑜板啴顢旈鐔剁箚缂備降鍨归弸鐔虹磼缂佹绠撻柍缁樻崌瀹曞綊顢欓悾灞兼喚闂傚倷绀侀幉锟犲蓟閵娧勫床婵☆垵娅ｉ弳锕傛煙鏉堝墽鐣辩紒鐘差煼閹鈽夊▍顓т邯椤㈡捇骞樼紙鐘电畾闂佺粯鍔曞Ο濠囧磿韫囨梻绠鹃柡澶嬪灥濡插宕￠柆宥嗙厵閺夊牓绠栧顕€鏌嶉柨瀣伌闁诡喖缍婂畷鍫曟晲閸屾矮澹曢悗瑙勬礀濞诧絿妲愬鈧缁樻媴鐟欏嫬浠╅梺鍛婃⒐閸ㄥ墎绮嬪鍥ㄥ磯闁惧繗顫夊▓楣冩偡濠婂懎顣奸悽顖涘笚閸庮偊姊绘担绋挎毐闁圭⒈鍋婂畷鎰節濮橆剙鍋嶉梺鍦劋椤ㄥ棝宕愰崹顐闁绘劘灏欐禒銏ゆ煕閺冣偓瀹€鎼佸蓟閿濆憘鏃€鎷呴搹鍦帎闂佺粯鎸堕崐婵嬪蓟閵娿儮鏀介柛鈾€鏅滄晥闂備胶绮幐璇裁洪悢鐓庤摕闁绘柨鍚嬮悞浠嬫煥閺囨浜炬繝鈷€鍌氬祮闁哄被鍔岄埥澶娢熸径瀵″洦鐓涚€光偓鐎ｎ剛蓱濡ょ姷鍋涢敃顏堝蓟濞戞瑦鍎熼柨婵嗘濮ｅ牓鎮楀▓鍨珮闁稿瀚伴、妯荤附缁嬭法鍊為梺鎸庢濡嫭鍒婃导瀛樷拻濞达絿顭堥幃鎴犵磼娴ｈ灏︾€殿喗褰冮埞鎴犫偓锝庝簽閻ゅ懘鎮峰鍛暭閻㈩垱顨婇幃锟犳偄閸忚偐鍘介梺鍝勫€圭€笛囧疮閻愮數妫柟顖嗗瞼鍚嬮梺鍝勭焿缂嶄線鐛幒妤佸€风€瑰壊鍠楅崰姗€姊绘担鑺ャ€冪紒璁圭節瀹曟澘鈽夐姀鐘栵箓鏌熼悧鍫熺凡缂佺姵濞婇弻鐔衡偓鐢殿焾閸撹鲸淇婇銈呮瀾濞ｅ洤锕幃娆擃敂閸曘劌浜鹃柡宥庡幖缁犳壆绱撴担璇＄劷闁绘繂鐖奸弻锟犲炊閵夈儳浠肩紒鐐劤椤兘寮婚悢鐓庣闁逛即娼у▓顓犵磼閻愵剙鍔ら柛姘儑閹广垹鈽夐姀鐘茶€垮┑鈽嗗灥濞咃絾绂掗悡搴富闁靛牆妫欓埛鎰繆椤愩垹鏆ｇ€殿喖顭烽弫鎰板幢濡搫濡抽梻渚€娼х换鍡涘箠閸ャ劍鍙忛柛銉墯閳锋垿鏌熺粙鎸庡攭濠㈣蓱閵囧嫰顢橀垾鍐插Х濡炪倧闄勫娆撳煘閹达富鏁婇柣鎾崇岸閹稿啰绱撴笟鍥ф灕妞ゆ泦鍥х叀濠㈣埖鍔曢～鍛存煟濡灝鐨洪柣娑掓櫆缁绘繈鎮介棃娑樺缂傚倸绉村Λ婵嗙暦濡も偓椤粓鍩€椤掆偓閻ｇ兘骞嬮敃鈧粻濠氭煕閿旇骞橀柡澶岊焾閳规垿鎮欓弶鎴犱桓濡炪値鍘煎ú顓℃閻熸粍鏌ㄩ～蹇撁洪鍕槶闂佸湱绮敮濠勮姳閹绢喗鈷戦柟鑲╁仜婵¤姤淇婇悙鑸殿棄妞?ask_user 缂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礃閹偤骞栧ǎ顒€濡奸柣顓燁殜楠炴牕菐椤掆偓婵¤偐绱掗幇顓ф畷缂佺粯鐩獮瀣枎韫囨洖濮堕梻浣芥〃缁€浣该洪妶澶婄厴闁硅揪闄勯崑鎰版倵閸︻厼孝妞ゃ儲绻堝?,
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["preference", "habit", "decision", "knowledge"],
                        "description": "闂傚倸鍊搁崐宄懊归崶褏鏆﹂柛顭戝亝閸欏繘鏌熼幆鏉啃撻柛濠傛健閺屻劑寮村Δ鈧禍鎯ь渻閵堝骸骞栭柣蹇旂箚閻忔帡姊虹粙璺ㄧ闁告鍕劅濠电姴娲﹂埛鎴犵磼鐎ｎ偄顕滄繝鈧幍顔剧＜妞ゆ柨鍚嬮幑锝吤瑰鍕€愰柟顔荤矙瀹曘劍绻濋崒娆忓闂傚倷鐒﹂幃鍫曞磿椤栫偛绀夌€光偓閳ь剙顕ユ繝鍐瘈婵﹩鍘鹃崢浠嬫⒑閸︻厼鍔嬮柛顭戝灦瀹曟垿濮€閵堝棛鍘搁柣蹇曞仩椤曆勪繆婵傚憡鐓冮柦妯侯樈濡叉悂鏌嶇拠鏌ヮ€楅摶锝夋煕濠靛棗顏存繛鐓庣矗eference=闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ磵閳ь剨绠撳畷濂稿Ψ椤旇姤娅堥梻浣告啞娓氭宕归崡鐐垫殾闁哄被鍎查悡娆撴煟濡も偓閻楀﹦娆㈤弻銉ョ倞? habit=濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鎮规潪鎷岊劅婵炲吋鐗滅槐鎾存媴閼测剝鍨垮畷锝堢疀濞戞瑧鍘介梺闈涚箞閸╁嫰鎮為崜褏妫? decision=闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫鎾绘偐閼碱剦妲烽梻浣告惈濞层劍鎱ㄩ幘顔㈠顫濋婊€绨婚梺瑙勫劤瀹曨剟鎮橀鍫熺厱? knowledge=闂傚倸鍊搁崐宄懊归崶褏鏆﹂柛顭戝亝閸欏繘鏌熼幆鏉啃撻柍閿嬫⒒閳ь剙绠嶉崕閬嵥囬婊冾棜閻熸瑥瀚换鍡涙煏閸繃鍣洪柛锝嗘そ閺?,
                    },
                    "content": {
                        "type": "string",
                        "description": "闂傚倸鍊搁崐宄懊归崶褏鏆﹂柛顭戝亝閸欏繘鏌熼幆鏉啃撻柛濠傛健閺屻劑寮村Δ鈧禍鎯ь渻閵堝骸骞栭柣蹇旂箚閻忔帡姊虹粙璺ㄧ闁告鍕劅濠电姴娲﹂埛鎴犵磼鐎ｎ厽纭堕柣蹇涗憾閺屾稓鈧綆鍋嗛妴鎺旂磼椤旇偐澧︾€规洘锕㈤、娆撴偩鐏炶棄绠炲┑鐘垫暩閸嬬偤宕归棃娑氭殾妞ゆ巻鍋撴い鏇稻閵堬綁宕橀埡鍐ㄥ箞闂備胶绮Λ鍐绩闁秴绐楁慨妞诲亾闁哄矉绱曟禒锔炬嫚閹绘帩鐎抽梻浣哥枃濡嫰藝椤栨繄浜介梻浣稿悑缁佹挳寮插☉娆愬弿濞寸厧鐡ㄩ埛鎺懨归敐鍫綈闁稿濞€閺屾稒绻濋崘顏勨拡闂佸憡甯楃敮锟犵嵁濡吋瀚氶柤纰卞墰閺嗩偊姊绘担铏瑰笡闁告梹娲熼獮鏍敃閵堝洣绗夊┑顔筋焾閸╂牠鍩涢幋鐐簻闁规儳宕俊鍧楁煟閿濆牓鍝虹紒缁樼洴瀹曞吋鎷呴崨濠傤槱闂佺粯鎸鹃崰鏍蓟閿濆绫嶉柛顐亝椤ユ牕鈹戦悙鑼ⅵ濞存粌鐖煎璇测槈濮橈絽浜鹃柨婵嗛娴滄繄鈧娲栭惌鍌炲蓟閳ュ磭鏆嗛柍褜鍓熷畷浼村箻鐠囪尙顔嗛梺缁橆焽缁垶宕甸幋鐐簻闁圭儤鍨垫禍鐐烘煕閻旈澧︽慨?,
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
            "description": "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤掍焦顔囬梻浣虹帛閸旀洟顢氶鐘典笉濡わ絽鍟悡鍐喐濠婂牆绀堟慨妯块哺瀹曞弶绻涢幋娆忕仼鐎瑰憡绻冮妵鍕箻鐠哄搫澹夐梺鍛婃煥椤﹁京妲愰幘瀛樺闁告挻褰冮崜鏉款渻閵堝繐顩柡浣筋嚙閻ｅ嘲煤椤忓嫮鍔﹀銈嗗笂闂勫秵绂嶅鍫熺厵闁绘垶锚閻忋儲銇勮箛濠冩珖缂佽鲸甯￠幃顏勨枎韫囨柨顦╅梺缁樻尪閸庤尙鎹㈠☉銏犵闁诲繑妞挎禍顏堛€侀弮鍫晜闁割偆鍠撻崢鎼佹⒑缁洖澧叉い銊ョ墢缁粯绻濆顓犲幐閻庡厜鍋撻柍褜鍓熷畷浼村冀椤撶姴绁﹀┑顔姐仜閸嬫挻銇勯姀鈥冲摵鐎规洏鍔戦、姘跺川椤曞懏顥㈠┑鐘垫暩婵兘寮幖浣哥；婵炴垯鍨洪崑瀣攽閻樺弶鎼愰柛銊ュ€块弻娑⑩€﹂幋婵囩彯濠电偛鍚嬮悧婊堝箟閹间焦鍋嬮柛顐ｇ箘閻熴劎绱撴担鍝勑￠柛妤佸▕閻涱噣寮介‖銉ラ叄椤㈡鍩€椤掑嫭鍊堕柍鍝勬噺閻撶喖鏌熼悜妯诲鞍闁稿﹥鍔欓弻鈥崇暆鐎ｎ剛袦闂佽鍠掗弲婊冾焽韫囨稑鐓涘ù锝呭閻庢潙鈹戦悩鍨毄濠殿喕鍗冲畷鐟懊洪浣插亾閿曞倸鐐婃い鎺嗗亾缂佺姵鐓￠弻鏇＄疀鐎ｎ亖鍋撻弴鐘差棜濠靛倸鎲￠悡鐔兼煙闁箑澧俊顐ｏ耿閺屾洘寰勯崱妯荤彆闂佺粯鎸诲ú鐔煎箖濮椻偓閹瑩妫冨☉妤€顥氶梻浣圭湽閸斿秹宕归崷顓燁潟闁圭儤鎸哥欢鐐测攽閻愯尙浠㈠ù鐙€鍣ｅ娲传閸曨厾鍔圭紓鍌氱С缁舵岸寮幇鐗堝€峰〒姘煎灡閺呫垽姊洪柅鐐茶嫰婢ь垰菐閸パ嶆敾缂佸倹甯為埀顒婄秵閸嬪棝宕㈤柆宥嗏拺闁告劕寮堕幆鍫ユ煕婵犲偆鐓煎┑鈩冩尦楠炴帒螖娴ｅ搫骞?闂傚倸鍊搁崐鎼佸磹閹间讲鈧箓顢楅崟顐わ紱闂佸憡娲﹂崐瀣洪鍛珖婵炶揪缍€椤宕抽悜鑺モ拻濞达絽婀卞﹢浠嬫煕閳轰礁顏€规洖缍婇、鏃堝醇濠靛牞绱遍梻浣烘嚀閸氬鎮伴惃?闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎮块鈧弻鐔煎礈娴ｇ儤鎲橀梺杞扮閿曨亪寮婚悢鍏肩劷闁挎洍鍋撻柡瀣枑閵囧嫰顢曢敐鍡欘槰缂備胶绮换鍫澪涢崘銊㈡闁告鍋涙竟鍫㈢磽閸屾瑨顔夐柛瀣崌閺屾稑鐣濋埀顒勫磻閻愮儤鍋傞柡鍥╁枂娴滄粓鏌熼柇锕€鏋涚€涙繈姊虹拠鍙夌濞存粠浜?recall_memory 闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛濠呭煐閹便劌螣閹稿海銆愮紒鐐劤濞硷繝寮婚悢鐓庣畾闁绘鐗滃Λ鍕⒑閸濆嫬顏ラ柛搴㈠▕閸┾偓妞ゆ巻鍋撻柛妯荤矒瀹曟垿骞樼紒妯煎帗閻熸粍绮撳畷婊堟偄閻撳孩妲梺閫炲苯澧柕鍥у楠炴帡骞嬪┑鍐ㄤ壕鐟滅増甯掑Ч鏌ユ煃閸濆嫭鍣洪柣鎾寸懇閺屟嗙疀閿濆懍绨奸柣蹇撶箳閺佸寮婚妶鍚ゆ椽顢旈崘鈺佹灓闂備胶鎳撶壕顓熺箾閳ь剚銇勯姀鈽嗘畷闁瑰嘲鎳樺畷婊兠圭€ｎ亙澹曞┑鐐村灟閸ㄦ椽鍩涢幋锔界厱婵犻潧妫楅瀛樹繆閹绘帒鎮戠紒缁樼⊕瀵板嫮鈧綆鍋嗛ˇ顓犵磽娓氬洤鏋涙い顓犲厴閻涱喖螣閼测晝锛滃┑鈽嗗灣閸樠囩嵁?ID闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔告綇妤ｅ啯顎嶉梺鎼炲€栭崝鏍Φ閸曨垰鍐€妞ゆ劦婢€缁爼姊哄Ч鍥р偓銈夊闯閿濆钃熺€广儱鐗滃銊╂⒑閸涘﹥灏甸柛鐘崇墵閻涱噣宕橀鍏煎祶濡炪倖鎸荤粙鎴炵妤ｅ啯鐓ユ繝闈涙閸戝湱绱掗妸銉吋闁哄矉绻濆畷鍗炩枎韫囨梻浜梻浣告惈婢跺洭宕滃┑瀣闁告稑鐡ㄩˉ鍫熺箾閹寸偛绗掑ù婊堢畺閺岋繝宕堕懜鐢电獧缂傚倸绉甸悧鐘诲蓟閺囷紕鐤€閻庯綆浜栭崑鎾诲即閻愬鍑介梻鍌氬€风粈渚€骞夐埄鍐懝婵°倕鎳庣粈鍫熺箾閹存瑥鐏柛搴㈩殕娣囧﹪濡堕崨顔兼闂佹娊鏀遍崹鍦閹烘柡鍋撻敐搴″箺缁绢厼澧庣槐鎺楁偐閸楃偛绁梺鍝勬湰閻╊垱鎱ㄩ埀顒勬煥濞戞ê顏╃€殿喓鍔戦幃妤冩喆閸曨剛顦銈冨灩閿曨亝淇婇悽绋跨疀闁哄娉曢濠囨⒑閸︻叀妾搁柛銊ㄤ含閳ь剙鐏氶悧鐘差潖缂佹鐟归柍褜鍓欓…鍥樄闁诡啫鍥у耿婵炴垶顭囬弻鍫ユ⒑缂佹﹩鐒炬い鏇嗗懎顥?,
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾缁愭鏌熼柇锕€鍔掓繛宸簻缁狅綁鏌ｅΟ鍏兼毄闁绘帒鍚嬬换娑㈠箻閺夋垹鍔伴梺绋款儐閹搁箖鍩€椤掑喚娼愭繛鍙夌矒閵嗕焦绻濋崶顬箓鏌熼悧鍫熺凡缂佺姵濞婇弻鐔虹磼閵忕姷浠柣搴＄仛閻楃姴顫忕紒妯肩懝闁逞屽墮椤洩顦归柟顔ㄥ洤骞㈡俊鐐存礃濡炰粙寮崘顔肩＜婵炴垶眉閹綁姊婚崒娆戣窗闁告挻鐟х划鏃堟偨缁嬭法锛涢梺鎸庣箓閹儻銇愰幒鎾存珳闂佸壊鍋掗崑鍛礊閸垻纾藉ù锝囨嚀閸斿爼鎮樿箛鏃傛噮婵?ID闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔告綇妤ｅ啯顎嶉梺绋款儏椤戝寮诲☉妯锋闁告鍋熸禒鈺呮⒑?recall_memory 缂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌ｉ幋锝呅撻柛濠傛健閺屻劑寮撮悙娴嬪亾閸濄儳涓嶉柡澶婄氨閺€浠嬫煟濡櫣锛嶆い锝嗙叀閺屾稒绻濋崨顔俱€愬銈庡弨濞夋洟骞戦崟顒傜懝妞ゆ牗鑹炬竟瀣⒒娴ｅ摜锛嶇紒顕呭灠椤繗銇愰幒鎳筹箓鏌涢弴銊ョ仩缂佺姷绮妵鍕冀椤垶鐣舵繛瀛樼矊婢т粙鍩€椤掑喚娼愭繛鍙夌墪闇夐柛宀€鍋涢懜褰掓煟閵忕姵鍟為柍閿嬪笒闇夐柨婵嗘噺閸熺偤鏌涢悢鍝勪槐闁哄矉缍侀幃銈夊磼濠婂懏娈奸梻浣筋嚃閸燁偊宕堕懜鍨珝闂備胶绮摫闁告挻鑹鹃…?,
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
            content="闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫㈢磽閸屾瑧璐伴柛瀣缁棁銇愰幒鎴ｆ憰閻庡箍鍎卞ú锕傚磻濮椻偓閺屽秹濡烽妷銉ョ婵犮垼顫夊ú婊呮閹捐纾兼繛鍡樺灥婵¤棄顪冮妶鍐ㄥ闁硅櫕锚閻ｇ兘骞囬悧鍫濅画闂備緡鍙忕粻鎴濃枔椤愶附鈷戦柛娑橈攻婢跺嫰鏌涚€ｎ偄娴€规洏鍎抽埀顒婄秵閸犳鎮￠弴銏＄厸闁搞儯鍎辨俊鍏碱殽閻愮摲鎴炵┍婵犲洤鐭楀璺猴功娴煎苯鈹戦纭峰姛闁稿簺鍊曢…鍥敂閸繄顓煎銈嗘⒒閸樠団€栨径瀣瘈闁汇垽娼цⅷ闂佹悶鍔嶅浠嬪极閸愵喖顫呴柕鍫濆暊閸?,
        )
        db.add(mem)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜滃ù鏍煏婵炵偓娅嗛柛濠傛健閺屻劑寮村Δ鈧禍鎯ь渻閵堝骸骞栭柣蹇旂箞閿濈偛顭ㄩ崼婵堝姦濡炪倖甯掔€氥劑鍩€?},
            db=db,
            user_id="tool-mem-1",
        )
        assert "memories" in result
        assert len(result["memories"]) >= 1
        assert "闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜滃ù鏍煏婵炵偓娅嗛柛濠傛健閺屻劑寮村Δ鈧禍鎯ь渻閵堝骸骞栭柣蹇旂箞閿濈偛顭ㄩ崼婵堝姦濡炪倖甯掔€氥劑鍩€? in result["memories"][0]["content"]


@pytest.mark.asyncio
async def test_recall_memory_empty_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-2", username="toolmem2", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻娑樷攽閸曨偄濮㈤梺娲诲幗閹瑰洭寮婚悢铏圭＜闁靛繒濮甸悘宥夋⒑缁嬫鍎嶉柛濠冪箞瀵寮撮悢铏诡啎闂佺粯鍔﹂崜姘舵偟閺冨牊鈷戦柛锔诲幗閸も偓闂佺粯鐗曢妶绋款嚕婵犳艾鍗抽柣鏃囨椤旀洟鎮峰鍐ら柍褜鍓氶崙褰掑闯閿濆拋鍤曢柟鎯板Г閸嬫劗绱撴担楠ㄦ岸骞忓ú顏呪拺闁告稑锕﹂埥澶愭煥閺囨ê鈧牠骞堥妸鈺佺倞妞ゆ帊鑳堕崢鐢告⒑閸涘﹤濮堥柣鎿勭節瀹曪綁宕熼鍙ョ盎?},
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
            {"category": "preference", "content": "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫ユ⒒娴ｅ湱婀介柛濠冾殜瀹曟垿骞樼拠鑼杽闂侀潧顭堥崕鍝勵焽閵娾晜鐓曢柍鈺佸暔娴狅妇绱掗妸銈囩煓婵﹥妞介幊锟犲Χ閸涱喚鈧箖姊洪崨濠冣拹婵炶尙鍠栭崹楣冩晜閻愵剙纾梺闈涱煭缁犳垹澹曢鐐粹拺闁诡垎鍛唶婵犫拃宥囩М闁轰礁绉瑰畷鐔碱敇閻欏懐搴婇梻鍌欒兌閸嬨劑宕曢柆宥呯柈闁秆勵殢閺佸倹銇勯幘璺盒涢柛瀣尭閳绘捇宕归鐣屽蒋闂備礁鎲￠幐楣冨窗鎼淬劍鍋╅柣鎴ｆ闁卞洭鏌￠崶鈺佷户闁告ê鎲＄换婵嬫偨闂堟刀銏ゆ煕閻旂顥嬬紒?},
            db=db,
            user_id="tool-mem-3",
        )
        assert result["status"] == "saved"

        mems = await db.execute(
            select(Memory).where(Memory.user_id == "tool-mem-3")
        )
        saved = mems.scalars().all()
        assert len(saved) == 1
        assert saved[0].content == "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫ユ⒒娴ｅ湱婀介柛濠冾殜瀹曟垿骞樼拠鑼杽闂侀潧顭堥崕鍝勵焽閵娾晜鐓曢柍鈺佸暔娴狅妇绱掗妸銈囩煓婵﹥妞介幊锟犲Χ閸涱喚鈧箖姊洪崨濠冣拹婵炶尙鍠栭崹楣冩晜閻愵剙纾梺闈涱煭缁犳垹澹曢鐐粹拺闁诡垎鍛唶婵犫拃宥囩М闁轰礁绉瑰畷鐔碱敇閻欏懐搴婇梻鍌欒兌閸嬨劑宕曢柆宥呯柈闁秆勵殢閺佸倹銇勯幘璺盒涢柛瀣尭閳绘捇宕归鐣屽蒋闂備礁鎲￠幐楣冨窗鎼淬劍鍋╅柣鎴ｆ闁卞洭鏌￠崶鈺佷户闁告ê鎲＄换婵嬫偨闂堟刀銏ゆ煕閻旂顥嬬紒?
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
        "message": f"闂傚倸鍊峰ù鍥敋瑜嶉～婵嬫晝閸岋妇绋忔繝銏ｅ煐閸旀牠宕戦妶澶嬬厸闁搞儮鏅涘皬闂佺粯甯掗敃銉╁Φ閸曨喚鐤€闁规崘娉涢埛鍫ユ⒑鏉炴壆顦﹂柨鏇ㄤ邯瀵鈽夐姀鐘栥劑鏌ㄥ┑鍡樺櫣妞ゎ剙顦扮换婵嗏枔閸喚浠梺鐟版啞婵炲﹪骞冮敓鐙€鏁冮柨鏇楀亾闁绘劕锕弻鏇熷緞閸繂濮庢繝娈垮枔閸ㄨ崵妲愰幘瀛樺闁荤喐婢橀～宥夋⒑閸愭彃妲婚柣娑欘劑ntent}",
    }


async def _delete_memory_handler(
    db: AsyncSession, user_id: str, memory_id: str, **kwargs
) -> dict[str, Any]:
    """Delete a long-term memory by ID."""
    deleted = await delete_memory(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "闂傚倸鍊峰ù鍥敋瑜嶉湁闁绘垼妫勭粻鐘绘煙閹规劦鍤欑紒鐘靛枛濮婁粙宕堕鈧闂佸湱澧楀妯肩矆閸愨斂浜滈柡鍐ㄥ€哥敮鍫曟煟鎼搭喖寮柟顔煎槻椤劑宕ㄩ褎姣夐梺姹囧焺閸ㄩ亶銆冩繝鍥ф槬婵炴垯鍨圭猾宥夋煕椤愩倕鏋旈柛姗嗕邯濮婃椽宕滈幓鎺嶇凹缂備浇顕х€氼參寮查崼鏇熺劶鐎广儱妫涢崢閬嶆⒑闂堟稓澧曢柟宄邦儏铻ｉ柍褜鍓熷铏规嫚閳ヨ櫕鐏曞銈庡亜椤︾敻鐛箛娑樺窛妞ゆ牗绋戦弸鍌炴⒑閸涘﹥澶勯柛妯恒偢瀹曠敻骞掗弮鍌滐紳?}
    return {"error": "闂傚倸鍊搁崐宄懊归崶褏鏆﹂柛顭戝亝閸欏繘鏌熼幆鏉啃撻柛濠傛健閺屻劑寮村Δ鈧禍鎯ь渻閵堝骸骞栭柣蹇旂箚閻忔帡姊虹粙璺ㄧ闁告鍕劅濠电姴娲﹂埛鎴犵磼鐎ｎ偄顕滄繝鈧幍顔剧＜閻庯綆鍋呭畷宀勬煕閳瑰灝鐏茬€殿噮鍣ｅ畷鎺懳旈埀顒佺閻愵剦娈介柣鎰皺娴犮垽鏌涢弮鈧畝鎼佸蓟閻斿吋鎯炴い鎰╁灩椤帒螖閻橀潧浠︽い銊ワ躬楠炲啴鍩￠崘顏嗭紲濠碘槅鍨抽崢褔鐛崼銉︹拻濞达絿鎳撻婊堟煛鐏炶濮傛鐐寸墵椤㈡洟鏁愰崟顓犵暰濠电偛顕慨鎾敄閸℃稒鍋傞柡鍥ュ灪閻撳繐鈹戦悩鑼闁告帗婢橀埞鎴︻敊閻撳簶鍋撴繝姘劦妞ゆ帊绶￠崯蹇涙煕閿濆骸娅嶇€规洘濞婇弫鎰緞婵犲嫮鏆梻浣稿暱閹碱偊骞婅箛娑樼畾闁绘劖鐣禍婊堟煙閹佃櫕娅呴柍褜鍓氶〃澶愬焻閺屻儲鈷掗柛灞捐壘閳ь剟顥撶划鍫熺瑹閳ь剟鐛径鎰櫖闁告洦鍓氬▓浼存⒑缂佹ê濮囨い鏇ㄥ幘缁粯銈ｉ崘鈺冨帗閻熸粍绮撳畷婊冾潩鏉堛劌搴?}
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
            "slots": [{"date": f"2026-04-{i:02d}", "weekday": "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣埖鍔栭崐鐢告煥濠靛棝顎楀褌鍗抽弻?, "free_periods": [{"start": "08:00", "end": "22:00", "duration_minutes": 840}], "occupied": []} for i in range(1, 8)],
            "summary": "2026-04-01 闂?2026-04-07 闂?7 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村蓟閵夛妇鍘介梺褰掑亰閸撴岸骞嗛崼銉︾厽闁规崘鎻懓鍧楁煛鐏炵硶鍋撻幇浣告倯闁硅偐琛ラ埀顒€纾鎴︽⒒娴ｇ懓鈻曢柡鈧潏鈺傛殰闁跨喓濮撮拑鐔哥箾閹寸們姘跺几鎼淬劎鍙撻柛銉╊棑缁嬪鏌嶇紒妯诲磳婵﹥妞藉畷顐﹀Ψ閵夈倗閽电紓鍌欑贰閸犳鎮烽埡渚囧殨濠电姵鑹炬儫闂侀潧顦崹娲綖瀹ュ應鏀介柍钘夋閻忥絿绱掗鍛仸妤犵偛绻橀弻鍡楊吋閸″繑瀚奸梻鍌欑贰閸嬪棝宕戝☉銏″殣妞ゆ牗绋掑▍鐘炽亜閺嶃劎鈼ョ紒璇叉閺屾稑鈻庤箛锝喰﹀┑鐐存儗閸犳濡?98 闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃繘骞戦姀銈呯疀妞ゆ棁妫勬惔濠囨⒑瑜版帒浜伴柛鐘愁殔閻ｇ兘寮婚妷锔惧幍闁诲孩绋掗…鍥╃不閵夛妇绠?0 闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤掍焦顔囬梻浣告贡閸庛倝宕甸敃鈧埥澶娢熼柨瀣澑闂佽鍑界紞鍡樼閻愪警鏁?,
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
                assert "7 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村蓟閵夛妇鍘介梺褰掑亰閸撴岸骞嗛崼銉︾厽闁规崘鎻懓鍧楁煛鐏炵硶鍋撻幇浣告倯闁硅偐琛ラ埀顒€纾鎴︽⒒娴ｇ懓鈻曢柡鈧潏鈺傛殰闁跨喓濮撮拑鐔哥箾閹寸們姘跺几鎼淬劎鍙撻柛銉╊棑缁嬪鏌嶇紒妯诲磳婵? in content
                return {"role": "assistant", "content": "濠电姷鏁告慨鐑藉极閹间礁纾婚柣妯款嚙缁犲灚銇勮箛鎾搭棞缂佽翰鍊濋弻鐔虹矙閸噮鍔夐梺鍛婄懃缁绘﹢寮诲☉銏犵婵°倐鍋撻悗姘煎墯閹梹绻濋崶銊㈡嫼闂佸憡绻傜€氼噣鍩㈡径鎰厱婵☆垳鍘х敮鑸点亜閺傝法绠伴柍瑙勫灩閳ь剨缍嗛崑鍡涘储椤忓懐绡€闁汇垽娼у瓭缂備胶绮敋妞ゎ剙锕、娆撳礈瑜忛敍婊堟⒑缂佹◤顏堝疮鐠恒劎绠旂憸鏃堝蓟瀹ュ牜妾ㄩ梺鍛婃尰閻熲晠骞冨Ο渚僵妞ゆ帒顦遍崬闈涒攽椤斿浠滈柛瀣崌閺岀喖顢欓妸銉︽悙妤犵偑鍨虹换娑氣偓娑櫳戠欢鍙夌箾鐏炲倸濮傛鐐村灴瀹曠喖顢涘В灏栨櫇閹叉瓕绠涘☉娆忎簵闂佸搫鍊哥花閬嶅绩娴犲鐓熼柟閭﹀墮缁狙囨煃缂佹ɑ绀€闂囧绻濇繝鍌氼伀缂佺姷鍋ら弻鈩冩媴閸濄儛銏ゆ煃鐟欏嫬鐏╅柍褜鍓ㄧ紞鍡涘磻閸℃稑鍌ㄩ柟闂寸劍閳锋垿鏌涘☉姗堝伐濠殿喖鍊块弻娑㈠棘閸ф寮伴悗瑙勬礃濡炰粙寮幇鏉垮耿闁哄洨濮烽悾鐐繆閻愵亜鈧牠宕濋幋锕€鍨傛繛宸簻绾惧鏌曟径鍡樻珕闁?}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                gen = run_agent_loop("闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈠Χ閸℃ぞ绮℃俊鐐€栭崝褏绮婚幋鐘差棜闁秆勵殕閻撴洟鏌熼柇锕€鐏遍柛銈咁儔閺屻倝寮堕幐搴′淮闂佸搫鏈粙鎴﹀煡婢舵劕纭€闁绘劕鍚€閸栨牠姊绘担瑙勩仧闁告鏅崰濠傤吋閸ャ劌搴婂┑鐐村灦閿曗晠宕崨顔轰簻闁哄啫娲ら崥褰掓煕閹存繄绉烘慨濠冩そ楠炴劖鎯旈敐鍌氼潓缂傚倷娴囬褔鎮ч幘鎰佸殨濠电姵纰嶉弲鎼佹煟濡灝鐨烘い锔哄姂濮婃椽妫冨ù銈嗙洴瀹曟﹢顢旈崟顐ゎ啈濠?, user, "test-session", db, AsyncMock())
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
        pref = Memory(user_id="ctx-user-1", category="preference", content="闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫㈢磽閸屾瑧璐伴柛瀣缁棁銇愰幒鎴ｆ憰閻庡箍鍎卞ú锕傚磻濮椻偓閺屽秹濡烽妷銉ョ婵犮垼顫夊ú婊呮閹捐纾兼繛鍡樺灥婵¤棄顪冮妶鍐ㄥ闁硅櫕锚閻ｇ兘骞囬悧鍫濅画闂備緡鍙忕粻鎴濃枔椤愶附鈷戦柛娑橈攻婢跺嫰鏌涚€ｎ偄娴€规洏鍎抽埀顒婄秵閸犳鎮￠弴銏＄厸闁搞儯鍎辨俊鍏碱殽閻愮摲鎴炵┍婵犲洤鐭楀璺猴功娴煎苯鈹戦纭峰姛闁稿簺鍊曢…鍥敂閸繄顓煎銈嗘⒒閸樠団€栨径瀣瘈闁汇垽娼цⅷ闂佹悶鍔嶅浠嬪极閸愵喖顫呴柕鍫濆暊閸?)
        habit = Memory(user_id="ctx-user-1", category="habit", content="濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔虹磼閵忕姵鐏堢紒鐐劤椤兘寮婚悢鐓庣畾鐟滄粓宕甸悢铏圭＜闁绘宕甸悾娲煛鐏炲墽娲撮柛銊﹀劤閻ｇ兘宕堕埡濠傛暪婵犵數濮幏鍐礃閵娧囩崜缂傚倷鑳剁划顖炴儎椤栫偟宓佹慨妞诲亾闁诡喚鍏橀獮宥夘敊閻撳海绱伴梻浣筋嚙妤犳悂鎮樺顒夌唵婵☆垰鐨烽崑鎾愁潩閻撳骸鈷嬮梺鎸庣箘閸嬫盯鍩為幋鐘亾閿濆骸浜滄繛鍫熺箖缁绘稒娼忛崜褍鍩岄梺鍝ュ櫏閸嬪懐绮嬪澶婂唨鐟滃寮?闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃繘骞戦姀銈呯疀妞ゆ棁妫勬惔濠囨⒑瑜版帒浜伴柛鐘愁殔閻ｇ兘寮婚妷锔惧幍闁诲孩绋掗…鍥╃不閵夛妇绠?)
        db.add_all([pref, habit])
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫㈢磽閸屾瑧璐伴柛瀣缁棁銇愰幒鎴ｆ憰閻庡箍鍎卞ú锕傚磻濮椻偓閺屽秹濡烽妷銉ョ婵犮垼顫夊ú婊呮閹捐纾兼繛鍡樺灥婵¤棄顪冮妶鍐ㄥ闁硅櫕锚閻ｇ兘骞囬悧鍫濅画闂備緡鍙忕粻鎴濃枔椤愶附鈷戦柛娑橈攻婢跺嫰鏌涚€ｎ偄娴€规洏鍎抽埀顒婄秵閸犳鎮￠弴銏＄厸闁搞儯鍎辨俊鍏碱殽閻愮摲鎴炵┍婵犲洤鐭楀璺猴功娴煎苯鈹戦纭峰姛闁稿簺鍊曢…鍥敂閸繄顓煎銈嗘⒒閸樠団€栨径瀣瘈闁汇垽娼цⅷ闂佹悶鍔嶅浠嬪极閸愵喖顫呴柕鍫濆暊閸? in context
        assert "濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔虹磼閵忕姵鐏堢紒鐐劤椤兘寮婚悢鐓庣畾鐟滄粓宕甸悢铏圭＜闁绘宕甸悾娲煛鐏炲墽娲撮柛銊﹀劤閻ｇ兘宕堕埡濠傛暪婵犵數濮幏鍐礃閵娧囩崜缂傚倷鑳剁划顖炴儎椤栫偟宓佹慨妞诲亾闁诡喚鍏橀獮宥夘敊閻撳海绱伴梻浣筋嚙妤犳悂鎮樺顒夌唵婵☆垰鐨烽崑鎾愁潩閻撳骸鈷嬮梺鎸庣箘閸嬫盯鍩為幋鐘亾閿濆骸浜滄繛鍫熺箖缁绘稒娼忛崜褍鍩岄梺鍝ュ櫏閸嬪懐绮嬪澶婂唨鐟滃寮?闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃繘骞戦姀銈呯疀妞ゆ棁妫勬惔濠囨⒑瑜版帒浜伴柛鐘愁殔閻ｇ兘寮婚妷锔惧幍闁诲孩绋掗…鍥╃不閵夛妇绠? in context


@pytest.mark.asyncio
async def test_warm_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-2", username="ctxtest2", hashed_password="x")
        db.add(user)
        decision = Memory(user_id="ctx-user-2", category="decision", content="濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴濆敤濡炪倖鎸鹃崑鐔兼偩閻戞绠鹃悗鐢殿焾瀛濆銈嗗灥閹冲繘宕曢锔解拻濞撴埃鍋撴繛浣冲泚鍥敇閵忕姷锛熼梺瑙勫劶濡嫰鎮為崹顐犱簻闁圭儤鍨甸弳娆撴煕濮橆剚璐＄紒杈ㄥ笚濞煎繘濡搁妷锕佺檨闁诲孩顔栭崳顕€宕抽敐鍛殾闁圭儤鍤╅幒鎴旀瀻闁诡垎鍐炬交闂備礁鐤囬～澶愬垂閸ф鏄ラ柕澶嗘櫅楠炪垺淇婇妶鍌氫壕缂備胶濮惧畷鐢垫閹惧鐟归柛銉戝嫮浜鹃梻浣芥〃濞村洭顢氳椤㈡岸鏁愰崱娆樻祫闁诲函绲介悘姘跺疾濠靛鈷戦柟绋挎捣缁犳挻淇婇顐㈠籍鐎?)
        db.add(decision)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴濆敤濡炪倖鎸鹃崑鐔兼偩閻戞绠鹃悗鐢殿焾瀛濆銈嗗灥閹冲繘宕曢锔解拻濞撴埃鍋撴繛浣冲泚鍥敇閵忕姷锛熼梺瑙勫劶濡嫰鎮為崹顐犱簻闁圭儤鍨甸弳娆撴煕濮橆剚璐＄紒杈ㄥ笚濞煎繘濡搁妷锕佺檨闁诲孩顔栭崳顕€宕抽敐鍛殾闁圭儤鍤╅幒鎴旀瀻闁诡垎鍐炬交闂備礁鐤囬～澶愬垂閸ф鏄ラ柕澶嗘櫅楠炪垺淇婇妶鍌氫壕缂備胶濮惧畷鐢垫閹惧鐟归柛銉戝嫮浜鹃梻浣芥〃濞村洭顢氳椤㈡岸鏁愰崱娆樻祫闁诲函绲介悘姘跺疾濠靛鈷戦柟绋挎捣缁犳挻淇婇顐㈠籍鐎? in context


@pytest.mark.asyncio
async def test_no_memories_still_works(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-3", username="ctxtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        context = await build_dynamic_context(user, db)
        # Should still have time info, just no memory section
        assert "闂傚倸鍊峰ù鍥х暦閻㈢绐楅柟閭﹀枛閸ㄦ繈骞栧ǎ顒€鐏繛鍛У娣囧﹪濡堕崨顔兼缂備胶濮抽崡鎶藉蓟濞戞ǚ妲堟慨妤€鐗婇弫鎯р攽閻愬弶鍣藉┑鐐╁亾闂佸搫鐭夌徊鍊熺亽濠电偛妫欓崕鍐测枔椤撶姷纾藉〒姘搐娴滄粎绱掓径濠勭Ш鐎殿喛顕ч埥澶愬閳哄倹娅囬梻浣瑰缁诲倸螞濞戔懞鍥Ω閳哄倵鎷? in context


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
            summary="濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔兼⒒鐎电濡介梺鍝勬噺缁诲牓寮婚弴鐔风窞闁糕剝蓱閻濓箓姊烘潪鎵槮闁哥喐鎸冲濠氬Χ閸氥倕婀遍埀顒婄秵閸嬪懎顭块幒妤佲拺缂佸顑欓崕鎰版煙閻熺増鍠樻鐐插暣閹稿﹥寰勯崱妯间簴闂備礁婀遍…鍫⑩偓娑掓櫊瀵娊鎮欓悜妯锋嫽婵炶揪缍侀ˉ鎾寸▔閼碱剛纾介柛灞剧⊕閻ㄦ垿鏌涢幒鎾崇瑨闁宠閰ｉ獮姗€鎼归銈傚亾椤掑嫭鍊垫鐐茬仢閸旀岸鏌熷畡閭﹀剰妞ゎ厼娲崺锟犲川椤撶娀鐛撻梻浣稿閸嬪懐绮欓幋鐐扮箚闁兼亽鍎崇粻楣冩煕椤愶絿鈽夐柣蹇撳级閹便劍绻濋崨顕呬哗闂佺懓寮堕幐鍐茬暦閻旂⒈鏁嗛柛灞惧閺嬪繘姊婚崒娆戝妽闁诡喖鐖煎畷鐟懊洪鍛簵闂佽法鍠撴慨浼村焵椤戣法顦︽い顐ｇ箞閹虫粓鎮介棃娑樞﹂梺璇查缁犲秹宕曢柆宥呯疇闁规澘鍙撻崶顏嶆▌濠殿喖锕ュ钘壩涢崘銊㈡閺夊牄鍓遍妶澶嬧拺缂佸灏呴弨缁樸亜閵娿儻宸ラ柣锝囧厴椤㈡稑鈽夊杈╂闂備焦鎮堕崕顖炲礉鐏炲墽顩锋い鏍仦閳锋垿鏌熼懖鈺佷粶闁告梹锕㈤弻娑㈠棘鐠恒劎浼囩紓渚囧枛閻楁挸鐣峰鈧、娆撴偩鐏炶棄濡囬梻鍌欒兌绾爼宕滃┑瀣ㄢ偓鍐川閺夋垶杈堥梺鎸庣箓椤︿即鎮″☉妯忓綊鏁愰崨顔藉枑閻庢稒绻堝鐑樺濞嗘垹蓱缂備浇顕ч悧鍡涙偩瀹勯偊娼ㄩ柍褜鍓熼悰顕€宕卞鍏夹繝鐢靛仜閹冲繘銆冮崼銏☆潟闁规崘顕х壕鍏兼叏濮楀棗鍘撮柛瀣崌楠炴牗鎷呴崫銉у炊婵犳鍠楅…鍫濃枖濞戞氨鐜绘俊銈呮噺閻撴盯鏌涢妷銏℃珔闂夊绻?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌熼梻瀵割槮缁炬儳缍婇弻娑㈩敃閿濆棛顦ョ紓浣插亾濠㈣埖鍔楅崣鎾绘煕閵夛絽濡块柍钘夘樀閺岋綁骞掗幋鐘辩驳闂侀潧娲ょ€氫即鐛幒妤€骞㈡俊鐐村劤椤ユ岸姊婚崒娆戭槮闁硅姤绮撳畷浼村箛椤撶姷顔曟繝鐢靛Т濞层倗绮诲顑锯偓鎺戭潩閿濆懍澹曟俊鐐€戦崹娲儎椤栫偛绠栨繛鍡樻尭缁狙囨煙鐎涙绠撴い銉ヮ樀濮婂宕掑▎鎴М闂佽绁撮埀顒冪М濞差亝鏅濋柛灞炬皑閿涙盯姊洪崷顓炲妺闁搞倧绠撻弫鎰板炊閵娿儳褰存繝鐢靛仦濞兼瑩顢栭崱娑崇稏鐎广儱顦伴埛鎴︽煕濠靛棗顏╅柡鍡樼懇閺屾稒绻濋崘鈺佲偓鎰版煟鎼淬劍鏁卞ǎ鍥э躬閹瑩顢旈崟銊ヤ壕闁哄稁鍘肩粻鏉库攽閻樺疇澹樼紒鐘崇墵閺屾稓浠﹂悙顒傛闂?,
        )
        db.add(summary)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃秹婀侀梺缁樺灱濡嫰寮告笟鈧弻鐔兼⒒鐎靛壊妲梺绋胯閸斿酣骞夐幖浣告閻犳亽鍔嶅▓楣冩⒑閹稿海绠撴い锔诲灦閻涱噣濮€閳ヨ尙绠氬銈嗙墬婢规洟骞忛埄鍐闁告瑥顦伴崐鎰叏婵犲懏顏犻柛鏍ㄧ墵瀵挳鎮欏ù瀣珶闂傚倷绀侀幉锟犲垂閻㈢數绀婂┑鐘插€婚弳锕傛煟閵忕姵鍟為柡鍛箞閺屾稓浠﹂崜褉妲堟繛? in context
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

WEEKDAY_NAMES = ["闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣埖鍔栭崐鐢告煥濠靛棝顎楀褌鍗抽弻?, "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣埖鍔栭崐鐢告煥濠靛棝顎楀褎褰冮埞?, "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣埖鍔栭崐鐢告煥濠靛棝顎楀褎澹嗙槐?, "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣埖鍔栭崐鍫曟煟閹邦喗鏆╅柛?, "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣埖鍔栭崐鐢告煥濠靛棝顎楀褎褰冮埞?, "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣泛澶囬崑鎾诲礂婢跺﹣澹曢梻浣告啞濞诧箓宕戦崱娑欏亗?, "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤撶姷鍘梻濠庡亜濞诧妇绮欓幋鐘电焼濠㈣泛澶囬崑鎾荤嵁閸喖濮庨梺?]


async def build_dynamic_context(user: User, db: AsyncSession) -> str:
    """Build the dynamic portion of the system prompt."""
    now = datetime.now(timezone.utc)
    today = now.date()
    weekday = today.isoweekday()

    parts: list[str] = []
    parts.append(f"闂傚倸鍊峰ù鍥х暦閻㈢绐楅柟閭﹀枛閸ㄦ繈骞栧ǎ顒€鐏繛鍛У娣囧﹪濡堕崨顔兼缂備胶濮抽崡鎶藉蓟濞戞ǚ妲堟慨妤€鐗婇弫鎯р攽閻愬弶鍣藉┑鐐╁亾闂佸搫鐭夌徊鍊熺亽濠电偛妫欓崕鍐测枔椤撶姷纾藉〒姘搐娴滄粎绱掓径濠勭Ш鐎殿喛顕ч埥澶愬閳哄倹娅囬梻浣瑰缁诲倸螞濞戔懞鍥Ω閳哄倵鎷洪梺鍦焾濞寸兘濡撮幒妤佺厱闁绘ê纾晶鐢碘偓娈垮枛椤攱淇婇幖浣肝ㄩ柕蹇婃濞兼梹绻濋悽闈涗粶婵☆偅鐟╅弫瀣節濞堝灝鏋ゆ繝鈧瀵?strftime('%Y-%m-%d %H:%M')}闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔衡偓娑欘焽缁犮儵鏌ｉ弬鎸庮棦闁哄矉绻濆畷鐓庘槈閹烘垳澹曞銈冨妿瀹撴摖AY_NAMES[weekday - 1]}闂?)

    if user.current_semester_start:
        delta = (today - user.current_semester_start).days
        week_num = delta // 7 + 1
        parts.append(f"闂傚倸鍊峰ù鍥х暦閻㈢绐楅柟閭﹀枛閸ㄦ繈骞栧ǎ顒€鐏繛鍛У娣囧﹪濡堕崨顔兼缂備胶濮抽崡鎶藉蓟濞戞ǚ妲堟慨妤€鐗婇弫鎯р攽閻愬弶鍣藉┑鐐╁亾闂佸搫鐭夌徊鍊熺亽缂佺偓濯芥ご绋啃掑畝鍕拺缂佸顑欓崕鎰版煙閸涘﹥鍊愰柛鈹垮劜瀵板嫰骞囬鍌ゅ敶闂備礁鍚嬫禍浠嬪磿濞差亜鐒垫い鎺嗗亾缂佸鎸抽崺鐐哄箣閿旇棄浜瑰銈嗗姦濠⑩偓濠㈣娲熷缁樻媴閼恒儳銆婇梺鍝ュУ閹稿骞堥妸鈺傚仺缂佸娉曢弻褍顪冮妶鍡楃瑐闁绘帪绠撳畷锝堢疀閺冣偓閸欏繑淇婇悙棰濆殭濞存粌澧界槐鎺旂磼閵忕姴绠洪梺璇″枛閸婃悂鎮鹃悜钘夊嵆闁靛繒濮烽悿鍛存⒑鐟欏嫬绲婚柣锝囶潎k_num}闂?)

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

    parts.append("\n濠电姷鏁告慨鐑藉极閹间礁纾绘繛鎴欏焺閺佸銇勯幘璺烘瀾闁告瑥绻橀弻鐔虹磼閵忕姵鐏嶉梺鍝勬噺缁诲牓寮婚弴銏犻唶婵犲灚鍔栫瑧濠碘剝顨呴幊蹇曟崲濠靛顫呴柨婵嗘噽閸橆偊姊洪崨濠冣拹闁绘濮撮悾鐑藉即閻戝棗鎮戞繝銏ｆ硾椤戝洭宕㈤柆宥嗏拺闁告繂瀚崒銊╂煕閺傛寧婀伴柡鍛埣椤㈡盯鎮欑€电寮虫繝鐢靛仦閸ㄥ爼鏁冮埡浣勶綁鎼归崷顓狅紲闁哄鐗勯崝宀€绮閺屽秷顧侀柛鎾卞妿缁辩偤宕卞Ο纰辨锤闂佸壊鍋呭ú鏍閹稿海绡€濠电姴鍊归崳鐣岀棯?)
    if not courses and not tasks:
        parts.append("- 闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎮块鈧弻锝呂旈埀顒勬偋婵犲洤鐭楅煫鍥ㄧ⊕閻撴瑧绱撴担闈涚仼闁哄鍠栭弻娑氣偓锛卞嫭鐝氶梺鍝勬湰濞叉鎹㈠☉銏″€锋い鎺嶈兌瑜板懐绱?)
    else:
        for course in courses:
            location = f" @ {course.location}" if course.location else ""
            parts.append(f"- {course.start_time}-{course.end_time} {course.name}{location}闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔告綇妤ｅ啯顎嶉梺绋款儏椤戝寮婚悢绋款嚤闁哄鍨抽崰濠囨⒑鏉炴壆顦︽い鎴濇喘閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏婵炵偓娅嗛柛搴㈩殕缁绘盯宕卞Ο璇查瀺闂佺锕﹂弫濠氬蓟閵娿儮鏀介柛鈩兠▍锝咁渻閵堝繒鍒扮痪缁㈠幘濡叉劙骞掑Δ鈧悞?)
        for task in tasks:
            status_mark = "闂? if task.status == "completed" else "闂?
            parts.append(f"- {task.start_time}-{task.end_time} {task.title}闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔衡偓娑欘焽缁犮儵鏌ｉ弬鎸庮棦闁哄备鍓濆鍕偓锝庡亜閻ㄢ暆tus_mark}闂?)

    # User preferences
    preferences = user.preferences or {}
    if preferences:
        parts.append("\n闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇楀亾妞ゎ亜鍟村畷褰掝敋閸涱垰濮洪梻浣侯潒閸曞灚鐣剁紓浣插亾濠㈣泛澶囬崑鎾荤嵁閸喖濮庡銈忓瘜閸ㄨ泛顕ｆ导鏉懳ㄩ柨鏂垮⒔椤旀洟姊洪悷鎵憼闁荤喆鍎甸幃姗€鍩￠崘顏咃紡闂佽鍨庡畝鈧崥瀣⒑缂佹ɑ鎯勯柛瀣工閻ｇ兘宕奸弴鐐嶁晠鏌ㄩ弴妤€浜鹃梺钘夊閵堢顫忛搹鍦煓婵炲棙鍎抽崜顓㈡⒑閸涘﹥鈷愰柛銊ョ仢椤?)
        if "earliest_study" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晜閽樺缃曢梻浣告啞閸旓箓宕伴弽顐㈩棜濠电姵纰嶉悡娆撴煕閹炬鎳庣粭锟犳⒑缂佹ɑ灏伴柣鈺婂灦瀵鈽夐姀鐘电杸闂佸憡鎸烽懗鎯版懌濠电姷鏁搁崑娑㈠箠鎼淬劌绠犻煫鍥ㄧ☉妗呴梺鍛婃处閸ㄦ壆绮婚幎鑺ョ厸闁稿本绋戦婊堟煟鎼粹€斥挃缂佽鲸鎸婚幏鍛村礈閹绘帒澹堥梻浣瑰濞诧附绂嶉鍫㈠祦闁告劦鍠栭悡娑㈡煕濞戝崬鏋熼柛搴簻椤啴濡堕崱妤€袝闂佺顑呴幊鎾诲焻閸洘鈷掗柛灞捐壘閳ь剚鎮傚畷鎰板箹娴ｅ摜锛欓梺褰掓？缁€浣哄閻熸噴褰掓偐瀹割喖鍓扮紓浣哄Т閻忔岸濡甸崟顔剧杸闁圭偓鎯屽Λ鈥愁渻閵堝骸浜濇繛鑼枛瀵鏁愭径濞⑩晠鏌ㄩ弮鍌涘殌鐟滄澘绱ferences['earliest_study']}")
        if "latest_study" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晜閽樺缃曢梻浣告啞閸旓箓宕伴弽顐㈩棜濠电姵纰嶉悡娆撴煕閹炬鎳庣粭锟犳⒑缂佹ɑ灏伴柣鈺婂灦瀵鈽夊Ο閿嬵潔闂佸憡顨堥崑鐐烘倶閺囩喓绡€闁靛骏缍嗗鎰版嫅闁秵鐓忛柛銉戝喚浼冨Δ鐘靛仦鐢€愁嚕椤掑嫬绠伴幖杈剧岛閸嬫捇宕滆绾捐棄霉閿濆懎顥忛柛搴＄箻閺屻劑寮撮妸銈夊仐濡ょ姷鍋涢崯鎾春閿熺姴宸濇い鏃囨閸旀帗淇婇悙顏勨偓鏍礉閿曞倸纾婚柛娑欏閸欓箖姊婚崒姘偓鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌熼梻瀵割槮缁惧墽鎳撻湁闁绘ê妯婇崕蹇曠磼閻樿尙浠涢柕鍥у缁犳盯骞橀幖顓燂紒婵＄偑鍊ら崑鍛洪悢鐓庤摕闁挎繂顦儫闂佹寧姊婚幊鎾广亹瀵亰ferences['latest_study']}")
        if "lunch_break" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫鎾绘偐椤旂懓浜鹃柛鎰靛枛瀹告繈鎮楀☉娅亝绂嶉柆宥嗏拺闁告稑锕ｇ欢閬嶆煕閵娾晙鎲鹃柨婵堝仱瀵挳濮€閿涘嫬甯鹃梻浣稿閸嬪懐鎹㈠鍛傦綀銇愰幒鎾跺幐闂佸憡绮堢粈浣规櫠椤栫偞鐓欏〒姘仢婵″ジ鏌嶇憴鍕伌鐎规洖銈搁幃銏ゅ传閵夈倗绀坮eferences['lunch_break']}")
        if "min_slot_minutes" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晜閽樺缃曢梻浣告啞閸旓箓宕伴弽顐㈩棜濠电姵纰嶉悡娆撴煕閹炬鎳庣粭锟犳⒑缂佹ɑ灏甸柛鐘冲姍婵＄敻宕熼姘鳖啋濠德板€愰崑鎾绘煕閻曚礁浜炵紒顔碱煼瀹曨偊宕熼妸锔芥澑闂備胶绮敃鈺呭磻閸曨剛顩查柣鎰靛墰缁犻箖鏌熼悙顒佺稇闁绘帒缍婇弻娑氣偓锝庡亝鐏忕敻鏌嶈閸撴岸顢欓弽顓為棷妞ゆ洍鍋撶€规洘鍨剁换婵嬪磼濠婂嫭顔曞┑鐘绘涧閸婃悂骞夐敓鐘茬；闁告洦鍨遍悡鏇㈡煙閹冩毐缂佺嫏鍛仏鐟滃秹鍩為幋锔藉亹闁割煈鍋呭В鍕⒑缁嬫鍎愰柣鈺婂灦楠炲啳顦剁紒鐘崇☉閳藉寮介妶鍛闂佺鐬奸崕鎰板极婵犲洦鐓熼柟浼存涧婢х粯绻涢懖鈺佹灈婵﹤鎼晥闁搞儜鍐剧€撮梻浣瑰墯娴滅偛鈻撳鍧抏rences['min_slot_minutes']}闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤掍焦顔囬梻浣告贡閸庛倝宕甸敃鈧埥澶娢熼柨瀣澑闂佽鍑界紞鍡樼閻愪警鏁?)
        if "school_schedule" in preferences:
            parts.append("- 闂傚倸鍊峰ù鍥敋瑜嶉湁闁绘垼妫勭粻鐘绘煙閹规劦鍤欑紒鐘靛枛閺屻劑鎮㈤崫鍕戯綁鏌涚€ｎ亜鈧潡寮婚妸鈺傚亜闁告繂瀚呴姀銈嗙厱閻忕偠顕ф慨鍌炴煛鐏炵偓绀嬬€规洜鍘ч埞鎴﹀炊瑜忛悰鈺冪磽娴ｇ懓鍔ゅ褌绮欏畷鎴﹀箻鐠囧弬锕傛煕閺囥劌鐏犵紒顐㈢Ч閺屾盯濡烽幋婵嗘殲闁稿寒浜炵槐鎾诲磼濞嗘埈妲銈嗗灥閹虫﹢寮崘顕呮晜闁割偅绻嗛幗鏇㈡⒑缂佹ɑ鈷掗柍宄扮墦瀵偊宕堕埡鍌氭瀾閻庡箍鍎遍ˇ浼村磹閸洘鐓冮柍杞扮閺嗘洜绱掔拠鍙夘棦闁哄矉缍侀獮鍥敇閻愮數銈烽梻渚€鈧偛鑻晶顕€鏌ｈ箛鏃傜疄闁挎繄鍋犵粻娑樷槈濞嗗繑顓奸梻渚€娼ч悧鍡涘箯鐎ｎ€稑顭ㄩ崼鐔哄幗闁瑰吋鎯岄崹宕囩矈閻戣姤鐓曢柡鍌涱儥濡偓閻?)

    # Hot memories (preferences + habits) 闂?always loaded
    hot_memories = await get_hot_memories(db, user.id)
    if hot_memories:
        parts.append("\n闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌ｉ姀銏╃劸缁炬儳顭烽弻鐔煎礈瑜忕敮娑㈡煟閹惧鎳呯紒杈ㄥ笧閳ь剨缍嗘禍鐐寸閵徛颁簻闁瑰搫顑呴悘鏌ユ煛鐏炲墽娲撮柛鈹惧墲閹峰懐鍖栭弴鐐板闂佺鍕垫當缂佺姵鐗犻幃宄扳枎韫囨搩浠炬繝娈垮灡閹告娊骞冨畡鎵虫瀻闊洦鎼╂导鈧梻浣告啞閸╁﹦妲愰弴鐘愁潟闁规儳鐡ㄦ刊瀵哥磼濞戞﹩鍎忔繛鍫弮濮婅櫣绮欓崠鈥充紣濠电偛鐨烽埀顒佸墯閸ゆ洘銇勯幇鈺佺労闁告艾顑呴…璺ㄦ崉閻氱鍚梺鍝ュ仩濞夋盯鍩為幋锔藉亹缂備焦蓱闁款參姊虹涵鍛彧闁告梹鐟ラ悾宄邦煥閸惊鈺呮煥閺傚灝鈷旈柣锕€鐗撳濠氬磼濮樺崬顤€缂備礁顑嗛崹鍧楀春閳ь剚銇勯幒鍡椾壕缂傚倸绉撮敃銈夋偩閻戣姤鍋￠柟浣冩珪閺傗偓闂備礁澹婇崑渚€宕规繝姘仼闁割偅娲橀悡鐔肩叓閸ャ劍绀€濞寸姵绮岄…鑳槺缂侇喗鐟╁畷娲閵堝懎宓嗛梺闈涢獜缁辨洟宕㈤挊澶嗘斀闁宠棄妫楅悘鐘绘煙绾板崬浜扮€殿喗濞婇弻鍡楊吋閸℃瑥骞堥梻浣告惈閸燁偊宕愯ぐ鎺戞辈妞ゆ帒瀚悡娑㈡倶閻愰鍤欏┑鈥炽偢閺屽秹鎸婃径妯恍﹀銈庡亝缁挸鐣烽崡鐑嗘建闁糕€崇箰娴滈箖鏌涢埄鍐噮缁?)
        for mem in hot_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Warm memories (recent decisions/knowledge) 闂?loaded at session start
    warm_memories = await get_warm_memories(db, user.id, days=7)
    if warm_memories:
        parts.append("\n闂傚倸鍊搁崐椋庣矆娓氣偓楠炴牠顢曚綅閸ヮ剦鏁冮柨鏇楀亾闁汇倗鍋撶换婵囩節閸屾粌顣洪梺鎼炲妼閸婂潡骞冭ぐ鎺撴優闁荤喐澹嗗▓銈夋⒑閸忓吋绶叉繛纭风節瀵濡搁妷銏☆潔濠碘槅鍨拃锔界閻愵剛绡€婵炲牆鐏濋悘鐘绘煏閸喐鍊愮€殿喖顭烽崺鍕礃閵娧呯嵁闂佺懓鍚嬮悾顏堝垂婵犳艾违濠电姴瀚壕钘壝归敐鍛儓閺嶏繝姊洪崷顓熷殌婵炲樊鍘奸锝嗙節濮橆儵鈺呮煏婢跺牆鐏い顐㈢Т閳规垿鍩ラ崱妤冧化闂佸憡顭嗛崵鍓佸厴閸┾偓妞ゆ帊鑳剁弧鈧梺姹囧灲濞佳勭閿曞倹鐓欓梺顐ｇ〒缁愭梻鈧娲樺钘夘嚕閸婄噥妾ㄩ梺?濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倻鎲搁悧鍫濈瑲闁稿﹤鐖奸弻娑㈩敃閻樻彃濮庨梺姹囧€楅崑鎾诲Φ閸曨喚鐤€闁圭偓鎯屽Λ鈥愁渻閵堝骸浜濇繛鍙夛耿楠炲牓濡搁妷搴ｅ枛瀹曞綊顢欓幆褍缂氶梻?)
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
        parts.append(f"\n濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔兼⒒鐎电濡介梺鍝勬噺缁诲牓寮婚弴鐔风窞闁糕剝蓱閻濓箓姊烘潪鎵槮闁哥喐鎸冲濠氬Χ閸氥倕婀遍埀顒婄秵閸嬪懎顭块幒妤佲拺缂佸顑欓崕鎰版煙閻熺増鍠樻鐐插暣閹稿﹥寰勯崱妯间簴闂備礁婀遍…鍫⑩偓娑掓櫊瀵娊鎮欓悜妯锋嫽婵炶揪缍侀ˉ鎾寸▔閼碱剛纾介柛灞剧⊕閻ㄦ垿鏌涢幒鎾崇瑨闁宠閰ｉ獮妯兼崉閾忓箍鍋婂┑鐘茬棄閺夊簱鍋撻幇鏉跨；闁瑰墽绮幊姘舵煥濠靛棙顥犵紒鐘荤畺閺屾盯鍩勯崘顏呭櫑婵炲瓨绮撶粻鏍蓟閿濆鏁囬柣鏇氱劍閻や礁鈹戦纭锋敾婵＄偘绮欓悰顕€骞囬鐔峰妳闂佹寧绻傞崐鎼侊綖鐏炲彞绻嗛柣鎰典簻閳ь剚鐗滈弫顕€鎮欓悜妯轰户闂佹眹鍩勯弳鈧瑃_summary.summary}")

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
            ConversationMessage(session_id="sess-1", role="user", content="闂傚倸鍊搁崐鐑芥倿閿曞倹鍎戠憸鐗堝笒閺勩儵鏌涢弴銊ョ仩闁搞劌鍊搁埞鎴﹀磼濠婂海鍔哥紓浣瑰姈椤ㄥ棙绌辨繝鍥ч柛娑卞枛濞咃綁姊洪幖鐐插闁稿﹤婀遍幑銏犫攽閸モ晝鐦堥梺绋挎湰缁矂路閳ь剟姊绘担渚劸閻庢稈鏅犲畷褰掑锤濡も偓缁犳牗淇婇妶鍛櫤闁哄懏鐓￠獮鏍垝閸忓浜鹃柟棰佺劍濞村洨绱撻崒姘偓鐑芥嚄閼稿灚鍙忛柣銏犳啞閸嬶繝鏌嶆潪鎵窗闁搞倖娲熼弻娑㈩敃閿濆棛顦ラ梺缁樻尰閻╊垶寮诲☉姘勃闁告挆鍛帒闂備線娼婚幀銉╁炊閵娿垺瀚奸梻浣藉吹閸犳劕顭垮鈧铏綇閵娿倗绠氬銈嗗姧缁茶法绮婚悙鎼闁绘劕寮堕ˉ銏⑩偓瑙勬礃閿曘垽銆佸▎鎾村殐闁冲搫锕ユ晥婵犵绱曢崑鎴﹀磹閺嶎厼绠伴柤濮愬€楅惌娆撴煙閻戞﹩娈旈柣銈夌畺閺岋綁骞囬鐓庡闂佹娊鏀辩敮锟犲蓟濞戞矮娌柟瑙勫姇椤ユ繈姊洪柅鐐茶嫰婢х増銇勯鐐靛ⅵ妞ゃ垺宀搁弫鎰板炊閵娿儳锛忓┑鐐存尰閸戝綊宕规潏鈹惧亾闂堟稓鐒告慨濠呮缁瑧鎹勯妸褌绱橀梻浣侯焾椤戝洭宕戦妶澶婃槬?),
            ConversationMessage(session_id="sess-1", role="assistant", content="濠电姷鏁告慨鐑藉极閹间礁纾婚柣妯款嚙缁犲灚銇勮箛鎾搭棞缂佽翰鍊濋弻鐔虹矙閸噮鍔夐梺鍛婄懃缁绘﹢寮诲☉銏犵婵°倐鍋撻悗姘煎墯閹梹绻濋崶銊㈡嫼闂佸憡绻傜€氼噣鍩㈡径鎰厱婵☆垳鍘х敮鑸点亜閺傝法绠伴柍瑙勫灩閳ь剨缍嗛崑鍡涘储椤忓懐绡€闁汇垽娼у瓭缂備胶绮敋妞ゎ剙锕、娆撳礈瑜忛敍?2濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村蓟閵夛妇鍘介梺褰掑亰閸撴岸骞嗛崼銉︾厽闁规崘鎻懓鍧楁煛鐏炵硶鍋撻幇浣告倯闁硅偐琛ラ埀顒€纾鎴︽⒒娴ｇ懓鈻曢柡鈧潏鈺傛殰闁跨喓濮撮拑鐔哥箾閹寸們姘跺几鎼淬劎鍙撻柛銉╊棑缁嬪寮崼鐔剁箚闁绘劦浜欑槐鏍归敐鍥剁劸妞ゅ浚鍋嗙槐?),
            ConversationMessage(session_id="sess-1", role="user", content="闂傚倸鍊搁崐鐑芥倿閿曞倹鍎戠憸鐗堝笒閺勩儵鏌涢弴銊ョ仩闁搞劌鍊搁埞鎴﹀磼濠婂海鍔哥紓浣瑰姈椤ㄥ棙绌辨繝鍥ч柛娑卞枛濞咃綁姊洪幖鐐插闁稿﹤婀遍幑銏犫攽閸モ晝鐦堥梺绋挎湰缁嬫垵鈻嶅┑瀣拺缂佸顑欓崕鎰版煙閻熺増鍠樻鐐插暣閹粓鎳為妷褍濮洪梻浣瑰閺屻劏銇愰妸顭戞▌闂佸搫鐭夌紞浣规叏閳ь剟鏌嶆潪鎷屽厡濞寸媭鍙冨娲捶椤撗呭姼濡炪値鍘鹃崗妯讳繆閹绢喖绀冩い鏃囧亹閸婄偛顪冮妶搴″⒒闁告挻鐩畷浼村箻閼告娼熼梺鍦劋閸わ箓鎮㈢拋鑳閹风娀宕ｆ径瀣絻濠电姷鏁告慨鐑藉极閸涘﹥鍙忓ù鍏兼綑閸ㄥ倿鏌ｉ幘宕囧哺闁哄鐗楃换娑㈠箣閻愬娈ら梺娲诲幗閹搁箖鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕鍫濇閸?),
            ConversationMessage(session_id="sess-1", role="assistant", content="闂傚倸鍊峰ù鍥敋瑜嶉～婵嬫晝閸岋妇绋忔繝銏ｅ煐閸旀牠宕戦妶澶嬬厸闁搞儮鏅涘皬闂佺粯甯掗敃銉ф崲濞戙垹骞㈡俊顖濐嚙绾板秹姊洪崫鍕靛剮缂佽埖宀稿濠氭偄閻撳海顔夐梺閫涘嵆濞佳冣枔椤撶姷纾?濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村矗婢跺瞼鐦堟繝鐢靛Т閸婂宕ラ崶顒佺厱闁靛鍠栨晶顕€鏌ｉ鐕佹當妞ゎ叀娉曢幑鍕传閸曞灚校闂備礁鎼鍡涙偡閳轰緡娼栭柧蹇撴贡绾惧吋鎱ㄥΔ鈧Λ娑㈠礉閸涘﹣绻嗛柣鎰▕閸ょ喐銇勯鐐靛ⅵ闁诡噣绠栭幃婊堟寠婢跺孩鎲伴梻渚€娼ч¨鈧┑鈥虫喘瀹?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_summary_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇楀亾妞ゎ亜鍟村畷褰掝敋閸涱垰濮洪梻浣侯潒閸曞灚鐣剁紓浣插亾濠㈣泛澶囬崑鎾荤嵁閸喖濮庡銈忓瘜閸ㄨ泛顕ｆ导鏉懳ㄩ柨鏂垮⒔椤旀洟姊洪悷鎵憼闁荤喆鍎甸幃姗€鍩￠崨顔惧弮闂佸憡鍔︽禍婊堝几濞戙垺鐓涢悘鐐靛亾缁€鍐磼閺冨倸鏋涙い銏＄☉椤繈顢楁径澶岀；闂傚倷妞掔槐顔剧礊閳ь剙鈹戦鍝勨偓妤呭箲閵忕姭妲堟慨姗堢到娴滅偓绻涢幋鐐垫噽闁绘帊绮欓弻锝夘敇閻戝洦鏁炬繛锝呮搐閿曨亪銆侀弴銏℃櫜闁搞儯鍔屽▍鎴︽⒒娴ｇ懓顕滄繛鎻掔箻瀹曞綊鎼归崗澶婁壕闂傚牊绋忛崑銏⑩偓娈垮枛閻栧ジ鐛€ｎ亖鏀介柛顐犲灩閺勩儵姊婚崒姘偓椋庢濮橆剦鐒界憸鎴﹀闯瑜版帗鈷戦梺顐ゅ仜閼活垱鏅剁€电硶鍋撳▓鍨珮闁稿锕ら悾鐑芥偄绾拌鲸鏅┑鐐村灦鐢鈧矮绮欏缁樻媴娓氼垳鍔搁梺鍝勭墱閸撶喖骞婂┑瀣鐟滃繐螞椤栨粍鍠愰幖娣灮閳瑰秴鈹戦悩鍙夊闁稿﹦鍏橀弻鐔虹磼濡搫娼戦梺绋款儐閹瑰洤鐣疯ぐ鎺濇晪闁告侗鍠氱粙浣虹磽閸屾艾鈧兘鎮為敃浣规噷缂傚倸鍊哥粔鏉懨洪銏犺摕婵炴垯鍨圭粻缁樹繆閵堝倸浜鹃梺鐟板槻椤戝懎宓勯梺缁樺灱婵倝鍩涢幋锔藉仯闁搞儜鍐獓闂佸湱娅㈢紞渚€寮婚悢鍏兼優妞ゆ劧绲界壕鎶芥煢濡崵绠為柡宀€鍠庨埢鎾诲垂椤旂晫浜堕梻浣告惈濡瑧鍒掗幘璇茶摕闁绘梻鍘х粻姘辨喐濠婂牆鍚归柣鏃€鎮舵禍婊堟煃閸濆嫬鈧宕ｉ埀顒勬⒑閸濆嫭婀伴柣鈺婂灦瀹曟椽宕熼姘鳖槰濡炪倕绻愰崐鐢稿磻閹捐绠抽柡鍐ｅ亾闁哥姵鍔欏娲敇閵娧呮殸闂佽楠忕粻鎾诲蓟閿涘嫪娌紒瀣仢閳峰姊洪悷鏉挎Щ闁硅櫕鍔欓獮澶愬箻椤旇偐顦板銈嗘尵閸嬫稑鈻撻妷銉㈡斀闁挎稑瀚禍濂告煕婵炑冩噽娑撳秹鏌熺€涙绠ラ柛銈嗘礋閺屾盯骞橀懠璺哄帯闂佹椿鍘介悷銉╁煘閹达附鍋愰柛娆忣槸椤︹晠姊虹粙娆惧剱闁告梹娲熸俊鎾箳閹搭厽鍍甸梺缁樻尭濞撮攱绂掗埡鍛拺閻犲洠鈧櫕鐏嗙紓浣藉煐閼归箖锝炶箛鎾佹椽顢旈崟顐ょ崺濠电姷鏁告慨鎾磹婵犳碍鍋￠柡灞诲劜閻撶喖鏌曡箛濠冩珔闁诲繐宕湁婵犲﹤鎳庢禒婊堝础?濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姴缍婇弻宥夊传閸曨偀鍋撴繝姘モ偓鍛村矗婢跺瞼顔曢梺绯曞墲钃遍悘蹇ｅ幘缁辨帡鎮╁畷鍥у绩闂佸搫鏈ú婵堢不濞戞埃鍋撻敐搴濈按闁稿鎹囧鎾偐閻㈢數鍔跺┑鐘灱閸╂牠宕濋弽顓熷亗闁告劦鍠楅悡銏′繆椤栨瑨顒熸俊鎻掔秺閺屾盯鏁愰崶銊︾彧缂備浇椴哥敮锟犲春閳?,
                "actions": ["闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈠Χ閸℃ぞ绮℃俊鐐€栭崝褏绮婚幋鐘差棜闁秆勵殕閻撴瑧绱撴担闈涚仼婵炲懏锕㈤弻鈩冩媴閸撴彃鍓辨繛锝呮搐閿曨亝淇婇崼鏇炲窛妞ゆ挾鍠愰宥夋⒒娴ｈ銇熼柛妯兼櫕閸犲﹤顓奸崶銊ュ簥濠电偞鍨堕敃鈺呭疮閸涱喓浜滈柡鍐ㄦ搐閸氬綊鏌涢幋婵堢Ш婵﹥妞介獮鎰償閿濆倸顫岀紓鍌欐祰椤曆囨偋閹炬剚鍤曞┑鐘崇閺呮悂鏌ｅΟ鍨毢妞わ负鍔戝娲濞淬倖鐩畷姗€顢旈崟顐ゎ啈濠?, "闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€归崕鎴犳喐閻楀牆绗掗柛銊ュ€搁埞鎴︽偐鐎圭姴顥濈紓浣瑰姈椤ㄥ﹪寮婚悢鍏煎亱闁割偆鍠撻崙锟犳⒑閹肩偛濡奸柛濠傜秺楠炲牓濡搁妷顔藉缓闂佺硶鍓濋〃鍛偓娑崇到閳规垿鎮欓懠顒€顤€濡炪們鍔屽Λ娆戠矚鏉堛劎绡€闁搞儴鍩栭弲顒€鈹戦悩璇у伐闁瑰啿娴风划顓㈠灳閺傘儲鏂€闂佺粯鍔樼亸娆愭櫠閿濆棛绠惧璺侯儑濞叉挳鏌嶉妷顖氼洭闁圭懓瀚版俊鎼佹晝閳ь剛澹曢鐐粹拺闁诡垎鍛唶婵犫拃宥囩М闁轰礁绉瑰畷鐔碱敇閻欏懐搴婇梻鍌欒兌閸嬨劑宕曢柆宥呯柈闁秆勵殢閺佸倹銇勯幇鍫曟闁绘挻鐟ч埀顒傛嚀鐎氫即宕戞繝鍥х？闁哄啫鐗婇悡鏇㈡煏婵炵偓娅囬柣锝堟閳ь剝顫夊ú姗€鏁冮姀銈呯疇闁绘ɑ妞块弫鍕煕椤垵鏋熼柣?],
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
        assert "濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴犵杸濡炪倖甯掗ˇ顖氣枔椤愶附鈷戦柛娑橈攻婢跺嫰鏌涚€ｎ偄娴€规洏鍎抽埀顒婄秵閸犳鎮￠弴銏＄厸闁搞儯鍎辨俊鍏碱殽閻愮摲鎴炵┍? in summary.summary


@pytest.mark.asyncio
async def test_end_session_extracts_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-2", username="sesstest2", hashed_password="x")
        db.add(user)

        msgs = [
            ConversationMessage(session_id="sess-2", role="user", content="闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛瀣ㄥ€濋弻鏇熺箾閻愵剚鐝旈梺鎼炲妼閸婂潡寮婚敐澶婎潊闁靛繆鏅濋崝鎼佹⒑閸涘﹤鐏╁┑鐐╁亾闂佸搫鑻粔闈涱焽椤忓牆绠€光偓婵犲倹鏆梻鍌欑閹碱偊顢栭崨瀛樼厐闁挎繂顦拑鐔兼煛閸ラ纾块柣銈傚亾濠电姷鏁告慨鎾磹閹间礁鐓曞鑸靛姈閳锋垿鏌熺粙鎸庢崳闁宠棄顦辩槐鎺撳緞鐎ｎ偄鍞夐梺绯曟杺閸庢彃顕ラ崟顖氱疀妞ゆ帒鍋嗛崯瀣磽閸屾瑧鍔嶇紒瀣崌楠炲﹪骞橀弶鎴殼闂佸綊鍋婇崜锕€銆掓繝姘厪闁割偅绻勭粻鎶芥煟閿濆牅鍚柍褜鍓氶鏍窗閺嶃劍娅犻幖杈剧到閸ㄦ繃绻涢崱妯哄缂佲檧鍋撻梻浣规偠閸庮垶宕濈仦鍓ь洸鐟滅増甯楅埛鎴︽煕閹剧懓鐨洪柛妯荤洴閺屾稓鈧綆浜滈顓㈡煕閳规儳浜炬俊鐐€栫敮鎺楀磹閸涘﹦顩风憸蹇曟閹烘挻缍囬柕濞垮劤閻熸煡鎮楅崹顐ｇ凡閻庢凹鍣ｉ崺鈧い鎺戯功缁夐潧霉濠婂懎浠辩€规洏鍨介獮鍥敊閸撗嶇闯濠电偠鎻徊鑲╁垝濞嗘挸浼犻柧蹇撴贡绾惧ジ鎮归崶顏勭毢濠⒀勬礃閵囧嫰寮撮鍡櫺滃Δ鐘靛仦閹瑰洭鐛幒鎴旀斀闁搞儜鍐ㄥ釜婵犵绱曢崑鎴﹀磹閺嶎厼绀夐柟杈剧畱绾捐淇婇妶鍛櫣缂佺姷鍠愰妵鍕疀閹捐泛顤€闂佹娊鏀遍崹鍓佹崲濞戙垺鍤戝Λ鐗堢箓閺佺晫绱撴担闈涘缂侇噮鍨舵俊鐢稿礋椤栨氨顓哄┑鐘绘涧濞村倸螞閿曞倹鍊垫繛鍫濈仢閺嬬喖鏌熼鐓庘偓鎼佹偩瀹勯偊娼ㄩ柍褜鍓熼妴渚€寮崼婵嗚€垮┑鐐叉閸ㄧ數鏁?),
            ConversationMessage(session_id="sess-2", role="assistant", content="濠电姷鏁告慨鐑藉极閸涘﹦绠鹃柍褜鍓氱换娑欐媴閸愬弶鎼愮痪鍓ф嚀閳规垿鎮╃€圭姴顥濋梺姹囧€楅崑鎾诲Φ閸曨垰绠涢柕濠忕畱濞呮岸姊洪崫鍕靛剱婵☆偄鍟村濠氭偄閸涘﹦绉舵俊銈忕到閸燁垶顢撳澶嬧拺闁告繂瀚刊濂告煕閹捐泛鏋涙鐐插暙椤粓鍩€椤掑嫬绠栨繛鍡樻尭缁狙囨煙鐎涙绠撶悮姗€姊婚崒娆愮グ妞ゆ泦鍛床闁规澘鍙撻崶顒佸仺缂佸娉曢悾娲煟閻斿摜鎳冮悗姘煎櫍閹柉銇愰幒鎾跺帗閻熸粍绮撳畷婊堟偄閻撳宫銉╂煕瀹€鈧崑鐐哄疾濠婂牊鐓曢柟鐐殔閹峰危閹间焦鈷掑ù锝堫潐閸嬬娀鏌涙惔顔肩仸鐎规洘绻冮幆鏃堝Ω閿濆倸浜?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇楀亾妞ゎ亜鍟村畷褰掝敋閸涱垰濮洪梻浣侯潒閸曞灚鐣剁紓浣插亾濠㈣泛澶囬崑鎾荤嵁閸喖濮庡銈忓瘜閸ㄨ泛顕ｆ导鏉懳ㄩ柨鏂垮⒔椤旀洟姊洪悷閭﹀殶闁稿鍠栭妴鍌炲蓟閵夛妇鍘遍柣搴秵閸嬫捇鎳撻崸妤佺厸閻忕偟鍋撶粈鍐磼缂佹娲寸€规洖缍婇、娆戝枈鏉堚斁鍋撻幘顔界厽闁绘柨鎽滈惌瀣攽閳╁啯鍊愮€规洘顨婇幃鈺呭垂椤愩垺鐣俊鐐€ら崢褰掑礉閹存繄鏆︽慨妞诲亾闁糕斁鍓濈换婵嬪礃閻愵剨绱樺┑鐘殿暜缁辨洟宕戦幋锕€纾归柡宥庡亝閺嗘粓鏌ｉ幇顒佹儓缂佹劖顨婇弻鐔兼焽閿曗偓閺嬨倝鏌ｉ鐔烘噧闁宠鍨块幃鈺呭矗婢跺妲遍梻浣侯焾椤戝棝宕濆▎鎾宠摕鐟滄垹绮诲☉銏℃櫜闁告侗鍓濋崺鍛節绾版ǚ鍋撻搹顐熸灆闂佹悶鍔忓▔娑綖韫囨梻绡€婵﹩鍓涢敍婊冣攽椤旀枻渚涢柛蹇旓耿瀹曟垿骞樼紒妯轰画闂備緡鍙忔俊鍥礉瀹勬壋鏀介柣鎰级椤ョ偤鏌涢弮鈧〃濠囧Υ閸涙潙钃熼柕澶涘閸樺崬鈹戦悙鏉戠仸闁挎洦鍋婂畷婵嬫偄閸忓皷鎷?,
                "actions": [],
                "memories": [
                    {"category": "preference", "content": "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞顨呴…銊╁礋椤掆偓瀵潡姊哄Ч鍥х伈婵炰匠鍥у瀭婵犻潧鐗冮崑鎾荤嵁閸喖濮庡銈忕細缁瑥顕ｉ锕€绀冩い顓烆儏缂嶅﹪骞冮埡渚囧晠妞ゆ梻鍘ф竟鍫㈢磽閸屾瑧璐伴柛瀣缁棁銇愰幒鎴ｆ憰閻庡箍鍎卞ú锕傚磻濮椻偓閺屽秹濡烽妷銉ョ婵犮垼顫夊ú婊呮閹捐纾兼繛鍡樺灥婵¤棄顪冮妶鍐ㄥ闁硅櫕锚閻ｇ兘骞囬悧鍫濅画闂備緡鍙忕粻鎴濃枔椤愶附鈷戦柛娑橈攻婢跺嫰鏌涚€ｎ偄娴€规洏鍎抽埀顒婄秵閸犳鎮￠弴銏＄厸闁搞儯鍎辨俊鍏碱殽閻愮摲鎴炵┍婵犲洤鐭楀璺猴功娴煎苯鈹戦纭锋敾婵＄偘绮欓獮濠囨晸閻樺弬褔鏌涘☉鍗炲闁硅娲樼换婵堝枈濡椿娼戦梺绋款儏閹虫﹢骞嗛崟顖ｆ晬闁绘劕鐡ㄥ▍婊堟⒑缂佹ê濮囬柟纰卞亰瀹曟﹢鍩€椤掆偓椤啴濡堕崱妯烘殫闂佸摜濮甸崝鏇㈠煝瀹ュ鍐€妞ゆ挾鍠撻崢浠嬫椤愩垺澶勬繛鍙夌墬缁傛帟顦归柡灞剧〒閳ь剨缍嗛崑鍛暦瀹€鍕厵妞ゆ梻鍋撻弳顒侇殽閻愯揪鑰跨€殿噮鍓熸俊鐑芥晜缂佹绉鹃梻鍌氬€烽懗鍫曞箠閹惧瓨娅犲ù鐘差儛閺佸棝鏌＄仦璇插姎缂佲偓婢舵劖鐓熼柡鍌涘閹插摜绱掗埦鈧崑鎾绘⒒娓氣偓閳ь剛鍋涢懟顖涙櫠鐎电硶鍋撶憴鍕８闁告梹鍨甸锝夊醇閺囩偟顓洪梺缁樺灥濡瑩藟閵堝鈷掗柛灞剧懅閸斿秹鏌熼鑲╁煟鐎规洘娲熼、姘跺焵椤掆偓椤曪綁寮婚妷銉у幐婵炴挻鑹惧ú銊╁礉?},
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
        assert "闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煟閵忋埄鐒剧痪鍓х帛缁绘盯骞嬮悜鍡欏姱濠电偞鍨惰彜婵℃彃鐗婇妵鍕敃椤愩垺鐏撶紓? in memories[0].content
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

_EXTRACT_PROMPT = """闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤掍焦顔囬梻浣告贡閸庛倝宕甸敃鈧埥澶娢熼柨瀣偓濠氭⒑閸︻厼浜炬繛鍏肩懇閸┾偓妞ゆ帒鍊归弳顒勬煛鐏炶鈧繈鐛笟鈧獮鎺楀箣濠靛柊鎴炰繆閻愵亜鈧劙寮插┑瀣婵せ鍋撶€殿喖顭峰鎾偄妞嬪海鐛梻浣稿閸嬪懐缂撴ィ鍐ㄧ；闁圭偓绶為弮鍫濆窛妞ゆ棃妫块悽濠氭⒒娴ｇ儤鍤€濠⒀呮櫕閸掓帡顢涢悙鑼紮闂佹眹鍨归幉锟犳偂閻斿吋鐓忛煫鍥э攻椤﹪鏌涢悢椋庣闁哄矉绻濋崺鈧い鎺嶇椤曢亶鎮楀☉娆樼劷闁告ü绮欏娲箰鎼淬埄姊垮┑鐐差槹濞茬喖骞嗙仦瑙ｆ瀻闁规儳顕崢鍛婄箾鏉堝墽鍒伴柟鑺ョ矊閻☆參姊绘担椋庝覆缂佹彃澧介幑銏ゅ醇濠靛牊娈惧┑顔姐仜閸嬫挻銇勯姀鈩冾棃鐎规洖宕埢搴ょ疀婵犲倷澹曢梺瑙勫劶婵倝鍩?JSON闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔告綇妤ｅ啯顎嶉梺绋款儏椤戝寮诲☉妯锋闁告鍋熸禒顖滅磽娴ｅ搫校闁哄被鍔戦垾锔炬崉閵婏箑纾梺缁樺灦钃遍柟鐑戒憾濮婃椽宕妷銉︾€婚梺鍦拡閸嬪﹤锕㈡笟鈧娲箰鎼达絿鐣靛┑鐐额嚋缁犳垿鍩㈠澶婂嵆闁绘鏁搁敍婵嬫⒑閸撴彃浜濈紒璇茬Ч閹剝绺介崨濠勫幐闁诲繒鍋涙晶钘壝虹€涙﹩娈介柣鎰▕閸庡繘鏌嶇憴鍕伌鐎规洖鐖兼俊鎼佸Ψ閵夈儺妫愰梻鍌氬€搁崐椋庣矆娓氣偓楠炲鏁撻悩鍐蹭画閻熸粍鏌ㄩ悾鐑藉箣閿曗偓缁犲鏌涢幘鑼跺厡闁绘帒娼″娲捶椤撶偛濡哄銈冨妼閹虫ê鐣峰鈧崺鈧い鎺戝閸嬧剝绻濇繝鍌氭殶閺佸牓鎮楀▓鍨珮闁稿锕ら悾閿嬬附缁嬪灝宓嗛梺缁樻煥閻ㄦ繈宕戦幘缁樺仺闁告稑锕﹂崢閬嶆⒑閹稿孩顥嗘い鏇嗗洨宓佹俊銈勯檷娴滄粓鐓崶銊︾闁哄姊荤槐鎺撴綇閵娿儳鐟插┑鐐靛帶缁绘ɑ淇婇幖浣肝ㄩ柕澶涢檮閸ゅ牓姊?
{
  "summary": "濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔虹磼閵忕姵鐏堢紒鐐劤椤兘寮婚悢鐓庣鐟滃繒鏁☉銏＄厽闁规儳鐡ㄧ粈鍐磼缂佹娲寸€规洖宕灃闁告劕鍟ㄩ崹浠嬪蓟濞戙垹妫橀悹鍥ㄥ絻婵箓姊洪崫鍕効缂傚秳绶氬顐﹀磼濠婂嫬纾梺闈浤涢崨顓炵畾婵犲痉鏉库偓妤佹叏閻戣棄纾婚柟鐗堟緲绾惧鏌熼崜褏甯涢柍閿嬪灴閺岋綁骞橀崘鑼О濠电偠鍋愰崰鏍蓟濞戞瑧绡€闁告劗鍋撻悾鍫曟⒑瀹曞洨甯涙俊顐㈠暞閹便劑鍩€椤掑嫭鐓忛柛顐ｇ箖閸ｈ棄螖閻樺弶鍠樻慨濠冩そ瀹曟﹢宕ｆ径瀣壍闂備胶顭堥敃銈夆€﹂悜鐣屽祦濠电姴娲ょ粈瀣亜閹存繂缍栫紒銊ヮ煼濮婇缚銇愰幒鎴滃枈闂佹悶鍔庢晶妤冪矉瀹ュ牄浜归柟鐑樻尵閸樻捇鎮峰鍕煉鐎规洘绮岄埥澶愬閻樺磭鈧剟姊鸿ぐ鎺擄紵闂傚嫬绉归崺鈧い鎴ｆ硶閸斿秶绱掔紒妯肩疄鐎规洖鐖兼俊鎼佸Ψ閵夈儮鎸勫┑鐘垫暩閸嬫盯顢氶鐔稿弿闁圭虎鍣弫鍕煕濞戝崬鐏犳い銉︽皑缁辨挻鎷呴懖鈩冨灴瀹曪綀绠涢弮鈧崣蹇斾繆閵堝倸浜惧┑鈽嗗亝椤ㄥ棛绮嬪澶嬪€烽柣鎴烆焽閸橀亶姊虹紒妯荤叆闁搞倖鐗曢蹇涘Ψ閳哄偆姊挎繝銏ｅ煐閸旀牠鎮￠悢鍛婂弿婵°倐鍋撴俊顐ｎ殕缁傚秴顭ㄩ崗鐘垫嚀椤劑宕ㄩ婵嗩棜缂?,
  "actions": ["闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗ù锝夋交閼板潡姊洪鈧粔鐢稿磻閿熺姵鐓欓柟顖滃椤ュ顨ラ悙顏勭伈闁哄苯绉瑰畷顐﹀礋椤愮喎浜剧憸鐗堝笒缁狙囨煙闂傚鍔嶉柍閿嬪笒闇夐柨婵嗘噺鐠愨剝绻濋埀顒佺鐎ｎ偆鍘遍梺鍝勫€藉▔鏇㈡倶闁秵鐓冪憸婊堝礈濮樿泛绀勭憸鐗堝笒閻鏌涢幇闈涙灓鐎规挷绶氶弻鈥愁吋鎼粹€崇闂佺粯鎸堕崕鐢稿箖濡ゅ懏鏅查幖绮光偓鑼泿婵＄偑鍊曠€涒晠骞愰幖浣哥厴闁硅揪闄勯崑鎰版偣閸ュ洤鍟╃槐锝夋⒒娴ｅ憡鎲搁柛锝冨劦瀹曟垶绻濋崶褏鐣哄┑鈽嗗灥閵嗏偓闁哄閰ｉ弻鐔兼倷椤掍胶绋囨繛?],
  "memories": [
    {"category": "preference|habit|decision|knowledge", "content": "闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ磵閳ь剨绠撳畷濂稿Ψ閿旇姤鐝栭梻浣瑰濞叉牠宕愰幖浣哥＜闁靛ě鍕瀾闂婎偄娲﹂幐鎾几鎼淬劍鐓忛煫鍥ь儏閳ь剚鐗犻幃鐐烘嚃閳规儳浜炬鐐茬仢閸旀碍淇婇銏㈢劯妤犵偛绻楅妵鎰板箳閹绢垱瀚奸梻渚€娼荤€靛矂宕ｆ惔銊﹀€垮Δ锝呭暞閸婂灚绻涢幋鐐茬瑲婵炲懎锕﹂埀顒冾潐濞叉ê顪冮挊澶屾殾闁圭儤顨嗛崐鐑芥煛婢跺鐏ｉ柛鏍ㄧ墪閳规垿鎮欑€涙ê闉嶉梺绯曟櫅閸熸潙鐣烽幋锕€绠绘繛锝庡厸缁ㄥ姊洪幐搴ｇ畵缂佺粯鍔欓妴鍛搭敆閸屾粎锛滈柡澶婄墐閺呮稒绂掓潏鈹惧亾鐟欏嫭绀€闁绘牕銈搁妴浣肝旀担鐟邦€撶紓浣割儏閻忔繈藟婢舵劖鈷掗柛灞剧懅椤︼箓鏌熷ù瀣у亾鐡掍焦妞介弫鍌炴偩瀹€濠冮敜婵犵數鍋涘Λ娆撳垂鐠鸿櫣鏆﹂柡灞诲劜閻撴洟鏌嶉埡浣告殶闁愁垱娲熼弻?}
  ]
}

闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾缁愭鏌熼幍顔碱暭闁稿绻濋弻鏇熺珶椤栨浜鹃梺绋款儐閹告悂锝炲┑瀣亗閹肩补妾ч幏顐︽煟鎼淬値娼愭繛鍙夌墱缁辩偞绻濋崶銉㈠亾娴ｇ硶妲堥柕蹇娾偓鏂ュ亾閻戣姤鍊垫繛鎴烆伆閹达附鍋?- summary 闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾缁愭鏌熼柇锕€鍔掓繛宸簻缁狅綁鏌ㄩ弮鍥棄婵炲牊鍨垮娲礈閹绘帊绨煎┑鐐插级閿曘垹鐣烽幋锕€鐓涢柛灞剧矌閻﹀牓姊婚崒姘卞缂佸甯￠幃姗€鍩￠崨顔惧幗闂佺懓顕崕鎰版倿娴犲鐓熼柣鏃傚劋閸も偓闂佸疇顫夐崹鍧楀箖閳哄懎绠甸柟鐑樼箑缁辨垶淇婇悙顏勨偓褏鈧潧鐭傚畷鏉课旈崘鈺佸簥濠电偞鍨崹鍦不閿濆鐓熼柟閭﹀幗缂嶆垿鏌ｉ妸锕€鐏存慨濠呮缁瑥鈻庨幆褍澹夐梻浣烘嚀閹诧繝骞冮崒鐐叉槬闁靛绠戠欢鐐烘煙闁箑澧版い鏃€甯″娲川婵犲孩鐣奸梺绋款儐閸旀瑥鐣烽幋锕€绠婚悹鍥ㄥ絻瀹撳棝鏌熸ウ鎸庣彧缂佸倸绉烽妵鎰板箳閹捐泛骞楅梻浣哥秺閸嬪﹪宕滃☉娆戭浄婵炴垯鍨洪崐?- memories 闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫鎾绘偐閸愯弓鐢绘俊鐐€栭悧妤冪矙閹炬眹鈧懘宕ｆ径宀€鐦堥梻鍌氱墛娓氭鎮為幆顬＄懓顭ㄩ崨顔兼畬闂侀潧妫欑敮鎺楋綖濠靛鏅查柛娑卞墮椤ユ岸姊虹拠鍙夊攭妞ゎ偄顦叅闁冲搫鍟扮粈濠偯归敐鍛棌闁搞倖娲栭湁闁绘ê妯婇崕娑㈡煛娴ｇ鏆ｉ柡灞诲妼閳规垿宕卞鍡橈紒婵＄偑鍊栭幐鍝ョ礊婵犲偆娼栫紓浣股戞刊瀵哥磼濞戞﹩鍎愮紓宥呯墦濮婃椽鎮烽悧鍫濇殘婵犵數鍋涢敃銈夘敋閿濆惟闁宠桨鑳堕、鍛存⒑缂佹ê濮囩紒瀣缁辩偞绗熼埀顒勬偘椤旈敮鍋撻敐搴℃灍闁稿鍔欓弻娑㈠箛椤撶偟绁峰Δ鐘靛仦閸ㄨ埖绌辨繝鍥ㄥ€锋い蹇撳閸嬫捇寮介‖顒佺⊕缁楃喖鍩€椤掑嫬鏋侀柟鎹愵嚙鍞梺瀹犳〃閼冲爼宕濋敃鈧—鍐Χ閸℃娼戦梺绋款儐閹瑰洭寮诲☉銏″亞濞达絽鎽滄禒鈺侇渻閵堝骸骞栨繛娴嬫櫇缁鈽夊Ο閿嬵潔濠碘槅鍨抽埛鍫澪ｉ崼鏇熺厽闁绘柨鎽滈惌濠囨⒑鐢喚绉鐐插暞閵堬綁宕橀埡鍐ㄥЦ闁诲骸绠嶉崕鍗炍涘☉銏犲偍闂侇剙绉甸悡鐔煎箹閹碱厼鐏ｇ紒澶愭涧闇夋繝濠傛噹娴犙呯磼椤斿墽甯涢悗浣冨亹閳ь剚绋掗…鍥储椤忓牊鈷戦柛鎾村絻娴滄繄绱掗濂稿弰闁诡垰鑻埢搴ょ疀婵犲啯鏉搁梻浣哄仺閸庤京澹曢銏犵闁绘绮悡娆戔偓鐟板婢ф宕抽悜妯镐簻闁挎梹鍎抽。濂告煙椤栨稒顥堥柡浣瑰姍瀹曢亶鍩￠崒婊呪槈闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅梺鍝勭▉閸樺ジ宕归崒姘ｆ斀闁稿本绮犻悞楣冩煕閵娿儱鈧灝顫忓ú顏嶆晢闁逞屽墰缁棃骞橀鐓庣€梺绋跨灱閸嬬偤鎮¤箛鎾斀闁绘劙娼ф禍鐐箾閸涱厽顥㈤柡宀嬬秮楠炴﹢宕樺ù瀣壕濠电姵鑹鹃悞鍨亜閹哄棗浜剧紓浣哄Т缁夌懓鐣烽弴銏＄劶鐎广儱妫楁禍鍗炩攽閻樿宸ラ柛妯诲劤鐓ゆい蹇撴噺濞呮粍绻濋姀锝嗙【妞ゆ垵娲畷銏ゆ焼瀹ュ棌鎷洪悷婊呭鐢帗绂嶆导瀛樼厱闁规儳顕ú鎾煛娴ｅ摜孝妞ゆ挸鍚嬪鍕偓锝庡墮楠?- 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻娑樷攽閸曨偄濮㈤梺娲诲幗閹瑰洭寮婚敐澶婄婵犲灚鍔栫紞妤呮⒑闁偛鑻晶顕€鏌熼搹顐€跨€殿噮鍋婂畷姗€顢欓懖鈺嬬床婵犳鍠楅敃銏㈡兜閹间礁鑸规繛宸簼閳锋帒銆掑锝呬壕濠电偘鍖犻崶锝傚亾閿曞偆鏁囬柕蹇婃閹稿啴姊洪崨濠冨闁搞劑浜跺畷鎰板垂椤旀艾缍婇幃鈺侇啅椤旂厧澹夐梻浣虹帛閹稿爼宕曢懠顒佸床婵炴垯鍨圭粻锝夋煟閹存繃顥犻柛鏃堟敱缁绘繈鍩涢埀顒佹媴閸濄儰绱欓梻浣告惈婢跺洭宕滃┑瀣闁告稑鐡ㄩˉ鍫熺箾閹寸偛绗掑ù婊呭亾缁绘繈妫冨☉鍗炲壋閻庤鎸风欢姘跺箖濡ゅ懏鏅查幖绮瑰墲閻忓秹姊虹粙娆惧剾濞存粍绻堟俊鐢稿礋椤栨艾鍞ㄩ梺姹囧灲濞佳囧春鐏炶В鏀?闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛瀣ㄥ€濋弻鏇熺箾閻愵剚鐝旈梺鎼炲妼閸婂潡寮诲☉銏╂晝闁挎繂妫涢ˇ銉モ攽椤旀娼愰柣鎿勭節瀵鏁愭径濠勭潉闂佹悶鍎崕顕€宕戦幘璇茬劦妞ゆ帒瀚悡鏇㈡倵閿濆骸浜濋悘蹇ｅ弮閺屽秹鎸婃径妯恍﹂梺浼欑悼閸忔ê鐣烽崼鏇炵厸闁告劦浜滈悙濠勭磽閸屾艾鈧悂宕愰悜鑺ュ€块柨鏇炲€堕埀顒€鍟村畷銊ヮ潰閵堝懏鍠樻鐐茬Ч椤㈡瑩宕滆椤?闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€哥粈鍫熸叏濡寧纭剧痪鎯ь煼閺屾稑鈽夐崡鐐典画闂佸搫妫欑划鎾诲蓟閿濆绫嶉柛灞绢殕鐎氭盯姊烘潪鎵槮闁挎洦浜璇测槈閵忕姈銊︺亜閺冨洤鍚归柡鍡橆殕缁绘稓鈧稒顭囬惌濠勭磽瀹ュ拑韬€殿喖顭烽弫鎾绘偐閼碱剙鈧偤姊洪崫鍕ⅱ闁轰焦鎮傚顐﹀冀椤剚妫冮幃鈺呮濞戞婢€闂備焦鎮堕崝瀣垝濞嗗浚鍤曞┑鐘崇閺呮彃顭块懜鐢点€掔紒瀣箰椤啴濡堕崱妤€娼戦梺绋款儐閹告悂鍩為幋锕€鐏抽柤纰卞墰閻撴捇姊洪崫鍕拱闁烩晩鍨跺畷娲晸閻樿尙锛滃┑鐘诧工鐎氼剟宕归柆宥嗏拻濞达絼璀﹂弨鐗堢箾閸涱喗绀嬫鐐村灴瀹曟儼顦撮柡鍡檮娣囧﹪顢涘☉鍗炲妼濠碘剝鐓＄粻鏍ь潖?0闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤掍焦顔囬梻浣告贡閸庛倝宕甸敃鈧埥澶娢熼崗鍏肩暦闂備礁鎲″ú锕傚磻閸℃稑钃熼柛顐犲劜閻撶喖骞栭幖顓炵仯缂佸鏁婚弻娑氣偓锝庝簼椤ャ垽鏌涢埞鍨伈鐎殿噮鍣ｅ畷鎺懳旈埀顒佺閻愵剦娈介柣鎰皺娴犮垽鏌涢弮鈧喊宥嗙┍婵犲浂鏁冮柨婵嗗閻や線姊虹涵鍛彧闁荤喆鍔戞俊鐢稿箛閺夎法顔婇梺瑙勫礃濞夋盯鐛幇鐗堚拻濞达絼璀﹂悞楣冩偠濮樼厧浜扮€规洘鍔欏鎾倻閸℃顓块梺鑽ゅУ娴滀粙宕濇惔锝咁棜?- 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔兼⒒鐎电濡介梺绋款儍閸婃繈寮婚弴鐔虹闁割煈鍠栨慨璺衡攽閻愬瓨灏い顓犲厴瀵鈽夊Ο鍏兼畷闂侀€炲苯澧寸€规洘鍨甸埥澶婎潩閸欐鐟濋梻浣烘嚀椤曨厽鎱ㄩ悽绋跨獥闁规壆澧楅崐鍫曟煟閹邦厼绲婚柍閿嬫閺屽秹鎮烽幍顔с垽鏌嶇憴鍕伌闁诡喒鏅犲畷锝嗗緞鐎ｎ偄鈧绱撻崒娆掑厡濠殿喚鏁搁弫顔嘉旈崨顓囷箓鏌涢弴銊ョ仩闁告劏鍋撻梻渚€娼ц噹闁告洦鍋呴悵顕€姊婚崒娆愮グ鐎规洜鏁诲畷浼村箛椤旇棄搴婇梺鍓插亖閸庤京绮婚弽顓熷仭婵炲棗绻愰顏勨攽椤栨凹鍤熺紒杈ㄥ笧閳ь剨缍嗛崢鐣屾兜閸洘鐓熼柍杞扮劍閹癸絿绱?濠电姷鏁告慨鐑藉极閹间礁纾绘繛鎴欏焺閺佸銇勯幘璺烘瀾闁告瑥绻橀弻鐔虹磼閵忕姵鐏嶉梺鍝勬噺缁诲牓寮婚弴銏犻唶婵犲灚鍔栫瑧濠碘剝顨呴幊蹇曟崲濠靛顫呴柨婵嗘閵嗘劕顪冮妶鍡楃仴婵炲樊鍙冨畷娲閵堝懐鐫勯梺绋挎湰椤ㄥ懏绂嶉悙顒夋闁绘劘灏欐禒銏ゆ煕閺冣偓绾板秵绌辨繝鍥舵晝闁挎繂瀛╅悿渚€鎮楃憴鍕８闁搞劋绮欓悰顕€骞掗幊铏⒐閹峰懐鍖栭弴鐐板闂佸壊鐓堥崑鍡欑不妤ｅ啯鐓欓悗娑欘焽缁犳﹢鏌ㄥ☉妯夹ょ紒杈ㄥ笚濞煎繘濡搁妷顔筋棆缂?闂?- 濠电姷鏁告慨鐑藉极閸涘﹥鍙忛柣鎴濐潟閳ь剙鍊圭粋鎺斺偓锝庝簽閸旓箑顪冮妶鍡楀潑闁稿鎹囬弻娑㈡偄闁垮浠撮梺绯曟杹閸嬫挸顪冮妶鍡楀潑闁稿鎸剧槐鎾愁吋閸滃啳鍚Δ鐘靛仜閸燁偉鐏掗柣鐘叉穿鐏忔瑧绮ｉ悙瀵哥瘈闁汇垽娼ф禒褔鏌涚€ｎ偅宕岄柟顕嗙節婵偓闁靛牆妫岄幏娲⒑閸濆嫬鈧爼宕曢幓鎺嗘瀺闁告稑鐡ㄩ悡鏇㈡煟閺囨氨顦﹂柣蹇ョ悼缁辨帡顢欑喊杈╁悑濡ょ姷鍋炵敮鎺曠亙婵炶揪绲介幖顐︾嵁閸績鏀介柣妯虹仛閺嗏晛鈹戦纰卞殶闁逞屽墯閸戝綊宕滃☉銏犳瀬妞ゆ洍鍋撶€规洘绮嶉幏鍛存惞閻у摜搴婇梻鍌欐祰椤曟牠宕归崼鏇樷偓鍌炴晝閸屾俺袝濡炪倖鍔ч梽鍕偂濞嗘垟鍋撻悷鏉款伃闁稿锕畷鏇㈠箛閻楀牏鍙嗗┑鐐村灦閻熴儲鎱ㄩ崼銉︾厵鐎瑰嫮澧楅崵鍥煙閻撳海绉虹€规洘绮撻獮鍥煛娴ｆ彃浜炬繝闈涙－濞兼牠鏌涘┑鍡楃彅鐟滄柨鐣烽幆閭︽Щ濡炪値鍓欓悧鎾诲蓟閿濆棙鍎熼柕蹇曞Т濮ｅ牊绻涚€涙鐭嬬紒璇插閸掓帒顫濋鐔虹Ф闂侀潧臎閸涱垱顫岄梻鍌欑劍閹爼宕曞鍫濆窛妞ゆ牗绋掗鎴炵節绾板纾块柛瀣灴瀹曟劙寮介鐔蜂罕闂佽宕橀褏澹曠憴鍕箚闁靛牆鎳庨弳鐔兼煟椤撶偞顥滈柍瑙勫灦瀵板嫮浠︾拋宕囩梾mories 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姵褰冮湁闁挎繂娲ㄩ妴濠囨煛鐎ｎ亞效闁哄被鍔岄埞鎴﹀幢閳哄倐锕傛⒑缂佹ɑ灏伴柨鏇樺灲瀵鍨鹃幇浣告倯闁硅偐琛ラ埀顒€纾鎰版⒒娴ｅ憡鎯堟い鎴濆濞嗐垹顫濈捄楦挎憰闂佺粯鏌ㄩ惃婵嬪几閺冨牊鐓曟い顓熷灥閺嬬喖鏌ｈ箛鏃€宕屾慨?""


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
                            user_answer = user_response.get("answer", "缂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礃閹偤骞栧ǎ顒€濡奸柣顓燁殜楠炴牕菐椤掆偓婵¤偐绱掗幇顓ф畷缂佺粯鐩獮瀣枎韫囨洖濮堕梻?)
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

Add the following under the `### 闂傚倸鍊峰ù鍥敋瑜嶉～婵嬫晝閸岋妇绋忔繝銏ｅ煐閸旀洜绮婚弽顓熺厱妞ゆ劧绲剧粈鈧紒鐐劤濞尖€愁潖濞差亶鏁嗛柍褜鍓涚划鏃堝箻椤旇棄鍓瑰┑掳鍊曢幊蹇涙偂濞嗘垹纾奸悗锝庝簽娴犮垺銇勯幒瀣仼闁宠鍨块、娑樷槈濞嗗繐鏀梻浣筋嚃閸犳牜绱炴繝鍥╁祦濞撴埃鍋撴鐐村浮楠炲鈹戦幇顔瑰亾閹绢喗鈷掑ù锝呮啞閹牊淇婇锝庢疁鐎?section in `Agent.md`:

```markdown
- recall_memory闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔兼倻濮楀棙鐣烽梺鎼炲€曢惌鍌炲蓟濞戙垹绠绘俊銈傚亾闁硅櫕鍔欒棟妞ゆ牜鍋為悡鐔煎箹閹碱厼鐏ｇ紒澶屾暬閺屾盯鎮╅幇浣圭杹闁芥鍠栭弻娑㈠焺閸愵亖濮囬梺缁樻尭閸熶即骞夌粙娆剧叆闁割偅绻勯ˇ顓炩攽閻愭潙鐏熼柛銊ユ贡缁鎮㈤崗鑲╁幗濠德板€愰崑鎾绘煟濡も偓閿曘儵宕氭繝鍥х妞ゆ梻鏅崢鍗炩攽閻愭潙鐏﹂柨鏇ㄥ亰瀹曟繈鎮㈤幖鐐扮盎闂佹寧鏌ㄩ幖顐﹀礉閿旀垝绻嗘い鎰╁灪閸ゅ洦銇勯姀鈩冪濠殿喒鍋撻梺鏂ユ櫅閸燁垶宕愰柨瀣瘈缁剧増蓱椤﹪鏌涚€ｎ亝鍤囬柟顖氬椤㈡稑顫濋悡搴㈩吙婵＄偑鍊栭崝褏绮婚幋婵囩函婵犵數濮伴崹鐓庘枖濞戙垺鏅濋柨鏇炲亞閺佸洦绻涘顔荤凹闁抽攱鍨块弻锝夊箛闂堟稑鈷夋繝銏ｎ潐閿曘垽寮诲☉娆戠瘈闁稿被鍊楅崥瀣渻閵堝啫鐏柨姘舵偂閵堝棎浜滈煫鍥ㄦ尰閸ｄ粙鏌涘鈧禍璺侯潖閾忚鍠嗛柛鏇ㄥ亜婵垻绱掗崜褑妾搁柛娆屽亾闂佺锕ら悺銊ф崲濠靛鍋ㄩ梻鍫熺◥缁爼姊虹紒姗嗘當闁挎洦浜滈悾鐤亹閹烘垵鐎銈嗘⒒閸嬫挸鈻撴ィ鍐┾拺缁绢厼鎳忚ぐ褏绱掗幓鎺撳仴闁诡喖娼￠崺鈧い鎺戝閳锋垿鎮峰▎蹇擃仼闁告柣鍊楅埀顒冾潐濞诧箓宕滃杈╃焿闁圭儤鍤氬ú顏嶆晜闁告侗浜濈€氬ジ姊婚崒姘偓鎼佹偋婵犲嫮鐭欓柟鐑橆檪婢跺ň鏋庨柟閭︿簽缁犳岸姊虹紒妯哄婵炲吋鐟х划顓☆槾闁逞屽墯椤旀牠宕锕€鐐婄憸蹇浰囬弶娆炬富闁靛牆妫涙晶顒佹叏濡濮傞柟顕€绠栭獮鍡氼檨婵炴挸顭烽弻鏇㈠醇濠靛浂妫ゆ繝鈷€灞藉缂佽鲸甯為埀顒婄秵閸嬪嫰鎮橀幘顔界厵妞ゆ梻鐓鍥╀簷闂備礁鎲℃笟妤呭窗濮樿泛鍌ㄩ梺顒€绉甸埛鎴犳喐閻楀牆绗掑ù婊€鍗抽弻娑㈠箻鐎靛憡鍒涢梺杞扮缁夋挳顢橀崗鐓庣窞閻庯綆鍓欓獮妤呮⒑閸︻厼鍔嬪┑鐐诧工閻ｇ兘寮撮姀鈽嗘濠电偞鍨靛畷顒€鈻撻妸銉富闁靛牆妫欑壕鐢告煕鐎ｎ偅灏甸柍褜鍓氶鏍窗濮樿泛鏋侀悹鍥у棘濞戙垹绀冮柕濞垮灪椤秹姊洪崷顓炲妺闁规悂绠栭崺鈧い鎺嗗亾闁靛牏顭堥～蹇曠磼濡顎撻柣鐔哥懃鐎氥劍绂掕閳规垿鎮欓棃娑樹粯濠电偛鐨烽埀顒€纾弳锔界節闂堟稒宸濈紒鈾€鍋撻梻浣规偠閸庢粓宕ㄩ鐐愭洖鈹戦敍鍕杭闁稿﹥鐗曢蹇旂節濮橆剛锛涢梺鐟板⒔缁垶鎮￠弴鐐╂斀闁绘ê寮剁粊鈺備繆椤愶絽鐏╃紒杈ㄥ浮椤㈡岸宕ㄩ鐐殿啈闁诲骸鐏氬妯尖偓姘煎枟缁傛帡鏁冮崒姘辩暰閻熸粌楠歌闁搞儜鈧弨浠嬫煟閹邦垰鐓愮憸鎶婂懐纾奸柤鑹板煐椤ュ鏌ㄩ弴妯虹伈鐎规洩绻濋幃娆忣吋韫囨洜袦婵犵鍓濋幃鍌炲极閸岀偛绀堢憸婊堝疮鎼淬劍鈷掑ù锝堟閵嗗﹪鏌嶈閸撴瑧澹曢鐘典笉婵鍩栭悡鏇㈡倵閿濆骸浜濈€规洖鏈〃銉╂倷閸欏顦╅梺鐟板槻閹虫ê鐣烽妸锔剧瘈閹肩补鍓濆▍濠囨⒒閸屾艾鈧嘲霉閸パ呮殾闁割煈鍋呴崣蹇涙煛婢跺娈繛宸簼閺呮粓鏌ｉ幇闈涘閹兼潙锕娲礈閹绘帊绨撮梺绋挎唉娴滎剛鍒掗崼銉ョ＜婵炴垶顨堢粻姘渻閵堝棛澧柤褰掔畺楠炲啴骞嬮敂钘夆偓鍨叏濡厧甯跺褎鎸抽弻锛勪沪閸撗勫垱濡ょ姷鍋涘ú顓炵暦濡ゅ懎浼犻柕澶堝劚濮ｅ牓姊婚崒娆戭槮闁圭⒈鍋勮灋婵°倕鍟畷鍙夋叏濡炶浜鹃悗娈垮枛椤攱淇婇幖浣肝ㄩ柕蹇婃濞兼梹绻濈喊妯活潑闁搞劋鍗抽幃妯衡攽鐎ｅ灚鏅滃銈嗘尪閸ㄦ椽宕戦埄鍐瘈濠电姴鍊搁鈺呭箚閻斿吋鈷戦柟鑲╁仜閸斺偓闂佸憡娲﹂崑鍡涘Χ閸洘鈷掗柛灞剧懅缁愭梹绻涙担鍐叉濞咃綁姊绘笟鈧埀顒傚仜閼活垱鏅堕幘顔界厱闁宠鍎虫禍鐐繆閻愵亜鈧牜鏁繝鍕偨闁跨喓濮甸崐鍨归悩宸剱闁绘挸鍟伴幉绋款煥閸繄顦┑鐐叉妤犲繘鎳撻崸妤佲拺妞ゆ巻鍋撶紒澶婎嚟婢规洘绻濆顓犲帾闂佸壊鍋呯换鍐闯閻戣姤鐓冪憸婊堝礈濮樿鲸鏆滈柍銉ョ－閺嗭附绻濇繝鍌氼仾濠殿垱鎸抽弻锝夋偄閸濆嫷鏆┑顕嗙到濞层倝鍩為幋锔藉€烽柤鎼佹涧濞懷呯磽娴ｇ懓绲绘繛纭风節閸ㄩ箖鏁冮崒姘跺敹闂侀潧顦崕鐢稿极濠婂嫮绡€闁汇垽娼у瓭濠电偠顕滅粻鎾诲箖閿熺姴鍗抽柣鏃囨椤旀洟姊虹化鏇炲⒉闁挎氨绱掑Δ浣哥缂佽鲸甯￠獮澶屸偓锝庡墰閺嗙娀鏌ら幐搴″闁哄本鐩俊鐑藉箣濠靛熆銉╂煕濮樼厧浜滈摶鏍煟濮椻偓濞佳勭閹烘梻纾奸柤鎼佹涧閸濇椽鏌曢崱鏇狀槮闁宠棄顦灒闂佸灝顑愬鏃€绻濋悽闈涗粶婵☆偅鐟ㄩ幗顐︽偠濮樷偓閸曨厾鐦堥梺姹囧灲濞佳勭閳哄懏鐓欐繛鑼额唺缁ㄧ晫绱掓潏鈺佷槐闁糕斁鍋撳銈嗗笂閼冲墎绮婚幆褜鐔嗛悹杞拌閸庢劗绱掗埀顒傗偓锝庡厴閸?- save_memory闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔兼倻濮楀棙鐣烽梺鎼炲€曢惌鍌炲蓟閻旂儤鍠嗛柛鏇ㄥ亜椤洦绻涚€涙鐭婃繝鈧柆宥呯疅闁告稑锕ラ崕鐔兼煥濠靛棙宸濋柣鎾存濮婃椽宕ㄦ繝搴㈢暭闂佺顑嗛崝娆忣嚕閵婏妇顩烽悗锝庡亞閸橀亶姊洪弬銉︽珔闁哥喍鍗抽獮濠囧礋椤栨稓鍘甸梺鍦帛鐢洭宕戦姀鈩冨弿濠电姴鍊归幆鍫ユ偂閵堝洨纾藉ù锝咁潠椤忓牆鐓濋煫鍥ㄧ⊕閳锋垿鏌涘☉姗堟敾闁绘挶鍎崇槐鎺撳緞鐏炴儳娈岄梺浼欑悼閸忔ê鐣烽锕€绀嬮柕濠忓瘜濞兼棃姊绘笟鈧褏鎹㈤幒鎾村弿闁哄鍩堥崵鏇㈡煟閹达絽袚闁绘挻鐟╅弻銈夊捶椤撶儐鏆悷婊勫Ω閸涱垳锛滈梺鍛婄懃椤︿即濡靛┑瀣厱闁宠鍎虫禍鐐繆閻愵亜鈧牜鏁繝鍕偨闁跨喓濮甸崐鍨归悩宸剱闁绘挻鐟﹂妵鍕籍閸ヨ泛娈悗瑙勬尭濡鍩為幋锕€鐒洪柛鎰ㄦ櫅閳ь剚鍔曢埞鎴﹀焺閸愨晛鈧劙鏌℃担绋挎殻闁糕斁鍋撳銈嗗坊閸嬫捇鏌嶉挊澶樻Ъ妞わ箒顫夐幈銊︾節閸屾稒鍎撻柡浣哥墦閺屾盯濡烽幋婵嗘灓闁诲孩濞婂铏规嫚閹绘帩鍔夐梺鍛婂灱椤绮嬪鍛斀闁割偁鍨婚悡鏃堟煛婢跺﹦澧戦柛鏂挎捣瀵囧焵椤掑嫭鈷戦柟鑲╁仜閸斺偓闂佸憡渚楅崹鍗炩枔閸濆嫧鏀介柨娑樺娴滃ジ鏌涙繝鍐⒌闁诡啫鍥х閻犲洩灏欓敍娆忊攽鎺抽崐鏇㈠疮娴煎瓨鍎楅柛鈩冾殢閻斿棝鎮归崫鍕▏闁割偅鎯婇敐澶婇唶闁靛濡囬崢鐢告⒑鐠団€崇€婚柛婊冨暟缁€濠囨⒑閸濄儱鏋旀い顓炵墦閳ユ棃宕橀鍢壯囨煕鐏炲墽鈯曢柣婵勫妿缁辨挻鎷呴崫鍕戯綁鏌熼悷鐗堝枠闁诡喕鍗抽、姘跺焵椤掑嫮宓侀柟鐑樺殾閺冨牆鐒垫い鎺嶇閸旀棃姊婚崒娆戝妽閻庣瑳鍐炬綎濠电姵鑹鹃悿鐐亜閹板墎鐣辩紒鈧径鎰厽闁硅揪绲借闂佹娊鏀遍崹鍨潖婵犳艾閱囬柣鏃囥€€婵洤顪冮妶鍐ㄥ姕缂侇喗鎹囧璇测槈濞嗘垹鐦堥梺鎼炲劥閸╂牠藟閺嶎厽鈷戦柣鐔稿閻ｎ參鏌涢妸銉хШ闁挎繄鍋涢埞鎴犫偓锝庝簽椤撳吋绻涙潏鍓хМ闁哄懎寮剁粩鐔煎即閻愨晜鏂€闂佺粯鍔栧娆撴倶閿斿浜滈煫鍥风导闁垱銇勯姀鈩冾棃鐎规洏鍔戦、娆撴偩鐏炶棄鈻忛梻鍌氬€烽懗鍓佸垝椤栫偐鈧箓宕煎┑鍐╃€洪梺鎸庣箓椤︿即宕戦鍫熺厓鐟滄粓宕滈悢濂夋綎婵炲樊浜滃婵嗏攽閻樻彃顏ゅ┑顔兼喘濮婄儤瀵煎▎鎴犘ｆ繛瀛樼矤娴滎亜鐣峰ú顏勭劦妞ゆ帊闄嶆禍婊堟煙閸濆嫭顥滃ù婊冨⒔缁辨挻鎷呴搹鐟扮闂佹寧宀搁弻锝夋晲閸涱厽些闁剧粯鐗犻弻娑樷槈閸楃偛绫嶉梺鍝ュ仜閻栫厧顫忓ú顏咁棃婵炴垶姘ㄩ悾楣冩⒑閸涘﹥灏扮紒璇插€块崺?ask_user 缂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礃閹偤骞栧ǎ顒€濡奸柣顓燁殜楠炴牕菐椤掆偓婵¤偐绱掗幇顓ф畷缂佺粯鐩獮瀣枎韫囨洖濮堕梻浣芥〃缁€浣该洪妶澶婄厴闁硅揪闄勯崑鎰偓瑙勬礀濞村倿寮抽敓鐘斥拺?闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛瀣ㄥ€濋弻鏇熺箾閻愵剚鐝旈梺鎼炲妼閸婃悂鍩為幋锕€纾兼慨姗嗗墻濡矂姊烘潪鎵槮闁挎洦浜璇测槈閵忕姈銊╂煥濠靛棙鍣规い顒€顦扮换婵嗏枔閸喚浠梺鐟版啞婵炲﹪骞冮敓鐙€鏁冮柨鏇楀亾闁绘劕锕﹂幉鍛婃償閵娿儳顔夐梺鎸庣箓椤︿即鎮￠弴銏＄厽闁哄倸鐏濆▓鈺呮椤掑澧撮柡宀嬬磿娴狅妇鎷犻幓鎺濈€抽梻浣哥枃濡嫰藝椤栫偛鐓濋幖娣妼缁狅綁鏌ｉ幇顓熺稇闁哄棭鍋婂濠氬磼濮橆兘鍋撴搴ｇ焼濞撴埃鍋撴鐐差樀閺佹捇鎮╅懠顒夋Х闂備礁鎼ú銏ゅ垂閸︻厾涓嶉柣妯款嚙缁犲綊鏌熺喊鍗炲箻闁告ɑ鐩弻鈩冩媴闂堚晞鍚梺鍝勭灱閸犳牠銆佸Δ鍛妞ゆ挾濮靛В鍥⒒娴ｅ憡鎯堥柡鍫墮鐓ら柣鏃堫棑閺嗭箓鏌涘Δ鍐ㄢ偓锝夊籍閸繄鍔﹀銈嗗笒鐎氼剟鎮為崹顐犱簻闁瑰搫绉堕崝宥夋煕婵犲啫濮堥柕鍥у婵偓闁炽儱鍟块幗闈涱渻閵堝啫鐏€光偓閹间礁鏄ラ柍褜鍓氶妵鍕箳閸℃ぞ澹曢梻浣风串缁插潡宕楀Ο璁崇箚闁绘垼妫勫敮闁瑰吋鐣崹娲煕閹烘鐓冪憸婊堝礈閵娧呯闁糕剝绋戠粈鍫熺箾閸℃ɑ灏紒?
  - preference闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔兼倻濡櫣鍔稿┑鐐茬毞閺呯娀寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閸濆嫷鍎庣紒鑸靛哺瀵寮撮姀鐘诲敹濠电姴鐏氶崝鏍懅缂傚倸鍊烽懗鑸靛垔鐎电绶ら柛褎顨呴悞鍨亜閹烘垵鈧綊宕甸埀顒勬煟鎼淬垻鐓柛妤佸▕婵℃挳宕掗悙瀛樻珖闂佺鏈粙鎴﹀焵椤掆偓閻忔繈鍩為幋锔藉亹闁圭粯宸婚崑鎾绘偨缁嬭法鍝楁繛瀵稿Т椤戝棝鎮￠弴銏″€堕柣鎰絻閳锋棃鏌嶉娑欑闁哄矉缍€缁犳盯鏁愰崨顔句壕缂?闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛瀣ㄥ€濋弻鏇熺箾閻愵剚鐝旈梺鎼炲妼閸婂潡寮婚敐澶婎潊闁靛繆鏅濋崝鎼佹⒑閸涘﹤鐏╁┑鐐╁亾闂佸搫鑻粔闈涱焽椤忓牆绠€光偓婵犲倹鏆梻鍌欑閹碱偊顢栭崨瀛樼厐闁挎繂顦拑鐔兼煛閸ラ纾块柣銈傚亾濠电姷鏁告慨鎾磹閹间礁鐓曞鑸靛姈閳锋垿鏌熺粙鎸庢崳闁宠棄顦辩槐鎺撳緞鐎ｎ偄鍞夐梺绯曟杺閸庢彃顕ラ崟顖氱疀妞ゆ帒鍋嗛崯瀣磽閸屾瑧鍔嶇紒瀣崌楠炲﹪骞橀弶鎴殼闂佸綊鍋婇崜锕€銆掓繝姘厪闁割偅绻勭粻鎶芥煟閿濆牅鍚柍褜鍓氶鏍窗閺嶃劍娅犻幖杈剧到閸ㄦ繃绻涢崱妯哄缂佲檧鍋撻梻浣规偠閸庮垶宕濈仦鍓ь洸鐟滅増甯楅埛鎴︽煙椤栧棗瀚々浼存⒑缁嬫鍎忛柟铏耿閵嗕礁鈻庤箛锝呮倯婵犮垼娉涢鍥储?闂?  - habit闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔兼倻濮楀棙鐣烽梺鎼炲€曢懟顖濈亙闂佹寧绻傞幊搴ㄥ几閵堝鐓涘ù锝呮啞椤ャ垽鏌″畝瀣М鐎殿噮鍓熼獮鎰償閵忕姵鐎鹃梻鍌欑绾绢厾鍒掗姣椽鎮㈤悡搴ゆ憰闂佹寧绻傞幉姗€鎮㈢粙璺ㄧ獮缂備礁顑嗙€笛囧磿閹剧粯鈷掑ù锝夘棑娑撹尙绱掗悩鍐茬伌闁哄苯锕弫鎰緞婵犲懏鎲伴梻浣虹帛濮婂鍩涢崼銉ユ瀬鐎广儱顦伴悡銉︾節闂堟稒顥為柛锝堟闇夐柣鎾虫捣婢с垻绱?闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛瀣ㄥ€濋弻鏇熺箾閻愵剚鐝旈梺鎼炲妼閸婂鍩€椤掑喚娼愭繛鍙夌墪鐓ら柕濞炬櫅绾偓濠殿喗顭堥崺鏍偂濞戞﹩鐔嗛悹杞拌閸庡繘鏌ｈ箛鎾缎ч柡宀嬬磿閳ь剨缍嗘禍顏堝矗閸曨垱鐓涢悘鐐垫櫕鏁堥梺绯曟杹閸撴繈骞忛崨鏉戝窛濠电姴鍠氶崬瑙勭節閻㈤潧浠滄い鏇ㄥ幗閹便劑鎮介崨濠冩珨濠碉紕鍋戦崐銈夊储閻撳寒鐒介柨鐔哄Т缁犵姵绻濇繝鍌滃妞ゃ儱鐗婄换娑㈠箣閻愬棙鍨块獮濠傗枎閹邦喚鐦堥梺姹囧灲濞佳勭濠婂嫨浜滅憸澶愬磻閹剧粯鈷掗柛灞捐壘椤忊晠鎮楀鐓庢灓闁?闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃繘骞戦姀銈呯疀妞ゆ棁妫勬惔濠囨⒑瑜版帒浜伴柛鐘愁殔閻ｇ兘寮婚妷锔惧幍闁诲孩绋掗…鍥╃不閵夛妇绠?闂?  - decision闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔兼倻濡櫣浠奸梺鍝勬濡繈寮婚悢鍏尖拻閻庨潧澹婂Σ顕€姊婚崒姘簽闁搞劌鐖煎璇测槈濡攱鏂€闂佸憡娲﹂崑鍕叏閺囥垺鈷戦柛婵勫劚閺嬪酣鏌熺喊鍗炰喊婵犫偓娓氣偓濮婃椽骞愭惔锝囩暤濠电偞娼欓崐鍧楀箖閻愭番鍋呴柛鎰ㄦ櫇閸樻悂鏌ｆ惔顖涒偓銉╁礃瑜嶉ˉ姘辩磽閸屾艾鈧悂宕愰幖浣哥９闁绘垼濮ら崐鍧楁煥閺傚灝鈷旈柣顓熺懇閺岀喖鎮滃鍡樼暦闂佺顑呴鍡涘Φ閸曨垰绠婚悹铏规磪閿濆棎浜?濠电姷鏁告慨鎾儉婢舵劕绾ч幖瀛樻尭娴滈箖鏌￠崶銉ョ仼缁炬儳婀遍惀顏堫敇閻愭潙娅ら梺鐟板暱閻倸顫忕紒妯诲闁告稑锕ラ崕鎾斥攽閳藉棗浜濋柣鈺婂灠閻ｉ攱瀵奸弶鎴濆敤濡炪倖鎸鹃崑鐔兼偩閻戞绠鹃悗鐢殿焾瀛濆銈嗗灥閹冲繘宕曢锔解拻濞撴埃鍋撴繛浣冲泚鍥敇閵忕姷锛熼梺瑙勫劶濡嫰鎮為崹顐犱簻闁圭儤鍨甸弳娆撴煕濮橆剚璐＄紒杈ㄥ笚濞煎繘濡搁妷锕佺檨闁诲孩顔栭崳顕€宕抽敐鍛殾闁圭儤鍤╅幒鎴旀瀻闁诡垎鍐炬交闂備礁鐤囬～澶愬垂閸ф鏄ラ柕澶嗘櫅楠炪垺淇婇妶鍌氫壕缂備胶濮惧畷鐢垫閹惧鐟归柛銉戝嫮浜鹃梻浣芥〃濞村洭顢氳椤㈡岸鏁愰崱娆樻祫闁诲函绲介悘姘跺疾濠靛鈷戦柟绋挎捣缁犳挻淇婇顐㈠籍鐎?闂?  - knowledge闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔兼倻濡鏆楅梺宕囨嚀缁夌數鎹㈠☉姗嗗晠妞ゆ梻绮崰姘舵⒑鏉炴壆顦︽い鎴濇喘閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏婵炵偓娅嗛柛搴㈩殕缁绘盯宕卞Ο璇查瀺闂佺锕﹂弫濠氬蓟閵娿儮鏀介柛鈩冧緱閳ь剚顨堥埀顒侇問閸ｏ絿绮婚弽顓炶摕婵炴垶锕╁鈺傘亜閹哄秶顦﹂柡瀣█濮婃椽宕崟顓犲姽缂傚倸绉崇欢姘跺Υ娴ｈ倽鐔哥瑹椤栨粌寮抽梻浣告啞閸旀垿宕濈仦鑺ユ瘎缂?闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇楀亾妞ゎ亜鍟村畷褰掝敋閸涱垰濮洪梻浣侯潒閸曞灚鐣剁紓浣插亾濠㈣泛澶囬崑鎾荤嵁閸喖濮庡銈忓瘜閸ㄨ泛顕ｆ导鏉懳ㄩ柨鏂垮⒔椤旀洟姊洪悷閭﹀殶闁稿鍠栭妴鍌炲蓟閵夛妇鍘遍梺缁樏鍫曀夊鍕╀簻妞ゆ挴鍓濈涵鍫曟煙閻熸澘顏柟顕呭櫍瀵爼骞嬪┑鎰祮缂傚倸鍊搁崐宄懊归崶顒夋晩濠电姴娲﹂崐鍧楁煥閺囩偛鈧摜绮婚悙鐑樼厪濠电偟鍋撳▍鍛磼閻樺啿鈻曢柡宀€鍠撻埀顒佺⊕椤洦淇婇崶顒佺厱閻庯綆鍋呯亸鐢告煙妞嬪骸孝妞ゆ柨绻橀、娆撳礂閸忚偐褰嬮梻鍌氬€风粈渚€宕ョ€ｎ剛鐭堥柟缁㈠枛閻ょ偓绻濇繝鍌氼仼闁搞劍鏌ㄩ埞鎴﹀磼濮橆厼鏆堥梺缁樻尵閸犳牠寮婚悢琛″亾閻㈡鐒鹃柍褜鍓氶悧鐘荤嵁鐎ｎ喗鍊锋繛鍫熷缁侇偅绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻鐎涙ê寮?闂?- 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻娑樷攽閸曨偄濮㈤梺娲诲幗閹瑰洭寮婚敐澶婄婵犲灚鍔栫紞妤呮⒑闁偛鑻晶顕€鏌熼搹顐€跨€殿噮鍋婂畷鎺楁倷閺夋垳鎮ｉ梺璇茬箳閸嬫盯骞夐敓鐘叉瀬闁割煈鍋嗙弧鈧梺姹囧灲濞佳囧煝閸喓绠惧ù锝呭暱閸氭ê鈽夊Ο閿嬵潔闂侀潧绻掓慨鐑筋敊閹达附鈷戠紓浣广€為幋鐘电焾闁哄鍤﹂敐澶婇唶闁靛濡囬崢鐢告⒑鐠団€崇€婚柛婊冨暟缁€濠囨⒒娴ｅ憡璐￠柡鍜佸亝閹便劑宕归銈傛敵婵犵數濮村ú锕傚磹閻戣姤鐓欑紓浣姑崸濠囨煕鐎ｎ偅宕岀€规洜顭堣灃闁告劑鍔庨妶锕傛⒒娓氣偓閳ь剛鍋涢懟顖涙櫠娴煎瓨鐓欓柟缁樺笚閹茬霉閻欏懐鐣电€规洘绮忛ˇ顕€鏌￠埀顒勬惞椤愩倗鐦堥梺姹囧灲濞佳冪摥婵犵數鍋涢惇浼村磹濡ゅ啫鍨濆┑鐘宠壘缁犳娊鏌熼幆褍缍佺紒銊ヮ煼濮婃椽宕崟顓夌娀鏌涙惔銊ゆ喚闁糕斁鍋撳銈嗗笂缁垛€斥枔濡偐纾?濠电姷鏁告慨鐑藉极閹间礁纾绘繛鎴欏焺閺佸銇勯幘璺烘瀾闁告瑥绻橀弻鐔虹磼閵忕姵鐏嶉梺鍝勬噺缁诲牓寮婚弴銏犻唶婵犲灚鍔栫瑧濠碘剝顨呴幊蹇曟崲濠靛顫呴柨婵嗘閵嗘劕顪冮妶鍡楃仴婵炲樊鍙冨畷娲閵堝懐鐫勯梺绋挎湰椤ㄥ懏绂嶉悙顒夋闁绘劘灏欐禒銏ゆ煕閺冣偓绾板秵绌辨繝鍥舵晝闁挎繂瀛╅悿渚€鎮楃憴鍕８闁搞劋绮欓悰顕€骞掗幊铏⒐閹峰懐鍖栭弴鐐板闂佸壊鐓堥崑鍡欑不妤ｅ啯鐓欓悗娑欘焽缁犳﹢鏌ㄥ☉妯夹ょ紒杈ㄥ笚濞煎繘濡搁妷顔筋棆缂?闂?- 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻娑樷攽閸曨偄濮㈤梺娲诲幗閹瑰洭寮婚敐澶婄婵犲灚鍔栫紞妤呮⒑闁偛鑻晶顕€鏌熼搹顐€跨€殿噮鍋婂畷鎺楁倷閺夋垳鎮ｉ梺璇茬箳閸嬫盯骞夐敓鐘叉瀬闁割煈鍋嗙弧鈧梺姹囧灲濞佳囧煝閸喓绠惧ù锝呭暱閸氭ê鈽夊Ο閿嬵潔闂侀潧绻掓慨鐑筋敊閹达附鈷戠紓浣癸供閻掕姤銇勯敐鍕煓鐎规洘鍨块獮姗€鎳滈棃娑欑€梻浣告啞濞诧箓宕㈡禒瀣疅婵炲棙鎸婚悡鐔肩叓閸ャ劍灏电紒鐘崇叀閺岋綁鎮㈠┑鍡樻悙缂佲偓閸℃稒鐓欓柣鎴烇供濞堟洟鏌￠崨顔藉€愰柡宀嬬到铻ｉ柛婵嗗妤犲洭鎮楃憴鍕碍缂佸鎳撻～蹇撁洪鍜佹濠电偞鍨兼禍顒勫矗濮樿埖鈷掗柛灞捐壘椤忊晠鎮楀鐓庡⒋闁糕斂鍨介獮妯兼嫚閺屻儱鏁归梻浣告惈濞层劑宕伴幘璇插偍闁汇垹鎲￠悡鐔兼煟濡搫绾х紒鈧畝鍕厓鐟滄粓宕滃┑鍡忔瀺闁哄洢鍨洪崐鍫曟煕椤愮姴鐏痪鎹愭闇夐柨婵嗩槹濞懷冣攽椤旂懓浜炬繝纰夌磿閸嬬偛顭囧▎鎾崇婵犲﹤鎳庨崹婵囩箾閸℃ê濮囩紒鍓佸仱閺岀喖寮剁捄銊ょ驳闂佸搫鎷戠紞浣割潖閾忓湱纾兼俊顖氭禋娴滅偞绔熼弴銏╂晣闁靛繒濮垫潏鍫ユ⒑缂佹◤顏嗗椤撶姷涓嶅Δ锝呭暞閻撱儲绻濋棃娑欘棡闁革綀娅ｇ槐鎺楀焵椤掆偓閻ｆ繈宕熼鍌氬箞闂備浇顫夐崕鎶筋敋椤撶姷涓嶉柡宥庡幗閸婄敻姊婚崼鐔衡棨闁稿鍨婚埀顒冾潐濞插繘宕濇惔銊ョ劦妞ゆ帊鑳堕埊鏇㈡嫅鏉堛劎绠鹃柛娑卞枤婢у灚鎱ㄦ繝鍐┿仢鐎规洘绮撻獮鎾诲箳瀹ュ拋妫滅紓鍌氬€搁崐鍝ョ矓閺夋嚦娑樷攽閸℃瑦娈鹃梺姹囧灩閹诧繝寮插鍫熺厱闁圭偓顨呴幏鎴犳閺屻儲鈷戦悹鍥ㄥ絻閸よ京绱撳鍛棡缂佸倸绉瑰畷濂稿即閻愮绱甸柣搴＄畭閸庨亶藝娴煎瓨鍋傞柛鎰典簼閸犳劖绻濇繝鍌滃缂佲偓閸屾稓绠鹃柟瀵稿剳娓氭稒绻涢幘鎰佺吋闁哄瞼鍠栭幃婊冾潨閸℃鏆ョ紓鍌欒兌婵敻鎮￠敓鐘茶摕闁哄浄绱曢悿鈧柣搴秵娴滄牠宕戦幘璇插嵆闁绘鏁搁悞鍏肩節閵忥絽鐓愰柛鏃€娲滅划濠氬箮閼恒儳鍘甸梺璇″灣婢ф藟婢舵劖鐓熼柟鐑樺灩娴犳盯鏌曢崶褍顏鐐差儔閹瑥顔忛鍏肩杺缂傚倸鍊峰鎺戭渻閹烘纭€闁规儼妫勯拑鐔衡偓骞垮劚閻楁粌顬婇妸鈺傗拺闁告稑锕ョ亸浼存煟閻斿弶娅呴柣锝囧厴椤㈡盯鎮欓懠顒夊敶闂備礁鍚嬫禍浠嬪磿闁秴绀堥柕濞垮労濞撳鏌曢崼婵囶棤濠⒀囦憾閺屾稓鈧綆鍓欐禒杈┾偓?- 闂傚倸鍊峰ù鍥х暦閻㈢绐楅柟閭﹀枛閸ㄦ繈骞栧ǎ顒€鐏繛鍛У娣囧﹪濡堕崨顔兼缂備胶濮靛妯跨亙闂佹寧绻傞幊搴ㄥ汲濞嗘挻鐓涢悗锝傛櫇缁愭棃鏌＄仦鐐鐎规洜鍘ч埞鎴﹀箛椤撳濡囩槐鎾存媴閸濆嫷鈧挾绱撳鍕獢鐎殿喖顭烽弫鎰緞婵炩拃鍥х閺夊牆澧界壕鍨归悡搴㈠枠婵?闂傚倸鍊搁崐鎼佸磹閹间讲鈧箓顢楅崟顐わ紱闂佸憡娲﹂崐瀣洪鍛珖婵炶揪缍€椤宕抽悜鑺モ拻濞达絽婀卞﹢浠嬫煕閳轰礁顏€规洖缍婇、鏃堝醇濠靛牞绱遍梻浣烘嚀閸氬鎮伴惃?闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎮块鈧弻鐔煎礈娴ｇ儤鎲橀梺杞扮閿曨亪寮婚悢鍏肩劷闁挎洍鍋撻柡瀣枑閵囧嫰顢曢敐鍡欘槰缂備胶绮换鍫澪涢崘銊㈡闁告鍋涙竟澶愭⒒?recall_memory 闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛濠呭煐閹便劌螣閹稿海銆愮紒鐐劤濞硷繝寮婚悢鐓庣畾闁绘鐗滃Λ鍕⒑閸濆嫬顏ラ柛搴㈠▕閸┾偓妞ゆ巻鍋撻柛妯荤矒瀹曟垿骞樼紒妯煎帗閻熸粍绮撳畷婊堟偄閻撳孩妲梺閫炲苯澧柕鍥у楠炴帡骞嬪┑鍐ㄤ壕鐟滅増甯掑Ч鏌ユ煃閸濆嫭鍣洪柣鎾寸懇閺屟嗙疀閿濆懍绨奸柣蹇撶箳閺佸寮婚妶鍚ゆ椽顢旈崘鈺佹灓闂備胶鎳撶壕顓熺箾閳ь剚銇勯姀鈽嗘畷闁瑰嘲鎳樺畷婊兠圭€ｎ亙澹曞┑鐐村灟閸ㄦ椽鍩涢幋锔界厱婵犻潧妫楅瀛樹繆閹绘帒鎮戠紒缁樼⊕瀵板嫮鈧綆鍋嗛ˇ顓犵磽娓氬洤鏋涙い顓犲厴閻涱喖螣閼测晝锛滃┑鈽嗗灣閸樠冾嚕閾忣偆绡€闁汇垽娼ф禒锕傛煕閵娿儳鍩ｉ柍銉畵瀹曞爼顢楁担绯曞亾閸洘鈷戞い鎺嗗亾缂佸鏁婚幃锟犲即閵忥紕鍘搁梺绋挎湰缁本绂掑鍕閻忕偛鍊搁埀顒侇殜楠炲骞橀鑺ユ珖闂佺鏈銊╊敊閹邦喚纾藉〒姘搐閺嬨倝鏌熼搹顐ｅ鞍闁哄懎鐖煎濠氬Ψ閿旀儳骞堥梻浣虹帛閺屻劑骞栭锝囶浄闂侇剙绉甸悡娑氣偓鍏夊亾閻庯綆鍓涜ⅵ婵＄偑鍊戦崹娲晪濡炪値鍘归崝鎴濈暦濮椻偓婵℃悂濡烽幇顓炵伌婵﹦绮幏鍛存嚍閵夛絺鍋撻崘顔解拻闁告洦鍋嗘晥閻庤娲橀崝鏇㈠煘閹寸姭鍋撻敐搴″缂佷緤绠撻弻锝嗘償椤栨粎校婵炲瓨绮庨崑銈咁嚕瀹曞洠鍋撻敐搴℃灍闁绘挻绋戦…璺ㄦ崉閻氭潙濮涙繛瀵稿О閸ㄨ櫣鎹㈠☉銏犻唶婵炴垶锚婵箑鈹戦纭锋敾婵＄偠妫勯悾鐑藉Ω閿斿墽鐦堥梺绋挎湰缁娀宕曠仦瑙ｆ斀闁绘ê鐏氶弳鈺呮煕鐎ｎ偄濮嶇€规洘鍨块獮姗€寮妷锔芥澑?```

- [x] **Step 2: Add few-shot example for memory**

Add the following as a new example after existing examples in `Agent.md`:

```markdown
### 缂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣婵ジ鏌＄仦璇插姎缁炬儳顭烽弻鐔煎箲閹伴潧娈紓浣哄珡閸ャ劎鍘介梺褰掑亰閸樼晫绱為幋鐐簻闁靛鍎洪崕蹇涙?闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔兼倻濡鏆楅梺宕囨嚀缁夌數鎹㈠☉姗嗗晠妞ゆ梻绮崰姘舵⒑鏉炴壆顦﹂柨鏇ㄤ邯瀵鈽夐姀鐘栥劍銇勯弮鍥у惞闁轰焦鐗犲鍝勑ч崶褉鍋撻幇鏉跨；闁瑰墽绮埛鎺懨归敐鍫燁仩闁靛棗锕弻娑㈠箻鐎靛摜鐤勯梺璇″枤閸忔﹢銆佸☉銏″€烽柤鑲╃礋閺囥垺鈷戦梺顐ゅ仜閼活垱鏅剁€涙ɑ鍙?
闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇楀亾妞ゎ亜鍟村畷褰掝敋閸涱垰濮洪梻浣侯潒閸曞灚鐣剁紓浣插亾濠㈣泛澶囬崑鎾荤嵁閸喖濮庡銈忓瘜閸ㄨ泛顕? "闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛瀣ㄥ€濋弻鏇熺箾閻愵剚鐝旈梺鎼炲妼閸婃悂婀侀梺鎸庣箓閹冲酣寮抽弬妫电懓顭ㄩ崘顏喰ㄩ梺鍝勬湰缁嬫垿鎮惧┑瀣劦妞ゆ帒瀚壕濠氭煟閹邦剚鎯堢痪鍓х帛缁绘繈妫冨☉鍗炲壉闂佺粯鎸鹃崰鎰┍婵犲洤围闁稿本鐭竟鏇㈡⒒娴ｈ櫣甯涙い銊ユ嚇閺佸啴顢旈崼婵堢暫闂佹眹鍨婚…鍫㈢不婵犳碍鐓涢柛灞久崝婊勩亜椤愩垻效婵﹥妞介幃鐑藉级鎼存挻瀵栨俊鐐€栫敮妤勩亹閸愵噮鏁婇煫鍥ㄧ☉鍞梺鎸庢濡椼劎鑺辨繝姘拺闁圭瀛╃壕鐢告煕鐎ｎ偅灏甸柍褜鍓氶鏍窗閺嶃劍娅犻幖杈剧到閸ㄦ繃绻涢崱妯哄缂佲檧鍋撻梻浣规偠閸庮垶宕濈仦鍓ь洸鐟滅増甯楅埛鎴︽煙椤栧棗瀚々浼存⒑缁嬫鍎忛柟铏耿楠炲啴鎮介崨濠冩闂佺粯蓱閺嬪ジ骞忛搹鍦＝闁稿本鐟ч崝宥嗐亜椤撶偞鍠橀柟顖氭湰缁绘繈宕橀鍡╁晭闂佽崵濮村▔褔宕ㄩ娑欘啅闂備胶绮幐鍫曞磹濠靛钃熼柣鏃囨閻瑩鏌涢…鎴濇灓婵″弶婢橀埞鎴︽倷閼碱剙顤€濡炪們鍔屽Λ婵嬬嵁閸儱惟闁靛瀛╁Λ鍐春閳ь剚銇勯幒鎴濐仾闁稿顑夐悡顐﹀炊閵婏妇顦梺娲诲幖濡鈥︾捄銊﹀磯閻炴稈鈧剚娼撻柣鐔哥矌婢ф鏁Δ鍛；闁归偊鍘规禍婊堟煛閸愩劌鈧摜鏁捄琛℃斀妞ゆ柨銈搁崣鍕叏婵犲懏顏犻柟椋庡█閸ㄩ箖鎼归銈勬喚濠碉紕鍋戦崐鎴﹀礉瀹€鍕亱闁圭偓鍓氶崵鏇熴亜閹拌泛鐦滈柡浣割儔閺屽秷顧侀柛鎾跺枛婵″瓨鎷呯化鏇熺€婚梺鍦亾濞兼瑩鎯傞崟顒傜瘈闁靛骏绲剧涵鎯р攽閸屾稒顥堢€规洘鐟︾粋鎺斺偓锝庡亐閹风粯绻涙潏鍓у閻犫偓閿曞倸缁╅柣妤€鐗忕粻鎯ь熆鐠轰警鍎戞繛鍙夋尦閺屸剝鎷呯粙鎸庢婵犲痉銈呯厫缂佹梻鍠栭弫鍐焵椤掆偓鐓ゆい鎾跺仧閺嗭箓鏌ㄥ┑鍡橆棞缂佸墎鍋ら幃姗€鎮欓崣澶婃殘闂佽绻愬Λ婵嗩潖缂佹ɑ濯撮柧蹇曟嚀缁椻€愁渻閵堝骸骞栭柣妤佹崌閵嗕礁顫濋幇浣光枌闁诲氦顫夊ú蹇涘垂娴犲宓佹慨妞诲亾妞ゃ垺鐟╅幐濠冨緞閸℃ぞ澹曢梺姹囧灩閹诧繝鎮￠悢鍏肩厽闁哄啫鍊哥敮璺好瑰鍛暭濞ｅ洤锕獮鎾诲箳閺冨倐銊╂⒑鐠団€虫灆缂侇喗鐟╅妴浣糕槈濡攱顫嶅┑鐐叉缁绘帡鏁嶉幘缁樼厽閹兼番鍊ゅ鎰箾閸欏鐭掔€规洘顨呰灒閻犱礁纾粻姘舵⒑瑜版帗锛熼柣鎺炵畵瀵彃顭ㄩ崼鐔哄幗闂佹寧绻傞幊鎾垛偓姘缁辨帡鎳犻鈧敮鍫曟煃鐟欏嫬鐏撮柟顔界懇瀵爼骞嬮悩杈敇闂傚倷鑳堕幊鎾诲箟閿熺姴绠栭柛宀€鍋涢弸渚€鏌涢幇闈涙灈閸ュ瓨绻濋姀锝嗙【闁挎洩绠撻幃?

闂?save_memory(category="preference", content="闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剛绮婚悩鑽ゅ彄闁搞儯鍔庨埊鏇㈡煕鎼淬埄娈曢柕鍥у瀵剟宕归瑙勫瘱缂傚倷鑳舵慨闈浳涢崘顔艰摕婵炴垶鐭▽顏堟煕閹炬せ鍋撴俊鎻掔墢缁辨挻鎷呯粙娆炬殺闂佺顑囬崰鏍春閳ь剚銇勯幒鍡椾壕缂備胶濮寸粔鐟扮暦閺囩喐缍囬柍瑙勫劤娴滅偓鎱ㄥΟ鐓庡付婵炲懎绉归弻鐔碱敍濞嗘垵濡介梺璇″灡濡啯淇婇幖浣规櫆闁诡垎鍐唶濠电姷鏁搁崑鐘诲箵椤忓棗绶ゅù鐘差儏缁犵儤绻濇繝鍌氼仾婵炲懐濞€閺屾洝绠涙繝鍐ㄦ珰闂佺顑嗛幑鍥х暦閻戠瓔鏁囩憸蹇涘礉閹间焦鈷戦梻鍫熺〒婢с垺銇勯鐐靛ⅵ妞ゃ垺宀搁弫鎰緞婵犲嫷鍟嬫俊鐐€栧Λ渚€宕戦幇閭︽晩闁圭儤鍩堝〒濠氭煏閸繃顥為柍閿嬪姍閺屾稒鎯旈姀鐘灆闂佺懓鍢茬换鎺楀焵椤掑﹦绉甸柛鐘愁殜閸╂盯骞嬮敂鐣屽幍缂備礁顑嗙€笛囧箲閿濆鐓冮柦妯侯樈濡偓闂佸搫琚崐鏇犲弲闁荤姴娲╃亸娆愮椤撶姷纾藉ù锝囶焾閳ь剙鎽滅划鏃堟偡閹殿喗娈鹃梺闈涱煭婵″洨寮ч埀顒勬⒑閸涘﹥澶勯柛銊╀憾椤㈡挸顓兼径瀣ф嫽婵炶揪绲块…鍫ュ箖閹存緷鐟邦煥閳ь剛鍒掑▎蹇曟殾闁哄洢鍨归拑鐔兼煏婢舵稓鐣卞ù鐘欏洦鈷戦柣鐔告緲閳锋梻绱掗鍛仸闁糕晜鐩獮鎺懳旀担鍝勫箞闂佽绻掗崑娑欐櫠娴犲鐓€闁哄洨濮风壕鐣屸偓骞垮劚濡鎮橀幘顔界厸鐎光偓鐎ｎ剛袦闂佽桨鐒﹂崝娆忕暦濮椻偓婵℃悂濡烽鐣岀У婵犲痉鏉库偓妤佹叏閻戣棄纾婚柣鎰仛閺嗘粓鏌ㄩ悢鍝勑ョ€规挷绶氶弻鐔兼倻濮楀棙鐣剁紓浣哄缁查箖濡甸崟顖氱閻犺櫣鍎ゅ▍鈺呮⒑閸愬弶鎯堥柛濠呭吹缁?)
闂?濠电姷鏁告慨鐑藉极閹间礁纾婚柣妯款嚙缁犲灚銇勮箛鎾搭棞缂佽翰鍊濋弻锕€螣閻氬绀嗗┑鐐村灦椤倿寮崼婵嗙獩濡炪倖鎸鹃崑娑欑閼哥數绡€闁汇垽娼ф禒锕傛煕閵娿儱顣抽柛鐘诧工椤撳吋寰勬繝鍕垫Н婵犵數濮撮敃銈団偓姘ュ妽缁傚秴顭ㄩ崼鐔哄幐闂佸憡鍔х徊鑺ョ閹屾富闁靛牆妫楅悘锕傛煟閻斿弶娅呴柣锝囧厴婵＄兘鍩℃担鍝勨偓鐐差渻閵堝棗绗傞柤鍐茬埣瀹曪綁宕卞缁樻杸闂佺粯鍔栧娆撴倶閿曞倹鐓熼柣鏃€绻傚ú銈囩不閻戞ǜ浜滈柕鍫濇祩閸旀湽user(type="confirm", question="闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛瀣ㄥ€濋弻鏇熺箾閻愵剚鐝旈梺鎼炲妼閸婃悂鍩為幋锕€纾兼慨姗嗗墻濡矂姊烘潪鎵槮闁挎洦浜璇测槈閵忕姈銊╂煥濠靛棙鍣规い顒€顦扮换婵嗏枔閸喚浠梺鐟版啞婵炲﹪骞冮敓鐙€鏁冮柨鏇楀亾闁绘劕锕﹂幉鍛婃償閵娿儳顔夐梺鎸庣箓椤︿即鎮￠弴銏＄厽闁哄倸鐏濆▓鈺呮椤掑澧撮柡宀嬬磿娴狅妇鎷犻幓鎺濈€抽梻浣哥枃濡嫰藝椤栫偛鐓濋幖娣妼缁狅綁鏌ｅΟ璇茬祷缂傚秴妫涚槐鎾诲磼濮橆兘鍋撻幖浣哥９闁告縿鍎抽惌鎾绘煟閵忕姵鍟為柡鍛箞閺屾洝绠涢弴鐑嗏偓宀勬煕閵堝棙绀嬮柡宀€鍠撶槐鎺懳熸潪鏉垮灁婵犵數鍋涢惃鐑藉疾濠婂牆桅闁告洦鍨扮粻娑㈡煃鏉炴媽顔夐柛瀣尭铻栭柛娑卞幘閻ゅ懎顪冮妶鍛闁硅櫕鍔楀褔鍩€椤掑嫭鈷戦梻鍫熺洴閻涙粎绱掗幓鎺戔挃婵炴垹鏁诲畷婊嗩槾缁惧墽鍘ч…璺ㄦ崉閻氭潙濮涢梺鎸庣☉缁夊爼鍩€椤掍緡鍟忛柛鐕佸亰瀹曟儼顦存い锔芥緲椤啴濡堕崱娆忣潷缂佺偓婢樼粔褰掑箖濡ゅ拋鏁嗛柛鏇ㄥ厴閹锋椽姊洪崨濠冨鞍鐟滄澘鍟粋宥夊冀椤撶喓鍘遍梺闈涱焾閸庡磭绮斿ú顏呯厵鐎规洖娲ゆ禒杈殽閻愭煡鍙勯柟宕囧仱婵＄柉顦叉鐐村姍濮婄粯鎷呯憴鍕哗闂佺瀵掗崹璺虹暦濠靛棭鍚嬮柛銉閸撱劑姊洪幐搴㈢闁稿﹤缍婇幃锟犳偄閸濄儳鐦堥梺鍓茬厛閸嬪嫭鎱ㄩ崶銊х闁告侗鍘炬晥闂佸搫澶囬崜婵嬪箯閸涙潙浼犻柕澶嬪姂閸婃洟婀侀梺缁樼懃閹虫劙鎮鹃崹顐ｅ弿濠电姴鎳庨崥褰掓煃瑜滈崜娆撴倶濮樿泛绠栭柛宀€鍋為崐鍨箾瀹割喕绨奸柍閿嬪笒闇夐柨婵嗘噺閸熺偤鏌涢悢鍝勪槐闁哄被鍊濋幃鐑藉级鎼存挻瀵栭梻浣稿悑濡炶姤绂嶉崼鏇炵疇闁哄稁鍘奸悡娑㈡煕鐏炶鈧牜绱炲Δ浣风箚闁绘劦浜滈埀顒佺墵楠炴劙宕奸弴鐐茬€梺闈╁瘜閸橀箖鎯岄崱娑欑厱鐎光偓閳ь剟宕戦悙鐑樺亗闁哄洨鍠嗘禍婊堟煙閺夊灝顣抽柟顔垮亹缁辨帡鎮╃粵纭呪偓鍧楁煛瀹€瀣瘈鐎规洖宕灒婵炶尙绮ˉ鍫ユ⒒娴ｅ憡鎯堥柣顒€銈稿畷浼村冀椤撶偟鐣哄┑鐘诧工閸氭﹢鎮㈤崗鍏煎劒闂侀潻瀵岄崢浠嬪吹閸愩劉鏀介柣妯虹仛閺嗏晠鏌涚€ｎ偆娲存鐐诧攻閹棃鏁愰崒姘濠殿喗锕╅崢鐣屾閸欏浜滄い鎰╁灮缁犺尙绱掔紒妯肩畵妞ゎ偅绻堥、妤呭磼閻愰潧绀堥梻鍌氬€峰ù鍥綖婢舵劕绠氱€光偓閸曨偄鍋嶉梺鐟扮摠鐢偤寮伴崒姘ｆ斀闁绘ê鐏氶弳鈺呮煕鐎ｎ剙浠辩€规洖婀遍幑鍕瑹椤栨稓绋佺紓鍌氬€烽悞锕佹懌闂佸憡鐟ョ换鎰版箒闂佺绻愰崥瀣礊閹达附鐓熼柟鐑樺灩娴犳盯鏌曢崶褍顏鐐村浮瀹曞崬顪冮幆褜妫滈梻鍌氬€烽懗鍫曗€﹂崼銉︽櫇闁靛鏅涚粻鏍煕瀹€鈧崑鎴﹀焵椤戣法顦︽い顐ｇ箖閿涙劕鈹戦崶銊︾彣闂傚倷绶氶埀顒傚仜閼活垱鏅堕鈧弻锝夋晲閸パ冨箣婵犵绱曢崗妯讳繆闁垮鍎熼柕蹇婃閹峰姊洪柅鐐茶嫰婢у墽绱撳鍛棦鐎规洘绮岄埢搴ㄥ箻瀹曞洨鏆?)
闂?闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇楀亾妞ゎ亜鍟村畷褰掝敋閸涱垰濮洪梻浣侯潒閸曞灚鐣剁紓浣插亾濠㈣泛澶囬崑鎾荤嵁閸喖濮庡銈忓瘜閸ㄨ泛顕ｆ导鏉懳ㄩ柨鏂垮⒔椤旀洟姊洪悷閭﹀殶闁稿鍠栭妴鍌炲蓟閵夛妇鍘遍棅顐㈡处濮婂鎯岀€ｎ喗鐓忛柛銉戝喚浼冮悗娈垮櫘閸ｏ綁宕洪埀顒併亜閹烘垵顏撮柡浣稿缁绘盯宕卞Ο璇茬闁?闂?save_memory
闂?闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€哥粻鏍煕椤愶絾绀€缁炬儳娼￠弻鐔煎箚閻楀牜妫勭紒鎯у⒔缁垳鎹㈠☉銏犵闁哄啠鍋撻柛? "濠电姷鏁告慨鐑藉极閸涘﹦绠鹃柍褜鍓氱换娑欐媴閸愬弶鎼愮痪鍓ф嚀閳规垿鎮╃€圭姴顥濋梺姹囧€楅崑鎾诲Φ閸曨垰绠涢柕濠忕畱濞呮岸姊洪崫鍕靛剱婵☆偄鍟村濠氭偄閸涘﹦绉舵俊銈忕到閸燁垶顢撳澶嬧拺闁告繂瀚刊濂告煕閹捐泛鏋涙鐐插暙椤粓鍩€椤掑嫬绠栨繛鍡樻尰閸ゅ绻涢崼鐔奉嚋妞ゃ儱顦靛缁樻媴鐟欏嫬浠╅梺绋匡攻閻楁粓寮鈧弫鎾绘偐閼碱剛鏆梺鑽ゅ枑閻熴儳鈧凹鍣ｉ幃鐤亹閹烘挾鍘撻悷婊勭矒瀹曟粓鎮㈤悡骞儵鏌涘畝鈧崑鐐哄疾濠婂牊鐓曢柟鐐殔閹峰危閹间焦鈷掑ù锝堫潐閸嬬娀鏌涙惔銏°仢鐎规洘绮岄埢搴ㄥ箳閺冨偆鍟嶉梻鍌氬€搁崐鐑芥嚄閸洍鈧箓宕奸妷銉ョ彉濡炪倖甯掔€氼參宕戦敓鐘崇厪闁割偅绻冪粚鍨攽椤旂厧鏆遍棁澶愭煟閹捐櫕鎹ｉ柟鐣屽█閺岋綁骞樼€涙顦ㄩ梺閫涚┒閸斿矂锝炲鍫濆耿婵°倐鍋撴い顐邯濮婃椽宕烽鐕佷户缂傚倸绉崇欢姘嚕婵犳艾鐒洪柛鎰ㄦ櫅椤庢捇鏌ｉ悢鍝ユ噧閻庢凹鍓涙竟鏇㈠礃閸欏倹妫冮幃鈺呮濞戞鎹曟俊鐐€栭崹鐢杆囬悽鍛婂仒妞ゆ洍鍋撶€规洖鐖奸、妤佸緞鐎ｎ偅鐝滄繝鐢靛О閸ㄧ厧鈻斿☉銏″仭闁冲搫鎳庨悡娑㈡煕鐏炲墽鐭屾い鏃€娲熷娲偡闁箑娈堕梺绋款儑閸嬨倝宕哄☉銏犵闁瑰瓨姊归弬鈧俊鐐€栧ú宥夊磻閹惧墎纾奸柣妯虹－婢х敻鏌曢崱鏇狀槮妞ゎ偅绮撻崺鈧い鎺戝瀹撲線鏌″鍐ㄥ濠殿垱鎸抽弻娑樷攽閸曨偄濮跺┑鈥冲级閹稿啿顫忕紒妯诲闁告稑锕ㄧ涵鈧梻浣侯焾缁ㄦ椽宕愬┑瀣祦闁归偊鍘剧弧鈧┑顕嗙悼椤牆煤閳哄惤鍥蓟閵夛富姊挎繝銏ｅ煐閸旀牠鎮￠弴銏㈠彄闁搞儯鍔忔竟妯好瑰鍐Ш闁哄矉缍侀獮娆撳礃閵娧傚寲缂傚倷娴囨ご鍝ユ暜濡ゅ拑缍栭柟杈剧畱閸愨偓閻熸粌绉堕悮鎯ь吋婢跺鈧敻鎮峰▎蹇擃仾缂佲偓閸愨斂浜滈柕濞垮劵瀹搞儵鏌ｉ敐鍥у幋闁诡喒鍓濋幆鏂课熺紒妯绘緫闂傚倷绀佹竟濠囧磻閸℃稑绐楅柟浼村亰閺佸洤螖閿濆懎鏆為柍閿嬪笒闇夐柨婵嗘噺閸熺偤鎮归幇鍓佺瘈闁哄本绋掗幆鏂库槈濡嘲浜炬俊銈呮噹閺嬩焦銇勯弬鎸庮潔闁哄啫鐗嗛悞鍨亜閹烘垵顏╅柣鎾寸箘閳ь剙绠嶉崕閬嵥囬婊呯焼閻庯綆鍋佹禍婊堟煛瀹ュ啫濡块柍缁樻崌閺岀喎鐣￠柇锔惧悑闂佸搫鐭夌徊楣冨箚閺冨牆顫呴柍鍨涙櫅椤矂姊洪挊澶婃殺濡炲瓨鎮傛俊鐢稿礋椤旀儳鏁ラ梻浣告啞濞诧箓宕㈡ィ鍐炬晩闁哄洢鍨洪埛鎴︽煕閹炬潙绲诲ù婊勭墵閺屾盯濡搁…鎴炵秷缂備礁鍊圭敮锟犮€佸☉銏″€烽悗鐢殿焾鐢?

闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇楀亾妞ゎ亜鍟村畷褰掝敋閸涱垰濮洪梻浣侯潒閸曞灚鐣剁紓浣插亾濠㈣泛澶囬崑鎾荤嵁閸喖濮庡銈忓瘜閸ㄨ泛顕? "闂傚倸鍊搁崐鎼佸磹閹间讲鈧箓顢楅崟顐わ紱闂佸憡娲﹂崐瀣洪鍛珖婵炶揪缍€椤宕抽悜鑺モ拻濞达絽婀卞﹢浠嬫煕閳轰礁顏€规洖缍婇、鏃堝醇濠靛牞绱遍梻浣筋潐閸庢娊顢氶鐘典笉濡わ絽鍟悡娆撴倵閻㈡鐒惧ù鐙呯畵閺岋綁骞橀崡鐐插闂侀潧娲ょ€氫即鐛€ｎ亖鏀介柛銉戝嫷浠梻鍌欑閹碱偊骞婃惔銊﹀亯濠靛倻顭堢粻鏍煃閸濆嫭鍣归柛銊ュ€归妵鍕箛閳轰胶浼勯悷婊呭閹稿啿顫忛搹瑙勫珰闁哄被鍎卞鏉库攽閻愭澘灏冮柛銉戝懐鏋€闂備浇娉曢崰鎾存叏閻㈢纾婚柍鍝勬噺閳锋垶銇勯幒鍡椾壕缂備礁顦遍弫濠氬箖閳ユ枼妲堥柕蹇ョ磿閸橀亶姊虹憴鍕凡濠⒀冩捣缁瑧绱掑Ο鑲╊啎闂佸憡渚楅崢濂稿汲閻旇櫣纾奸弶鍫涘妼缁楁帡鎽堕弽顓熺厓鐟滄粓宕滈悢椋庢殾闁规壆澧楅崑锟犳⒑椤撱劎鐣辨繛鍫亰濮婃椽宕ㄦ繝鍐槱闂佺顑嗙敮鈥崇暦閵壯€鍋撻敐搴℃灍闁绘挻娲熼弻锟犲炊閵夈儱顬堝Δ鐘靛仦钃卞ǎ鍥э躬瀹曪絾寰勬繝鍕礉婵犳鍠栭敃锕傚磿閵堝拋鐒芥い蹇撶墕缁犮儲銇勯弮鍌氬付妞ゎ剙顦扮换婵嬫偨闂堟刀鐐烘煕閵婏附銇濋柡浣稿暣婵偓闁靛牆鍟犻崑?

闂?recall_memory(query="闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎮块鈧弻锝呂熷▎鎯ф闂佹眹鍊楅崑鎾舵崲濞戙垹骞㈡俊顖濇娴犺偐绱撴担鍝勑ｆ俊顐㈠暣瀵鈽夊顐ｅ媰闂佸憡鎸嗛埀顒€危閸垻纾藉ù锝囶焾椤ｆ娊鏌涚€ｎ剙鏋涢柛鈹惧亾濡炪倖宸婚崑鎾剁磼閻樿尙效鐎规洘娲樺蹇涘煘閹傚濠殿喗顭囬崢褍鈻嶅澶嬬厵妞ゆ牗鐟ч崝宥夋煙椤栨稒顥堝┑鈩冩倐閺佸倿骞嗚缁犵増绻濋悽闈涗哗闁规椿浜炵槐鐐哄焵椤掍降浜滄い鎰╁焺濡茬儤绻涢崱鎰伈鐎规洩绲惧鍕醇濠婂懐娉?)
闂?闂傚倸鍊搁崐鎼佸磹閻戣姤鍤勯柛顐ｆ礀缁犵娀鏌熼崜褏甯涢柛濠呭煐閹便劌螣閹稿海銆愮紒鐐劤濞硷繝寮婚悢鐓庣畾闁绘鐗滃Λ鍕⒑閸濆嫬顏ラ柛搴㈠▕閸┾偓妞ゆ巻鍋撻柛妯荤矒瀹曟垿骞樼紒妯煎帗閻熸粍绮撳畷婊堟偄閼测晛绁﹂棅顐㈡处濞插秹宕戦幘缁樻櫜閹肩补鍓濋悘鍫㈢磽娴ｅ搫鐝￠柛銉ｅ妼娴狀垶姊虹拠鈥冲箺閻㈩垱甯楁穱濠囧锤濡や胶鍘?闂?闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫宥夊礋椤掍焦顔囬梻浣虹帛閸旀洟顢氶鐘典笉濡わ絽鍟悡鍐喐濠婂牆绀堟慨妯块哺瀹?闂?闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€哥粻鏍煕椤愶絾绀€缁炬儳娼￠弻鐔煎箚閻楀牜妫勭紒鎯у⒔缁垳鎹㈠☉銏犵闁哄啠鍋撻柛? "闂傚倸鍊峰ù鍥敋瑜嶉湁闁绘垼妫勭粻鐘绘煙閹规劦鍤欑紒鐘靛枛濮婁粙宕堕鈧闂佸湱澧楀妯肩矆閸愨斂浜滈柡鍐ㄥ€哥敮鍫曟煟鎼搭喖寮柟顔煎槻椤劑宕ㄩ褎姣夐梺姹囧焺閸ㄩ亶銆冩繝鍥ф槬婵炴垯鍨圭猾宥夋煕椤愩倕鏋旈柛姗嗕邯濮婃椽宕滈幓鎺嶇凹缂備浇顕х€氼參寮查崼鏇烆潊闁靛繈鍨婚敍婊堟⒑缂佹﹩鐒鹃悘蹇旂懅缁柨煤椤忓懐鍘搁柣蹇曞仧椤牊鏅堕懠顒傜＜闁哄啫鍊搁弸搴ㄦ煃閻熸澘鏆ｇ€规洖缍婇、娆撴偡妫颁礁顥氶梻渚€娼ч悧鍡浰囬鐐村殝鐟滅増甯楅悡鏇熴亜閹板墎绋荤紒鈧崼銉︾厱婵炲棙鍔栧畷宀勬煛鐏炲墽娲村┑锛勫厴楠炲鈹戦崱鈺€绱濇繝纰樻閸嬪懘宕归崹顕呮綎?
```

- [x] **Step 3: Commit**

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

- [x] **Step 1: Write the failing tests**

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
        {"role": "user", "content": "濠电姷鏁告慨鐑藉极閹间礁纾婚柣妯款嚙缁犲灚銇勮箛鎾搭棞缂佽翰鍊濋弻鐔虹矙閸噮鍔夐梺鍛婄懃缁绘﹢寮婚悢铏圭＜闁靛繒濮甸悘鍫ユ煕?},
        {"role": "assistant", "content": "濠电姷鏁告慨鐑藉极閹间礁纾婚柣妯款嚙缁犲灚銇勮箛鎾搭棞缂佽翰鍊濋弻鐔虹矙閸噮鍔夐梺鍛婄懃缁绘﹢寮婚悢铏圭＜闁靛繒濮甸悘鍫ユ煕閵夈儳鎽犵紒缁樼〒閳ь剛鏁搁…鍫濈摥婵＄偑鍊栭崹闈浳涘┑鍡╁殨闁哄被鍎洪弫鍡涙煃瑜滈崜鐔凤耿娓氣偓濮婃椽骞愭惔锝囩暤闂佺粯顨嗙划宀勨€﹂崶顒€绠涙い鏂垮⒔閿涙粓姊虹紒妯忣亪宕捄銊х當闁圭儤顨嗛ˉ鍡楊熆閼搁潧濮堥柣鎾跺枑閹便劌螖閳ь剙螞濡や胶顩叉繝濠傚幘閻熼偊鐓ラ柛娑卞幒婢规洜绱撴担铏瑰笡闁烩晩鍨堕悰顔锯偓锝庡枟閸婄兘鎮楅悽娈跨劸鐎殿喗濞婂缁樻媴閾忕懓绗″銈冨妼閹冲氦鐏嬪┑鐘诧工閻楀棙顢婇梻浣告贡婢ф顭垮鈧幆灞轿旈埀顒勨€︾捄銊﹀磯闁惧繐婀遍崝绋库攽閻愬瓨缍戦悗姘緲椤繐煤椤忓拋妫冨┑鐐村灱妞存瓕鍊撮梻鍌欒兌椤牆顫濋敂鐣岊洸妞ゆ帒瀚崵宥夊级閸碍娅嗛悗姘哺閹攱鎷呮搴М缂傚倸绉撮敃顏勵嚕椤愶箑绠涢柡澶庢硶閸婄偛顪冮妶搴″⒒闁哥姵鎹囧畷鏇㈡嚑椤掍礁搴婂┑鐐村灟閸ㄥ綊鏌嬮崶顒佺厽闁哄啫鐗滃Λ鎴澝归悡搴ｇ劯婵?},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    """Long conversations should have older messages compressed."""
    messages = [{"role": "system", "content": "System prompt"}]
    # Add 20 user/assistant pairs
    for i in range(20):
        messages.append({"role": "user", "content": f"闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇楀亾妞ゎ亜鍟村畷褰掝敋閸涱垰濮洪梻浣侯潒閸曞灚鐣剁紓浣插亾濠㈣泛澶囬崑鎾荤嵁閸喖濮庡銈忓瘜閸ㄨ泛顕ｆ导鏉懳ㄩ柨鏂垮⒔椤旀洟姊洪悷閭﹀殶闁稿﹥鍨甸～婵嬵敄閳哄绉€规洖銈告俊鐑芥晜閹冪疄濠碉紕鍋戦崐鏍礉閹达箑纾归柡鍥ュ灩閸戠姷鈧箍鍎卞ú銊у?{i}"})
        messages.append({"role": "assistant", "content": f"闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫鎾绘偐閼艰埖鎲伴梻浣芥硶閸犳挻鎱ㄩ幘顔藉仾闁绘劦鍓涚弧鈧繝鐢靛Т閸婃悂顢旈鍛闁告侗鍨版牎缂備胶绮换鍐崲濠靛纾兼繝濠傚枤閺嗩偊姊绘担铏瑰笡闁告梹娲熼弫鍐敂閸繆鎽曢梺鎸庣箓椤︻垳绮诲☉娆嶄簻闁瑰搫绉烽澶愭煛鐎ｎ偆鎳冮柍?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙闁藉啰鍠栭弻鏇熺箾閻愵剚鐝﹂梺杞扮鐎氫即寮诲☉妯锋闁告鍋為悘宥呪攽閻愬弶鍣藉┑鐐╁亾闂佸搫鐭夌徊鍊熺亽闂佸吋绁撮弲娑氱箔閿熺姵鈷戠紒瀣健椤庢绱掓径濠勭Ш鐎殿喛顕ч埥澶愬閻樻彃绁梻渚€娼ч…鍫ュ磿娴煎瓨鍤嬫い蹇撶墛閳锋垿鏌熼懖鈺佷粶闁逞屽墯椤ㄥ棛鎹㈠☉銏犵劦妞ゆ帒瀚悡娆愩亜閺冨洤浜圭紒澶庢閳ь剝顫夊ú鏍偉閸忛棿绻嗘慨婵嗙焾濡查箖姊烘导娆戠М濞存粏娉涢～蹇撁洪鍛簵闁硅壈鎻徊鑲╁垝閻㈠憡鈷戦柟鑲╁仜婵″吋绻涚亸鏍ゅ亾閹颁礁娈ㄥ銈嗗姂閸╁嫰宕ョ€ｎ喗鐓曟繛鎴濆船閻忊剝绻涢崼鐔哥婵﹥妞介弻鍛存倷閼艰泛顏繝鈷€鍐惧殶闁逞屽墯椤旀牠宕抽鈧畷鎴炵節閸愌呯畾闂佸吋鎮傚褏娆㈤悙娴嬫斀闁绘ɑ褰冮鎾煕濮橆剚鍤囬柡宀嬬稻閹棃鏁愰崱妤佺暚闂佽瀛╅崙褰掑储婵傜硶鈧箓宕归銉у枛閹剝鎯旈敐鍥╂憣濠电姷鏁搁崑娑樜熸繝鍐洸婵犻潧顑呴悡鏇㈡煙鐎电浜煎ù婊勭矒閺岀喖鎳滈鈧俊鐓庮熆瑜嶅鍫曞Φ閸曨垱鏅濋柛灞诲€栭ˉ鏍磽?0闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇氱秴闁搞儺鍓﹂弫鍐煥閺囨浜剧紓浣插亾闁割偆鍠撶弧鈧梻鍌氱墛缁嬫挻鏅堕姀銈嗙厽妞ゆ挾鍠愬畷宀勬煛瀹€瀣М妤犵偛顑夐弫鎰板幢閳哄偆妫勭紓鍌氬€烽懗鑸垫叏閻㈠灚鏆滄俊銈呮噹妗呴梺鍛婃处閸ㄤ即宕橀埀顒勬⒑闂堟侗妲堕柛搴櫍瀹曟垿骞樺鍕瀹曟﹢顢旈崱娆忓Ц婵犵數濮伴崹濂稿春閺嶎厼绀夐柡宥庡幗閸嬪倿鏌￠崶銉ョ仾闁绘挻鐩弻娑氫沪閸撗呯厐闂佸憡鏌ㄩ鍡欐崲濞戙垹宸濇い鎾跺櫏濡偛顪冮妶搴″绩闁稿骸顭疯棟鐎规洖娲ㄧ壕鍏笺亜閺冨洤袚鐎规洖鐬奸埀顒侇問閸犳牠鈥﹀畡鎵殾濠靛倻顭堝敮闂佹寧娲嶉崑鎾绘煟瑜嶇€氼厾鎹㈠┑瀣潊闁挎繂妫涢妴鎰渻閵堝繒鐣冲瀛樻倐婵￠潧鈻庨幘瀛樺劒濡炪倖鍔戦崐妤咁敊閺囥垺鐓熼幖娣灮閳洘銇勯鐐村枠闁诡垰鏈换婵嬪礃瑜忕粻姘渻閵堝棗濮х紓宥呮閳绘捇寮崼鐔蜂簵闂侀潧鐗嗛ˇ浼存偂濞戞埃鍋撻獮鍨姎闁哥噥鍋呮穱濠囨嚃閳哄啰锛滈梺鍛婃尫缁€浣圭瑜旈弻宥堫檨闁告挻鐟х划璇差吋婢跺﹦锛熼梻渚囧墮缁夋挳鎮块鈧弻锝呂熷▎鎯ф缂?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # System prompt should be preserved
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"

    # Should have a summary message
    assert any("濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙闁藉啰鍠栭弻鏇熺箾閻愵剚鐝﹂梺杞扮鐎氫即寮诲☉妯锋闁告鍋為悘宥呪攽閻愬弶鍣藉┑鐐╁亾闂佸搫鐭夌徊鍊熺亽闂佸吋绁撮弲娑氱箔閿熺姵鈷戠紒瀣健椤庢绱掓径濠勭Ш鐎殿喛顕ч埥澶愬閻樻彃绁梻渚€娼ч…鍫ュ磿娴煎瓨鍤嬫い蹇撶墛閳锋垿鏌熼懖鈺佷粶闁逞屽墯椤ㄥ棛鎹㈠☉銏犵劦妞ゆ帒瀚悡? in m.get("content", "") for m in result)

    # Recent messages should be preserved (last 12 non-system messages = 6 pairs)
    assert len(result) <= 14  # system + summary + 12 recent


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    """The most recent messages should be kept intact."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(20):
        messages.append({"role": "user", "content": f"婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻锝夊閻樺啿鏆堥梺绋款儏椤戝懘鍩為幋锔藉亹闁圭粯甯楀▓顓烆渻?{i}"})
        messages.append({"role": "assistant", "content": f"闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€哥粻鏍煕椤愶絾绀€缁炬儳娼￠弻鐔煎箚閻楀牜妫勭紒鎯у⒔缁垳鎹㈠☉銏犵闁哄啠鍋撻柛?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇㈡晝閳ь剟鎮块鈧弻锝呂熷▎鎯ф闂佹眹鍊楅崑鎾舵崲濠靛洨绡€闁稿本纰嶉悘鏇㈡⒑閸忓吋绶叉繛纭风節瀵濡搁妷銏☆潔濠碘槅鍨拃锔界闁秵鈷戠紒瀣儥閸庢劙鏌熼悷鐗堝枠妤犵偛鍟撮幐濠冨緞閸℃浜栭梻浣告贡椤牏鈧稈鏅犲鎶芥倷閻戞ǚ鎷绘繛杈剧秮椤ユ挻绋夐懠顒傜＝闁稿本绋掗惃鎴︽煕閹烘挸绗掗柍璇查叄楠炴鎹勯搹骞垮亰濠电姴鐥夐弶搴撳亾閹版澘纾婚柟鍓х帛閹虫岸鏌ㄥ┑鍡橆棤缂佺娀绠栭弻娑㈠焺閸愵亝鍣ф繛瀛樼矒缁犳牠寮?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # Last message should be the most recent assistant reply
    assert result[-1]["content"] == "闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€哥粻鏍煕椤愶絾绀€缁炬儳娼￠弻鐔煎箚閻楀牜妫勭紒鎯у⒔缁垳鎹㈠☉銏犵闁哄啠鍋撻柛?19"
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: FAIL 闂?`ImportError: cannot import name 'compress_conversation_history'`

- [x] **Step 3: Add compress_conversation_history to context_compressor.py**

Append to `app/services/context_compressor.py`:

```python
from app.agent.llm_client import chat_completion as _chat_completion

_SUMMARIZE_PROMPT = """闂傚倸鍊搁崐宄懊归崶褏鏆﹂柛顭戝亝閸欏繘鏌℃径瀣婵炲樊浜堕弫鍥煃鐠虹儤鎯堟い锔炬暬閻涱喖螣閸忕厧鐝伴梺鍛婄懃椤﹂亶鍩€?-3闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫鎾绘偐閸愯弓鐢婚梻浣瑰缁诲倿藝椤栨粌顥氶柛褎顨嗛悡娆戠磽娴ｉ潧鐏╅柡瀣枛閺屾稒鎯旈埥鍛紣闂傚洤顦甸弻锝呂熼悜妯锋灆闂佺楠哥换鎺旀閹烘鍋愰柛鎰皺娴煎矂姊洪崫鍕潶闁稿﹥鐗犻獮鍫ュΩ閳轰胶鐤€濡炪倖鍨煎Λ鍕閻愵兛绻嗛柕鍫濆€告禍楣冩⒑瀹曞洨甯涙俊顐㈠暞閹便劑鍩€椤掑嫭鐓熸俊顖滃劋椤ユ粎绱撳鍜冭含妤犵偛鍟撮崺锟犲椽娴ｈ娅撻梻浣虹帛閹稿憡顨ラ幖渚婄稏闁圭儤姊荤壕浠嬫煕鐏炲墽鎳呴柛鏂跨У閵囧嫰濡搁妷锕€娈楀Δ鐘靛仜閿曨亪鐛崶顒€绾ч悹鎭掑妼婵附淇婇悙顏勨偓鏍暜閹烘纾圭憸鐗堝笒濮规煡鏌嶉崫鍕偓鑸电濠婂牊鐓忛煫鍥ㄦ礀椤庢捇妫呴澶婂⒋闁哄瞼鍠栭、娑樷枎閹存繂顬夌紓鍌欑閸婂湱鏁悙鍝勭劦妞ゆ帒锕︾粔闈浢瑰鍛槐閽樻繈鏌曟繛鐐珕闁抽攱鍨块弻娑樷槈濮楀牊顣肩紓浣哥埣娴滃爼寮诲☉妯锋瀻闊洦绋戝浼存倵鐟欏嫭澶勯柛銊ㄦ硾閻ｇ兘宕奸弴銊︽櫌婵炶揪绲介幖顐ゆ暜妤ｅ啯鈷掑ù锝堟閵嗗﹪鏌涢幘瀵哥疄闁靛棗鍟村畷銊╁级閹寸姴濮︽俊鐐€栧濠氬磻閹惧绠鹃悘蹇旂墤閸嬫挸鐣烽崶銊︻啎闂備浇顫夐崕鐓幬涢崟顓犱笉闁荤喐鍣磋ぐ鎺撴櫜闁搞儯鍔屽▓宀勬⒑闁偛鑻晶浼存煕韫囨枂顏堬綖韫囨拋娲敂瀹ュ棙娅囬梻浣瑰缁诲倸煤閵忋倕鐒垫い鎺嶇缁椦呯磼鏉堛劌娴柟顔规櫆濞煎繘鍩￠崘顏勫箚闂傚倷绀侀幖顐︽儗婢跺瞼绀婂〒姘ｅ亾鐎殿噮鍋婇獮鍥级閸喛鈧灝鈹戦悙鍙夘棡闁告梹娲栭埢鎾圭疀閺囩姷锛濋梺绋挎湰閻熝囁囬敂鐐枑闁哄顑欏Ο鈧悗瑙勬穿缁绘繈鐛惔銊﹀癄濠㈣泛鐬奸弳顐⑩攽閻愬樊鍤熷┑顔芥尦椤㈡牠宕ㄩ鐓庡闂傚倸鍊烽悞锔锯偓绗涘厾鍝勵吋婢跺﹦锛涢梺鐟板⒔缁垶鎮￠悢鍏肩厵闁诡垎鍛喖缂備讲鍋撻悗锝庡枟閻撴盯鎮橀悙鎻掆挃闁靛棙甯￠弻宥堫檨闁告挶鍔庣槐鐐哄幢濞戞锛涢梺绯曞墲缁嬫帡宕戦崒娑栦簻闁哄秲鍔庨惌宀€鐥幆褋鍋㈤柡灞炬礃缁绘盯宕归鍙ユ偅濠电姭鎷冮崱妤冩缂備浇椴哥敮鈥崇暦閹烘垟妲堟俊顖涙閻т線姊绘担铏广€婇柡鍌欑窔瀹曟垿骞橀幇浣瑰瘜闂侀潧鐗嗗Λ妤冪箔閸岀偞鐓犻柛鎰皺閸╋綁鏌涢埞鍨伈鐎殿喗鎸虫慨鈧柨娑樺楠炲牊淇婇悙顏勨偓鏍礉閹达箑纾归柡鍥ュ灩閸戠娀鏌熸潏楣冩闁绘挻鐟﹂妵鍕冀閵娧佲偓鎺楁煙閸愭彃鏆ｆ俊顐＄劍瀵板嫰骞囬鐘插汲婵犵數濞€濞佳兾涘▎鎾嶅顭ㄩ崟顓狀啎闂佸壊鍋侀崹褰掑煝閸儲鐓涢悘鐐垫櫕鍟稿銇卞倻绐旈柡灞剧缁犳盯寮崒娑樺灡闂備胶顢婂▍鏇€冩繝鍌滄殾濠靛倻顭堥崡鎶芥煟閹邦剙鎮佺紒杈ㄧ矋缁绘繄鍠婂Ο娲绘綉闂佹悶鍔嬮崡鍐茬暦閵壯€鍋撻敐搴′簻闁搞劍鏌ㄩ埞鎴﹀磼濮橆厼鏆堥梺缁樻尭缁绘﹢寮诲☉銏╂晝闁挎繂娲ㄩ悾闈涱渻閵堝懏绂嬮柛瀣躬瀵鈽夐姀鈥充簻闂佸憡鍨崐鏇熷閹扮増鈷掗柛銉戝本鈻堥梺鍝勭焿缁蹭粙锝炲鍫濆耿婵＄偛澧介惄搴♀攽閻愯尙鎽犵紒顔奸叄瀹曟垿骞橀懜闈涘簥濠电偞鍨崹鍦不閿濆鐓熼柟閭﹀墻閸ょ喖鏌涘▎蹇旑棦婵﹨娅ｇ槐鎺戭潨閸℃鏆ラ梺璇插閻噣宕￠崘鑼殾婵炲樊浜滈悞鍨亜閹哄秹妾峰ù婊勭矒閺岀喓鈧數顭堟禒婊勩亜閺囩喓鐭岀紒杈ㄥ笚閹峰懎鐣￠弶璺ㄣ偖闂備礁鎼張顒€煤閻旈鏆﹂柛妤冨€ｉ弮鍫濈劦妞ゆ帒瀚Ч鏌ユ煟閹邦剦鍤熺紒鐘荤畺閺岋綁骞橀搹顐ｅ闯缂備胶濮惧畷鐢稿焵椤掑喚娼愭繛娴嬫櫇缁辩偞鎷呴柅娑氱畾闂佹眹鍊ら崹鐓幬ｆ繝姘拺闁告繂瀚崳鎶芥煛閸涱喚鐭岄柟骞垮灩閳藉顫濋敐鍛闂佹眹鍨洪鏍倿閸撗勫仏闁靛鏅滈埛鎴犵磼鐎ｎ偒鍎ラ柛搴㈠姍閺岀喖宕ㄦ繝鍐ㄢ偓鎰版煕閳瑰灝鍔滅€垫澘瀚伴獮鍥敆娓氬洦顥ら梻浣藉吹婵灚绂嶆禒瀣鐎光偓閸曗斁鍋撻崒鐐村€绘俊顖濆亹椤旀洟鏌ｆ惔銏⑩姇妞ゎ厼娲幆灞剧節閸ャ劎鍘甸柣鐘叉厂閸涱垽绱电紓鍌氬€搁崐褰掑箲閸ヮ剙绠犻柣鎰惈鍞梺鎸庢磵閸嬫挾鈧鍠栧鈥愁潖閾忚鍏滈柛娑卞幘閸旂兘姊洪崨濠冪叆闁哄牜鍓涚划?""


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
        summary = response.get("content", "闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔告綇妤ｅ啯顎嶉梺绋款儏椤戝懘鍩為幋锔藉亹闂婎偒鍙€閹舵鈹戦悙鏉戠仧闁糕晛瀚板顐﹀炊椤掍胶鍘棅顐㈡处濞叉牕鐡梻浣虹帛缁诲啴鏁冮姀鐙€娼栭柧蹇撴贡绾惧吋淇婇婵嗗惞闁告瑥妫楅—鍐Χ閸愩劌顬堥梻浣稿簻缁蹭粙鎮鹃悜鑺ュ仺闁告稑锕ゆ禍鍦磽閸屾瑧鍔嶉柨姘归悪鈧崹璺侯潖濞差亜绠归柣鎰絻婵矂姊洪崨濠冪叆婵炴挳顥撻崚鎺撶節濮橆剙鍞ㄥ銈嗘尵閸犳捇宕㈤悽鍛娾拺闁革富鍘剧敮娑㈡偨椤栨粌浠遍柡浣哥Т椤撳吋寰勭€ｎ剙骞嶉梻浣藉亹閳峰牓宕滃▎鎾扁偓鍌涚附閸涘﹦鍘甸悗鐟板婢ф宕抽悜妯镐簻闁挎梹鍎抽。濂告煙椤栨稒顥堥柡浣瑰姍瀹曞崬螖娴ｈ桨绨梻鍌氬€搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫鎾绘偐閸愯弓鐢绘俊鐐€栭悧婊堝磻濞戙垹鍨傞柛宀€鍋為悡娆撴煙椤栨粌顣兼い銉ヮ樀閺岋紕鈧絺鏅濈粣鏃堟煛鐏炵偓绀嬬€规洜鍘ч埞鎴﹀箛椤撳／鍥ㄢ拺?)
    except Exception:
        summary = "闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏃堟暜閸嬫挾绮☉妯诲櫧闁活厽鐟╅弻鐔告綇妤ｅ啯顎嶉梺绋款儏椤戝懘鍩為幋锔藉亹闂婎偒鍙€閹舵鈹戦悙鏉戠仧闁糕晛瀚板顐﹀炊椤掍胶鍘棅顐㈡处濞叉牕鐡梻浣虹帛缁诲啴鏁冮姀鐙€娼栭柧蹇撴贡绾惧吋淇婇婵嗗惞闁告瑥妫楅—鍐Χ閸愩劌顬堥梻浣稿簻缁蹭粙鎮鹃悜鑺ュ仺闁告稑锕ゆ禍鍦磽閸屾瑧鍔嶉柨姘归悪鈧崹璺侯潖濞差亜绠归柣鎰絻婵矂姊洪崨濠冪叆婵炴挳顥撻崚鎺撶節濮橆剙鍞ㄥ銈嗘尵閸犳捇宕㈤悽鍛娾拺闁革富鍘剧敮娑㈡偨椤栨粌浠遍柡浣哥Т椤撳吋寰勭€ｎ剙骞嶉梻浣藉亹閳峰牓宕滃▎鎾扁偓鍌涚附閸涘﹦鍘甸悗鐟板婢ф宕甸崶顒佺厵妞ゆ梻鏅惌濠囨懚閿濆洨纾藉ù锝囨娓氭稑霉閻樻瑥娲﹂埛鎺楁煕鐏炲墽鎳嗛柛蹇撶焸閺岀喖鎼归锝呯３闂佽鍠楀鑺ヤ繆閹间礁鐓涘ù锝勮濡茬兘姊绘担鍛婃儓婵炲眰鍨藉畷鍦喆閸曞灚鏁梻鍌氬€烽懗鍫曞箠閹炬椿鏁嬫い鎾跺枑閸欏繘鏌ｉ姀銏╂毌闁稿鎸搁～婵嬵敆婢跺苯鎮戦梻浣告惈閺堫剙煤濡警鍤楅柛鏇ㄥ€犻悢鍏兼優闂侇偅绋戠€佃尙绱撻崒姘偓椋庢媼閺屻儱纾?

    summary_msg = {
        "role": "user",
        "content": f"[濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙闁藉啰鍠栭弻鏇熺箾閻愵剚鐝﹂梺杞扮鐎氫即寮诲☉妯锋闁告鍋為悘宥呪攽閻愬弶鍣藉┑鐐╁亾闂佸搫鐭夌徊鍊熺亽闂佸吋绁撮弲娑氱箔閿熺姵鈷戠紒瀣健椤庢绱掓径濠勭Ш鐎殿喛顕ч埥澶愬閻樻彃绁梻渚€娼ч…鍫ュ磿娴煎瓨鍤嬫い蹇撶墛閳锋垿鏌熼懖鈺佷粶闁逞屽墯椤ㄥ棛鎹㈠☉銏犵劦妞ゆ帒瀚悡娆愩亜閺冨洤浜圭紒澶庢閳ь剝顫夊ú鏍偉閸忛棿绻嗘慨婵嗙焾濡查箖姊烘导娆戠ɑ婵＄偠妫勯～蹇涙惞鐟欏嫬鏋傞梺鍛婃处閸嬪棛绮婃搴ｇ＜闁告挆鍡橆€楅梺鍛婄懃閸熸挳鎮伴钘夌窞闁归偊鍘兼禍閬嶆⒑閸撴彃浜愰柟鍐叉喘瀵?{summary}",
    }

    return system_msgs + [summary_msg] + recent_msgs
```

- [x] **Step 4: Run tests to verify they pass**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: All 3 tests PASS

- [x] **Step 5: Integrate into agent loop**

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

- [x] **Step 6: Run all tests**

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
- [ ] Plan 4: Memory + 濠电姷鏁告慨鐑藉极閹间礁纾婚柣鎰惈閸ㄥ倿鏌涢锝嗙缂佺姳鍗抽弻鐔兼⒒鐎电濡介梺鍝勬噺缁诲牓寮婚妸銉㈡斀闁糕剝锚缁愭稓绱撴担鍝勑ｆ俊顐㈠暣瀵鈽夊Ο閿嬵潔濠电偛妫欓崝妤冪矙閸パ€鏀介柍钘夋娴滄繈鏌ㄩ弴妯虹伈鐎殿喛顕ч埥澶愬閻樻牓鍔戦弻鏇＄疀婵犲倸鈷夐梺缁樼箰缁犳挸顫忓ú顏勫窛濠电姴鍊婚崝浼存⒑缁嬫鍎愰柟鐟版搐椤繒绱掑Ο璇差€撻梺鑺ッˇ顖炲箚閻愮儤鈷戠紒瀣儥閸庢劗绱掔€ｎ偄鐏遍柣蹇擃儔閺岋絾鎯旈妸锔介敪闂佺顕滅换婵嬫晲?0 濠?task闂?```

Update "闂傚倸鍊峰ù鍥х暦閻㈢绐楅柟閭﹀枛閸ㄦ繈骞栧ǎ顒€鐏繛鍛У娣囧﹪濡堕崨顔兼缂備胶濮抽崡鎶藉蓟濞戞ǚ妲堟慨妤€鐗婇弫鎯р攽閻愬弶鍣藉┑鐐╁亾闂佸搫鐭夌徊鍊熺亽闂佺粯鍨惰彜闁哄鐟ラ埞鎴︽倷閻戞﹫绱甸梺鍛婎殕婵炲﹤顕ｆ繝姘╅柕澶堝灪閺傗偓闂備胶纭堕崜婵嬫晪濠电偛鎳岄崐婵嗩潖缂佹绡€閹肩补鈧枼鎷婚梻浣告啞閹搁箖宕伴弽褜鍤曞┑鐘崇閸嬪嫰鏌ц箛鎾磋础闁伙綀娉涢埞鎴︽倷閺夋垹浠搁柦鍐憾閺屻劌鈽夊Ο澶寡囨煛瀹€瀣瘈闁糕斁鍋? to reflect Plan 4 completion.

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with Plan 4 completion status"
```
