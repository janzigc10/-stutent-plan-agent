# Plan 4: Memory 缂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾剧懓顪冪€ｎ亜顒㈡い鎰矙閺屻劑鎮㈤崫鍕戙垽鏌涢妸銉モ偓鍨潖婵犳艾閱囬柣鏃€浜介埀顒佸浮閺岋繝宕遍鐘垫殼闂佸搫鐭夌紞浣规叏閳ь剟鏌曢崼婵囶棡闂佹鍙冨?+ 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢鍏尖拻閻庣數顭堟俊浠嬫⒑閸濆嫭鍣虹紒璇茬墦瀵濡搁妷銏℃杸闂佺硶鍓濋敋缂佹劖绋撶槐鎾存媴閸濆嫅锝嗕繆椤愩垹鏆ｇ€殿喛顕ч埥澶娢熼柨瀣垫綌婵犵數鍋涘Λ娆撳礉濡ゅ啰鐭欓柛銉戔偓閺€浠嬫煃閽樺顥滃ù婊勭箞閺屻劑寮村Ο铏逛紙閻庢鍠涢褔鍩ユ径鎰潊闁绘ɑ鐗撻崝鎴﹀蓟閺囷紕鐤€濠电姴鍊搁埛澶愭⒑缂佹绠扮紒鐘虫尭椤繐煤椤忓嫬绐涙繝鐢靛Т閸婂宕濇导瀛樷拺缂佸顑欓崕鎰版煙閻熺増鎼愭い?
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer memory system (working/short-term/long-term) and context window management to keep conversations coherent across sessions without blowing up the context window.

**Architecture:** Memory CRUD service handles persistence. Two new agent tools (`recall_memory`, `save_memory`) give the LLM on-demand access. Tool result compression summarizes verbose outputs inline. Session lifecycle hooks generate summaries and extract memories at session end. The system prompt builder loads hot/warm memories at session start.

**Tech Stack:** SQLAlchemy async (existing), OpenAI-compatible LLM for summarization, existing agent tool system

**Depends on:** Plan 1 (Memory, SessionSummary, ConversationMessage models), Plan 2 (agent loop, tool_executor, llm_client)

---

## File Structure

```
student-planner/
闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?app/
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?services/
闂?  闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?memory_service.py          # Memory CRUD: create, query, update, delete, staleness
闂?  闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇闁糕晜鐗犲畷婵嬪即閵忊€崇彅闂佺粯鏌ㄩ崥瀣偂閵夆晜鐓熼柡鍌涘閹牏鈧稒绻勭槐鎾诲磼濞嗘帩鍞归梺鍝勬噽婵炩偓鐎殿喖顭峰鎾晬閸曨厽婢戦梺璇插嚱缂嶅棙绂嶉弽顓炵；闁规崘顕ч崡鎶芥煏韫囧ň鍋撻崗鍛殫濠电姵顔栭崰妤呭Φ濞戙垹纾婚柟鍓х帛閻?context_compressor.py      # Tool result summarization + conversation compression
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?agent/
闂?  闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?tools.py                   # (modify: add recall_memory, save_memory definitions)
闂?  闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?tool_executor.py           # (modify: add recall_memory, save_memory handlers)
闂?  闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?loop.py                    # (modify: add tool result compression after each tool call)
闂?  闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?context.py                 # (modify: add hot/warm memory loading)
闂?  闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇闁糕晜鐗犲畷婵嬪即閵忊€崇彅闂佺粯鏌ㄩ崥瀣偂閵夆晜鐓熼柡鍌涘閹牏鈧稒绻勭槐鎾诲磼濞嗘帩鍞归梺鍝勬噽婵炩偓鐎殿喖顭峰鎾晬閸曨厽婢戦梺璇插嚱缂嶅棙绂嶉弽顓炵；闁规崘顕ч崡鎶芥煏韫囧ň鍋撻崗鍛殫濠电姵顔栭崰妤呭Φ濞戙垹纾婚柟鍓х帛閻?session_lifecycle.py       # Session end: generate summary + extract memories
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?routers/
闂?  闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇闁糕晜鐗犲畷婵嬪即閵忊€崇彅闂佺粯鏌ㄩ崥瀣偂閵夆晜鐓熼柡鍌涘閹牏鈧稒绻勭槐鎾诲磼濞嗘帩鍞归梺鍝勬噽婵炩偓鐎殿喖顭峰鎾晬閸曨厽婢戦梺璇插嚱缂嶅棙绂嶉弽顓炵；闁规崘顕ч崡鎶芥煏韫囧ň鍋撻崗鍛殫濠电姵顔栭崰妤呭Φ濞戙垹纾婚柟鍓х帛閻?chat.py                    # (modify: call session lifecycle on disconnect/timeout)
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇闁糕晜鐗犲畷婵嬪即閵忊€崇彅闂佺粯鏌ㄩ崥瀣偂閵夆晜鐓熼柡鍌涘閹牏鈧稒绻勭槐鎾诲磼濞嗘帩鍞归梺鍝勬噽婵炩偓鐎殿喖顭峰鎾晬閸曨厽婢戦梺璇插嚱缂嶅棙绂嶉弽顓炵；闁规崘顕ч崡鎶芥煏韫囧ň鍋撻崗鍛殫濠电姵顔栭崰妤呭Φ濞戙垹纾婚柟鍓х帛閻?config.py                      # (modify: add context window thresholds)
闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?tests/
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?test_memory_service.py         # Memory CRUD unit tests
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?test_context_compressor.py     # Compression logic tests
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?test_memory_tools.py           # recall_memory / save_memory tool tests
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇婵炲鐩、鏍炊椤掍礁浠ч梺鍓插亝濞叉﹢鎮″☉銏＄厱闁靛绲介崝姘舵煟韫囧﹥娅囩紒杈ㄦ尰閹峰懘宕ｆ径瀣綃闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喖顫呴柍銉ュ帠缁ㄥ灚绻濆▓鍨灍闁靛洦鐩畷鎴﹀箻缂佹鍘?test_session_lifecycle.py      # Session end flow tests
闂?  闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕闂佽鍠栧鈥崇暦閸洦鏁嗗┑鐘插閳笺倕鈹戦悩顔肩伇闁糕晜鐗犲畷婵嬪即閵忊€崇彅闂佺粯鏌ㄩ崥瀣偂閵夆晜鐓熼柡鍌涘閹牏鈧稒绻勭槐鎾诲磼濞嗘帩鍞归梺鍝勬噽婵炩偓鐎殿喖顭峰鎾晬閸曨厽婢戦梺璇插嚱缂嶅棙绂嶉弽顓炵；闁规崘顕ч崡鎶芥煏韫囧ň鍋撻崗鍛殫濠电姵顔栭崰妤呭Φ濞戙垹纾婚柟鍓х帛閻?test_context_loading.py        # Hot/warm memory in system prompt tests
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
            content="闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銏㈢＝闁稿本鐟х拹浼存煕鐎ｎ亜顏紒顔芥閵囨劙骞掗幋锝嗘啺闁诲骸绠嶉崕鍗灻洪敃鍌氱；婵せ鍋撻柡灞界Ч婵＄兘濡烽妷銉ь儓濠电姰鍨奸～澶娒哄鍛潟闁规崘顕х壕鍏肩箾閸℃ê鐏ュ┑陇妫勯—鍐Χ閸愩劌顬堥梺纭呮珪閿氶柣锝囧厴楠炲洭鎮ч崼婵呯敾闂傚倷绶￠崣蹇曠不閹存績鏋旀い鎰堕檮閳锋垿鏌涘☉姗堟敾濠㈣泛瀚伴弻娑氣偓锝庡亜濞搭喚鈧娲忛崕鎶藉焵椤掑﹦绉甸柛鐘愁殜閹繝寮撮姀锛勫幐闂佹悶鍎崕杈ㄤ繆閸忕⒈娈介柣鎰懖閹寸偟鈹嶅┑鐘叉搐閻顭跨捄鐚村姛濞寸厧鑻埞鎴︻敊绾嘲濮涢梺绋跨昂閸婃洟鈥﹂崶顒夋晜闁割偅绻勯鐓庮渻閵堝棙鈷掗柛妯犲洠鈧牗寰勭€ｎ剛鐦堥梺姹囧灲濞佳嗏叿闂備焦鎮堕崝宥咁渻娴犲鏋侀柛鎰靛枛椤懘鏌曢崼婵嗘殜闁?,
            source_session_id="session-abc",
        )
        assert mem.id is not None
        assert mem.category == "preference"
        assert mem.content == "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銏㈢＝闁稿本鐟х拹浼存煕鐎ｎ亜顏紒顔芥閵囨劙骞掗幋锝嗘啺闁诲骸绠嶉崕鍗灻洪敃鍌氱；婵せ鍋撻柡灞界Ч婵＄兘濡烽妷銉ь儓濠电姰鍨奸～澶娒哄鍛潟闁规崘顕х壕鍏肩箾閸℃ê鐏ュ┑陇妫勯—鍐Χ閸愩劌顬堥梺纭呮珪閿氶柣锝囧厴楠炲洭鎮ч崼婵呯敾闂傚倷绶￠崣蹇曠不閹存績鏋旀い鎰堕檮閳锋垿鏌涘☉姗堟敾濠㈣泛瀚伴弻娑氣偓锝庡亜濞搭喚鈧娲忛崕鎶藉焵椤掑﹦绉甸柛鐘愁殜閹繝寮撮姀锛勫幐闂佹悶鍎崕杈ㄤ繆閸忕⒈娈介柣鎰懖閹寸偟鈹嶅┑鐘叉搐閻顭跨捄鐚村姛濞寸厧鑻埞鎴︻敊绾嘲濮涢梺绋跨昂閸婃洟鈥﹂崶顒夋晜闁割偅绻勯鐓庮渻閵堝棙鈷掗柛妯犲洠鈧牗寰勭€ｎ剛鐦堥梺姹囧灲濞佳嗏叿闂備焦鎮堕崝宥咁渻娴犲鏋侀柛鎰靛枛椤懘鏌曢崼婵嗘殜闁?
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

        await create_memory(db, "mem-user-2", "preference", "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹潡顢氶埀顒勫蓟閿濆憘鐔封枎閹勵唲闂備焦鐪归崐妤呭磻閹捐埖宕叉繛鎴欏灩楠炪垺淇婇婵囶仩濞寸姾鍋愮槐鎾存媴閸濆嫅锝嗕繆椤愩垹鏆ｇ€殿喛顕ч埥澶婎潩椤愶絽濯伴梻浣告啞閹稿棝鍩€椤掆偓鍗遍柛顐犲灮绾捐棄霉閿濆浂鐒炬い锝嗗▕閺屾稓鈧綆鍓欓弸娑㈡煕閳规儳浜炬俊鐐€栧濠氬磻閹惧墎纾奸柣妯垮皺鏁堥悗瑙勬礃濞叉ê顭囪箛娑樼厴闁诡垎鍌氼棜婵犳鍠楅…鍥储瑜嶉埢宥咁吋婢跺鍘靛銈嗙墬閻熝囧礉瀹ュ鐓欐い鏍ㄧ⊕椤ュ牆鈹戦埄鍐╁€愰柡浣稿€块獮鍡氼槻缂佺姷澧楃换婵嬫偨闂堟稐鍝楅梺瑙勬た娴滅偟妲愰悙鍝勭劦妞ゆ帊闄嶆禍婊勩亜閹扳晛鐒烘俊鑼劋缁绘盯宕遍幇顒備紙閻庤娲╃徊鎯ь嚗閸曨垰閱囨繝濠傛噽濞?)
        await create_memory(db, "mem-user-2", "habit", "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢铏圭＜闁靛繒濮甸悘鍫㈢磼閻愵剙鍔ゆい顓犲厴瀵鎮㈤悡搴ｇ暰閻熸粍绮撳畷鐢告偄閾忓湱锛滈梺缁橆焾瀹曠敻鎮惧ú顏呯厸閻忕偛澧藉ú鎾煕閵婏箑鍔ら柣锝囧厴瀹曞爼鍩℃繝鍌涙毆濠电姷鏁告慨顓㈠箯閸愵喖绀冮柕濞у洨宕滅紓鍌氬€烽懗鍓佸垝椤栫偞鍎庢い鏍仧瀹撲焦鎱ㄥ璇蹭壕闂佽鍠氶崗姗€鐛澶樻晩闁绘挸娴风槐浼存⒒?闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪箻楠炴垿濮€閵堝懐鐤€濡炪倖妫佸Λ鍕償婵犲洦鈷戠憸鐗堝笒娴滀即鏌涢悩鎰佹當闁伙絿鍏樺濠氬Ψ閿旀儳骞嶉梺璇插缁嬫帡鈥﹂崶鈺冧笉闁靛濡囩粻?)
        await create_memory(db, "mem-user-2", "decision", "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋婵嗘暏婵＄偑鍊栭幐楣冨磻閻斿吋鍋╅柣鎴烆焽缁犻箖鎮楅悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁瑰啿绻樺畷鏇㈩敃閿旇В鎷绘繛鎾村焹閸嬫挻绻涙担鍐叉硽閸ヮ剦鏁囬柕蹇曞Х閿涚喖姊虹憴鍕姸婵☆偄瀚伴幃鐐哄垂椤愮姳绨婚梺鍦劋閸ㄧ敻寮冲▎鎾寸厱婵﹩鍓氱拹锛勭磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽敃浣烘闂佽瀛╅鏍闯椤曗偓瀹曟娊鏁愰崨顖涙闂佸湱鍎ら崵鈺呭箳閹存梹鐎婚梺璇″瀻閸愮偓浜ら梻鍌欑閻ゅ洭锝炴径鎰瀭闁秆勵殔閺勩儵鏌曟径鍡樻珔妤犵偑鍨烘穱濠囧Χ閸屾矮澹曠紓鍌欒兌婵儳鐣烽悽鍨潟闁规儳顕悷褰掓煕閵夋垵瀚禍楣冩⒒娴ｈ姤銆冩繛鏉戞喘椤㈡俺顦规い銏″哺閺佹劙宕卞▎妯荤カ闂佽鍑界徊浠嬫倶濮樿泛鐤炬繝闈涱儐閳锋垿鏌熺粙鎸庢崳缂佺姵鎸绘穱濠囶敃椤愩垹绫嶉悗?)

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
        await create_memory(db, "mem-user-3", "decision", "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋婵嗘暏婵＄偑鍊栭幐楣冨磻閻斿吋鍋╅柣鎴烆焽缁犻箖鎮楅悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁瑰啿绻樺畷鏇㈩敃閿旇В鎷绘繛鎾村焹閸嬫挻绻涙担鍐叉硽閸ヮ剦鏁囬柕蹇曞Х閿涚喖姊虹憴鍕姸婵☆偄瀚伴幃鐐哄垂椤愮姳绨婚梺鍦劋閸ㄧ敻寮冲▎鎾寸厱婵﹩鍓氱拹锛勭磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽敃浣烘闂佽瀛╅鏍闯椤曗偓瀹曟娊鏁愰崨顖涙闂佸湱鍎ら崵鈺呭箳閹存梹鐎婚梺璇″瀻閸愮偓浜ら梻鍌欑閻ゅ洭锝炴径鎰瀭闁秆勵殔閺勩儵鏌曟径鍡樻珔妤犵偑鍨烘穱濠囧Χ閸屾矮澹曠紓鍌欒兌婵儳鐣烽悽鍨潟闁规儳顕悷褰掓煕閵夋垵瀚禍楣冩⒒娴ｈ姤銆冩繛鏉戞喘椤㈡俺顦规い銏″哺閺佹劙宕卞▎妯荤カ闂佽鍑界徊浠嬫倶濮樿泛鐤炬繝闈涱儐閳锋垿鏌熺粙鎸庢崳缂佺姵鎸绘穱濠囶敃椤愩垹绫嶉悗?)

        # Old memory (simulate 30 days ago)
        old_mem = Memory(
            user_id="mem-user-3",
            category="decision",
            content="缂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌ｉ幋锝呅撻柛濠傛健閺屻劑寮撮悙娴嬪亾閸濄儱顥氶柛褎顨嗛悡娆撴煙椤栨粌顣兼い銉ヮ槸椤╁ジ宕ㄩ娑欐杸濡炪倖鏌ㄩ～鏇熺濠婂牊鐓曢悗锝庡亝鐏忕敻鏌嶈閸撴繈锝炴径濞掓椽鏁冮崒姘鳖槶闂佺粯姊婚鏇㈠焵椤戣法顦﹂摶鏍煕濞戝崬骞樻い锔芥緲椤啴濡堕崱妤€娼戦梺绋款儐閹告悂婀侀梺缁橆焾濞呮洟濡靛┑鍥ㄥ弿濠电姴鍟妵婵囦繆椤愩垹鏆欓柍钘夘槹濞煎繘鍩℃担鎰燁亪姊婚崒娆掑厡妞ゎ厼鐗撻弻濠囨晲閸℃瑯娲搁梺鍓插亝濞叉牜绮婚弽顓熺叆闁绘柨鎼瓭闂佸憡顨嗘繛濠囧蓟閿濆绠涙い鎺戝€愰敐澶嬬厽闁冲搫锕ら悘锔筋殽閻愭彃鏆㈡い锕€婀遍埀顒冾潐濞叉牠濡堕幖浣碘偓渚€寮撮姀鐘栄囨煕濞戝崬甯ㄩ柕濞炬櫆閳锋帡鏌涚仦鍓ф噮妞わ讣闄勯妵鍕箻閼碱剛鐓撻悗娈垮枛閻栫厧鐣疯ぐ鎺濇晩濠㈡儼顫夊ú鐔奉潖?,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.add(old_mem)
        await db.commit()

        warm = await get_warm_memories(db, "mem-user-3", days=7)
        assert len(warm) == 1
        assert warm[0].content == "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋婵嗘暏婵＄偑鍊栭幐楣冨磻閻斿吋鍋╅柣鎴烆焽缁犻箖鎮楅悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁瑰啿绻樺畷鏇㈩敃閿旇В鎷绘繛鎾村焹閸嬫挻绻涙担鍐叉硽閸ヮ剦鏁囬柕蹇曞Х閿涚喖姊虹憴鍕姸婵☆偄瀚伴幃鐐哄垂椤愮姳绨婚梺鍦劋閸ㄧ敻寮冲▎鎾寸厱婵﹩鍓氱拹锛勭磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽敃浣烘闂佽瀛╅鏍闯椤曗偓瀹曟娊鏁愰崨顖涙闂佸湱鍎ら崵鈺呭箳閹存梹鐎婚梺璇″瀻閸愮偓浜ら梻鍌欑閻ゅ洭锝炴径鎰瀭闁秆勵殔閺勩儵鏌曟径鍡樻珔妤犵偑鍨烘穱濠囧Χ閸屾矮澹曠紓鍌欒兌婵儳鐣烽悽鍨潟闁规儳顕悷褰掓煕閵夋垵瀚禍楣冩⒒娴ｈ姤銆冩繛鏉戞喘椤㈡俺顦规い銏″哺閺佹劙宕卞▎妯荤カ闂佽鍑界徊浠嬫倶濮樿泛鐤炬繝闈涱儐閳锋垿鏌熺粙鎸庢崳缂佺姵鎸绘穱濠囶敃椤愩垹绫嶉悗?


@pytest.mark.asyncio
async def test_recall_memories_keyword_search(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-4", username="memtest4", hashed_password="x")
        db.add(user)
        await db.commit()

        await create_memory(db, "mem-user-4", "decision", "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋婵嗘暏婵＄偑鍊栭幐楣冨磻閻斿吋鍋╅柣鎴烆焽缁犻箖鎮楅悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁瑰啿绻樺畷鏇㈩敃閿旇В鎷绘繛鎾村焹閸嬫挻绻涙担鍐叉硽閸ヮ剦鏁囬柕蹇曞Х閿涚喖姊虹憴鍕姸婵☆偄瀚伴幃鐐哄垂椤愮姳绨婚梺鍦劋閸ㄧ敻寮冲▎鎾寸厱婵﹩鍓氱拹锛勭磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽敃浣烘闂佽瀛╅鏍闯椤曗偓瀹曟娊鏁愰崨顖涙闂佸湱鍎ら崵鈺呭箳閹存梹鐎婚梺璇″瀻閸愮偓浜ら梻鍌欑閻ゅ洭锝炴径鎰瀭闁秆勵殔閺勩儵鏌曟径鍡樻珔妤犵偑鍨烘穱濠囧Χ閸屾矮澹曠紓鍌欒兌婵儳鐣烽悽鍨潟闁规儳顕悷褰掓煕閵夋垵瀚禍楣冩⒒娴ｈ姤銆冩繛鏉戞喘椤㈡俺顦规い銏″哺閺佹劙宕卞▎妯荤カ闂佽鍑界徊浠嬫倶濮樿泛鐤炬繝闈涱儐閳锋垿鏌熺粙鎸庢崳缂佺姵鎸绘穱濠囶敃椤愩垹绫嶉悗瑙勬磸閸庨潧鐣烽妸褉鍋撳☉娅辨岸骞忕紒妯肩閺夊牆澧介幃濂告煙閾忣偅宕屾い銏¤壘椤劑宕ㄩ婊愮床闂佽鍑界紞鍡涘磻閸曨垱鍊堕悗鐢电《閸嬫挸鈻撻崹顔界亾闂佽桨绀侀…鐑藉Υ娴ｈ倽鏃堝川椤撶媭妲规俊鐐€栭崝鎴﹀磹閺嶎厽鍋傞柨婵嗩槹閳锋帒銆掑锝呬壕濠电偘鍖犻崶浣告喘椤㈡洟鏁冮埀顒勬偪閻愵剛绠鹃柟瀛樼懃閻忊晝绱掗埀顒勫礋椤栨稓鍘藉┑鈽嗗灥濞咃綁鏁嶅鍥╃＜闁抽敮鍋撻柛瀣尭閳规垿鎮╅崹顐ｆ瘎闂佺顑囬崑銈呯暦閺囥垺鎯炴い鎰╁€ゅú鎼佹⒑閸涘﹥瀵欓柛娑卞灲缁卞啿鈹戦悙鑸靛涧缂傚秮鍋撳銈嗘礃閻楁洟鍩㈤幘璇茬睄闁逞屽墴婵＄敻宕熼娑欐珕闂佺粯鍔﹂崜姘掗崼銉﹀€?)
        await create_memory(db, "mem-user-4", "preference", "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銏㈢＝闁稿本鐟х拹浼存煕鐎ｎ亜顏紒顔芥閵囨劙骞掗幋锝嗘啺闁诲骸绠嶉崕鍗灻洪敃鍌氱；婵せ鍋撻柡灞界Ч婵＄兘濡烽妷銉ь儓濠电姰鍨奸～澶娒哄鍛潟闁规崘顕х壕鍏肩箾閸℃ê鐏ュ┑陇妫勯—鍐Χ閸愩劌顬堥梺纭呮珪閿氶柣锝囧厴楠炲洭鎮ч崼婵呯敾闂傚倷绶￠崣蹇曠不閹存績鏋旀い鎰堕檮閳锋垿鏌涘☉姗堟敾濠㈣泛瀚伴弻娑氣偓锝庡亜濞搭喚鈧娲忛崕鎶藉焵椤掑﹦绉甸柛鐘愁殜閹繝寮撮姀锛勫幐闂佹悶鍎崕杈ㄤ繆閸忕⒈娈介柣鎰懖閹寸偟鈹?)
        await create_memory(db, "mem-user-4", "knowledge", "濠电姷鏁告慨鐑藉极閸涘﹥鍙忛柣銏犲閺佸﹪鏌″搴″箹缂佹劖顨嗘穱濠囧Χ閸涱厽娈查梺鍝勬缁捇寮婚悢鍏煎€绘慨妤€妫欓悾鍓佺磼閻愵剙鍔ょ紓宥咃躬楠炲啳銇愰幒鎴犲€為悷婊冮叄閸┿垽寮撮姀锛勫幈闂佺粯妫冮弨閬嶅吹閸ヮ剚鐓涢悘鐐额嚙閳ь剚娲熷﹢渚€鏌ｆ惔顖滅У闁稿鎳橀幃鐢稿即閻旇櫣鐦堝┑鐐茬墕閻忔繈鎮橀悩缁樼厪闁割偆鍠愰崐鎰偓娈垮枛椤兘寮幇顓炵窞濠电姴瀚烽崥鍛存⒒娴ｈ櫣甯涢柛鏃€娲栬灋婵炲棙鎸搁崹鍌炴煕閹捐尪鍏岄柣顓烆樀閺岀喖鎮滃Ο铏瑰姼濠电偟顑曢崝鎴﹀蓟瀹ュ牜妾ㄩ梺鍛婃尰閻熲晠鏁?)

        results = await recall_memories(db, "mem-user-4", query="婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～?)
        assert len(results) >= 1
        assert any("婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～? in m.content for m in results)


@pytest.mark.asyncio
async def test_recall_updates_last_accessed(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        from app.models.user import User

        user = User(id="mem-user-5", username="memtest5", hashed_password="x")
        db.add(user)
        await db.commit()

        mem = await create_memory(db, "mem-user-5", "decision", "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋婵嗘暏婵＄偑鍊栭幐楣冨磻閻斿吋鍋╅柣鎴烆焽缁犻箖鎮楅悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁瑰啿绻樺畷鏇㈩敃閿旇В鎷绘繛鎾村焹閸嬫挻绻涙担鍐叉硽閸ヮ剦鏁囬柕蹇曞Х閿涚喖姊虹憴鍕姸婵☆偄瀚伴幃鐐哄垂椤愮姳绨婚梺鍦劋閸ㄧ敻寮冲▎鎾寸厱婵﹩鍓氱拹锛勭磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽敃浣烘闂佽瀛╅鏍闯椤曗偓瀹曟娊鏁愰崨顖涙闂佸湱鍎ら崵鈺呭箳閹存梹鐎婚梺璇″瀻閸愮偓浜ら梻鍌欑閻ゅ洭锝炴径鎰瀭闁秆勵殔閺勩儵鏌曟径鍡樻珔妤犵偑鍨烘穱濠囧Χ閸屾矮澹曠紓鍌欒兌婵儳鐣烽悽鍨潟闁规儳顕悷褰掓煕閵夋垵瀚禍楣冩⒒娴ｈ姤銆冩繛鏉戞喘椤㈡俺顦规い銏″哺閺佹劙宕卞▎妯荤カ闂佽鍑界徊浠嬫倶濮樿泛鐤炬繝闈涱儐閳锋垿鏌熺粙鎸庢崳缂佺姵鎸绘穱濠囶敃椤愩垹绫嶉悗?)
        original_accessed = mem.last_accessed

        # Small delay to ensure timestamp differs
        results = await recall_memories(db, "mem-user-5", query="婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～?)
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

        mem = await create_memory(db, "mem-user-6", "preference", "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹潡顢氶埀顒勫蓟閿濆憘鐔封枎閹勵唲闂備焦鐪归崐妤呭磻閹捐埖宕叉繛鎴欏灩楠炪垺淇婇婵囶仩濞寸姾鍋愮槐鎾存媴閸濆嫅锝嗕繆椤愩垹鏆ｇ€殿喛顕ч埥澶婎潩椤愶絽濯伴梻浣告啞閹稿棝鍩€椤掆偓鍗遍柛顐犲灮绾捐棄霉閿濆浂鐒炬い锝嗗▕閺屾稓鈧綆鍓欓弸娑㈡煕閳规儳浜炬俊鐐€栧濠氬磻閹惧墎纾奸柣妯垮皺鏁堥悗瑙勬礃濞叉ê顭囪箛娑樼厴闁诡垎鍌氼棜婵犳鍠楅…鍥储瑜嶉埢宥咁吋婢跺鍘?)
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

        mem = await create_memory(db, "mem-user-7", "preference", "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹潡顢氶埀顒勫蓟閿濆憘鐔封枎閹勵唲闂備焦鐪归崐妤呭磻閹捐埖宕叉繛鎴欏灩楠炪垺淇婇婵囶仩濞寸姾鍋愮槐鎾存媴閸濆嫅锝嗕繆椤愩垹鏆ｇ€殿喛顕ч埥澶婎潩椤愶絽濯伴梻浣告啞閹稿棝鍩€椤掆偓鍗遍柛顐犲灮绾捐棄霉閿濆浂鐒炬い锝嗗▕閺屾稓鈧綆鍓欓弸娑㈡煕閳规儳浜炬俊鐐€栧濠氬磻閹惧墎纾奸柣妯垮皺鏁堥悗瑙勬礃濞叉ê顭囪箛娑樼厴闁诡垎鍌氼棜婵犳鍠楅…鍥储瑜嶉埢宥咁吋婢跺鍘?)
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
            content="闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹虫粏銇愰幒鎾跺幐闁诲繒鍋犻褔宕濆鎵佸亾閻熺増鍟炵紒璇插暣婵＄敻宕熼姘辩潉闂佺鏈惌顔界珶閺囩偐鏀介柣鎰皺婢ф盯鏌熼鐓庘偓鎼侊綖韫囨洜纾兼俊顖濐嚙椤庢捇姊洪崨濠勨槈闁挎洏鍊濆鎶藉醇閵夛腹鎷洪梺鍛婄☉閿曘儵鍩涢幇顓犵闁告瑥顦遍惌瀣磼閺冨倸鏋涚€殿喗鎸虫慨鈧柍鍝勫€瑰▍宥夋⒒娓氣偓濞佳呮崲閸℃稑鐒垫い鎺嗗亾闁告ɑ鐗曞嵄?,
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
                "weekday": "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｅ煐閸旀牠宕愰悽鍛婄叆婵犻潧妫濋妤€顭胯婢瑰棛妲?,
                "free_periods": [
                    {"start": "08:00", "end": "10:00", "duration_minutes": 120},
                    {"start": "14:00", "end": "16:00", "duration_minutes": 120},
                ],
                "occupied": [
                    {"start": "10:00", "end": "12:00", "type": "course", "name": "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～?},
                ],
            },
            {
                "date": "2026-04-02",
                "weekday": "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｅ煐閸旀牠宕愰崼鏇熺厽闁归偊鍠楅弳鈺呮煕?,
                "free_periods": [
                    {"start": "09:00", "end": "11:00", "duration_minutes": 120},
                ],
                "occupied": [],
            },
        ],
        "summary": "2026-04-01 闂?2026-04-02 闂?3 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙钃熼柕澶涘閸樹粙姊鸿ぐ鎺戜喊闁告挻宀搁獮鍡涘醇閵夛妇鍘介梺瑙勫礃閹活亪鎳撻崸妤佺厸閻忕偟纭堕崑鎾诲箛娴ｅ憡鍊梺纭呭亹鐞涖儵鍩€椤掆偓绾绢參顢欓幋锔解拻濞达絿鎳撻埢鏇㈡煛閳ь剚娼忛埡鍌涙闂佽法鍠撴慨鎾嫅閻斿摜绠鹃柟瀵稿€戝璺哄嚑閹兼番鍔庨崣鎾绘煕閵夆晩妫戠紒瀣煼閺屽秶绱掑Ο璇茬３濠殿喖锕ュ钘夌暦椤愶箑唯闁靛鍊楅柦鐢电磽閸屾瑧璐伴柛鐘愁殜閹兘鍩℃笟鍥ф婵犵數濮甸懝鐐劔闂備線娼чˇ顓㈠垂濞差亷缍栫€广儱鎳夐弨浠嬫煃閽樺顥滈柣蹇ョ悼缁辨帡顢氶崨顓犱桓濡ょ姷鍋涚换姗€寮婚崱妤婂悑闁糕€崇箲鐎氬ジ姊婚崒娆戣窗闁稿妫濆畷鎴濃槈閵忊€虫濡炪倖鐗楃粙鎺戔枍閻樼偨浜滈柡宥冨妿閳笺儳绱掔拠鍙夘棦闁哄本绋戦埢搴ょ疀閿濆柊锕€鈹戦悙瀛樺剹闁哥姵顨婃俊?6 闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪箻楠炴垿濮€閵堝懐鐤€濡炪倖妫佸Λ鍕償婵犲洦鈷戠憸鐗堝笒娴滀即鏌涢悩鎰佹當闁伙絿鍏樺濠氬Ψ閿旀儳骞嶉梺璇插缁嬫帡鈥﹂崶鈺冧笉闁靛濡囩粻?0 闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎺嶇劍椤斿洭姊绘担鍛婅础闁稿簺鍊濆畷鐢告晝閳ь剟鍩ユ径濞㈢喖鏌ㄧ€ｎ偅婢戦梻浣筋嚙閸戠晫绱為崱妯碱洸闁绘劒璀﹂弫?,
    }
    compressed = compress_tool_result("get_free_slots", result)
    # Should use the existing summary field
    assert "3 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙钃熼柕澶涘閸樹粙姊鸿ぐ鎺戜喊闁告挻宀搁獮鍡涘醇閵夛妇鍘介梺瑙勫礃閹活亪鎳撻崸妤佺厸閻忕偟纭堕崑鎾诲箛娴ｅ憡鍊梺纭呭亹鐞涖儵鍩€椤掆偓绾绢參顢欓幋锔解拻濞达絿鎳撻埢鏇㈡煛閳ь剚娼忛埡鍌涙闂佽法鍠撴慨鎾嫅閻斿摜绠鹃柟瀵稿€戝璺哄嚑閹兼番鍔庨崣鎾绘煕閵夆晩妫戠紒瀣煼閺屽秶绱掑Ο璇茬３濠? in compressed
    assert "6 闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪箻楠炴垿濮€閵堝懐鐤€濡炪倖妫佸Λ鍕償婵犲洦鈷戠憸鐗堝笒娴滀即鏌涢悩鎰佹當闁伙絿鍏樺濠氬Ψ閿旀儳骞嶉梺璇插缁嬫帡鈥﹂崶鈺冧笉闁靛濡囩粻? in compressed
    # Should NOT contain the full slot details
    assert "free_periods" not in compressed


def test_compress_list_courses():
    result = {
        "courses": [
            {"id": "1", "name": "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～?, "teacher": "闂?, "weekday": 1, "start_time": "08:00", "end_time": "09:40"},
            {"id": "2", "name": "缂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌ｉ幋锝呅撻柛濠傛健閺屻劑寮撮悙娴嬪亾閸濄儱顥氶柛褎顨嗛悡娆撴煙椤栨粌顣兼い銉ヮ槸椤╁ジ宕ㄩ娑欐杸濡炪倖鏌ㄩ～鏇熺濠婂牊鐓曢悗锝庡亝鐏忕敻鏌?, "teacher": "闂?, "weekday": 3, "start_time": "10:00", "end_time": "11:40"},
            {"id": "3", "name": "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕閻庤娲忛崕鎶藉焵椤掑﹦绉甸柍褜鍓﹂崣蹇曠礊娓氣偓閻涱噣骞掑Δ鈧Λ姗€鏌涢…鎴濇灓濞存粍婢橀埞鎴炲箠闁稿ě鍛筏濞寸姴顑呯粣妤佹叏濡寧纭鹃柡?, "teacher": "闂?, "weekday": 2, "start_time": "08:00", "end_time": "09:40"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_courses", result)
    assert "3" in compressed
    assert "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～? in compressed


def test_compress_list_tasks():
    result = {
        "tasks": [
            {"id": "1", "title": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€块弻锝夊箻瀹曞洤鍝洪梺鍝勵儐閻楁鎹㈠☉銏犵闁绘劕顕▓銈夋⒑濞茶骞楅柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏閸繃顥為柛娆忕箲閵囧嫰骞掗幋婵愪痪闂佺粯鎸诲ú鐔煎蓟閿熺姴鐐婇柕澶堝劚椤牊绻濋埛鈧崨顖氱缂備胶绮惄顖氱暦婵傚憡鍋嗗ù锝呮贡閺嗭箑鈹戦悜鍥╁埌婵炲眰鍊濋弫鍐敂閸稈鍋撴担绯曟婵妫涢崣鍡涙⒑閸涘﹣绶遍柛姗€绠栭、鏇㈠礂閼测晝鐦堥梺姹囧灲濞佳勭濠婂牊鐓熸俊銈傚亾婵☆偅鐟╁鏌ユ嚋閸偄鍔呴梺鎸庣箓濡厼顭囬悢鍏尖拺闁革富鍘奸崝瀣煕閵堝繒鐣电€殿噮鍣ｉ崺鈧い鎺戝€瑰畷鍙夌節闂堟侗鍎忕痪鎯у悑閹便劌顫滈崱妤€顫銈嗘煥濞层劎妲愰幘璇茬＜婵﹩鍏橀崑鎾绘倻閼恒儱鈧潡鏌ㄩ弴鐐测偓鎼佹嫅閻斿吋鐓忓┑鐐靛亾濞呮捇鏌℃担鍓插剱闁靛洤瀚伴獮妯兼崉閻╂帇鍨介弻?, "status": "completed"},
            {"id": "2", "title": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€块弻锝夊箻瀹曞洤鍝洪梺鍝勵儐閻楁鎹㈠☉銏犵闁绘劕顕▓銈夋⒑濞茶骞楅柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏閸繃顥為柛娆忕箲閵囧嫰骞掗幋婵愪痪闂佺粯鎸诲ú鐔煎蓟閿熺姴鐐婇柕澶堝劚椤牊绻濋埛鈧崨顖氱缂備胶绮惄顖氱暦婵傚憡鍋嗗ù锝呮贡閺嗭箑鈹戦悜鍥╁埌婵炲眰鍊濋弫鍐敂閸稈鍋撴担绯曟婵妫涢崣鍡涙⒑閸涘﹣绶遍柛姗€绠栭、鏇㈠礂閼测晝鐦堥梺姹囧灲濞佳勭濠婂牊鐓熸俊銈傚亾婵☆偅鐟╁鏌ユ嚋閸偄鍔呴梺鎸庣箓濡厼顭囬悢鍏尖拺闁革富鍘奸崝瀣煕閵堝繒鐣电€殿噮鍣ｉ崺鈧い鎺戝€瑰畷鍙夌節闂堟侗鍎忕痪鎯у悑閹便劌顫滈崱妤€顫銈嗘煥濞层劎妲愰幘璇茬＜婵﹩鍏橀崑鎾绘倻閼恒儮鎸冮悗骞垮劚椤︻垳绮堟径濠庣唵闁兼悂娼ф慨鍥煟閵堝洤浜剧紒缁樼箞濡啫鈽夊顒夋毇闂?, "status": "pending"},
            {"id": "3", "title": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€块弻锝夊箻瀹曞洤鍝洪梺鍝勵儐閻楁鎹㈠☉銏犵闁绘劕顕▓銈夋⒑濞茶骞楅柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏閸繃顥為柛娆忕箲閵囧嫰骞掗幋婵愪痪闂佺粯鎸诲ú鐔煎蓟閿熺姴鐐婇柕澶堝劚椤牆螖閻橀潧浠﹂拑鍗炃庨崶褝韬い銏℃礋椤㈡洟濮€椤厼鎽嬪┑锛勫亼閸娿倝宕㈤悡搴劷闁炽儱纾弳锔界節婵犲倸顏柣鐔风秺閺屾盯濡烽姀鈩冪彅婵犳鍠栭妶绋款潖?, "status": "pending"},
        ],
        "count": 3,
    }
    compressed = compress_tool_result("list_tasks", result)
    assert "3" in compressed
    assert "1" in compressed  # completed count


def test_compress_create_study_plan():
    result = {
        "tasks": [
            {"title": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€块弻锝夊箻瀹曞洤鍝洪梺鍝勵儐閻楁鎹㈠☉銏犵闁绘劕顕▓銈夋⒑濞茶骞楅柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏閸繃顥為柛娆忕箲閵囧嫰骞掗幋婵愪痪闂佺粯鎸诲ú鐔煎蓟閿熺姴鐐婇柕澶堝劚椤牊绻濋埛鈧崨顖氱缂備胶绮惄顖氱暦婵傚憡鍋嗗ù锝呮贡閺嗭箑鈹戦悜鍥╁埌婵炲眰鍊濋弫鍐敂閸稈鍋撴担绯曟婵妫涢崣鍡涙⒑閸涘﹣绶遍柛姗€绠栭、鏇㈠礂閼测晝鐦堥梺姹囧灲濞佳勭濠婂牊鐓熸俊銈傚亾婵☆偅鐟╁鏌ユ嚋閸偄鍔呴梺鎸庣箓濡厼顭囬悢鍏尖拺闁革富鍘奸崝瀣煕閵堝繒鐣电€殿噮鍣ｉ崺鈧い鎺戝€瑰畷鍙夌節闂堟侗鍎忕痪鎯у悑閹便劌顫滈崱妤€顫銈嗘煥濞层劎妲愰幘璇茬＜婵﹩鍏橀崑鎾绘倻閼恒儱鈧潡鏌ㄩ弴鐐测偓鎼佹嫅閻斿吋鐓忓┑鐐靛亾濞呮捇鏌℃担鍓插剱闁靛洤瀚伴獮妯兼崉閻╂帇鍨介弻?, "date": "2026-04-01"},
            {"title": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€块弻锝夊箻瀹曞洤鍝洪梺鍝勵儐閻楁鎹㈠☉銏犵闁绘劕顕▓銈夋⒑濞茶骞楅柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏閸繃顥為柛娆忕箲閵囧嫰骞掗幋婵愪痪闂佺粯鎸诲ú鐔煎蓟閿熺姴鐐婇柕澶堝劚椤牊绻濋埛鈧崨顖氱缂備胶绮惄顖氱暦婵傚憡鍋嗗ù锝呮贡閺嗭箑鈹戦悜鍥╁埌婵炲眰鍊濋弫鍐敂閸稈鍋撴担绯曟婵妫涢崣鍡涙⒑閸涘﹣绶遍柛姗€绠栭、鏇㈠礂閼测晝鐦堥梺姹囧灲濞佳勭濠婂牊鐓熸俊銈傚亾婵☆偅鐟╁鏌ユ嚋閸偄鍔呴梺鎸庣箓濡厼顭囬悢鍏尖拺闁革富鍘奸崝瀣煕閵堝繒鐣电€殿噮鍣ｉ崺鈧い鎺戝€瑰畷鍙夌節闂堟侗鍎忕痪鎯у悑閹便劌顫滈崱妤€顫銈嗘煥濞层劎妲愰幘璇茬＜婵﹩鍏橀崑鎾绘倻閼恒儮鎸冮悗骞垮劚椤︻垳绮堟径濠庣唵闁兼悂娼ф慨鍥煟閵堝洤浜剧紒缁樼箞濡啫鈽夊顒夋毇闂?, "date": "2026-04-02"},
            {"title": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€块弻锝夊箻瀹曞洤鍝洪梺鍝勵儐閻楁鎹㈠☉銏犵闁绘劕顕▓銈夋⒑濞茶骞楅柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏閸繃顥為柛娆忕箲閵囧嫰骞掗幋婵愪痪闂佺粯鎸诲ú鐔煎蓟閿熺姴鐐婇柕澶堝劚椤牆螖閻橀潧浠﹂拑鍗炃庨崶褝韬い銏℃礋椤㈡洟濮€椤厼鎽嬪┑锛勫亼閸娿倝宕㈤悡搴劷闁炽儱纾弳锔界節婵犲倸顏柣鐔风秺閺屾盯濡烽姀鈩冪彅婵犳鍠栭妶绋款潖?, "date": "2026-04-03"},
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
        return f"[缂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾剧懓顪冪€ｎ亝鎹ｉ柣顓炴閵嗘帒顫濋敐鍛闁诲孩顔栭崰姘跺极婵犳哎鈧礁螖閸涱厾鍔﹀銈嗗笒鐎氀囧焵椤掍焦顥堢€规洘锕㈤、娆撴寠婢跺本顎嶆繝鐢靛О閸ㄥ綊宕㈠鍫濈柧婵犲﹤鎳愰惌娆撴煙閻戞ɑ鈷掗柣顓烆樀閺岀喖鎮滃Ο鑽ゅ幐闂佺顑嗛幑鍥极閹邦厽鍎熸繝闈涚墛閺呭ジ姊绘担瑙勩仧闁稿瀚埀顒佺濠㈡﹢锝炶箛鎾佹椽顢旈崨顓濈暗闂佺懓鍚嬮悾顏堝垂瑜版帒姹查柛顐ｇ箥濞撳鏌曢崼婵囶棡闁抽攱鍔欓弻锝呂旈崘銊愩垽鏌ｉ敐鍥у幋妞ゃ垺顨嗛幏鍛瑹椤栨稓銈梻浣筋嚙閸戠晫绱為崱娑樼；闁糕剝绋戦崒銊╂煙闂傚鍔嶉柣鎾跺枛閻擃偊宕堕妸锔绢槬婵炲濮弲婊堝Φ閸曨垰鍗抽柛鈩冾殕閹兼劗绱掗埀顒佸緞閹邦厾鍘繝銏ｅ煐缁嬫牜绮堢€ｎ€㈢懓顭ㄩ崟顓犵厜闂佸搫鐭夌换婵嗙暦閸洖鐓涘ù锝呮贡瑜版瑦绻濋悽闈涗粶闁绘锕垾锕傚炊閳哄偆娼熼梺鍦劋閹歌崵绱為崶顒佺厪濠电偛鐏濋崝婊堟偣閸モ晛浠滈摶鏍煟濮椻偓濞佳勭閿斿浜滄い鎾跺仦閸犳﹢鏌涢埞鎯т壕婵＄偑鍊栫敮鎺楀磹瑜版帒姹叉い鎺戝閻撴盯鏌涘☉鍗炴灓闁告瑢鍋撻柣搴ゎ潐濞叉﹢鎮疯椤?{summary}"
    slots = result.get("slots", [])
    total = sum(len(d.get("free_periods", [])) for d in slots)
    return f"[缂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾剧懓顪冪€ｎ亝鎹ｉ柣顓炴閵嗘帒顫濋敐鍛闁诲孩顔栭崰姘跺极婵犳哎鈧礁螖閸涱厾鍔﹀銈嗗笒鐎氀囧焵椤掍焦顥堢€规洘锕㈤、娆撴寠婢跺本顎嶆繝鐢靛О閸ㄥ綊宕㈠鍫濈柧婵犲﹤鎳愰惌娆撴煙閻戞ɑ鈷掗柣顓烆樀閺岀喖鎮滃Ο鑽ゅ幐闂佺顑嗛幑鍥极閹邦厽鍎熸繝闈涚墛閺呭ジ姊绘担瑙勩仧闁稿瀚埀顒佺濠㈡﹢锝炶箛鎾佹椽顢旈崨顓濈暗闂佺懓鍚嬮悾顏堝垂瑜版帒姹查柛顐ｇ箥濞撳鏌曢崼婵囶棡闁抽攱鍔欓弻锝呂旈崘銊愩垽鏌ｉ敐鍥у幋妞ゃ垺顨嗛幏鍛瑹椤栨稓銈梻浣筋嚙閸戠晫绱為崱娑樼；闁糕剝绋戦崒銊╂煙闂傚鍔嶉柣鎾跺枛閻擃偊宕堕妸锔绢槬婵炲濮弲婊堝Φ閸曨垰鍗抽柛鈩冾殕閹兼劗绱掗埀顒佸緞閹邦厾鍘繝銏ｅ煐缁嬫牜绮堢€ｎ€㈢懓顭ㄩ崟顓犵厜闂佸搫鐭夌换婵嗙暦閸洖鐓涘ù锝呮贡瑜版瑦绻濋悽闈涗粶闁绘锕垾锕傚炊閳哄偆娼熼梺鍦劋閹歌崵绱為崶顒佺厪濠电偛鐏濋崝婊堟偣閸モ晛浠滈摶鏍煟濮椻偓濞佳勭閿斿浜滄い鎾跺仦閸犳﹢鏌涢埞鎯т壕婵＄偑鍊栫敮鎺楀磹瑜版帒姹叉い鎺戝閻撴盯鏌涘☉鍗炴灓闁告瑢鍋撻柣搴ゎ潐濞叉﹢鎮疯椤?{len(slots)} 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€婚幉鎼佹偋閸繄鐟查梺绋匡工閻栧ジ寮诲☉銏╂晝闁绘ɑ褰冩慨搴ㄦ⒑濮瑰洤鈧宕戦幘璇参﹂柛鏇ㄥ枤閻も偓闂佸湱鍋撻幆灞轿涢垾鎰佹富闁靛牆楠告禍婵囩箾閸欏鐒介柟骞垮灩閳规垹鈧綆鍋掑Λ鍐ㄢ攽閻愭潙鐏ョ€规洦鍓熷畷婊堝箥椤斿墽锛濇繛杈剧稻瑜板啯绂?{total} 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙钃熼柕澶涘閸樹粙姊鸿ぐ鎺戜喊闁告挻宀搁獮鍡涘醇閵夛妇鍘介梺瑙勫礃閹活亪鎳撻崸妤佺厸閻忕偟纭堕崑鎾诲箛娴ｅ憡鍊梺纭呭亹鐞涖儵鍩€椤掆偓绾绢參顢欓幋锔解拻濞达絿鎳撻埢鏇㈡煛閳ь剚娼忛埡鍌涙闂佽法鍠撴慨鎾嫅閻斿摜绠鹃柟瀵稿€戝璺哄嚑閹兼番鍔庨崣鎾绘煕閵夆晩妫戠紒瀣煼閺屽秶绱掑Ο璇茬３濠?


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = [c["name"] for c in courses[:5]]
    names_str = "闂?.join(names)
    if count > 5:
        names_str += f" 缂?{count} 闂?
    return f"[闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煕椤垵浜濋柛娆忕箻閺屸剝寰勭€ｎ亝顔呭┑鐐叉▕娴滄粌娲块梻浣虹《閸撴繆鎽梺缁樼箞閺€杈╂崲濞戞埃鍋撻悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁硅櫕锕㈤獮鍐灳閺傘儲鏂€闂佺硶鈧磭绠查柡鍌楀亾闂傚倷鑳堕…鍫ュ嫉椤掑倸鍨濋柣妯肩帛閸婂潡鏌涢幘妤€鎳愰敍婊堟⒑闁偛鑻晶瀵糕偓瑙勬礀瀹曨剝鐏掗梺闈╁瘜閸橀箖鎮炬ィ鍐┾拻濞撴埃鍋撴繛浣冲洦鍋嬮柛鈩冪☉缁犵娀骞栭幖顓犲帥闁轰礁鍊块弻鏇熷緞閸℃ɑ鐝曢梺缁樻尭閸熶即骞夌粙娆剧叆闁割偅绻勯ˇ顓炩攽閻愬弶顥為柟绋挎憸婢?闂?{count} 闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌熼梻瀵割槮缁炬儳缍婇弻鐔兼⒒鐎靛壊妲紒鐐劤缂嶅﹪寮诲☉銏╂晝闁挎繂妫涢ˇ銉х磽娴ｆ彃浜炬繝銏ｅ煐閸旀宕ｉ幘缁樼厱闁靛绲芥俊铏圭磼閸洑鎲鹃柡灞稿墲閹峰懘宕滈幓鎺戝闂備礁鎼惉濂稿窗閺嶎厾宓侀柛鈩冪☉缁狙囨煕閻斿嘲鏆為柟鐟版喘瀵鏁撻悩鍙夈仢婵炶揪绲块…鍫ワ綖椤忓牊鈷戦梺顐ｇ〒閳规帡鏌涢弬璺ㄧ劯闁糕晝鍋ら獮瀣晝閳ь剟鏌嬮崶銊х瘈濠电姴鍊搁弳娆撴煟韫囧骸浼恗es_str}"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    pending = count - completed
    return f"[婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾剧粯绻涢幋娆忕労闁轰礁顑嗛妵鍕箻鐠虹儤鐎鹃梺鍛婄懃缁绘劘鐏冮梺鎸庣箓閹冲酣寮搁妶澶嬬厸濞达絽澹婇崕鎴︽煙閹绘帗鍟為柟顖涙婵℃悂濡疯閺変粙姊绘笟鈧褑澧濋梺鍝勬噺缁挸鐣烽幋锕€绀嬫い鏍ㄧ〒閸樹粙姊虹憴鍕婵炲懏娲熼獮鎴︽晲閸℃劒绨婚梺鎸庢椤曆勭濠婂牊鐓冮悷娆忓閻忥附顨ラ悙璇ц含闁哄本绋掔换婵嬪礃閳哄喚妲堕梻渚€鈧偛鑻晶顖炴煕濠靛棝鍙勭€规洘绻堥獮瀣晝閳ь剟寮伴妷鈺傜厓鐟滄粓宕滃璺何﹂柛鏇ㄥ灠缁犳娊鏌涢埄鍐︿沪濠㈣娲熷?闂?{count} 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙鐭楀璺虹灱椤旀洟姊虹化鏇炲⒉閽冮亶鎮樿箛锝呭箻缂佽鲸甯￠幃鈺佺暦閸パ冪哗闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喗鍋愰柣銏㈡暩閸旇泛鈹戦悩顔肩伇闁糕晜鐗犲畷婵嬪冀椤撶喎浜楅梺鍛婂姦閸犳鎮￠姀鈥茬箚妞ゆ牗鐟ㄩ鐔镐繆閹绘帞绉洪柡灞剧洴閺佹劙宕堕妸锔惧涧缂傚倷娴囨ご鍝ユ暜閿熺姴鏄ラ柍褜鍓氶妵鍕箳瀹ュ洤濡藉┑鐐叉噽婵炩偓闁哄本绋栭ˇ鍙夌箾閼测晩娈檖leted} 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙鐭楀璺虹灱閻﹀牊绻濋悽闈浶㈤柛濠勭帛閺呭爼寮撮悩鐢碉紲闂侀€炲苯澧寸€规洜鍠栭、娑樷槈濮橆剙姹插┑鐘垫暩閸嬬偤宕归崼鏇熸櫔婵＄偑鍊曠换鍫ュ磹濠靛钃熸繛鎴炲焹閸嬫捇鏁愭惔鈥茬凹閻庤娲栭惌鍌炲蓟閻旂⒈鏁婇柟顖嗗啫绠ｉ梻浣筋嚃閸燁偊宕惰閸炲爼姊虹紒妯烩拻妞ゎ厼鐗撻、鏃€瀵肩€涙ǚ鎷婚梺绋挎湰閻熝囧礉瀹ュ鐓欐い鏃囧亹閸╋絿鈧娲樼换鍌烆敇婵傜宸濇い鏍ㄧ⊕閻ｇ兘姊绘担鍝ョШ婵☆偉娉曠划鍫熺瑹閳ь剙顕ｉ崨濠冨閻炴稈鈧厖澹曞Δ鐘靛仜閻忔繈宕濆顓犵闁肩⒈鍓欓埢鍫⑩偓瑙勬礃閸ㄥ潡鐛Ο鑲╃＜婵妫欓ˉ鍫熺節閻㈤潧浠﹂柛銊ョ埣閹虫繃銈ｉ崘鈺冨帒闂侀潻绲洪崑鎼塪ing} 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙鐭楀璺虹灱閻﹀牊绻濋悽闈浶㈤柛濠傜秺瀹曟娊鎮滃Ο闀愮盎闂佸綊鍋婃禍鐐烘儗濞嗘挻鐓涚€光偓鐎ｎ剛袦閻庢鍣崳锝呯暦閸洖唯闁靛繒濮虫竟鏇㈡⒑闁偛鑻晶鎾煛鐏炲墽銆掗柍褜鍓ㄧ紞鍡涘磻閸涱厾鏆︾€光偓閸曨剛鍘靛銈嗘⒐閸庢娊宕㈤幘顔界厵妞ゆ柣鍔屽ú銈夋煁閸ヮ剚鐓熼柡鍐ㄥ亞閻掔偓銇勮箛搴″祮婵?


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    return f"[婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€块弻锝夊箻瀹曞洤鍝洪梺鍝勵儐閻楁鎹㈠☉銏犵闁绘劕顕▓銈夋⒑濞茶骞楅柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏閸繃顥為柛娆忕箲閵囧嫰骞掗幋婵愪痪闂佺粯鎸诲ú鐔煎蓟閿熺姴鐐婇柕澶堝劚椤牆螖閻橀潧浠︽い銊ユ嚇閸╃偤骞嬮敂缁樻櫖濠殿喗菧閸庤鲸绂掗鈧娲传閸曨喖顏紓浣割槼椤绌辨繝鍥ㄥ€婚柦妯猴級閵娾晜鐓忓鑸电洴濡绢噣鏌ｉ敂鑲╃М婵﹦绮幏鍛驳鐎ｎ亝顔勭紓鍌欒兌缁垶宕濆▎鎰箚?闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃秹锝炲┑瀣櫇闁稿矉濡囩粙蹇旂節閵忥絽鐓愰柛鏃€鐗犲畷鎴﹀Χ婢跺鍘搁梺鎼炲劗閺呮稑鐨梻浣虹帛鐢帡鏁冮妷褎宕叉繛鎴欏灩楠炪垺淇婇婵愬殭缁炬澘绉瑰娲传閸曢潧鍓紓浣藉煐瀹€绋款嚕婵犳碍鍋勯柣鎾虫捣椤斿姊洪柅娑樺祮婵炰匠鍐ｆ灁妞ゆ挾濮风壕?{count} 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙鐭楀璺虹灱閻﹀牊绻濋悽闈浶㈤柛濠傤煼瀹曘儵宕堕浣哄幈闂侀潧顦介崰鏍ㄦ櫠椤曗偓閺岋綁顢橀悤浣圭暥濡炪値鍙€濞夋洟骞戦崟顖氫紶闁告洖鐏氭牎闂傚倷绀侀幖顐︻敄閸℃稒鍋￠柍杞扮贰濞兼牠鏌ц箛鎾磋础缁炬儳鍚嬮幈銊ノ旈埀顒€螞濞戙垹绀夐柛娑橈梗缁诲棝鏌ｉ幇顒佲枙闁搞倗鍠愰妵鍕敇閻愰潧鈪甸梺璇″櫍缁犳牠骞冨鍫熷癄濠㈣泛瀛╅幉浼存⒒娓氣偓濞佳嚶ㄩ埀顒€鈹戦垾铏枠鐎?


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
            "description": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾剧粯绻涢幋娆忕労闁轰礁顑嗛妵鍕箻鐠虹儤鐎鹃梺鍛婄懃缁绘﹢寮婚埄鍐ㄧ窞閻庯綆浜濋鍛存偡濠婂懎顣奸悽顖涱殜瀹曟劖绻濆顓犲弮濠碘槅鍨拃锕€危瑜版帗鐓熼幖鎼枛婢у瓨鎱ㄦ繝鍐┿仢婵☆偄鍟埥澶婎潩椤掑姣囧┑锛勫亼閸娧呪偓闈涚焸瀹曠懓鐣烽崶褍鐏婃繝鐢靛У绾板秹寮查弻銉︾厱婵犲ň鍋撻柣鎺炲閳ь剟娼ч惌鍌炲蓟閿濆棙鍎熸い鏍ㄧ矌鏍″┑鐐茬摠缁秶鍒掗幘姹団偓浣肝旈崨顓ф綂闂侀潧鐗嗗Λ娑㈠储娴犲鈷戦柟绋挎捣缁犳挻銇勯敂璇叉珝妤犵偛顦甸幃娆擃敆娴ｇ浼庡┑鐘垫暩婵挳宕戦崱娑欏亗濠靛倸鎲￠悡鏇㈡煃鐟欏嫬鍔ゅù婊呭亾娣囧﹪鎮欓鍕ㄥ亾閺嶎偅鏆滈柟鐑樻煛閸嬫挸顫濋悡搴☆潾缂備緡鍠氱划顖溾偓闈涖偢瀵爼骞嬮悪鈧崯鍥ㄧ節閻㈤潧鍓崇紓宥呮瀹曟粌鈻庨幘鏉戔偓鍫曟煃閸濆嫭鍣洪柣鎾跺枛閺岀喖鎮滃Ο璇查瀺闂佺锕ラ崝娆撳蓟閳ュ磭鏆嗛悗锝庡墰琚﹂梻浣筋嚃閸犳帡寮插鍐剧劷闊洦绋戦悡娑樏归敐鍛棌闁诲孩娼欓埞鎴︽偐閸偅姣勬繝娈垮枙閸楀啿鐣烽悷鎳婃椽顢旀担鎻掍壕闁挎洖鍊搁悙濠冦亜閹哄棗浜剧紓浣哄У閻擄繝寮婚弴锛勭杸閻庯綆浜栭崑鎾诲即閻樺樊妫滈梺绋跨箺閸嬫劗绮绘ィ鍐╃厵閻庣數顭堟禒婊堟煟閹烘垹绉洪柡宀嬬磿閳ь剨缍嗛崑鍡樻櫠椤忓懌浜滄い蹇撳閺嗭絽鈹戦垾宕囧煟鐎规洖宕灒闁绘垶蓱椤斿倿姊婚崒娆戠獢婵炶壈宕靛濠冪節濮橆剛锛熼梻渚囧墮缁嬪嫮绱為弽顓犲彄闁搞儯鍔庨埥澶岀磼閳ь剟宕奸姀鈥虫瀾闂婎偄娲﹀ú鏍夊鑸电厽闁规儳纾弰鍌炴煃瑜滈崜姘辨暜閹烘缍栨繝闈涱儛閺佸棝鏌涚仦鍓ф噯婵＄偓鎮傚缁樻媴缁涘娈┑鐐茬摠瀹€绋跨暦閺夎鏃堝礃閳轰礁绨ユ繝鐢靛仦閸垶宕归崷顓犳／鐟滄棃寮婚悢鐓庣妞ゆ挾鍋涚粻娲⒑鐎圭媭鍤欓柣妤佹崌楠炲啫螖閸愨晛鏋傞梺鍛婃处閸撴盯藝閵娿儺娓婚柕鍫濆暙婵″ジ鏌ㄩ弴妯衡偓婵嬪箖閹呮殝闁归攱姊瑰Λ鍐ㄧ暦閵娾晩鏁囬柣鎰暩瀹曞搫鈹戦敍鍕杭闁稿﹥鐗滈弫顕€骞掑Δ鈧壕鐟扳攽閻樺磭顣查柛瀣ф櫅铻栭柨婵嗘噹閺嗙偤鏌嶉柨瀣瑨闂囧鏌ㄥ┑鍡樺窛闁硅棄鍊块弻娑㈠Χ閸涱厽娈婚梺鍝勬湰缁嬫垿鍩㈡惔銈囩杸婵炴垶锚閸欏﹪鏌ｆ惔銈庢綈婵炲弶鐗滅槐鐐寸節閸ャ儮鍋撴担鑲濇棃宕ㄩ鐙€妲规俊鐐€栭崝鎴﹀磹閺囩喐鍙忛柨鏃€鍨濈换鍡涙煟閹板吀绨婚柍褜鍓氶悧鏇㈩敊韫囨梻绡€婵﹩鍓涢敍娑㈡⒑閻熸澘鈷旂紒顕呭灦閹繝寮撮悙鈺傛杸闂佺粯蓱瑜板啴鍩€椤掆偓缂嶅﹪鐛径鎰紶闁靛／鍜冪床闂佸搫顦悧鍐疾濞戞瑧顩风憸鏃堝蓟瀹ュ牜妾ㄩ梺鍛婃尪閸斿海妲愰悙鍝勫耿婵炴垶顭囬悰銉モ攽鎺抽崐鏇㈠箚閵堝棗绶為柟閭﹀墮閼板灝鈹戦悙鏉戠仸闁荤啙鍥у偍闁瑰墽绮崑鈩冪節婵犲倸顏柣顓熷笧閳ь剝顫夊ú妯煎垝瀹€鍕叀濠㈣埖鍔曢～鍛存煟濡吋鏆╅柡瀣у亾闂傚倸鍊烽懗鍓佸垝椤栫偑鈧啴宕ㄧ€涙ê浜辨繝鐢靛Т閸燁偊宕归弮鍫熺厵缂備降鍨归弸鐔兼煟閹惧瓨绀冪紒缁樼洴楠炲鎮滈崶褍褰嗛梻浣告啞濮婂宕伴幇鏉课﹂柛鏇ㄥ灡閺呮粓鏌涘┑鍡楊仼濠殿噯绠戦埞鎴﹀煡閸℃ぞ绨婚梺纭呮珪閿曘垽濡存笟鈧鎾閻欌偓濞煎﹪姊洪弬銉︽珔闁哥噥鍨跺畷鎰版煥鐎ｎ剛鐦堢紒鍓у钃辨い顐躬閺屾稓鈧綆浜濋崵鍥煙椤栨艾顏い銏＄☉椤繈鎮℃惔銏╁悪濠碉紕鍋戦崐鏍礉瑜忕划濠氬箣濠靛洨鍑藉┑鐘垫暩婵即宕归悡搴樻灃婵炴垯鍨洪弲婵嬫煥閺囩偛浜為柡浣告处缁绘稑顔忛鑽ゅ嚬闂佹娊鏀遍崹鍧楀蓟閿濆绠涢梻鍫熺☉閳峰绻濋姀锝庢綈闁挎洏鍨藉璇测槈濞嗘垹鐦堥梺绋胯閸婃宕ョ€ｎ亶娓婚柕鍫濆暙閻忣亪鏌ㄥ鑸靛亗闁靛牆妫庢禍婊堢叓閸ャ劍灏伴柛锝勭矙閺屾稑顫滈埀顒佺鐠轰警娼栭柧蹇氼潐閸犲棝鏌涢弴銊ヤ簻濠殿喓鍨荤槐鎺楀礈瑜戝鎼佹煕濞嗗苯浜鹃梻浣侯焾閿曘倝鎮洪妸褎宕叉繝闈涱儐閸嬨劑姊婚崼鐔衡棩缂侇喖鐖煎铏圭磼濮楀棙鐣堕梺鎸庢处娴滄粓鎮鹃悿顖樹汗闁圭儤鍨甸悗顓烆渻閵堝棙鈷掗柛瀣尭閳绘挻銈ｉ崘鈹炬嫼缂佺虎鍘奸幊蹇氥亹瑜忕槐鎺楀箵閹烘挸浠撮梺璇″枛濞硷繝宕洪埀顒併亜閹烘垵顏柍閿嬪灴閹嘲鈻庤箛鎿冧患闂佸憡鏌ｉ崐妤呭焵椤掑喚娼愭繛璇х畵瀹曟粌顫濇潏鈺冪効闂佸湱鍎ら崵姘洪宥嗘櫆闂佸憡渚楁禍婵堚偓姘偢濮婂宕掑顑藉亾閹间焦鍋嬪┑鐘插閻瑩鏌熼悜姗嗘濠㈣泛艌閺嬪酣鏌熼柇锔跨敖缂佺姵宀稿铏圭磼濡搫顫嶅┑鐐插悑閻熝呭垝椤撯槅妲鹃梺閫炲苯澧い鏃€鐗犲畷顖烆敃閿曗偓閻愬﹦鎲歌箛娴板洭寮跺▎鐐瘜闂侀潧鐗嗗Λ娑欐櫠椤掍焦鍙忔俊顖滎焾婵倿鏌熼鈧粻鏍嵁閸℃凹妾ㄥ┑鐐存尭椤兘寮婚弴銏犻唶婵犻潧娴傚Λ銈嗙節閳封偓鐏炶棄顫紓浣介哺鐢偤鍩€椤掑﹦绉甸柛瀣閹﹢骞橀鐣屽幍濡炪倖姊婚悡顐︻敂閸モ晙绨烽梻鍌欑閹测剝绗熷Δ鍛獥婵娉涢崒銊╂⒑椤掆偓缁夌敻鍩涢幋鐘冲枑闁绘鐗嗙粭鎺懨瑰鈧崡鎶藉蓟濞戙垹绠婚悗闈涙啞閸掓盯姊烘潪鎵槮缂佸鎸抽、姗€宕楅悡搴ｇ獮闁诲函缍嗛崜娆撶嵁濡ゅ懏鈷戦柛锔诲幖閸斿鈹戦悙璇у伐闁伙絿鍏樺鎾閳藉棙顥堟繝鐢靛仦閸ㄩ潧鐣烽鈧埢鎾诲Ω閵夘喗瀵岄梺闈涚墕濡瑧澹曢悽鍛婄厱閻庯綆鍋呯亸鐢告煃瑜滈崜姘额敊閺嶎厼绐楁慨妯挎硾閺嬩線鎮归崶褍妫樻繛鎴欏灩缁€鍐煏婵炲灝鐏い顐㈢Ч濮婃椽宕烽鐐插闂佽鎮傜粻鏍春閳ь剚銇勯幒鍡椾壕闂侀潧鐗忛…鍫ワ綖韫囨洜纾兼俊顖濐嚙椤庢捇鏌ｉ悢鍝ユ噧閻庢哎鍔嶇粋鎺曨槻闁宠鍨块幃娆撴濞戞ü绮繝鐢靛仜閻ㄧ兘鍩€椤掆偓绾绢參寮抽敂鐣岀瘈闂傚牊绋掑婵堢磼閳锯偓閸嬫捇姊绘担瑙勫仩闁稿孩绮撳畷銊╊敇閻愭劖娲栭埞鎴︽晬閸曨偂鏉梺绋匡攻閻楁洟顢欒箛鏃傜瘈婵﹩鍓涢敍娑㈡⒑閻熸澘鈷旂紒顕呭灦閹繝寮撮悙鈺傛杸闂佺粯蓱瑜板啴顢旈鍛闁告侗鍠楃粈瀣煛瀹€鈧崰鏍偘椤曗偓瀹曞綊顢欓崣銉х濠德板€楁慨鐑藉磻濞戙埄鏁勫鑸靛姇閺嬩線鏌涢幇闈涙灈闁绘帒鐏氶妵鍕箳閹存繍浠鹃梺绋匡工閸㈡煡鍩為幋锔藉亹闁告瑥顦ˇ鈺呮⒑缂佹ɑ灏甸柛鐘崇墵瀵鎮㈤崗鑲╁姺闂佹寧娲嶉崑鎾搭殽閻愬澧辩紒杈ㄥ浮楠炴捇骞掑┑鍫濇倯闂備礁鎼惌澶岀礊娴ｅ壊鍤曞ù鐘差儛閺佸洦绻濋棃娑欐悙闁哄鍊栫换婵嗏枔閸喗鐏堥梺鎸庢磸閸庨亶鈥旈崘顔藉癄濠㈣埖锚濞堛劑姊洪崨濠冨矮闁绘帪绠戦悾閿嬪緞閹邦厾鍘繝鐢靛Т閸燁偅鎱ㄩ崒鐐寸厱濠电姴鍟版晶閬嶆煙楠炲灝鐏╅柍钘夘樀婵偓闁绘顕ч弫褰掓⒒娴ｈ櫣甯涙俊顐㈠暣钘熼柟鎯ь嚟椤╁嘲鈹戦崒姘暈闁抽攱鍨块弻锝夋偄閸涘﹦鍑″┑陇灏欑划顖炲Φ閸曨垰绠ｆ繝鍨姈绗戞俊鐐€栧ú鈺冪礊娴ｅ摜鏆︽繝濠傚婵挳鏌ｉ悢绋款棆闁挎稑绻樺缁樼瑹閳ь剙顭囪閸ｅ綊姊洪崨濠佺繁闁哥姵顨婇、娆撳箻缂佹ǚ鎷婚梺绋挎湰閼归箖鍩€椤掑嫷妫戠紒顔肩墛缁楃喖鍩€椤掑嫮宓佸鑸靛姈閺咁剟鏌涢弴銊ュ婵炲牊婢橀埞鎴炲箠闁稿﹥娲熼獮濠傜暆閸曨偆鍔﹀銈嗗坊閸嬫捇鏌涢悤浣哥仩妞ゆ洏鍎靛畷鐔碱敍濮樿京鏉告俊鐐€栭崹鐔煎棘閸岀偛纾块柣銏㈩焾閽冪喐绻涢幋娆忕仼缂佺姵鐩濠氬醇閻旇　濮囬梺璇茬箰閻楁挸顕?,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖骞戦幇闈涙闁荤喐鐟辩粻鎾诲箖濡ゅ懏鏅查幖绮光偓鎰佹交闂備焦鎮堕崝宥囨崲閸儳宓侀柡宥庣仈鎼搭煈鏁嗛柍褜鍓氭穱濠囨嚃閳哄啯锛忛梺璇″瀻娴ｉ晲鍒掗梻浣告惈閺堫剙煤濡吋宕叉繛鎴欏灪閸婇攱銇勯幒宥堝厡鐟滄澘鎳愮槐鎾诲磼濞嗘帩鍞归梺绋款儐閹瑰洭寮诲☉妯兼殕闁逞屽墴瀹曟垿鎮欓悜妯轰簵濠电偛妫欓幐濠氭偂濞嗘劑浜滈柡宥冨妿閳洜绱掗幆鏉跨毢闁诡噮鍠栭～婵嬫嚋绾版ɑ瀚奸梻浣告啞缁诲倻鈧凹鍙冭棢闁绘劗鍎ら悡鐔兼煃閸濆嫸宸ラ柣蹇ラ檮椤ㄣ儵鎮欓幓鎺撴闂侀潧娲﹂崝娆撶嵁閹烘绠ｉ柣妯荤ゴ閸嬫捇鎮欓悜妯轰画濠电姴锕ら崯鎵不婵犳碍鐓曢柍鐟扮仢閻忊晠鏌ｉ敐鍡欑疄闁糕斁鍋撳銈嗗笒閸婂綊锝為弴銏＄厵闁绘垶蓱鐏忔壆绱撳鍛枠闁哄本娲樼换娑滎槻闁硅櫕鍔欏鎶筋敃閳垛晜鏂€?闂傚倸鍊搁崐鎼佸磹閹间礁纾圭€瑰嫭鍣磋ぐ鎺戠倞鐟滄粌霉閺嶎厽鐓忓┑鐐靛亾濞呭棝鏌涙繝鍌涘仴闁哄被鍔戝鏉懳旈埀顒佺閹屾富闁靛牆楠搁獮鏍煟韫囨梻绠為柨婵堝仜椤劑宕煎┑鍫濆Е婵＄偑鍊栫敮鎺斺偓姘ュ姂閸┾偓妞ゆ垼娉曢ˇ锕傛懚閺嶎厽鐓曟繛鎴濆船閺嬫稑霉濠婂嫮鐭岀紒杈ㄦ尰閹峰懘宕滈幓鎺戝婵犵數鍋涢ˇ鏉棵哄鍛灊闁挎繂顦伴崐鐑芥煟閹寸伝顏堝焵椤掆偓閻忔岸銆冮妷鈺傚€烽柤纰卞厸閾忓酣姊洪崨濠冣拹鐎光偓閹间礁绠栨俊銈傚亾妞ゎ偅绻堥幃鈩冩償閵忋垹缍嗛梻鍌欐祰椤曟牠宕归鐐村€块柨鏇炲€哥粻姘舵煛閸愩劎澧涢柡鍛叀閺屾盯濡烽姀鈩冪彣缂備礁宕鍓佹崲濠靛鍋ㄩ梻鍫熺◥濞岊亪姊洪幖鐐插闁绘牕銈搁獮鍐偪椤栵絾歇闂備礁鎼幊搴ㄦ偉婵傜钃熼柛鈩冾殢閸氬鏌涢埄鍐噧妤?闂?闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪箻閸┾偓妞ゆ帊鑳堕埢鎾绘煛閸涱垰孝闁伙絽鍢查～婊堝焵椤掑嫬绠犻柨鐔哄Т鍥撮梺鎼炲劗閺咁亞妲愰搹顐ょ瘈婵炲牆鐏濋弸鐔兼煥濮樻墎鍋撶憴鍕闁告挻宀搁獮鍫ュΩ閳哄﹥鏅㈤梺鍛婃处閸撴盯宕㈤柆宥嗏拺闁告繂瀚崒銊╂煕閺傛寧婀伴柡鍛板煐鐎佃偐鈧稒顭囬崢鎾剁磽閸屾瑧鍔嶉拑杈╃磼閳ь剛鈧綆鍠楅悡娑氣偓鍏夊亾閻庯綆鍓欓崺宀勬煣娴兼瑧绉柡灞剧☉閳规垿宕卞Δ濠佺棯婵犳鍣徊楣冨礉濞嗗浚娼?",
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
            "description": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧潡鏌熺€电孝缂佽翰鍊濋弻锕€螣娓氼垱锛嗗┑鐐叉▕娴滄繈寮插鍫熺厽闁逛即娼ф晶顕€骞栭弶鎴含婵﹨娅ｇ划娆戞崉閵娧傜礃闂備胶顭堥鍥磻閵堝懐鏆﹂柟杈剧畱鍥存繝銏ｆ硾椤戝洭宕㈤鍛瘈闁汇垽娼у瓭缂備胶绮崝娆撳Υ閸涙惌鏁嗛柛鏇ㄥ墰閸樻挾绱撻崒娆戝妽閽冭鲸銇勯妷銉уⅵ闁哄矉绱曟禒锕傛偩鐏炴縿鍎查妵鍕槺缂佽埖宀稿璇测槈閵忕姷顔掗柣鐘烘閸庛倝鎮楃拠宸富闁靛牆妫欑粚璺ㄧ磽瀹ュ嫮顦﹂柣锝夋敱缁虹晫绮欓崹顔肩ギ闂備胶绮弻銊╁箟閿熺姵鍋熸い鎰堕檮閳锋帒霉閿濆懏鍟為柛鐔哄仦缁绘稓鎷犺閻ｇ數鈧娲樼划宀勶綖濠靛鏁勯柤鎭掑劤娴滄牠姊绘笟鈧褏鎹㈤崼銉ョ９闁哄稁鍘奸悡鏇㈡煙鏉堥箖妾柛瀣у墲缁绘盯宕卞Δ鍐唶濡炪倕娴氭禍顏堝箖濡法鐤€闁靛鏅滈宥夋⒑闂堟稒鎼愰悗姘卞娣囧﹪鎮滈懞銉︽珕闂佽姤锚椤﹂亶銆傞弻銉︹拻濞达絽鎽滈敍宥囩磼椤曞懎鐏︽鐐村灴瀹曞爼顢楅崒姘便偊闂佽鍑界紞鍡涘窗濡ゅ懎鐤炬繝濠傜墛閸嬧剝绻涢崱妯兼噮缂佸顭烽幃妤€顫濋澶屽悑濠殿喖锕︾划顖炲箯閸涙潙宸濆┑鐘叉噽椤㈠懏淇婇悙顏勨偓銈夊储婵傚憡鍋嬮煫鍥ㄧ☉閻掑灚銇勯幒宥堝厡闁崇粯鎹囬弻锟犲川椤栨銏ゆ煟閿濆懎妲婚悡銈嗐亜韫囨挸顏柨娑欑矒濮婅櫣绱掑Ο鍝勵潔濠电偛鍚嬮悷锔剧矉閹烘鏁嶆繛鎴炴皑椤旀洟鏌℃径濠勫濠⒀呮櫕缁棃顢楁担鍏哥盎濡炪倖鍔戦崺鍕ｉ悜妯肩闁糕剝鍔曢悘鏌ユ煙瀹曞洤鈻堟い銏☆殜瀹曟帒顭ㄩ幇顔肩哎闂傚倷娴囧畷鍨叏閺夋嚚娲晝娴ｅ吀姹楅梺鍛婂姦閸犳牠鎮為崹顐犱簻闁瑰搫绉堕ˇ锔姐亜閺囩喓鐭婇懣鎰版煕閵夋垵绉烽崥顐⑽旈悩闈涗沪闁挎洏鍨介妴浣糕枎閹炬潙娈愰梺鍐叉惈椤戝洦鎯旀繝鍌楁斀闁绘ɑ鍓氶崯蹇涙煕閻樻剚娈滈柡浣稿暣閸╋繝宕ㄩ鐙€妲舵繝娈垮枟椤牓宕洪弽顓熷亗闁靛璐熸禍婊堟煙閹规劖纭鹃柡瀣⒒缁辨帡鎮╅懡銈囨毇闂佸搫琚崝宀勫煘閹达箑骞㈡俊顖滃劋椤忊€斥攽閻橆喖鐏辨繛澶嬬〒閳ь剚鍑归崰姘ｉ幇鏉跨闁哄啠鍋撻悗姘哺閺岀喓绱掑Ο鍝勬綉闂佺顑嗛幑鍥х暦缁嬭鏃堝焵椤掑倻涓嶉柡宥冨妿缁犲墽鈧懓澹婇崰鏇犺姳婵犳艾绠氶柣鏂垮悑閳锋垿鏌涢幇顒€绾ч柟顖氱墦閺屾稒绻濋崒娑樻殘缂備礁鍊圭敮鎺斿弲濡炪倕绻愰幊澶愬箯濞差亝鈷掗柛灞炬皑婢ф稑銆掑顓ф疁闁诡噯绻濋、姗€鎮╅悽纰夌床闂備胶绮敋闁哥喎娼￠幃姗€骞橀鐣屽幍濡炪倖娲栧Λ娑氬姬閳ь剟鎮楀▓鍨灍闁规瓕娅曢幈銊╁焵椤掑嫭鐓ユ繛鎴灻鈺傤殽閻愭潙濮嶆慨濠勭帛閹峰懘宕ㄦ繝鍌涙畼婵犵數鍋犻婊呯不閹惧磭鏆﹂柟杈剧畱瀹告繈鏌℃径瀣仼妞ゆ柨顦靛娲箰鎼达絿鐣靛銈忕細閸楁娊骞冮敓鐘茬妞ゆ梻鏅崢顏呯節閵忥絽鐓愮紒瀣灴閹礁顭ㄩ崼鐔哄幗闂佺懓鎼粔鍫曟儗濞嗘挻鐓涚€光偓閳ь剟宕伴弽顓溾偓浣糕枎閹寸偛鐝伴梺鍦帛鐢偤濡堕灏栨斀闁绘ɑ顔栭弳顖炴煕閹惧绠炴鐐插暣瀹曟帒鈽夊Δ鍐暰闂備礁缍婂Λ鍧楁倿閿曞倸鐤炬繝闈涱儐閻撳啰鎲稿鍫濈婵炲棙鎸搁悡鈥愁熆鐠哄搫鐦ㄦ俊顖氬閳规垿顢欑涵宄颁紣闂佸湱鈷堥崑鍛村疾閵夆晜鈷戦柟鑲╁仜閸斺偓闂佸憡鍔曟晶浠嬪焵椤掍礁鈻曟慨濠呮閹风娀骞撻幒婵嗗Ψ闂備礁鎲￠崹鐢电礊婵犲倻鏆︽繝濠傚枤濞尖晠寮堕崼姘珖闁绘帒娼￠幃妤呯嵁閸喖濮庡銈忓瘜閸ㄤ即顢欒箛鎾斀闁糕€崇箲閺傗偓闂備胶绮摫鐟滄澘鍟撮、鏃堫敇閻斿墎绠氱紓鍌欓檷閸ㄥ綊寮搁悢铏圭＜缂備焦顭囩粻鎾绘煃缂佹ɑ宕岀€规洖缍婇、娆撴偩鐏炲吋鍠氶梻鍌氬€风粈渚€骞夐敓鐘茶摕闁靛ě鍕簥濠碘槅鍨靛▍锝夊汲閿曞倹鐓欓弶鍫濆⒔閻ｈ京绱掗悩宸吋闁诡喗顨呴埥澶娾枍椤撗傞偗妞ゃ垺鎹囬獮妯肩礄閻樼數鐣鹃梻浣虹帛閸旀洖螣婵犲洤纾块煫鍥ㄦ⒒缁犻箖鏌℃径瀣仴婵℃彃顭峰畷锟犳焼瀹ュ棛鍘甸柡澶婄墦缁犳牕顬婇鈧弻宥夋煥鐎ｎ亞浼岄梺璇″枛缂嶅﹤鐣烽崼鏇熸櫜闁稿本鐭竟鏇㈡倵鐟欏嫭绀€婵炶绲垮Σ鎰潨閳ь剙顫忕紒妯诲閻熸瑥瀚禒鈺呮⒑閸涘﹥鈷愰柛銊ュ缁顓奸崶銊ョ／闂佹儳绻楅～澶娾枔妤ｅ啯鍋℃繝濠傛噹椤ｅジ鎮介娑樼瑲闁稿寒鍋婂缁樻媴缁嬫寧姣愰梺鍦拡閸嬪﹤鐣烽幇顓犵瘈婵﹩鍓欓崑宥夋⒑閸︻厼鍔嬫い銊ユ瀹曟劙宕归顐ｎ啍闂佺粯鍔樼亸娆愮閵忋倖鐓曢柡鍐ｅ亾鐎光偓閹间礁钃熼柨婵嗘啒閺冣偓閹峰懘鎼归崷顓炲笌闂備胶绮幐鍫曞磹濠靛钃熼柕濞垮劗閺€浠嬫煕閳锯偓閺呮粍鏅ラ梻鍌欒兌缁垶骞愮拠瑁佹椽鎮㈤悡搴ゆ憰闂佺粯鏌ㄩ崥瀣倿娴犲鐓ラ柡鍥殔娴滅偓绻濋埛鈧崒姘ギ闂佸搫琚崝宀勫煡婢跺á鐔稿緞鐎碘€虫处閻撴稓鈧厜鍋撻悗锝庡墰钃辨俊銈囧Х閸嬫盯鏁冮鍫濊摕婵炴垶鐟﹂崕鐔兼煥濠靛棙顥炴慨锝呯墦閹鈻撻崹顔界彯闂佺顑呯€氫即銆佸Ο鑽ら檮缂佸娉曢崐鐐烘⒑閹稿孩顥嗘俊顐㈠閸掑﹥瀵肩€涙ǚ鎷绘繛杈剧悼椤牓骞冮幋鐘电＜濞达綀顫夌亸锔锯偓娈垮枟瑜板啴鍩為幋鐘亾閿濆簼绨介柣銈呮嚇閹嘲顭ㄩ崨顓ф毉闁汇埄鍨遍〃濠囧箖閿熺姵鍋勯柛蹇氬亹閸樹粙姊洪崫鍕偓鍦偓绗涘洤鐤柣鎰暩濡垶鏌熼鍡楃灱閸氬姊洪崫鍕効缂傚秳绶氶悰顕€骞掑Δ浣糕偓椋庘偓鐟板閸犳宕板鈧缁樻媴閼恒儯鈧啰绱掔拋鍦瘈鐎规洘婢橀埥澶愬閻樻牭绠撻弻鐔兼偋閸喓鍑＄紓浣哄У婵炲﹪寮婚悢琛″亾閻㈡鐒鹃柛鎾归哺娣囧﹪顢曢妶鍛€炬繛锝呮搐閿曨亪骞冨▎鎿冩晜闁告洏鍔屾禍楣冩煛瀹ュ骸骞栫紒鐘冲缁辨挻鎷呯拠锛勫姺闂佺粯绻傞悥濂稿蓟閿熺姴鐐婇柕澶堝劤娴犺偐绱掗悙顒€鍔ゆい顓犲厴瀵鎮㈤悡搴ｎ唹闂侀€涘嵆濞佳冣枔椤撶姷纾奸柣鎰靛墮閸斻倝鏌涘顒夊剳闁瑰箍鍨归埥澶愬閻樿尪鈧灝鈹戦埥鍡楃仴婵炲拑绲剧粋鎺楁偂鎼搭喗瀵岄梺闈涚墕濡瑩鍩涢幇顓濈箚妞ゆ劑鍨归弳锝団偓娈垮枛椤兘寮幇鏉垮耿婵☆垰鎼俊鎶芥⒒娓氣偓濞佳呮崲閸℃稑绠犻柛銉ｅ妽閸欏繘鏌涢妷顔煎闁抽攱鍨块弻鐔虹矙閹稿骸鏀繝銏ｎ潐钃遍柕鍥у椤㈡﹢鍨鹃崘鎻捫ユ俊鐐€ч梽鍕焽濞嗘挸鐓橀柟杈惧瘜閺佸﹪鏌ｉ幘宕囧哺闁圭鍟扮槐鎾寸瑹閸パ勭仌濡炪倖娉﹂崶褏鍙€婵犮垼鍩栭崝鏇綖閸涘瓨鐓熸俊顖氱仢閻ㄦ椽鏌ｅ☉鎺撴珕缂佺粯绻堥幃浠嬫濞戞ê顥愮紓鍌氬€哥粔鏉懳涘┑鍡欐殾婵°倐鍋撴い顐ｇ矒閸┾偓妞ゆ巻鍋撻柣锝囧厴楠炲鏁冮埀顒傜不婵犳碍鐓曢柨鏃囶嚙楠炴﹢鏌℃径宀婄劸闁宠鍨块幃娆撳级閹寸姳妗撴俊鐐€ら崢鐓幟洪鈩冾棨闁荤喐绮嶉弻銊╋綖韫囨拋娲敂閸曨収妲堕梻浣告贡缁垳鏁繝鍕С闁圭虎鍠楅埛鎴︽煙閼测晛浠滃┑陇濮ゆ穱濠囨倷閼告妫勫?ask_user 缂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙闁诡垳鍋ら獮鏍庨鈧俊濂告煟椤撶噥娈滄鐐寸墪鑿愭い鎺嗗亾濠德ゅ亹缁辨帡骞囬褎鐣风紓浣虹帛閻╊垶鐛€ｎ亖鏋庨煫鍥ㄦ礀婵爼姊绘担鑺ャ€冪紒鈧担璇ユ椽濡舵径濠勫幋闂佺鎻梽鍕磻閹扮増鍊甸柛锔诲幖瀛濆銈冨劜缁诲牆顕?,
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["preference", "habit", "decision", "knowledge"],
                        "description": "闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煕椤垵浜濋柛娆忕箻閺岀喖骞嗛弶鍟冩捇鏌涙繝鍌涘仴闁哄被鍔戝鏉懳旈埀顒佺閹屾富闁靛牆楠搁獮鏍煟韫囨梻绠氶柣蹇斿浮濮婅櫣绮欑捄銊ь唺闂佸憡顭嗛崟顒€鍔呮繝鐢靛Т濞诧箓鍩涢幋鐘电＜閻庯綆鍋勯婊勭節閳ь剟骞嶉鍓э紲濡炪倖鏌ㄩ崥瀣箲閿濆悿鐟邦煥閸曨剙鈧劙鏌熼鑽ょ煓鐎规洏鍔嶇换婵嬪磼濞嗗繐顕ч梻鍌氬€烽悞锕傚箖閸洖纾挎い鏍仜缁€澶屸偓鍏夊亾闁逞屽墮椤曘儲绻濋崘顏嗙槇濠殿喗锕╅崢楣冨储娴犲鈷戦柛锔诲幖閸斿鏌涢…鎴濈仸鐎规洘鍨挎慨鈧柕鍫濇閸樻悂鏌ｈ箛鏇炰哗妞ゆ泦鍕箚濠靛倸鎲￠悡鍐煢濡警妯堟俊鍙夋倐閺屽秶鎷犻弻銉偓妤呮懚閿濆鐓曟繝闈涙椤忓瓨绻涢悡搴ｇ煑eference=闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙５闁逞屽墾缁犳挸鐣锋總绋课ㄦい鏃囧Г濞呭牓姊绘担鍛婂暈濞撴碍顨婂畷褰掑础閻愬灚娈鹃梺鍝勮閸庢煡鎮″▎鎾寸厽婵°倐鍋撻柣妤€锕﹀▎銏ゅ蓟閵夈儳鍊? habit=婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块幃瑙勬姜閹峰矈鍔呭┑鐐插悑閻楁粎妲愰幘瀛樺闁兼祴鍓濋崹鍨暦閿濆牏鐤€婵炴垶鐟ч崢浠嬫⒑闂堟稓绠為柛鈺佸閹偤宕滆濡? decision=闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极閹剧粯鍋愰柤纰卞墻濡茬兘姊绘担鍛婃儓婵炲眰鍔嶉幈銊╁箻椤斻垹顦～婵嬵敇濠娾偓缁ㄥ姊虹憴鍕姢鐎规洦鍓熼幃姗€顢旈崼鐔哄幈? knowledge=闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煕椤垵浜濋柛娆忕箻閺岀喖骞嗛弶鍟冩捇鏌嶉柨瀣拻闁逞屽墮缁犲秹宕曢柆宓ュ洭顢涘鍐炬闁荤喐鐟ョ€氼亞鎹㈤崱娑欑厪闁割偅绻冮崳娲煕閿濆棙銇濋柡?,
                    },
                    "content": {
                        "type": "string",
                        "description": "闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煕椤垵浜濋柛娆忕箻閺岀喖骞嗛弶鍟冩捇鏌涙繝鍌涘仴闁哄被鍔戝鏉懳旈埀顒佺閹屾富闁靛牆楠搁獮鏍煟韫囨梻绠氶柣蹇斿浮濮婅櫣绮欑捄銊ь唺闂佸憡顭嗛崟顒€鍔呮繝鐢靛Т濞诧箓鍩涢幋鐘电＜閻庯綆鍘界涵鍫曟煟韫囨稐鎲鹃柡灞剧〒閳ь剨缍嗛崑鍡涘Υ閹烘梻纾兼い鏃囧亹婢э妇鈧娲橀敃銏ゃ€佸▎鎾村仼閻忕偠妫勭粻鐐测攽閻樺灚鏆╅柛瀣仱瀹曞綊妫冨☉姘濡炪倖宸婚崑鎾淬亜閺囶亞绋婚柕鍫秮瀹曟﹢鍩￠崘銊ョ疄闂傚倷鑳剁划顖毼涢崘顔肩哗闂侇剙绉寸粣妤佹叏濡炶浜鹃梺鍝勭焿缁辨洘绂掗敂鐐珰闁圭粯甯╅悗鎶芥⒒娴ｅ摜鏋冩俊顐㈠钘濇い鏍ㄧ箘娴滀粙姊绘担绋挎倯缂佷焦鎸冲鎻掆槈濞嗘劕寮挎繛瀵稿帶閻°劑鍩涢幒鎳ㄥ綊鏁愰崼顐ｇ秷闂佺顑囨繛鈧柡灞剧⊕缁绘繈宕橀鍕ㄦ嫛闂備礁鎲＄敮妤冩暜閿熺姷宓佹俊顖氬悑鐎氭岸鏌ょ喊鍗炲闁哄棭鍋婂缁樻媴閾忕懓绗￠梺鍛婃⒐濞茬喖鐛弽顓ф晝闁靛牆娲ｇ粭澶娾攽椤旂瓔鐒鹃柛鈺傜墵閸╂盯骞嬮悙顏冪盎闂佽鍎冲畷顒佷繆閸ф鐓熼柨婵嗙墦閸濊櫣绱掔紒妯兼创鐎规洖鍚嬮幏鍛村川婵犲偆妲遍梻浣虹帛閹搁箖宕伴弽顓炶摕闁挎繂顦猾宥夋煕椤愵偄浜濇い銉︾墪閳规垿鎮欓懠顒€鈪垫繛瀛樼矊閻栫厧顕ｇ拠娴嬫婵﹫绲芥禍楣冩煥濠靛棝顎楀ù婊勭箘閳ь剝顫夊ú鏍儗閸岀偛钃熼柍銉ョ－閺嗗棝鏌嶈閸撶喎鐣锋导鏉戠閻犲洩灏欓鍡涙⒑缂佹﹩鐒界紒顕呭灦瀹曠敻骞嬮悙顏冪盎闂佸湱鍎ら崹鍨閻愮儤鐓曢柣鏃堫棑婢э附鎱?,
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
            "description": "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎺嶇劍椤斿洭姊绘担铏瑰笡闁告梹娲熼、姘额敇閻樺吀绗夋俊銈忕到閸燁垶鎮￠崘顏呭枑婵犲﹤鐗嗙粈鍫熸叏濡潡鍝虹€规洖寮剁换娑㈠箣濞嗗繒浠奸悗鐟版啞缁诲啴濡甸崟顖氱閻犲搫鎼竟澶愭⒑閸涘﹥鐓ユい锕佷含濡叉劙骞樼€涙ê顎撻梺鍛婃尰瑜板啴宕滈弶娆炬富闁靛牆绻愰々顒勬煛娴ｇ瓔鍤欓柣锝呭槻鐓ゆい蹇撳閸旓箑顪冮妶鍡楃瑐闂傚嫬绉电粋宥咁煥閸喓鍘甸梺缁樺灦閿氶柣蹇嬪劜閵囧嫯绠涙繝鍐╃彇缂備浇椴哥敮锟犲箖椤忓嫧鏋庨煫鍥ㄦ煥椤︹晠姊虹紒妯诲蔼闁稿氦灏欓幑銏犫槈閵忕姷顓洪梺璇茬箲濡炴寧绂嶉鍫涒偓渚€寮崼顐ｆ櫆闂佸壊鍋嗛崰鎾诲储閹间焦鈷戠紒顖涙礀婢у弶銇勯妸銉уⅱ缂侇喚绮换婵嗩潩椤撶姴骞愰柣搴″帨閸嬫捇鏌嶈閸撶喎鐣锋导鏉戝唨妞ゆ挾濮寸粊锕€鈹戦濮愪粶闁稿鎸婚妵鍕閳ュ啿鎽甸悗瑙勬磸閸旀垿銆佸璺哄窛妞ゆ洖鎳忛ˉ銏犫攽閻樺灚鏆╁┑顔惧厴瀵偊骞栨担鍝ワ紱濠电偞鍨崹娲磻鐎ｎ亖鏀介柣妯哄级閹兼劙鏌涢妸銉モ偓鍧楀蓟濞戔懇鈧箓骞嬪┑鍥╁蒋婵犵數鍋涢崥瀣偋濠婂牆绠熼柟闂寸劍閸嬪鏌涢锝囩畼闁荤喆鍔庣槐鎾存媴閸濆嫅锟犳煕濡や礁鈻曢柣娑卞櫍瀵粙鈥栭妷銉╁弰妞ゃ垺顨婇崺鈧い鎺戝閸婂爼鏌嶉崫鍕櫤闁绘挾鍠栭弻鐔兼倻濡闉嶉梺绋匡攻閸旀瑩寮婚垾宕囨殕閻庯綆鍓涜ⅵ闂備浇顕栭崰鎺楀疾濠婂喚鐒介煫鍥ㄧ☉閻撴稑霉閿濆懎顥忛柣搴㈡綑閳规垿鎮╅崹顐ｆ瘎婵犳鍠曢崡鍐茬暦閻熸噴娲敂娴ｆ彃浜鹃柨鏇炲€搁悙濠冦亜閹哄棗浜剧紓浣哄У閻擄繝寮婚弴锛勭杸閻庯綆浜栭崑鎾诲即閻樺樊妫滄繝闈涘€搁幉锟犳偂閻斿吋鐓欓梺顓ㄧ畱婢ь喗淇婇锝忚€块柡灞炬礃瀵板嫰宕卞Ο鑽ゅ絾闂備胶绮幐璇裁洪悢鐓庣畺婵せ鍋撻柟顔界懇濡啫鈽夊Δ鈧ˉ姘舵⒒娴ｅ湱婀介柛鏂跨Ч瀹曞綊宕烽鐕佹綗闂佸湱鍎ら幐鍝ユ閻愭祴鏀介柣鎰皺娴犮垹霉閻欌偓閸ｏ絽顫忓ú顏勪紶闁告洦鍘鹃崝鍦磽閸屾氨小缂佽埖宀稿顐﹀箛閻楀牆鈧嘲銆掑鐓庣仭闁哄懌鍨藉娲焻閻愯尪瀚板褜鍨拌彁闁搞儜宥嗘暰缂備礁鍊圭敮鐐哄焵椤掑﹦绉甸柛瀣瀹曘垽鏌嗗鍡忔嫼闂佸憡鍔曞鍫曞箚閸儲鐓曞┑鐘插亞閻撶厧鈹戦埄鍐╁唉妤犵偞甯掕灃濞达絽鎼獮?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂磋閳ь剨绠撻、妤呭礋椤愩倧绱遍梻浣告啞濞诧箓宕愮€ｎ€㈡椽顢旈崨顔界彇濠电偠鎻紞鈧い顐㈩樀瀹曟娊鎮滈懞銉㈡嫽婵炶揪绲藉﹢鍗烇耿娴犲鐓曢柍杞扮椤忣厾鈧娲栫紞濠囥€侀弮鍫濋唶婵犻潧鐗炵槐閬嶆⒒娴ｇ儤鍤€闁告艾顑夐幃浼存儍?闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹潡顢氶埀顒勫蓟閻旂厧绀堝ù锝囧劋閹叉﹢姊烘潪鎵槮闁挎洦浜濠氭偄閸忚偐鍔烽梺鎸庢磵閸嬫捇鏌＄€ｎ剙鏋戦柕鍥у椤㈡洟鏁愰崱娆樻О缂傚倷鑳剁划顖滄崲閸惊娑㈠礃閵娿垺顫嶉梺鍛婎殘閸嬫稒绔熼崼銏㈢＝闁稿本鐟ㄩ澶愭煕鐎ｎ偅宕岄柡灞剧☉閻ｆ繈鍩€椤掑嫬纾婚柣鎰劋閸嬪倿鏌￠崶鈺佹瀭濞存粍绮撻弻鐔兼焽閿曗偓閺嬫稓鈧稒绻堝铏规嫚閸欏顩版繛瀛樼矤娴滎亜顕?recall_memory 闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涙繝鍛厫闁逛究鍔岃灒闁圭娴烽妴鎰磼閻愵剙鍔ゆ繛纭风節瀵鎮㈤悡搴ｇ暰闂佺粯顨呴悧婊兾涢崟顖涒拺闁告繂瀚銉╂煕鎼淬垹鈻曢柛鈹惧亾濡炪倖宸婚崑鎾绘煕濡崵鐭掔€规洘鍨块獮妯肩磼濡厧甯楅柣鐔哥矋缁挸鐣峰鍫熷亜闁绘挸瀛╁Σ顒勬⒑闁偛鑻晶顖炴煏閸パ冾伃妤犵偞甯￠獮瀣攽閸愩劋澹曢悷婊呭鐢帒效閺屻儲鐓冮柛婵嗗閸ｆ椽鏌ｉ幘瀵告噰闁哄睙鍡欑杸闁挎繂鎳嶇花濂告煟韫囨挾绠抽柡浣割煼瀵濡堕崥銈嗘そ椤㈡棃宕橀埡浣圭亾闂傚倷鑳堕幊鎾跺椤撶喓绠鹃柍褜鍓氶妵鍕閳藉棙鐣烽梺鐟板槻閹虫ê鐣峰鍏犲湱鈧綆浜欐竟鏇炩攽閻愭潙鐏熼柛銊︽そ閸╂盯骞嬮敂鐣屽幈濠电娀娼уΛ妤咁敂鐎涙ü绻嗛柟缁樺笒閹垹绱掔紒妯尖姇鐎垫澘瀚埀顒婄秵閸嬪棝藝椤撶姷纾藉〒姘搐閺嬫稒銇勯鐘插幋闁绘侗鍠栬灒闁兼祴鏅濋敍婊冣攽閳藉棗鐏ｉ柛妯犲洨宓?ID闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍛婄秶濡わ絽鍟宥夋⒑閹肩偛鈧牠宕濋弽顓炍﹂柛鏇ㄥ灠閸愨偓濡炪倖鍔﹀鈧紒顔肩埣濮婂搫效閸パ€鍋撻妶澶婇棷闁挎繂顦拑鐔衡偓骞垮劚閻楁粌顬婇妸鈺傗拺闁告稑锕ョ亸鐢告煕閻樺磭澧甸柣娑卞櫍瀹曟﹢顢欓崗鐓庣ザ婵＄偑鍊栭幐鑽ょ矙閹寸偟顩插Δ锝呭暞閻撱儲绻濋棃娑欘棤闁告垵婀辩槐鎺楀Ω閵夘喚鍚嬮梺鍝勭焿缁绘繂鐣烽崡鐐╂瀻闊洦姊绘禍顏堟⒒娴ｅ憡鎯堝璺烘喘瀹曟粌鈹戠€ｎ亞顔嗛梺鍛婄☉閻°劑藟閸喓绠鹃柟瀵稿仜缁楁帒霉濠婂牏鐣洪柡宀嬬節瀹曞爼鎳滈悽鐢电崸缂傚倸鍊哥粔鐢告偋閻樿钃熼柡鍥风磿閻も偓闁诲函缍嗘禍鏍磻閹捐鍗抽柣鎰嚟閸戜粙姊婚崒姘偓椋庣矆娓氣偓楠炲鍩勯崘顏嗘嚌濠德板€曢幊搴ｇ矆閸喓绠鹃柟瀛樼懃閻忣亪鏌涙惔銏╂畷濞ｅ洤锕俊鍫曞川椤斿吋顏￠梻浣瑰▕閺€閬嶅垂閸︻厽顫曢柟鐑樻煛閸嬫捇鏁愭惔鈥崇缂佺虎鍘兼晶搴ｆ閹烘鍋愰柛妤冨仜缁侇噣姊洪崫鍕拱闁烩晩鍨遍幈銊╁焵椤掑嫭鐓ユ繛鎴灻鈺冣偓娈垮枔閸旀垿骞冨Δ鍐╁枂闁告洦鍓涢ˇ顓烆渻閵堝啫鐏╅柨鏇ㄤ簼娣囧﹪鎮界粙璺ㄧ杸闂佸搫顦冲▔鏇㈩敊婵犲洦鈷戦柛锔诲弨濡炬悂鏌涢妸銊ゅ惈闁逞屽墮閻忔岸鎮ч悩宸綎缂備焦顭囬悷褰掓煃瑜滈崜娆撯€﹂崶顏嶆▌闂佽鍟崶褍鑰垮┑鐐村灦椤洭寮婚崼銉︹拺缂備焦锕╅悞鐐亜閺囧棗鎳庨ˉ?,
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煟閵忋埄鐒剧紒鎰殜閺岀喖鏌囬敃鈧崝鎺撶箾瀹割喕绨荤紒鐙呯秮閺岋絽螣閸忓吋姣勯梺缁樺笒閸氬鎹㈠☉銏犵闁哄鍨归崝浼存⒑缁嬫鍎愰柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏鐭掗柕鍡曠劍缁绘繈宕堕‖顒婄畵閺岀喖鎮ч崼鐔哄嚒缂備胶濮垫繛濠囧蓟閻旇櫣纾奸柕蹇曞Х娴狀參鏌ｆ惔锛勪粵闁绘濮撮～蹇曠磼濡偐鎳濋梺閫炲苯澧い顓炴穿椤﹀綊鏌熼銊ユ搐楠炪垺淇婇悙瀛樼婵＄偘绮欏顐﹀礃椤旇偐锛滃┑鐐村灦鐪夐柟顕嗙秮濮婂宕掑▎鎴ｇ獥闂佸憡鎸婚悷褏鍒掗弮鍫熷仺缂佸娉曢敍娑㈡⒑閹稿海绠撻柟顔垮劵閵囨劙骞掗幘瀛樼彸闂備礁澹婇崑鎺楀磻閸涱垳绀婇柛顐犲灮绾捐棄霉閿濆洦鍤€闁告柨鐖奸幃妯跨疀閺冨倹鍣┑?ID闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍛婄秶濡わ絽鍟宥夋⒑缁嬫鍎忔い鎴濐樀瀵鈽夊Ο閿嬵潔闂佸憡顨堥崑鐔哥閳哄懏鈷?recall_memory 缂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌熼梻瀵割槮缁炬儳缍婇弻锝夊箣閿濆憛鎾绘煕婵犲倹鍋ラ柡灞诲姂瀵挳鎮欏ù瀣壕闁告縿鍎虫稉宥夋煛婢跺﹦姘ㄩ柡鈧禒瀣厽婵☆垵娅ｉ敍宥嗐亜閿濆棛鍙€闁哄本绋掔换婵嬪川椤斾勘鈧劕顪冮妶搴″绩婵炲娲熼獮鎴﹀礋椤掑倻鎳濆銈嗙墬閼圭偓绔熺€ｎ喗鈷掑ù锝呮憸閿涘秶绱掗鍛仩妞ゎ偄绻楅妵鎰板箳閹崇绠撻弻娑㈠即閵娿儳浠╃紓浣哄Х缁垶濡甸崟顖氬唨妞ゎ厽鍨堕悾鑸电箾鐎涙鐭婂褌绮欓崺鈧い鎺戝枤濞兼劖绻涢崣澶屽ⅹ闂囧鏌涘畝鈧崑娑㈡嚋瑜版帗鐓熼柕蹇曞У閸熺偤鏌嶉柨瀣瑨闂囧鏌ㄥ┑鍡樺櫤闁哥喓鍋ら弻娑㈡偄閸濆嫪妲愰梺鍝勭焿缂嶄線骞冮妶澶婄＜婵犲﹤鎳忓▓濂告⒒娴ｇ瓔鍤冮柛鐕佸亰瀹曞爼鎳滈崹顐ｇ彎闂傚倷鑳剁划顖濇懌闂佸憡鎸婚懝楣冣€?,
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
            content="闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銏㈢＝闁稿本鐟х拹浼存煕鐎ｎ亜顏紒顔芥閵囨劙骞掗幋锝嗘啺闁诲骸绠嶉崕鍗灻洪敃鍌氱；婵せ鍋撻柡灞界Ч婵＄兘濡烽妷銉ь儓濠电姰鍨奸～澶娒哄鍛潟闁规崘顕х壕鍏肩箾閸℃ê鐏ュ┑陇妫勯—鍐Χ閸愩劌顬堥梺纭呮珪閿氶柣锝囧厴楠炲洭鎮ч崼婵呯敾闂傚倷绶￠崣蹇曠不閹存績鏋旀い鎰堕檮閳锋垿鏌涘☉姗堟敾濠㈣泛瀚伴弻娑氣偓锝庡亜濞搭喚鈧娲忛崕鎶藉焵椤掑﹦绉甸柛鐘愁殜閹繝寮撮姀锛勫幐闂佹悶鍎崕杈ㄤ繆閸忕⒈娈介柣鎰懖閹寸偟鈹嶅┑鐘叉搐閻顭跨捄鐚村姛濞寸厧鑻埞鎴︻敊绾嘲濮涢梺绋跨昂閸婃洟鈥﹂崶顒夋晜闁割偅绻勯鐓庮渻閵堝棙鈷掗柛妯犲洠鈧牗寰勭€ｎ剛鐦堥梺姹囧灲濞佳嗏叿闂備焦鎮堕崝宥咁渻娴犲鏋侀柛鎰靛枛椤懘鏌曢崼婵嗘殜闁?,
        )
        db.add(mem)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "闂傚倸鍊搁崐鎼佸磹閹间礁纾圭€瑰嫭鍣磋ぐ鎺戠倞鐟滄粌霉閺嶎厽鐓忓┑鐐靛亾濞呭棝鏌涙繝鍌涘仴闁哄被鍔戝鏉懳旈埀顒佺閹屾富闁靛牆楠搁獮鏍煟韫囨梻绠為柨婵堝仜椤劑宕煎┑鍫濆Е婵＄偑鍊栫敮鎺斺偓姘ュ姂閸┾偓?},
            db=db,
            user_id="tool-mem-1",
        )
        assert "memories" in result
        assert len(result["memories"]) >= 1
        assert "闂傚倸鍊搁崐鎼佸磹閹间礁纾圭€瑰嫭鍣磋ぐ鎺戠倞鐟滄粌霉閺嶎厽鐓忓┑鐐靛亾濞呭棝鏌涙繝鍌涘仴闁哄被鍔戝鏉懳旈埀顒佺閹屾富闁靛牆楠搁獮鏍煟韫囨梻绠為柨婵堝仜椤劑宕煎┑鍫濆Е婵＄偑鍊栫敮鎺斺偓姘ュ姂閸┾偓? in result["memories"][0]["content"]


@pytest.mark.asyncio
async def test_recall_memory_empty_results(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="tool-mem-2", username="toolmem2", hashed_password="x")
        db.add(user)
        await db.commit()

        result = await execute_tool(
            "recall_memory",
            {"query": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮诲☉妯锋斀闁告洦鍋勬慨銏ゆ⒑濞茶骞楅柟鐟版喘瀵鎮㈤搹鍦紲闂侀潧绻掓慨鐢告倶瀹ュ鈷戠紒瀣儥閸庡秹鏌涙繝鍐疄鐎殿喖顭峰鎾偄閾忚鍟庨梻浣虹帛閸旓箓宕滃鑸靛仧闁哄啫鐗婇埛鎴︽煕閿旇骞楅柛銈傚亾闂備胶绮悧鏇㈠Χ缁嬫鍤曞┑鐘宠壘閸楁娊鏌ｉ弮鍥仩妞ゆ梹娲熼幃宄邦煥閸愵€倝鏌嶈閸撴岸宕欒ぐ鎺戦棷闁挎繂鎷嬮崵鏇㈡煙閹澘袚闁稿鍔楃槐鎾存媴妤犮劍宀搁獮蹇撁洪鍛嫼闂佸憡绋戦敃锕傚煡婢舵劖鐓ラ柡鍥埀顒佺墵楠炲牓濡搁埡浣哄€炲銈嗗笂閼冲爼宕㈤悽鍛娾拺闁告稑锕ゆ慨鍫ユ煟閹垮嫮绡€鐎规洩缍佸畷鐔碱敄閸欍儳鐩?},
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
            {"category": "preference", "content": "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銉︹拻濞达絽婀卞﹢浠嬫煕婵犲喚娈滅€规洘鍨块獮妯兼嫚閼碱剛鏉介梻渚€娼ч…鍫ュ磿閸濆嫷鐒介柕濞炬櫆閻撴洟鏌嶉埡浣告殧濞寸媴濡囩槐鎺楀Ω閵堝洨鐓撳┑顔硷攻濡炰粙骞婇敓鐘参ч柛娑卞枤閳ь剟绠栧娲川婵犲啠鎷瑰┑鐐跺皺閸犳牠宕规ィ鍐╂櫆闁绘劦鍓欑壕顖炴⒑闂堟侗鐓紒鐘冲灩婢规洟顢涢悙绮规嫼闂佽鍨庨崨顖ｅ敹濠电姭鎷冨鍥┬滈梺杞扮缁夌懓鐣烽悢纰辨晣闁绘瑥鎳愭惔濠囨⒒閸屾瑨鍏岄柛瀣ㄥ姂瀹曟洟鏌嗗鍛焾闂佺鍕垫闁轰礁鍊归妵鍕箻鐠虹洅娑㈡煕鐎ｎ偅灏柍缁樻崌瀹曞綊顢欓悾灞借拫闂傚倷绀侀幉锟犲箰妤ｅ啫绐楅幖娣妽閸嬧晠鏌ｉ幋锝嗩棄闂佸崬娲弻锟犲炊閳轰椒鎴烽梺鍛娒幉锛勬崲濠靛鍋ㄩ梻鍫熷垁閵忋倖鐓曢柣鏃傤焾椤ュ绱?},
            db=db,
            user_id="tool-mem-3",
        )
        assert result["status"] == "saved"

        mems = await db.execute(
            select(Memory).where(Memory.user_id == "tool-mem-3")
        )
        saved = mems.scalars().all()
        assert len(saved) == 1
        assert saved[0].content == "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銉︹拻濞达絽婀卞﹢浠嬫煕婵犲喚娈滅€规洘鍨块獮妯兼嫚閼碱剛鏉介梻渚€娼ч…鍫ュ磿閸濆嫷鐒介柕濞炬櫆閻撴洟鏌嶉埡浣告殧濞寸媴濡囩槐鎺楀Ω閵堝洨鐓撳┑顔硷攻濡炰粙骞婇敓鐘参ч柛娑卞枤閳ь剟绠栧娲川婵犲啠鎷瑰┑鐐跺皺閸犳牠宕规ィ鍐╂櫆闁绘劦鍓欑壕顖炴⒑闂堟侗鐓紒鐘冲灩婢规洟顢涢悙绮规嫼闂佽鍨庨崨顖ｅ敹濠电姭鎷冨鍥┬滈梺杞扮缁夌懓鐣烽悢纰辨晣闁绘瑥鎳愭惔濠囨⒒閸屾瑨鍏岄柛瀣ㄥ姂瀹曟洟鏌嗗鍛焾闂佺鍕垫闁轰礁鍊归妵鍕箻鐠虹洅娑㈡煕鐎ｎ偅灏柍缁樻崌瀹曞綊顢欓悾灞借拫闂傚倷绀侀幉锟犲箰妤ｅ啫绐楅幖娣妽閸嬧晠鏌ｉ幋锝嗩棄闂佸崬娲弻锟犲炊閳轰椒鎴烽梺鍛娒幉锛勬崲濠靛鍋ㄩ梻鍫熷垁閵忋倖鐓曢柣鏃傤焾椤ュ绱?
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
        "message": f"闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃秹锝炲┑瀣櫇闁稿矉濡囩粙蹇旂節閵忥絽鐓愰柛鏃€鐗犲畷鎴﹀Χ婢跺鍘搁梺鎼炲劗閺呮稑鐨梻浣虹帛鐢帡鏁冮妷鈺佄﹂柛鏇ㄥ枤閻も偓闂佽宕樺▔娑㈠煕閸儲鈷戦弶鐐村椤︼箓鏌ㄩ弴銊ら偗鐎殿喛顕ч埥澶愬閻樻牓鍔戦弻銊モ攽閸℃ê娅ｅ銈庡墮椤︽壆鎹㈠┑鍡忔灁闁割煈鍠氭禒顓㈡⒑閻熺増鍟炲┑鐐诧躬楠炲啴鏁撻悪鈧弫鍐煥閺囨浜鹃梺缁樺姇閿曨亪寮婚弴鐔风窞闁割偅绻傛慨搴㈢節濞堝灝鏋旈柛銊ㄥ吹濡叉劙骞樼€涙ê顎撻梺鑽ゅ枑濠㈡﹢锝炲澶嬧拺闁告劖褰冨Σ濠氭煟濞戞瑯鍔憂tent}",
    }


async def _delete_memory_handler(
    db: AsyncSession, user_id: str, memory_id: str, **kwargs
) -> dict[str, Any]:
    """Delete a long-term memory by ID."""
    deleted = await delete_memory(db, user_id, memory_id)
    if deleted:
        return {"status": "deleted", "message": "闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃秹婀侀梺缁樺灱濡嫮绮婚悩缁樼厵闁硅鍔﹂崵娆戠磼閻橀潧鏋涙慨濠佺矙瀹曞爼顢楅埀顒侇攰闂備礁婀辨晶妤€顭垮Ο鑲╃焼闁告劏鏂傛禍婊堟煛閸愩劌鈧摜鏁崼鏇熺厽閹兼惌鍠栧顕€鏌熼鐓庢Щ妞ゎ厹鍔戝畷銊╊敇瑜庡В澶愭⒑濮瑰洤鐒洪柛銊╀憾閵嗗啯绻濋崶褎妲┑鐐村灟閸ㄥ湱鐚惧澶嬬厱妞ゆ劑鍊曢弸鏃堟煕濮楀棔閭慨濠冩そ瀹曟粓骞撻幒宥囧嚬缂傚倷娴囬褏鈧凹鍙冨鏌ュ醇閺囩喓鍔堕悗骞垮劚濡盯宕㈤柆宥嗏拺闂傚牊绋撴晶鏇㈡煙瀹勯偊鍎忛摶锝夋煃瑜滈崜鐔奉潖閾忚瀚氶柍銉ㄦ珪閻忔洖顪冮妶搴′簻妞わ妇鏁婚悰顔跨疀濞戞ê绐涘銈嗙墬缁嬫垿寮搁崒鐐粹拺闁告稑锕ユ径鍕煕濡亽鍋㈢€规洜鏁婚獮鎺楀籍閸屾粣绱?}
    return {"error": "闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煕椤垵浜濋柛娆忕箻閺岀喖骞嗛弶鍟冩捇鏌涙繝鍌涘仴闁哄被鍔戝鏉懳旈埀顒佺閹屾富闁靛牆楠搁獮鏍煟韫囨梻绠氶柣蹇斿浮濮婅櫣绮欑捄銊ь唺闂佸憡顭嗛崟顒€鍔呮繝鐢靛Т濞诧箓鍩涢幋鐘电＜閻庯綆鍋勯婊勭節閳ь剟骞嶉鍓э紲闁诲函缍嗛崑鍛暦瀹€鍕厱闁崇懓鐏濋悘鑼偓娈垮櫘閸ｏ絽鐣烽幒鎳虫棃鍩€椤掍胶顩查柣鎰靛墻濞堜粙鏌ｉ幇顖氱毢濞寸姰鍨介弻娑㈠籍閳ь剙鐣濋幖浣歌摕闁绘柨鍚嬮幆鐐淬亜閹扳晛鐏╂い顐ｅ笒铻栭柣姗€娼ф禒锔姐亜閵娿儻韬鐐插暣閸╋繝宕橀鍡床婵犵妲呴崹鎶藉储瑜旈悰顕€宕奸妷锔规嫽婵炶揪绲块幊鎾活敋濠婂牊鐓涢悘鐐额嚙婵倹顨ラ悙瀵稿⒌妞ゃ垺娲熼弫鎰板礋椤撶姷鏆版繝鐢靛仜椤曨厽鎱ㄩ幘顕呮晞闁糕剝绋掗崑鍌炴煛閸ャ儱鐏柣鎾崇箰閳规垿鎮╅懠顒傤唺闂佸憡甯楀姗€鍩為幋锔绘晩闁绘挸绨堕崑鎾寸節濮橆剛鍔﹀銈嗗笂缁讹繝宕箛娑欑厱闁挎繂楠稿▍宥団偓瑙勬礃婵炲﹪寮幇顓炵窞濠电姴瀚弳顐︽⒒娴ｇ鏆遍柟纰卞亰楠炲﹨绠涘☉妯肩暰闂佺粯鍔栭悾顏呯濠婂牊鐓欓柟浣冩珪濞呭懘鏌嶈閸撴岸銆冩径鎰劵闁哄被鍎查埛鎺楁煕鐏炴崘澹橀柍褜鍓熼ˉ鎾跺垝閸喓鐟归柍褜鍓熼悰顔藉緞閹邦厽娅栭梺鍛婃处閸撴艾鈻撴导瀛樷拺缂備焦锚婵洦銇勯弴銊ュ箻缂侇喚绮妶锝夊礃閳哄啫甯楅柣鐔哥矋缁挸鐣峰鍐炬僵閺夊牄鍔屾惔?}
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
            "slots": [{"date": f"2026-04-{i:02d}", "weekday": "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｅ煐閸旀牠宕愰悽鍛婄叆婵犻潧妫濋妤€顭胯閸楁娊寮?, "free_periods": [{"start": "08:00", "end": "22:00", "duration_minutes": 840}], "occupied": []} for i in range(1, 8)],
            "summary": "2026-04-01 闂?2026-04-07 闂?7 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙钃熼柕澶涘閸樹粙姊鸿ぐ鎺戜喊闁告挻宀搁獮鍡涘醇閵夛妇鍘介梺瑙勫礃閹活亪鎳撻崸妤佺厸閻忕偟纭堕崑鎾诲箛娴ｅ憡鍊梺纭呭亹鐞涖儵鍩€椤掆偓绾绢參顢欓幋锔解拻濞达絿鎳撻埢鏇㈡煛閳ь剚娼忛埡鍌涙闂佽法鍠撴慨鎾嫅閻斿摜绠鹃柟瀵稿€戝璺哄嚑閹兼番鍔庨崣鎾绘煕閵夆晩妫戠紒瀣煼閺屽秶绱掑Ο璇茬３濠殿喖锕ュ钘夌暦椤愶箑唯闁靛鍊楅柦鐢电磽閸屾瑧璐伴柛鐘愁殜閹兘鍩℃笟鍥ф婵犵數濮甸懝鐐劔闂備線娼чˇ顓㈠垂濞差亷缍栫€广儱鎳夐弨浠嬫煃閽樺顥滈柣蹇ョ悼缁辨帡顢氶崨顓犱桓濡ょ姷鍋涚换姗€寮婚崱妤婂悑闁糕€崇箲鐎氬ジ姊婚崒娆戣窗闁稿妫濆畷鎴濃槈閵忊€虫濡炪倖鐗楃粙鎺戔枍閻樼偨浜滈柡宥冨妿閳笺儳绱掔拠鍙夘棦闁哄本绋戦埢搴ょ疀閿濆柊锕€鈹戦悙瀛樺剹闁哥姵顨婃俊?98 闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪箻楠炴垿濮€閵堝懐鐤€濡炪倖妫佸Λ鍕償婵犲洦鈷戠憸鐗堝笒娴滀即鏌涢悩鎰佹當闁伙絿鍏樺濠氬Ψ閿旀儳骞嶉梺璇插缁嬫帡鈥﹂崶鈺冧笉闁靛濡囩粻?0 闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎺嶇劍椤斿洭姊绘担鍛婅础闁稿簺鍊濆畷鐢告晝閳ь剟鍩ユ径濞㈢喖鏌ㄧ€ｎ偅婢戦梻浣筋嚙閸戠晫绱為崱妯碱洸闁绘劒璀﹂弫?,
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
                assert "7 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙钃熼柕澶涘閸樹粙姊鸿ぐ鎺戜喊闁告挻宀搁獮鍡涘醇閵夛妇鍘介梺瑙勫礃閹活亪鎳撻崸妤佺厸閻忕偟纭堕崑鎾诲箛娴ｅ憡鍊梺纭呭亹鐞涖儵鍩€椤掆偓绾绢參顢欓幋锔解拻濞达絿鎳撻埢鏇㈡煛閳ь剚娼忛埡鍌涙闂佽法鍠撴慨鎾嫅閻斿摜绠鹃柟瀵稿€戝璺哄嚑閹兼番鍔庨崣鎾绘煕閵夆晩妫戠紒瀣煼閺屽秶绱掑Ο璇茬３濠? in content
                return {"role": "assistant", "content": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｅΟ娆惧殭缂佺姴鐏氶妵鍕疀閹炬惌妫炵紓浣界堪閸婃繈寮婚悢铏圭煓闁割煈鍣崝澶愭⒑閸涘﹦鎳冪紒缁橈耿瀵鈽夐姀鐘殿啋濠德板€愰崑鎾绘倵濮樼厧澧柟顖涙⒐缁绘繈宕堕妸銏″闂備礁鎲＄换鍌溾偓姘煎櫍閸┿垺寰勯幇顓犲幈濠碘槅鍨抽崢褏鏁懜鐐逛簻闁哄倽娉曠粻浼存煃鐟欏嫬鐏╅柍褜鍓ㄧ紞鍡涘磻閸℃稑鍌ㄦい蹇撴噽缁♀偓闂佹眹鍨藉褍鐡紓鍌欒兌缁垶鏁嬪銈庡墮閿曨亪銆佸▎鎾崇鐟滃繘鏁嶅鍫熲拺缂備焦鈼ら鍫濈柈閻犳亽鍔庣粻鏃傛喐閺冨牆钃熺€广儱鐗滃銊╂⒑閸涘﹥灏伴柣鐔叉櫊楠炲啫螣娓氼垱鍍靛銈嗗笒椤﹂亶宕棃娑掓斀妞ゆ柨顫曟禒婊堟煕鐎ｎ偅宕岄柡宀€鍠栭、娆撳Ω閵夛附鎮欏Δ鐘靛亼閸ㄨ櫣鎹㈠☉姘ｅ亾濞戞鎴犳閸欏绠鹃悘鐐插€告慨鍌涱殽閻愭潙鐏寸€规洜鍠栭、娑樞掔亸鏍ㄦ珖闁瑰弶鐡曠粻娑樷槈濞嗗繋绨甸梻浣告惈閸婂摜鑺遍柆宥呯哗濞寸姴顑嗛悡鐔兼煙闁箑澧紒鐙欏洦鐓冪紓浣股戠粈鈧梻鍥ь槹缁绘繃绻濋崒姘间紑缂備胶濮烽崑銈夊蓟閳╁啯濯撮柛婵勫剾閵忋倖鐓冮悷娆忓閻忊晠鏌嶈閸撱劎绱為崱娑樼；闁糕剝绋戦崒銊╂煙闂傚鍔嶉柍閿嬪灴閺屾稑鈽夊鍫濅紣婵犳鍠栭崐鍧楀蓟濞戙垹妫橀柛褎顨呭浼存倵鐟欏嫭绀冩俊鐐扮矙瀵偊骞囬弶鍨€块梺鍝勬川婵兘鎮鹃悙顑跨箚闁绘劦浜滈埀顒佺墵瀹曟繈骞嬮敃鈧崹鍌涚箾瀹割喕绨荤痪鎯ь煼閺屾洘寰勯崱妯荤彆闂?}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                gen = run_agent_loop("闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏犖ч柛鈩冦仦缁剝淇婇悙顏勨偓鏍礉瑜忕划濠氬箣閻樺樊妫滈梺绉嗗嫷娈曢柣鎾存礋閺岀喖鏌囬敃鈧悘閬嶆煕閵堝拋鍎旈柡灞诲€濆鍫曞箰鎼粹€叉樊闂備礁鎼張顒傜矙閹达箑鐓″鑸靛姇绾偓闂佺粯鍔曢崥鈧柛鏍ㄧ墵濮婄粯鎷呯憴鍕╀户闂佸憡顭囬弲顐﹀窗婵犲偆鍚嬮柛銉ｅ妼鎼村﹤鈹戦悙鏉戠仸闁挎洍鏅犲畷顖炲川椤旇桨绨婚梺鍝勫暙濞层倝宕ヨぐ鎺撶厱闁瑰瓨绻勭粔鐑樻叏婵犲啯銇濇鐐村姈閹棃鏁愰崒姘兼綋缂傚倸鍊峰ù鍥敋瑜旈幃褔骞橀幇浣告婵犵數濮电喊宥夊疾閹间焦鐓熸俊顖氱仢閻ㄧ儤銇勯敂鍝勫婵﹥妞藉Λ鍐归妶鍡欐创鐎规洘锕㈤、鏃堝礋椤愩値鍟堟繝?, user, "test-session", db, AsyncMock())
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
        pref = Memory(user_id="ctx-user-1", category="preference", content="闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銏㈢＝闁稿本鐟х拹浼存煕鐎ｎ亜顏紒顔芥閵囨劙骞掗幋锝嗘啺闁诲骸绠嶉崕鍗灻洪敃鍌氱；婵せ鍋撻柡灞界Ч婵＄兘濡烽妷銉ь儓濠电姰鍨奸～澶娒哄鍛潟闁规崘顕х壕鍏肩箾閸℃ê鐏ュ┑陇妫勯—鍐Χ閸愩劌顬堥梺纭呮珪閿氶柣锝囧厴楠炲洭鎮ч崼婵呯敾闂傚倷绶￠崣蹇曠不閹存績鏋旀い鎰堕檮閳锋垿鏌涘☉姗堟敾濠㈣泛瀚伴弻娑氣偓锝庡亜濞搭喚鈧娲忛崕鎶藉焵椤掑﹦绉甸柛鐘愁殜閹繝寮撮姀锛勫幐闂佹悶鍎崕杈ㄤ繆閸忕⒈娈介柣鎰懖閹寸偟鈹嶅┑鐘叉搐閻顭跨捄鐚村姛濞寸厧鑻埞鎴︻敊绾嘲濮涢梺绋跨昂閸婃洟鈥﹂崶顒夋晜闁割偅绻勯鐓庮渻閵堝棙鈷掗柛妯犲洠鈧牗寰勭€ｎ剛鐦堥梺姹囧灲濞佳嗏叿闂備焦鎮堕崝宥咁渻娴犲鏋侀柛鎰靛枛椤懘鏌曢崼婵嗘殜闁?)
        habit = Memory(user_id="ctx-user-1", category="habit", content="婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢铏圭＜闁靛繒濮甸悘鍫㈢磼閻愵剙鍔ゆい顓犲厴瀵鎮㈤悡搴ｇ暰閻熸粍绮撳畷鐢告偄閾忓湱锛滈梺缁橆焾瀹曠敻鎮惧ú顏呯厸閻忕偛澧藉ú鎾煕閵婏箑鍔ら柣锝囧厴瀹曞爼鍩℃繝鍌涙毆濠电姷鏁告慨顓㈠箯閸愵喖绀冮柕濞у洨宕滅紓鍌氬€烽懗鍓佸垝椤栫偞鍎庢い鏍仧瀹撲焦鎱ㄥ璇蹭壕闂佽鍠氶崗姗€鐛澶樻晩闁绘挸娴风槐浼存⒒娴ｇ瓔鍤欏Δ鐘虫倐閹ê顫濋澶屽數濠碘槅鍨伴惃鐑藉磻閹炬剚娼╅柣鎾抽閳峰姊洪幐搴ｇ畼闁稿鐩崺鐐哄箣閻橆偄浜鹃柨婵嗛娴滄粍绻涢崼鐔虹畺缂佺粯绋掑蹇涘礈瑜嶉崺宀勬⒑閸濄儱娅忛柛瀣噽缁顓兼径濠傚敤閻熸粌顦靛?闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪箻楠炴垿濮€閵堝懐鐤€濡炪倖妫佸Λ鍕償婵犲洦鈷戠憸鐗堝笒娴滀即鏌涢悩鎰佹當闁伙絿鍏樺濠氬Ψ閿旀儳骞嶉梺璇插缁嬫帡鈥﹂崶鈺冧笉闁靛濡囩粻?)
        db.add_all([pref, habit])
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銏㈢＝闁稿本鐟х拹浼存煕鐎ｎ亜顏紒顔芥閵囨劙骞掗幋锝嗘啺闁诲骸绠嶉崕鍗灻洪敃鍌氱；婵せ鍋撻柡灞界Ч婵＄兘濡烽妷銉ь儓濠电姰鍨奸～澶娒哄鍛潟闁规崘顕х壕鍏肩箾閸℃ê鐏ュ┑陇妫勯—鍐Χ閸愩劌顬堥梺纭呮珪閿氶柣锝囧厴楠炲洭鎮ч崼婵呯敾闂傚倷绶￠崣蹇曠不閹存績鏋旀い鎰堕檮閳锋垿鏌涘☉姗堟敾濠㈣泛瀚伴弻娑氣偓锝庡亜濞搭喚鈧娲忛崕鎶藉焵椤掑﹦绉甸柛鐘愁殜閹繝寮撮姀锛勫幐闂佹悶鍎崕杈ㄤ繆閸忕⒈娈介柣鎰懖閹寸偟鈹嶅┑鐘叉搐閻顭跨捄鐚村姛濞寸厧鑻埞鎴︻敊绾嘲濮涢梺绋跨昂閸婃洟鈥﹂崶顒夋晜闁割偅绻勯鐓庮渻閵堝棙鈷掗柛妯犲洠鈧牗寰勭€ｎ剛鐦堥梺姹囧灲濞佳嗏叿闂備焦鎮堕崝宥咁渻娴犲鏋侀柛鎰靛枛椤懘鏌曢崼婵嗘殜闁? in context
        assert "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢铏圭＜闁靛繒濮甸悘鍫㈢磼閻愵剙鍔ゆい顓犲厴瀵鎮㈤悡搴ｇ暰閻熸粍绮撳畷鐢告偄閾忓湱锛滈梺缁橆焾瀹曠敻鎮惧ú顏呯厸閻忕偛澧藉ú鎾煕閵婏箑鍔ら柣锝囧厴瀹曞爼鍩℃繝鍌涙毆濠电姷鏁告慨顓㈠箯閸愵喖绀冮柕濞у洨宕滅紓鍌氬€烽懗鍓佸垝椤栫偞鍎庢い鏍仧瀹撲焦鎱ㄥ璇蹭壕闂佽鍠氶崗姗€鐛澶樻晩闁绘挸娴风槐浼存⒒娴ｇ瓔鍤欏Δ鐘虫倐閹ê顫濋澶屽數濠碘槅鍨伴惃鐑藉磻閹炬剚娼╅柣鎾抽閳峰姊洪幐搴ｇ畼闁稿鐩崺鐐哄箣閻橆偄浜鹃柨婵嗛娴滄粍绻涢崼鐔虹畺缂佺粯绋掑蹇涘礈瑜嶉崺宀勬⒑閸濄儱娅忛柛瀣噽缁顓兼径濠傚敤閻熸粌顦靛?闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪箻楠炴垿濮€閵堝懐鐤€濡炪倖妫佸Λ鍕償婵犲洦鈷戠憸鐗堝笒娴滀即鏌涢悩鎰佹當闁伙絿鍏樺濠氬Ψ閿旀儳骞嶉梺璇插缁嬫帡鈥﹂崶鈺冧笉闁靛濡囩粻? in context


@pytest.mark.asyncio
async def test_warm_memories_in_context(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-2", username="ctxtest2", hashed_password="x")
        db.add(user)
        decision = Memory(user_id="ctx-user-2", category="decision", content="婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋婵嗘暏婵＄偑鍊栭幐楣冨磻閻斿吋鍋╅柣鎴烆焽缁犻箖鎮楅悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁瑰啿绻樺畷鏇㈩敃閿旇В鎷绘繛鎾村焹閸嬫挻绻涙担鍐叉硽閸ヮ剦鏁囬柕蹇曞Х閿涚喖姊虹憴鍕姸婵☆偄瀚伴幃鐐哄垂椤愮姳绨婚梺鍦劋閸ㄧ敻寮冲▎鎾寸厱婵﹩鍓氱拹锛勭磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽敃浣烘闂佽瀛╅鏍闯椤曗偓瀹曟娊鏁愰崨顖涙闂佸湱鍎ら崵鈺呭箳閹存梹鐎婚梺璇″瀻閸愮偓浜ら梻鍌欑閻ゅ洭锝炴径鎰瀭闁秆勵殔閺勩儵鏌曟径鍡樻珔妤犵偑鍨烘穱濠囧Χ閸屾矮澹曠紓鍌欒兌婵儳鐣烽悽鍨潟闁规儳顕悷褰掓煕閵夋垵瀚禍楣冩⒒娴ｈ姤銆冩繛鏉戞喘椤㈡俺顦规い銏″哺閺佹劙宕卞▎妯荤カ闂佽鍑界徊浠嬫倶濮樿泛鐤炬繝闈涱儐閳锋垿鏌熺粙鎸庢崳缂佺姵鎸绘穱濠囶敃椤愩垹绫嶉悗?)
        db.add(decision)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋婵嗘暏婵＄偑鍊栭幐楣冨磻閻斿吋鍋╅柣鎴烆焽缁犻箖鎮楅悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁瑰啿绻樺畷鏇㈩敃閿旇В鎷绘繛鎾村焹閸嬫挻绻涙担鍐叉硽閸ヮ剦鏁囬柕蹇曞Х閿涚喖姊虹憴鍕姸婵☆偄瀚伴幃鐐哄垂椤愮姳绨婚梺鍦劋閸ㄧ敻寮冲▎鎾寸厱婵﹩鍓氱拹锛勭磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽敃浣烘闂佽瀛╅鏍闯椤曗偓瀹曟娊鏁愰崨顖涙闂佸湱鍎ら崵鈺呭箳閹存梹鐎婚梺璇″瀻閸愮偓浜ら梻鍌欑閻ゅ洭锝炴径鎰瀭闁秆勵殔閺勩儵鏌曟径鍡樻珔妤犵偑鍨烘穱濠囧Χ閸屾矮澹曠紓鍌欒兌婵儳鐣烽悽鍨潟闁规儳顕悷褰掓煕閵夋垵瀚禍楣冩⒒娴ｈ姤銆冩繛鏉戞喘椤㈡俺顦规い銏″哺閺佹劙宕卞▎妯荤カ闂佽鍑界徊浠嬫倶濮樿泛鐤炬繝闈涱儐閳锋垿鏌熺粙鎸庢崳缂佺姵鎸绘穱濠囶敃椤愩垹绫嶉悗? in context


@pytest.mark.asyncio
async def test_no_memories_still_works(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="ctx-user-3", username="ctxtest3", hashed_password="x")
        db.add(user)
        await db.commit()

        context = await build_dynamic_context(user, db)
        # Should still have time info, just no memory section
        assert "闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾缁愭鏌熼柇锕€鏋涢柛銊︾箞楠炴牕菐椤掆偓閻忣亝绻涢崨顖毿ｅǎ鍥э躬婵″爼宕ㄩ鍏碱仩缂傚倷鑳舵慨鎶藉础閹惰棄钃熸繛鎴炃氬Σ鍫熸叏濡も偓閻楀﹪寮幆褉鏀介柣鎰级閸ｈ棄鈹戦悙鈺佷壕闂備礁鎼惌澶屽緤閸婄喓浜芥繝鐢靛仜濡瑩宕曢崘娴嬫灁妞ゆ挾濮风壕钘夈€掑顒佹悙濞存粍绮庣槐鎺撳緞婵犲嫮楔閻庢鍠涢褔鍩ユ径鎰潊闁冲搫鍊瑰▍鍥⒒娴ｇ懓顕滅紒璇插€歌灋婵炴垟鎳為崶顒€惟闁冲搫鍊甸幏? in context


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
            summary="婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢鍏尖拻閻庣數顭堟俊浠嬫⒑閸濆嫭鍣虹紒璇茬墦瀵寮撮悢椋庣獮闂佺硶鍓濊摫闁绘繐绠撳鐑樻姜閹殿噮妲梺鍝ュ枑閹稿啿顕ｆ繝姘ч柛姘ュ€曞﹢閬嶅焵椤掑﹦绉甸柛瀣噹椤潡骞掑Δ浣叉嫼缂備礁顑嗛娆撳磿閹扮増鐓欓柣鐔哄閸犳ɑ顨ラ悙鎻掓殻闁圭锕ュ鍕幢濡棿绨撮梻鍌欑濠€閬嶁€﹂崼鈶╁亾濞戞帗娅婄€殿喗濞婇幃娆撴倻濡攱瀚藉┑鐐舵彧缂嶄線藟閹惧鈻旈柤纰卞墰绾句粙鏌涚仦鍓р姇闁汇劍鍨块弻娑㈠箳閹惧磭鐟ㄩ梺瀹狀嚙闁帮綁鐛鈧幖褰掝敃閵堝倸浜炬い鎺戝閸婂灚顨ラ悙鑼虎闁告梹宀搁弻鐔风暋闁箑鍓板銈庡幖濞差參宕洪敓鐘插窛妞ゆ挾濞€閻涙捇姊绘担绋款棌闁稿鎳愮划娆撳箣閻愭壆绠氶梺鍏间航閸庡磭绮绘ィ鍐╃厱妞ゆ劧绲块埥澶愭煟韫囨挸绾ч柟渚垮妽缁绘繈宕ㄩ鍛摋闂備胶鎳撳鍫曞箰閸愯尙鏆﹂柣鏃傗拡閺佸棝鏌涚仦鎯ь棜闁哄绻樺濠氬磼濞嗘垵濡介梺璇″枛閻栫厧鐣烽悷鎳婃椽顢旈崨顓濈暗闂備浇娉曢崰鎾存叏娴兼潙鐒垫い鎴ｆ硶椤︼附銇勯锝囩疄闁硅櫕绮撻幃浠嬫濞戞锕傛⒑鐠囨煡顎楃紒鐘茬Ч瀹曟洟鏌嗗鍛枃闂佽婢橀崣鎾诲炊椤忓秵鈻屾繝娈垮枛閿曘儱顪冮挊澹╂盯宕橀妸銏☆潔闁哄鐗勯崜閬嶅Χ婢跺鎷虹紓浣割儏鐏忓懘寮ㄧ紒妯镐簻闁靛鍎诲銉╂煟閿濆洤鍘存い銏＄☉閳藉顫濇潏鈺傤潓闂傚倷鐒﹂幃鍫曞磿椤栫偛绀夐悘鐐插⒔椤╅攱銇勯弽顐沪闁抽攱鍨块弻鐔兼嚃閳轰椒绮堕梺鍛婃⒐閿曘垽寮诲☉銏犳閻犳亽鍔庢导鍥╃磽娓氬洤鏋涢柣妤佹尭閻ｅ嘲顫滈埀顒勩€佸▎鎾村仼閻忕偠妫勬俊鍥⒒閸屾瑨鍏岀痪顓炵埣瀹曟粌鈹戠€ｃ劉鍋撻崘顔煎窛闁哄鍨舵潏鍫ユ⒑閹稿海绠撴い锔垮嵆閹€斥槈濡繐缍婇弫鎰板川椤旇棄鏋戦柣搴㈢⊕缁诲牆顫忛悜妯侯嚤婵炲棙鍨硅摫缂傚倷娴囬褔鎮ч崱娑欏仼鐎瑰嫰鍋婂銊╂煃瑜滈崜鐔兼偘椤曗偓瀹曞崬顫濋崗澶诡亝绻濋悽闈涗粶闁瑰啿绻橀妴鍐醇閵忊槅娼熼梺瑙勫礃椤曆呭閸忓吋鍙忔慨妤€妫楅崢鎾煕鐎ｎ偅宕屾鐐寸墬閹峰懘宕妷褍鐐婂┑鐘愁問閸犳鈥﹂崼婵冩灃婵炴垶姘ㄩ悳缁樹繆閵堝懏鍣洪柣鎾寸洴閺屾盯濡烽姀鈩冪彅闂傚顑嗙换?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌熼梻瀵割槮缁炬儳缍婇弻鐔兼⒒鐎靛壊妲紒鐐劤缂嶅﹪寮诲☉銏╂晝闁挎繂妫涢ˇ銉х磽娴ｆ彃浜炬繝銏ｅ煐閸旀宕ｉ幘缁樼厱闁靛绲芥俊鍧楁煃閽樺妯€闁哄矉缍侀獮鎺楀箣閻樿京椹抽梻渚€娼уú銈団偓姘嵆閻涱噣骞掑Δ鈧獮銏′繆閻愭潙鍔ゆい銉﹀哺濮婂宕掑▎鎴М闂佺濮ょ划鎾崇暦娴兼潙绠涙い鎾跺Х椤旀洘绻濋悽闈浶㈡繛灞傚€楃划璇差潩椤戦敮鍋撻幒鎴僵闁挎繂鎳嶆竟鏇熶繆閻愵亜鈧垿宕瑰ú顏呭剮妞ゆ牜鍋涚粻鏍ㄧ箾閸℃ɑ灏紒鐙欏洦鐓欓悗娑欘焽缁犳挻銇勯妷銉█婵﹤顭峰畷鎺戔枎閹搭厽袦闂備浇顫夌粊鎾焵椤掑啰袦婵炲樊浜濋弲婵嬫煕鐏炵偓鐨戦柨娑欑洴濮婃椽宕烽鐐插闂佹悶鍊х粻鎾诲极閹版澘鐐婇柕濞垮劤瑜板瓨绻濋悽闈涗沪婵炲吋鐟╅、鏍幢濞戝磭绋忛悗骞垮劚椤︿即鍩涢幋锔界厱婵犻潧妫楅鈺呮煛閸℃鎳囬柡灞剧⊕缁绘繈宕橀埡浣插亾閹扮増鐓熼幖娣妽閺佸崬菐閸パ嶈含闁诡喗鐟╅、鏃堝礋閵娿儰澹曢梺鍝勭▉閸樿偐绮婚弶搴撴斀闁绘ê鐤囨竟妯肩磼閻樺磭澧甸柡灞剧〒娴狅箓鎮欓鍌涱吇闂?,
        )
        db.add(summary)
        await db.commit()

        context = await build_dynamic_context(user, db)
        assert "闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪Ч濠€渚€姊虹紒妯虹伇婵☆偄瀚板鍛婄瑹閳ь剟寮婚悢鍏尖拻閻庨潧澹婂Σ顕€姊虹粙鑳潶闁告柨閰ｉ獮澶愬箹娴ｅ憡顥濋柣鐘充航閸斿秴鈻撴ィ鍐┾拺闁圭娴风粻鎾淬亜閿旇鐏﹂柣娑卞櫍婵偓闁炽儴灏欑粻姘渻閵堝棛澧瑙勬礋楠炲繘鍩勯崘顏嗩啎闂佸憡鐟ラˇ浼村磹閹邦厽鍙忓┑鐘叉噺椤忕娀鏌涢弽銊у⒌鐎殿喗鎸抽幃娆徝圭€ｎ偄鐝堕梻鍌氬€风粈渚€骞夐敓鐘插瀭闁汇垻鏁哥粈濠傗攽閻樻彃鈧寮抽敃鍌涚厽闁靛繒濮甸崯鐐烘煛閸涱喚绠為柡灞剧〒娴狅箓宕滆濡插牊绻? in context
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

WEEKDAY_NAMES = ["闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｅ煐閸旀牠宕愰悽鍛婄叆婵犻潧妫濋妤€顭胯閸楁娊寮?, "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｅ煐閸旀牠宕愰悽鍛婄叆婵犻潧妫濋妤€顭胯瑜板啴鍩?, "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｅ煐閸旀牠宕愰悽鍛婄叆婵犻潧妫濋妤€顭胯婢瑰棛妲?, "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｅ煐閸旀牠宕愰崼鏇熺厽闁归偊鍠楅弳鈺呮煕?, "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｅ煐閸旀牠宕愰悽鍛婄叆婵犻潧妫濋妤€顭胯瑜板啴鍩?, "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｆ硾婢跺洭宕戦幘璇茬濠㈣泛锕ｆ竟鏇㈡⒒娴ｅ憡鍟炴繛璇х畵瀹曟垿宕卞☉娆忎簵?, "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎾跺Х閸橆垶姊绘繝搴′簻婵炶濡囩划娆撳箣閻樼數鐒兼繝銏ｆ硾婢跺洭宕戦幘鑽ゅ祦闁割煈鍠栨慨搴ㄦ⒑?]


async def build_dynamic_context(user: User, db: AsyncSession) -> str:
    """Build the dynamic portion of the system prompt."""
    now = datetime.now(timezone.utc)
    today = now.date()
    weekday = today.isoweekday()

    parts: list[str] = []
    parts.append(f"闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾缁愭鏌熼柇锕€鏋涢柛銊︾箞楠炴牕菐椤掆偓閻忣亝绻涢崨顖毿ｅǎ鍥э躬婵″爼宕ㄩ鍏碱仩缂傚倷鑳舵慨鎶藉础閹惰棄钃熸繛鎴炃氬Σ鍫熸叏濡も偓閻楀﹪寮幆褉鏀介柣鎰级閸ｈ棄鈹戦悙鈺佷壕闂備礁鎼惌澶屽緤閸婄喓浜芥繝鐢靛仜濡瑩宕曢崘娴嬫灁妞ゆ挾濮风壕钘夈€掑顒佹悙濞存粍绮庣槐鎺撳緞婵犲嫮楔閻庢鍠涢褔鍩ユ径鎰潊闁冲搫鍊瑰▍鍥⒒娴ｇ懓顕滅紒璇插€歌灋婵炴垟鎳為崶顒€惟闁冲搫鍊甸幏娲⒑閸︻収鐒炬繛瀵稿厴婵℃挳骞掑Δ浣哄幈闂佺粯锚绾绢厽鏅堕悽纰樺亾濞堝灝鏋涙い顓㈡敱娣囧﹪骞栨担鑲濄劑鏌曡箛濠冾潑婵炲吋姊圭换婵嬫偨闂堟稐绮跺┑鈽嗗亝閻熲晠寮€ｎ偆绡€婵炲牆鐏濋弸銈嗙節閳ь剙顕ｇ€?strftime('%Y-%m-%d %H:%M')}闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢琛″亾濞戞瑯鐒界紒鐘劦閺岋綁寮幐搴＆闂佸搫鐭夌换婵嗙暦閻撳簶妲堥柟鐑樺灣婢规洖顪冮妶鍐ㄥ鐎规挻鎽朅Y_NAMES[weekday - 1]}闂?)

    if user.current_semester_start:
        delta = (today - user.current_semester_start).days
        week_num = delta // 7 + 1
        parts.append(f"闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾缁愭鏌熼柇锕€鏋涢柛銊︾箞楠炴牕菐椤掆偓閻忣亝绻涢崨顖毿ｅǎ鍥э躬婵″爼宕ㄩ鍏碱仩缂傚倷鑳舵慨鎶藉础閹惰棄钃熸繛鎴炃氬Σ鍫熸叏濡も偓閻楀﹪寮幆褉鏀介柣鎰级閸ｈ棄鈹戦悙鈺佷壕闂備礁鎼惌澶屽緤閸婄喓浜界紓浣哄亾婵姤銇旂粙鍟冩帒鐣濋崟顑芥嫼缂備礁顑嗛娆撳磿閹扮増鐓欓柛娑橈攻閸婃劙鏌涢埞鍨姕鐎垫澘瀚伴獮鍥敆閸屻倕鏁堕梻鍌欑閸氬绂嶆禒瀣？婵炲樊浜滈悞鍨亜閹哄棗浜剧紓浣割槹閹告娊宕洪悙鍝勭闁挎棁妫勬禍鐟邦渻閵堝棗濮︽繝鈶╁亾婵犮垼顫夊ú鐔奉潖缂佹ɑ濯撮柤鎭掑劤閵嗗﹪姊洪崫銉バｉ柟绋款煼楠炲牓濡搁埡鍌氫缓缂備礁顑堝▔鏇㈠蓟瑜嶉—鍐Χ閸℃鐟愰梺缁樺釜缁犳挸鐣烽敐鍫㈢杸闁哄啠鍋撻柛娆忕箲娣囧﹪鎮欐０婵嗘婵炲瓨绮屾晶鐣屾閹烘梻纾奸柕蹇曞Т缁犳椽姊虹拠鈥虫灈闁稿﹥鎮傞幃楣冩倻閽樺宓嗛梺闈涚箳婵兘鎮块崨瀛樷拺閻熸瑥瀚徊濠氭煟閿濆浂娼巏_num}闂?)

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

    parts.append("\n婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾剧粯绻涢幋娆忕労闁轰礁顑嗛妵鍕箻鐠虹儤鐎鹃梺鍛婄懃缁绘﹢寮婚悢铏圭＜闁靛繒濮甸悘宥夋⒑閸濆嫭鍣虹紒璇茬墦瀵寮撮姀鐘诲敹濠电姴鐏氶崝鏍懅婵犵鍓濋〃鍛村箠韫囨洘宕叉繝闈涱儏椤懘鏌ㄥ┑鍡樺櫧闁告﹩鍋婂娲川婵犲啠鎷归梺缁橆殘婵挳鎮鹃悜钘夊嵆闁绘垵妫楅幃鎴炵節閵忥絾纭炬い鎴濇喘瀹曘垽鏌嗗鍡忔嫼闂佸憡绻傜€氼參宕掗妸鈺傜厱闁哄倹瀵у﹢浼存煛閸涱厾鍩ｆい銏＄洴閹瑧鈧數顭堝铏節閻㈤潧浠﹂柛銊ョ埣閺佸啴鍩℃担鍕剁秮閹煎綊宕烽鐙呯床闂佸搫顦悧鍕礉瀹€鈧划顓☆樄闁哄苯绉烽¨渚€鏌涢幘鍗炲缂佽京鍋ゅ畷鍗炍熺喊杈ㄩ敜闂備礁澹婇崑鍛洪弽顐㈩棜闁圭娴风弧鈧繝鐢靛Т閸婂綊宕抽悾宀€妫?)
    if not courses and not tasks:
        parts.append("- 闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹潡顢氶埀顒勫蓟閿濆憘鏃堝焵椤掑嫭鍋嬪┑鐘叉搐閻鐓崶銊р姇闁绘挻鐟х槐鎾存媴闂堟稓浠奸梺鍝勵儑閸犳牠寮诲☉姘ｅ亾閿涘崬瀚悵姘舵⒑閸濆嫭婀版繛鍙夘焽閹广垹鈽夐姀鈥斥偓閿嬨亜閹哄秷鍏岀憸鏉挎噽缁?)
    else:
        for course in courses:
            location = f" @ {course.location}" if course.location else ""
            parts.append(f"- {course.start_time}-{course.end_time} {course.name}{location}闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍛婄秶濡わ絽鍟宥夋⒑缁嬫鍎忔い鎴濐樀瀵鎮㈢粙娆惧殼闂佸搫顦伴崹鎶藉窗婵犲洦鈷戦弶鐐村椤︼附銇勯幋婵囧枠闁糕斁鍋撳銈嗗笒閸犳艾顭囬幇顓犵闁告瑥顦辨晶顏堟偂閵堝鐓忓┑鐐靛亾濞呭棝鏌涙惔銏╂畷缂佺粯鐩畷鍗炍熺拠鏌ョ€洪梻浣侯焾閿曪箓寮繝姘摕闁靛鍎弨浠嬫煕閳╁厾顏勨枍閿濆拋娓婚柕鍫濈箳閸掓壆鐥紒銏犲箻婵″弶鍔欓獮鎺懳旈埀顒勬倿?)
        for task in tasks:
            status_mark = "闂? if task.status == "completed" else "闂?
            parts.append(f"- {task.start_time}-{task.end_time} {task.title}闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢琛″亾濞戞瑯鐒界紒鐘劦閺岋綁寮幐搴＆闂佸搫澶囬崜婵嗩嚗閸曨厸鍋撻敐搴′簻闁汇劉鏆唗us_mark}闂?)

    # User preferences
    preferences = user.preferences or {}
    if preferences:
        parts.append("\n闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴妤€浜惧銈庝簻閸熸潙鐣疯ぐ鎺濇晪闁告侗鍨版慨娲⒒娴ｄ警娼掗柛鏇炵仛閻ｅ墎绱撴担鎻掍壕婵犮垼娉涙径鍥磻閹捐崵宓侀柛顭戝枛婵骸顪冮妶蹇撶槣闁搞劏娉涢锝嗗閺夋嚦銊╂煥閺傚灝鈷旀い鏃€娲熷娲偡閹殿喗鎲奸梺鑽ゅ枂閸庣敻骞冨鈧崺锟犲礃椤忓拑绱￠梻浣筋嚃閸ㄥ骸鐣濋埀顒勫触鐎ｎ喗鈷戠紓浣股戦幆鍕煕鐎ｎ亷宸ラ柣锝囧厴瀹曞ジ寮撮悙宥佹櫊閺屻劑寮村Δ鈧禍楣冩⒑閽樺顏╅柕鍫㈩焾椤繘鎼归崷顓犵厯濠电偛妫欓崕鎶藉礈椤撱垺鈷戦柛娑橈攻閳锋劙鏌涢妸銉т虎妞?)
        if "earliest_study" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫆闁芥ê顦純鏇㈡⒒娴ｅ憡鍟為柛鏃撶畵瀹曚即寮介銏╂婵犵數濮电喊宥夋偂濞嗘挻鐓曢柟鐐殔閹冲海绮敓鐘斥拺缂備焦蓱鐏忎即鏌ｉ埡濠傜仸鐎殿喛顕ч埥澶愬閻樼數鏉搁梻浣告啞閹哥兘鎳楅幆鐗堟噷婵犵數濮烽弫鎼佸磻濞戙垹绠犻幖娣妼缁犵娀鐓崶銊р槈濡楀懘姊洪崨濠冨闁搞劍澹嗙划濠氬箮閼恒儳鍘搁梺绋挎湰缁嬫垿顢氬鍫熺厽閹肩补鈧枼鎸冪紓浣介哺閹稿骞忛崨鏉戠闁圭粯甯掓竟鍫ユ⒒娴ｇ懓顕滄繛璇ч檮缁傚秹顢旈崼銏犵ウ闂佸憡鍔﹂崰鏍偂濞戙垺鐓曟繛鎴濆船閺嬬喖鏌涙惔顔荤盎妞ゎ亜鍟存俊鍫曞幢濡も偓琚濋梻浣侯焾椤戝懘骞婇幘璇茬劵闁割偅娲橀埛鎺楁煕鐏炴崘澹橀柍褜鍓氶幃鍌氱暦閹版澘绠瑰ù锝呮憸閿涙瑩姊鸿ぐ鎺擄紵缂佲偓娴ｅ搫顥氶柣鐔稿櫞瑜版帗鍋愮€瑰壊鍠栭崜鎵磽娴ｅ搫孝闁诲繑宀告俊鐢稿礋椤斿墽鏉搁梺鍦亾閹苯螞閳ユ剚娓婚柕鍫濋娴滄繃绻涢懠顒€鏋涚€殿喖顭烽弫鎰緞婵炩懇鏅犻弻銊╁籍閸屾稑娈岄悷婊勬緲缁鳖柅ferences['earliest_study']}")
        if "latest_study" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫆闁芥ê顦純鏇㈡⒒娴ｅ憡鍟為柛鏃撶畵瀹曚即寮介銏╂婵犵數濮电喊宥夋偂濞嗘挻鐓曢柟鐐殔閹冲海绮敓鐘斥拺缂備焦蓱鐏忎即鏌ｉ埡濠傜仸鐎殿喛顕ч埥澶娢熼柨瀣垫綌闂備礁鎲￠〃鍫ュ磻閻愮儤鍊堕柡鍥╁枔缁♀偓闂侀潧楠忕紞鍡楊焽閹扮増瀚呴梺顒€绉甸悡蹇涙煕閵夋垵鍠氭导鍐ㄎ旈悩闈涗沪閻㈩垪鈧剚鍤曟い鎺戝缁犱即骞栨潏鍓у矝闁稿鎹囧畷婊嗩槾缁炬崘妫勯湁闁挎繂鎳庨ˉ蹇涙煕鎼达紕绠婚柡灞诲姂瀵挳濡搁妶澶婁粣婵°倗濮烽崑娑㈠疮閹绢喖鏄ラ柨鐔哄Т瀹告繃銇勯弮鍥棄闁告梹甯楁穱濠囨倷椤忓嫧鍋撻弽顓炵闁挎洖鍊哥壕濠氭煕濞戞瑥顥愰柛娆撶畺濮婂宕掑顑藉亾閹间礁纾归柟闂寸绾惧綊鏌熼梻瀵割槮缁炬儳缍婇弻鐔兼⒒鐎靛壊妲紒鎯у⒔閹虫捇婀侀梺缁樏Ο濠囧磿韫囨洜纾奸柣妯垮皺娴犳盯鏌曢崶褍顏紒鐘崇洴楠炴﹢骞栭鐕傜磼濠碉紕鍋戦崐銈夊磻閸涱劶娲偄閻撳氦鎽曢梺鎸庣箓椤︻垱鍎梻浣瑰濮婂骞婇幘骞夸汗鐎殿喗浜癴erences['latest_study']}")
        if "lunch_break" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极閹剧粯鍋愭い鏃傛嚀娴滈箖鏌涢幇闈涙灈鐎瑰憡绻堥幃妤€鈽夊▍顓т簼缁傚秹鏌嗗鍡忔嫼闂佸憡绋戦敃锝囨闁秵鐓曢柕濞炬櫃閹查箖鏌ㄥ┑鍫濅槐鐎殿喗鎸虫慨鈧柨娑樺鐢箖姊绘担绋款棌闁稿鎳愰幑銏狀吋閸涘偊缍€閵囨劙骞掗幘璺哄箰闂備礁鎲＄划鍫㈢矆娴ｈ娅犳い鏍仦閻撴瑥銆掑顒備虎濠碘€炽偢閺屽秶鎲撮崟顐や紝閻庤娲栭妶鎼佸箖閵忋倕浼犻柕澶堝€楃粈鍧甧ferences['lunch_break']}")
        if "min_slot_minutes" in preferences:
            parts.append(f"- 闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫆闁芥ê顦純鏇㈡⒒娴ｅ憡鍟為柛鏃撶畵瀹曚即寮介銏╂婵犵數濮电喊宥夋偂濞嗘挻鐓曢柟鐐殔閹冲海绮敓鐘斥拺缂備焦蓱鐏忕敻鏌涢悩鍐插濠碉紕鏁诲畷鐔碱敍濮橀硸鍟嬫繝寰锋澘鈧劙宕戦幘缁樼厱闁绘洑绀佹禍鐐电磼椤旂⒈鐓肩€规洦鍋婂畷鐔煎Ω閿旇姤婢戦梻鍌欒兌缁垶鏁冮埡鍛；闁告洦鍓涢々鏌ユ煟閹伴潧澧扮紒鐘荤畺閺岀喖鎮欓浣虹▏闂佺粯甯掔紞濠囧蓟濞戞埃鍋撻敐搴′簼閻忓繒鏁婚弻宥堫檨闁告挻宀搁、娆撳冀椤撶偤妫峰銈嗘磵閸嬫挾鈧娲橀崹鍓佹崲濠靛纾兼繝濠傚椤旀洖鈹戦悩缁樻锭闁稿﹥鎮傞獮澶愭晸閻樿尙锛涢梺鍛婃处閸ㄩ亶鎮￠弴銏＄厵闁诡垎鍐╂瘣缂備胶瀚忛崨顔间粡閻熸粌绉归崺鐐哄箣閿旇棄浜归梺鍓茬厛閸嬪懎袙閸曨垱鈷戠紒瀣儥閸庢劙鏌ｉ埡濠傜仸妤犵偛鍟抽ˇ鍓佺磼閻樺磭鈽夐柍钘夘樀瀵粙濡堕崨顒€顥氶梻浣侯焾閻ジ宕曢幇鏉挎瀬濠电姴娲﹂悡鐔兼煙娴煎瓨娑у褏绮换娑㈡嚃閳轰焦鐏堝┑顔硷工閹碱偅鏅ラ梺鎼炲劀閸愬墽鈧挳姊绘担鐟板濞存粎鍋涢埢鎾愁瀶閸ф姀rences['min_slot_minutes']}闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎺嶇劍椤斿洭姊绘担鍛婅础闁稿簺鍊濆畷鐢告晝閳ь剟鍩ユ径濞㈢喖鏌ㄧ€ｎ偅婢戦梻浣筋嚙閸戠晫绱為崱妯碱洸闁绘劒璀﹂弫?)
        if "school_schedule" in preferences:
            parts.append("- 闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃秹婀侀梺缁樺灱濡嫮绮婚悩缁樼厵闁硅鍔﹂崵娆戠磼閻橀潧鏋涢柡灞诲姂閹垽宕崟鎴秮閺屾稓鈧綆浜滈埀顒€娼″濠氬Ω閳哄倸浜滈梺鍛婄箓鐎氬懘濮€閵堝棛鍘遍柣蹇曞仩椤曆勬叏閸岀偞鐓涢悘鐐靛亾缁€瀣偓瑙勬礈閸樠囧煘閹达箑鐐婄憸蹇涙偘閳哄啰纾藉ù锝囨嚀閸斻倕顭胯缁瑥鐣烽幋锕€绠婚悹鍥у棘閿曞倹鐓曢柡鍥ュ妼閻忕姷绱掗銏⑿ч柡灞剧洴婵＄兘骞嬪┑鍡樻闂佺瀵掓禍鐐垫閹捐纾兼繛鍡樺焾濡差喖顪冮妶鍡楃仴闁硅櫕锕㈠顐﹀礃椤曞懏鏅滈梺鍓插亝缁诲棝骞楅弴銏♀拺缂備焦蓱閳锋帡鏌嶅畡鎵ⅵ鐎殿噮鍋婂畷鍫曞煛閸屾碍鐎鹃柣搴＄畭閸庨亶藝娴兼潙纾归柛顐ｆ礃閻撳啴鏌嶆潪鎵槮闁哄棙娲滅槐鎺旀嫚閸欏妫﹂梺鍝勭焿缂嶄線鐛崶顒夋晣闁绘劗鏁搁妶鐑芥⒒娓氣偓閳ь剛鍋涢懟顖涙櫠椤曗偓閺岋綀绠涢弮鍌滅杽闂佹寧绻勯崑鐘电不濞戞ǚ妲堟繛鍡楃箲椤撳ジ姊绘笟鈧褔鎮ч崱娑樼閻庯綆鈧厽绋戦…銊╁醇閻斿搫骞楅梺鐟板悑閹矂宕瑰畷鍥╃焾闁绘垼濮ら悡鏇㈡煛閸屾侗鍎ユ俊顖楀亾闁?)

    # Hot memories (preferences + habits) 闂?always loaded
    hot_memories = await get_hot_memories(db, user.id)
    if hot_memories:
        parts.append("\n闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾惧綊鏌熼梻瀵割槮缁炬儳缍婇弻锝夊閵忊晝鍔哥紒鐐劤椤兘寮婚悢鐓庣鐟滃繒鏁☉銏＄厽闁规儳顕幊鍛磼鏉堛劌绗ч柍褜鍓ㄧ紞鍡樼閻愬顩烽柕寰涢绨婚梺鐟版惈椤戝懘鎮橀弻銉︾厸閻忕偛澧藉ú鎾煕閳规儳澧查柟宄版噽閸栨牠寮撮悙鏉款棜闂備胶顫嬮崟鍨暥缂備胶濮甸悧鐘诲箖瀹勬壋鏋庨煫鍥ㄦ惄娴犵偓绻濆▓鍨仭闁瑰憡濞婇獮鍐ㄧ暋閹佃櫕鐎婚棅顐㈡处閹尖晜瀵奸埀顒勬⒒娴ｅ憡鍟為柛鈺侊功濡叉劙寮撮悩鎰佹綗闂佽鍎抽悺銊﹀垔鐎靛摜纾兼繛鎴烇供閸庡繑绻涢崼顐㈠籍婵﹨娅ｇ划娆撳礌閳ュ厖绱ｆ繝鐢靛仜閻ㄧ兘鍩€椤掍礁澧柛銈嗘礃閵囧嫰骞囬埡浣哄姶闂佸憡鑹鹃鍛粹€︾捄銊﹀磯闁绘氨顥愰崥顐︽⒑閸濄儱浠╂繛澶嬬洴閸╃偤骞嬮敂钘変汗缂傚倷鐒﹁摫闂佹鍙冨铏规兜閸涱喚褰ч梺鍛婃⒐閻熴儵鎮惧畡閭︾叆闁割偅鎯婇埡鍛叆闁哄倸鐏濋埛鏃堟煟閿曗偓閻楁挸顫忔繝姘＜婵ê宕·鈧紓鍌欑椤戝棝宕归崸妤€鏄ラ柍褜鍓氶妵鍕箳閸℃ぞ澹曠紓鍌氬€哥粔鎾晝閵堝鍋╅柣鎴ｅГ閸嬶繝鏌熸担鍐╃彧闁哄倵鍋撻梻鍌欑婢瑰﹪宕戞笟鈧畷瑙勭節濮橆厼浠奸梺鍓插亝濞叉﹢鎮￠悢鑲╁彄闁搞儯鍔嶇粈鈧繛瀵稿У缁矂鈥﹂懗顖ｆШ缂備緡鍠楅悷鈺佺暦濞差亜顫呴柕鍫濇噹瀹撳棝姊洪棃娑㈢崪缂佽鲸娲熷畷銏ゆ寠婢跺棙鏂€闂佸疇妫勫Λ妤呮倶閻樼粯鐓欑痪鏉垮船娴滄壆鈧鍠楁繛濠囧蓟閸℃鍚嬮柛鈩冪懃楠炲牓姊绘担鍛婃儓闁哥噥鍋婂畷鎰亹閹烘垶杈堝銈嗗笒鐎氼參鎮″☉銏″€堕柣鎰邦杺閸ゆ瑥鈹戦垾鐐藉仮闁哄苯绉归幐濠冨緞濡亶锕€顪冮妶搴′簼缂侇喗鎸搁悾鐑藉础閻戝棙寤洪梺绯曗偓宕囩濞存粓绠栭弻娑㈠焺閸愵亝鍣紒?)
        for mem in hot_memories:
            parts.append(f"- [{mem.category}] {mem.content}")

    # Warm memories (recent decisions/knowledge) 闂?loaded at session start
    warm_memories = await get_warm_memories(db, user.id, days=7)
    if warm_memories:
        parts.append("\n闂傚倸鍊搁崐鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偞鐗犻、鏇氱秴闁搞儺鍓﹂弫鍐煥閺囨浜鹃梺姹囧€楅崑鎾舵崲濠靛洨绡€闁稿本绮岄。娲⒑閹肩偛濡奸柛濠傛健楠炲啳銇愰幒鎾村劒闂佽崵鍠愭竟鍡椻枔閵堝鈷戦柛蹇撳悑缁跺弶绻涚涵椋庣瘈鐎殿喖顭锋俊鎼佸Ψ閵忊槅娼旀繝纰樻閸垳鎷冮敂鐣岊浄闁绘劦鍓涚弧鈧┑鐐茬墕閻忔繈鎮橀悩缁樼厪闁割偆鍠愰崐鎰偓娈垮枛椤兘宕洪崟顖氱闁靛ě鍛祦闂備胶鎳撻崥瀣偩椤忓牆鍨傚┑鐘宠壘杩濇繝鐢靛Т鐎氼喚澹曢挊澹濆綊鏁愰崨顔藉創闁哄稄绻濆娲捶椤撶喎娈屽┑鐐叉▕閸樺ジ顢氶敐鍡欑瘈婵﹩鍎甸埡鍛厪濠㈣泛鐗嗛悘顏呫亜椤愩垻孝闁宠鍨块崺銉╁幢濡ゅ啩鍖栭梻浣告啞椤棝宕甸崜浣稿幋闁糕斁鍋撳銈嗗笂閼冲墎寮ч埀顒勬⒑濮瑰洤鐏叉繛浣冲嫮顩烽柨鏇炲€归悡娆撴⒑椤愶絿銆掔紒鎰⒒閳ь剝顫夊ú妯侯渻閽樺鍤曢柛濠勫櫏濡俱劑姊?婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繐霉閸忓吋缍戦柛銊ュ€婚幉鎼佹偋閸繄鐟查梺绋匡工閻栧ジ寮诲☉銏╂晝闁绘ɑ褰冩慨搴ㄦ⒑濮瑰洤鈧宕戦幘璇参﹂柛鏇ㄥ枤閻も偓闂佸湱鍋撻幆灞轿涢垾鎰佹富闁靛牆楠告禍婵囩箾閸欏鑰挎鐐茬墦婵℃悂濡锋惔锝呮灈鐎规洖缍婇、娆撳箚瑜嶇紓姘舵⒒?)
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
        parts.append(f"\n婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢鍏尖拻閻庣數顭堟俊浠嬫⒑閸濆嫭鍣虹紒璇茬墦瀵寮撮悢椋庣獮闂佺硶鍓濊摫闁绘繐绠撳鐑樻姜閹殿噮妲梺鍝ュ枑閹稿啿顕ｆ繝姘ч柛姘ュ€曞﹢閬嶅焵椤掑﹦绉甸柛瀣噹椤潡骞掑Δ浣叉嫼缂備礁顑嗛娆撳磿閹扮増鐓欓柣鐔哄閸犳ɑ顨ラ悙鎻掓殻闁圭锕ュ鍕幢濡棿绨撮梻鍌欑濠€閬嶁€﹂崼鈶╁亾濞戞帗娅婄€殿喗濞婇幃娆撴倻濡攱瀚藉┑鐐舵彧缂嶄線藟閹惧鈻旈柤纰卞墰绾句粙鏌涚仦鍓р姇闁汇劍鍨块弻娑㈠箳閹惧磭鐟ㄩ梺瀹狀嚙闁帮綁鐛Ο鍏煎磯闁惧繐绠嶉崑濠傗攽閻樿尙妫勯柡澶婄氨閸嬫捇骞囬弶璺紱闂佺懓澧界划顖炲箠濮樿埖鐓ユ繝闈涙椤ョ姷绱掗悩鑽ょ暫闁哄本鐩崺鍕礃椤忓懎娅戝┑鐐茬摠缁挾绮婚弽顓炶摕闁挎繂顦介弫鍥煟閺囨氨鍔嶉柣銈勭閳规垿顢欑涵閿嬫暰濠碉紕鍋樼划娆撴偘椤曗偓楠炲洭顢橀悢宄板Τ闂備焦瀵х换鍌炲磹閹间緤缍栭悘鐐插綖缁诲棝鏌ｉ幇鍏哥盎闁逞屽墯閻楁粓寮鈧幃娆撴倻濡桨鎴烽梻浣圭湽閸╁嫰寮抽埀鐟僟summary.summary}")

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
            ConversationMessage(session_id="sess-1", role="user", content="闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€归崕鎴犳喐閻楀牆绗掗柡鍕╁劦閺屾盯寮撮妸銉т哗闂佹悶鍔岄崐鎼佸煘閹达箑纾兼繝濠傛捣閸斿摜绱撴担鐟板妞ゃ劌妫欑粚杈ㄧ節閸ヮ灛褔鏌涘☉鍗炴灈婵炲拑缍佸娲箹閻愭彃顬堥梺绋匡工濠€閬嶅箲閵忕姭鏀介柛銉㈡櫇閻﹀牓姊虹粙鎸庢拱缂侇喖鐭傝矾闁逞屽墴濮婄粯鎷呮笟顖滃姼闁诲孩绋堥弲鐘茬暦瑜版帒閿ゆ俊銈傚亾缂佺姵鐗楁穱濠囧Χ閸涱喖娅ら梺鍝勬噺閻擄繝鐛弽顐㈠灊闁稿繐顦禍楣冩煙妫颁胶鍔嶆繛鏉戞川缁辨捇宕掑顑藉亾閻戣姤鍤勯柤绋跨仛閸欏繘鏌ｉ姀鐘冲暈闁稿绻濋弻宥嗘姜閹殿喛绐楅梺鎼炲€栧ú鐔煎蓟濞戙埄鏁冮柨婵嗘椤︺儵姊虹紒妯诲鞍闁烩晩鍨跺璇测槈濮橆偅鍕冮梺鍛婃寙閸涱垰甯掗梻鍌欑窔濞煎骞€閵夆晛鐐婇柕濞垮灪鐎氬ジ姊绘担钘夊惞闁哥姵鍔曢…鍨潨閳ь剙顕ｉ搹顐ｇ秶闁靛鍊楃粻姘渻閵堝棗濮х紒鑼舵硶缁鎮欓幖顓燁啍闂佺粯鍔曞鍫曀夐姀鈶╁亾鐟欏嫭绀冮柨鏇樺灲閵嗕礁鈻庨幘鏉戞異闂佸啿鎼敃銉︽櫏濠电姷顣槐鏇㈠磻閹达箑纾归柡宥庡幖缁犱即鏌ゆ慨鎰偓妤呮儗濞嗘挻鐓欓柣鎴烇供濞堟棃鏌ｉ妶澶岀暫闁哄矉缍侀獮鍥敊閻撳骸顬嗛梻浣瑰▕閺€杈╂暜閿熺姴钃熸繛鎴炵煯濞岊亪鏌熺憴鍕妞ゃ儲绻堝娲焻閻愯尪瀚板褏澧楅妵鍕敇閻愰潧鈪靛銈冨灪瀹€鎼佸极閹版澘鐐婇柕濞垮劤閿涘繐鈹戦悙瀛樺鞍闁告垵缍婂畷瑙勬綇閳规儳浜鹃梻鍫熺〒閻掑憡鎱ㄦ繝鍛仩缂侇喗鐟ч幑鍕Ω瑜岀槐姗€姊绘担渚劸妞ゆ垵娲畷鎴﹀Χ婢跺﹥妲?),
            ConversationMessage(session_id="sess-1", role="assistant", content="婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｅΟ娆惧殭缂佺姴鐏氶妵鍕疀閹炬惌妫炵紓浣界堪閸婃繈寮婚悢铏圭煓闁割煈鍣崝澶愭⒑閸涘﹦鎳冪紒缁橈耿瀵鈽夐姀鐘殿啋濠德板€愰崑鎾绘倵濮樼厧澧柟顖涙⒐缁绘繈宕堕妸銏″闂備礁鎲＄换鍌溾偓姘煎櫍閸┿垺寰勯幇顓犲幈濠碘槅鍨抽崢褏鏁懜鐐逛簻闁哄倽娉曠粻浼存煃鐟欏嫬鐏╅柍褜鍓ㄧ紞鍡涘磻閸℃稑鍌ㄦい蹇撴噽缁♀偓闂佹眹鍨藉褍鐡紓鍌欒兌缁垶鏁嬪銈庡墮閿曨亪銆佸▎鎾崇鐟滃繘鏁?2婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙钃熼柕澶涘閸樹粙姊鸿ぐ鎺戜喊闁告挻宀搁獮鍡涘醇閵夛妇鍘介梺瑙勫礃閹活亪鎳撻崸妤佺厸閻忕偟纭堕崑鎾诲箛娴ｅ憡鍊梺纭呭亹鐞涖儵鍩€椤掆偓绾绢參顢欓幋锔解拻濞达絿鎳撻埢鏇㈡煛閳ь剚娼忛埡鍌涙闂佽法鍠撴慨鎾嫅閻斿摜绠鹃柟瀵稿€戝璺哄嚑閹兼番鍔庨崣鎾绘煕閵夆晩妫戠紒瀣煼瀵偊宕奸悢鍓佺畾闂佺粯鍔︽禍娆戞閺嶎灐褰掓晲閸ュ墎鍔稿銈呮禋閸嬪棛妲?),
            ConversationMessage(session_id="sess-1", role="user", content="闂傚倸鍊搁崐鎼佸磹閻戣姤鍊块柨鏇炲€归崕鎴犳喐閻楀牆绗掗柡鍕╁劦閺屾盯寮撮妸銉т哗闂佹悶鍔岄崐鎼佸煘閹达箑纾兼繝濠傛捣閸斿摜绱撴担鐟板妞ゃ劌妫欑粚杈ㄧ節閸ヮ灛褔鏌涘☉鍗炴灈婵炲拑缍佸娲箹閻愭彃顬堥梺绋匡工濠€閬嶅箲閵忕姭鏀介柛銉㈡櫇閻﹀牓姊虹粙鎸庢拱缂佸鍨甸埢宥呪攽鐎ｎ偀鎷虹紓浣割儐椤戞瑩宕曢幇鐗堢厵闁荤喓澧楅崰妯活殽閻愭彃鏆ｉ柟顔界矒閹崇偤濡疯婵椽姊绘担鐟邦嚋闁哄被鍔忛妵鎰板Ω椤垶鈻岄梻浣告惈閻绱炴担瑙勫弿闁逞屽墴閺屽秵娼幏灞藉帯婵炲濯崣鍐潖濞差亜鎹舵い鎾楀懎濮兼俊鐐€ら崢楣冨礂濡绻嗛柟缁㈠枛缁€鍐┿亜閺冨洤浜归柛濠勫仜椤啴濡舵惔鈥斥拻闂佸憡鎸婚惄顖氱暦娴兼潙绠婚柤鍛婎問濞肩喖姊洪崷顓炲妺闁搞倧绠撻幃銏㈡媼閼愁垱顏犻柟椋庡█瀹曪絾寰勭€ｎ剙绲绘繝鐢靛Х閺佸憡鎱ㄩ悜钘夋瀬闁告稑锕ラ崣蹇撁归崗鍏肩稇闁搞劌鍊块弻锝夊箻瀹曞洤鍝洪梺鍝勵儐閻楁鎹㈠☉銏犵闁绘劕顕▓銈夋⒑濞茶骞楅柟鎼佺畺閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏閸繃顥為柛?),
            ConversationMessage(session_id="sess-1", role="assistant", content="闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃秹锝炲┑瀣櫇闁稿矉濡囩粙蹇旂節閵忥絽鐓愰柛鏃€鐗犲畷鎴﹀Χ婢跺鍘搁梺鎼炲劗閺呮稑鐨梻浣虹帛鐢帡鏁冮妷褎宕叉繛鎴欏灩楠炪垺淇婇婵愬殭缁炬澘绉瑰娲传閸曢潧鍓紓浣藉煐瀹€绋款嚕婵犳碍鍋勯柣鎾虫捣椤斿姊洪柅娑樺祮婵炰匠鍐ｆ灁妞ゆ挾濮风壕?婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙鐭楀璺虹灱閻﹀牊绻濋悽闈浶㈤柛濠傤煼瀹曘儵宕堕浣哄幈闂侀潧顦介崰鏍ㄦ櫠椤曗偓閺岋綁顢橀悤浣圭暥濡炪値鍙€濞夋洟骞戦崟顖氫紶闁告洖鐏氭牎闂傚倷绀侀幖顐︻敄閸℃稒鍋￠柍杞扮贰濞兼牠鏌ц箛鎾磋础缁炬儳鍚嬮幈銊ノ旈埀顒€螞濞戙垹绀夐柛娑橈梗缁诲棝鏌ｉ幇顒佲枙闁搞倗鍠愰妵鍕敇閻愰潧鈪甸梺璇″櫍缁犳牠骞冨鍫熷癄濠㈣泛瀛╅幉浼存⒒娓氣偓濞佳嚶ㄩ埀顒€鈹戦垾铏枠鐎?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_summary_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴妤€浜惧銈庝簻閸熸潙鐣疯ぐ鎺濇晪闁告侗鍨版慨娲⒒娴ｄ警娼掗柛鏇炵仛閻ｅ墎绱撴担鎻掍壕婵犮垼娉涙径鍥磻閹捐崵宓侀柛顭戝枛婵骸顪冮妶蹇撶槣闁搞劏娉涢锝嗗閺夋嚦銊╂煥閺傚灝鈷旀い鏃€娲熷娲偡閹殿喗鎲奸梺鑽ゅ枂閸庣敻骞冨鈧崺锟犲川椤旀儳寮梻浣告啞閸旓附绂嶅鍫濆嚑婵炴垯鍨洪悡娑㈡倶閻愰潧浜剧紒鈧崘顏嗙＜闁哄啫鍊搁弸娑欍亜閵忥紕鈽夋い顐ｇ箞椤㈡寰勬径宀€锛涢梻鍌氬€峰鎺旀椤斿墽绀婇柍褜鍓欓埞鎴︻敊閸濆嫧鍋撳Δ鍛闁靛繒濮Σ鍫熸叏濮楀牏鍒板ù婊呭亾缁绘盯骞嬮悙鍨櫧闂佺粯甯婄划娆撳蓟閿濆鏁囬柣鎴濇处閺佺偓绻涢敐鍛悙闁挎洦浜妴渚€寮撮姀鈩冩珳闂佹悶鍎崝灞解枍閹达附鈷掑ù锝囨嚀椤曟粍绻涢幓鎺旂鐎规洖缍婇幖褰掑礂婢跺﹣澹曢梻鍌氱墛缁嬪繘宕戦姀鈶╁亾濞堝灝鏋涢柣鏍с偢閻涱喚鈧綆浜栭弨浠嬫煕椤愮姴鐏╅柡鍕╁劦濮婂宕掑顑藉亾妞嬪孩顐芥慨姗嗗墻閻掔晫鎲搁幋锕€闂憸鐗堝笚閳锋垿姊洪銈呬粶闁兼椿鍨遍弲鍓佲偓鐢电《閸嬫挸鈻撻崹顔界彯闂佺顑呴敃銈夋偩閻戣姤鍋勭痪鎷岄哺閺咁剙鈹戦悙鏉戠仸閻㈩垱顨堥埀顒佺煯缁瑥顫忕紒妯诲濞撴凹鍨抽崝鎼佹⒑閸濆嫮澧遍柛鎾跺枛楠炲﹤鈹戠€ｎ亞顦悷婊冪箰铻炴い鏍ㄧ矋閸犳劙骞栧ǎ顒€鐏柍鐟扮Т閳规垿鎮╅崣澶婎槱闂佺锕﹂崗姗€寮婚悢铏圭＜婵☆垰鎼鎴︽⒑缁嬫鍎愰柟鐟版搐閻ｇ柉銇愰幒婵囨櫔闂佸憡渚楅崰姘辩矙娴ｈ櫣纾介柛灞捐壘閳ь剛鍏橀幃鐐烘晝娴ｈ鍣风紓鍌氬€搁崐鍝ョ矓閺夋嚚娲敇閵忕姾鎽曞┑鐐村灟閸ㄥ湱绮荤紒妯圭箚闁靛牆鍊告禍楣冩⒑閻熸澘妲绘い鎴濇噹瀹撳嫰姊虹紒妯虹伇濠殿喓鍊濋崺娑㈠箣閿旇棄浠梺鎼炲劀閸愵亪鐛撻梻浣告贡濞呫垻绱炴笟鈧濠氭偄閸忓吋鍎銈嗗姧缁茬晫澹曢幎鑺ョ參婵☆垵宕电粻鐐烘煛瀹€鈧崰搴ㄥ煝閹捐鍨傛い鏃傛櫕娴滃爼姊绘担鍛婃儓婵☆偅鐟ч崚鎺楀箻鐠囪尪鎽曢梺缁樻⒒閸樠呯不濮樿鲸鍠愭繝濠傜墕閸氬綊鏌ｉ弮鈧幃鑸电濠婂牊鐓冮柛婵嗗閳ь剙顭峰畷锝夊焵椤掑嫭鈷戦柛婵嗗濠€浼存煟閳哄﹤鐏︾€规洘妞藉畷鐔碱敍濮橀硸妲版俊鐐€曠换鎰板磹閻㈢纾婚柟鎹愵嚙缁犳娊鏌￠崘锝呬壕闂佸摜濮甸崝娆忣潖濞差亶鏁囬柕濞у懏娈搁梻浣筋嚙妤犲繒绮婚幘璇茶摕闁挎稑瀚▽顏嗙磼鐎ｎ亞浠㈤柍宄邦樀濮婃椽鎮烽弶鎸幮╅梺纭呮珪閸旀瑩鐛径鎰妞ゆ棁鍋愰ˇ鏉款渻閵堝棙灏甸柛瀣☉閳绘捇濡烽妷銏℃杸闂佹寧绋戠€氼剚绂嶆總鍛婄厱濠电倯鍐╁櫧濞戞挸绉归弻鐔衡偓娑欘焽缁犮儵鏌涢妶鍡樼闁哄本鐩獮姗€鎳犵捄鍝勫腐闂備焦妞块崢浠嬫偡閵夆晛鐓橀柟杈鹃檮閸嬫劙鏌涘▎蹇ｆЦ妞わ腹鏅犲铏圭矙濞嗘儳鍓遍梺鍛婃⒐濞茬喐淇婇幘顔肩闁规惌鍘介崓鐢告⒑缂佹ɑ灏繛鎾敱缁傛帡鍩￠崨顔规嫼闁荤姴娲犻埀顒冩珪閻忓棛绱撴担钘夌厫闁煎綊绠栭敐鐐剁疀閹句焦妞介、鏃堝礋椤愩倗宕烘繝鐢靛Х閺佸憡鎱ㄩ幘顔肩９濠电姵纰嶉崑锟犳煛鐏炶鍔滈柣鎾跺枛閺屾洝绠涙繝鍐╃彅闂佽绻愬畷顒勬箒濠电姴锕ら幊搴㈢濠婂牆纭€?婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄Т缂嶅﹪寮诲澶婁紶闁告洦鍋€閸嬫挻绻濆銉㈠亾閸涙潙鐭楀璺虹灱椤旀洟姊虹化鏇炲⒉閽冮亶鎮樿箛锝呭箻缂佽鲸甯￠幃鈺佺暦閸パ冪哗闂備礁鎼張顒€煤濠靛牏涓嶆繛鎴炲焹閸嬫捇鏁愭惔婵堟寜闂佺顑嗛幑鍥ь嚕閹绢喗鍋愰柣銏㈡暩閸旇泛鈹戦悩顔肩伇闁糕晜鐗犲畷婵嬪冀椤撶喎浜楅梺鍛婂姦閸犳鎮￠姀鈥茬箚妞ゆ牗鐟ㄩ鐔镐繆閹绘帞绉洪柡灞剧洴閺佹劙宕堕妸锔惧涧缂傚倷娴囨ご鍝ユ暜閿熺姴鏄ラ柍?,
                "actions": ["闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏犖ч柛鈩冦仦缁剝淇婇悙顏勨偓鏍礉瑜忕划濠氬箣閻樺樊妫滈梺绉嗗嫷娈曢柣鎾寸懅缁辨挻鎷呴棃娑氫患濠电偛鎳忛敃銏ゅ蓟閳╁啯濯撮柛鎾村絻閸撹鲸绻涢敐鍛悙闁挎洦浜濇穱濠囧醇閺囩偛绐涘銈嗘尵閸犳劙顢欏澶嬧拻濞达綀顫夐妵鐔兼煕濡吋娅曢柛鐘诧工椤撳ジ宕堕妸銉ョ哎婵犵數鍋為崹鍫曟晝閳哄懎鐤柛娑卞枔娴滄粓鏌￠崘銊︽悙闁告艾缍婇弻娑㈠箣濠靛牏楔濠殿喖锕ュ浠嬬嵁閹邦厽鍎熼柨婵嗗€搁～宀€绱撻崒娆愮グ妞ゆ泦鍥ㄥ亱闁圭偓鍓氶崵鏇炩攽閻樺磭顣查柡鍛倐閺岋絽螣閸喚姣㈠銈忚礋閸旀垵顫忓ú顏咁棃婵炴番鍊栭惄顖氱暦濮椻偓椤㈡棃宕熼銈庡晥婵?, "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓褰掑磿閹寸姵鍠愰柣妤€鐗嗙粭鎺楁煕閵娿儱鈧悂鍩為幋锔藉亹閻庡湱濮撮ˉ婵堢磽娴ｇ懓濮堟い銊ワ躬瀵鎮㈤崗鐓庝罕闂佸壊鍋嗛崰鎾诲礄閿熺姵鈷戦柟鑲╁仜婵″ジ鏌涙繝鍌滅Ш妤犵偛鐗撴俊鎼佸Ψ椤旇棄缂撻梻浣虹《閸撴繈銆冮崨顖楀亾濞戝磭鍒伴柍瑙勫灴閹瑩鎳犻鈧·鈧俊鐐€戦崝灞轿涘▎鎴犵煔閺夊牄鍔庣弧鈧梺鎼炲劥閸╂牠寮查鈧埞鎴︽偐鐠囇冧紣闂佺懓鍟垮ù椋庡垝椤撱垹鐏抽柡鍌樺劜閺傗偓闂備胶绮崝妯间焊濞嗘劖娅犻柨婵嗘缁犳儳顭跨捄渚剳婵炲弶鎸抽弻宥夊Ψ椤栨凹娲梺鍦嚀鐎氱増淇婇幖浣规櫇闁逞屽墰婢规洟顢涢悙绮规嫼闂佽鍨庨崨顖ｅ敹濠电姭鎷冨鍥┬滈梺杞扮缁夌懓鐣烽悢纰辨晣闁绘瑥鎳愭惔濠囨⒒閸屾瑨鍏岄柛瀣ㄥ姂瀹曟洟鏌嗗鍛焾闂佺鍕垫闁轰礁鍊归妵鍕箛閸洘顎嶉梺缁樻尰閻熝囧焵椤掑倹鍤€閻庢矮鍗冲畷鎴炵節閸パ咃紵闂佸搫鍟悧濠囨偂閺囥垺鐓忓┑鐐靛亾濞呭洭鏌ｉ敐鍫燁仩闁逞屽墲椤煤濮椻偓閺佸啴濮€閵堝懐鐤囬梺缁樕戝鍧楀极閸曨垱鐓曟い顓熷灥閺嬬喖鏌?],
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
        assert "婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋鐘垫澑婵＄偑鍊栫敮鎺椝囬姘ｆ灁妞ゆ劧闄勯埛鎴︽煕濞戞﹫鏀诲璺哄閺屾稓鈧綆鍋勫ù顔锯偓瑙勬磸閸庢娊鍩€椤掑﹦绉甸柛鐘愁殜閹繝寮撮姀锛勫幐闂佹悶鍎崕杈ㄤ繆閸忕⒈娈介柣鎰懖閹寸偟鈹? in summary.summary


@pytest.mark.asyncio
async def test_end_session_extracts_memories(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="sess-user-2", username="sesstest2", hashed_password="x")
        db.add(user)

        msgs = [
            ConversationMessage(session_id="sess-2", role="user", content="闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涚€ｃ劌鈧繈寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閹肩偛濡奸柛濠傛健瀵鏁愭径濠庢綂闂侀潧绻嗛弲婵嬪礉閹间焦鈷戦柛娑橈工閻忊晛鈹戦悙鈺佷壕闂備礁鎼懟顖滅矓闂堟侗鐒芥い蹇撶墕缁狀垳鈧厜鍋撳┑鐘插€归弳顓㈡⒒閸屾瑧顦﹂柟纰卞亰椤㈡牠宕ㄧ€涙鍘愰梺鎸庣箓椤︻垶鎷戦悢鍏肩厸闁搞儵顥撶壕鍧楁煟閵堝倸浜炬繝鐢靛Х閺佸憡鎱ㄩ幘顔肩９闁归棿绀侀悡鏇烆熆閼搁潧濮堥柍閿嬪灴閺岀喓绮欓幐搴㈠闯闂佸疇妫勯ˇ杈╂閹烘挸绶為悗锝庡亜閸炲姊虹化鏇熸澓闁稿孩褰冮銉╁礋椤栨氨鐤€濡炪倖甯掗崑鍡涘疮鐎ｎ剛纾介柛灞剧懅閸斿秶绱掔€ｎ偅宕屾鐐诧躬楠炴﹢寮堕幋顓炴闂備礁缍婇崑濠囧礈閿曗偓閵嗘帗绻濆顓犲帾闂佸壊鍋呯换鍕不閹惰姤鐓熼柨婵嗙墔閸氼偊鏌嶈閸撴岸顢欓弽顓炵獥闁哄秲鍔嶅▍鐘诲箹鏉堝墽鍒伴柛銊︾箖缁绘盯宕卞Ο鍝勵潕缂備讲妾ч崑鎾绘⒒娴ｈ鍋犻柛搴灦瀹曟繄浠﹂崜褜娲搁悷婊呭鐢鍩涢幋锔界厱闁瑰墽鎳撻惃娲煕濡崵娲撮柡灞剧〒閳ь剨缍嗘禍婊堫敂椤撱垺鐓曢柍瑙勫劤娴滅偓淇婇悙顏勨偓鏍暜閹烘纾归柛娑橈功椤╅鎲歌箛鏇燁潟闁圭儤鎸荤紞鍥煏婵炲灝鍔ら柣鐔哥叀閹宕归锝囧嚒闁诲孩鍑归崳锝夊春閳ь剚銇勯幒鎴姛缂佸娼ч湁婵犲﹤鎳庢禒杈┾偓瑙勬磸閸ㄤ粙鐛崶顒夋晩闁告挆宥囬棷婵犵數鍋犻幓顏嗗緤閼测晛鍨濇繛鍡樻尭娴肩娀鏌ц箛鎾磋础缁炬儳銈搁幃褰掑炊椤忓嫮姣㈡繝鈷€鍕闁靛洤瀚板鎾敂閸℃婊兾旈悩闈涗沪闁圭懓娲悰顕€骞掗幋鏃€鏂€闂佹悶鍎滈崘銊ラ嚋濠电姷顣槐鏇㈠磻閹达箑纾归柡宥庡幖缁€澶愭煙鏉堝墽鐣辩痪鎹愵潐娣囧﹪濡堕崨顔兼缂備胶濮烽崰鎰板Φ閸曨喚鐤€闁规崘娉涢·鈧梻浣瑰▕閺€閬嶅垂閸撲焦宕叉繛鎴欏灪閸ゆ垵螞閻楀牏绠撻柡浣烘櫕缁辨挻鎷呴棃娑橆瀷缂備緡鍣崹鑸典繆閻㈢绀嬫い鏍ㄦ皑椤撳搫鈹戦悩缁樻锭婵炴潙鍊歌灋闁挎洖鍊归崐鍨箾閸繄浠㈤柡瀣枛閺岀喖顢欓悡搴樺亾閹间焦鍋╃€瑰嫰鍋婂銊╂煃瑜滈崜鐔煎Υ娓氣偓瀵噣宕煎┑鍡氣偓鍨攽閻愬弶顥為柛銊ф暩閺?),
            ConversationMessage(session_id="sess-2", role="assistant", content="婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈功缁犻箖鏌嶈閸撴氨鎹㈠☉娆愬闁告劕寮堕幖鎰棯閸撗勫殌闁宠鍨块幃鈺冣偓鍦Т椤ユ繈姊哄Ч鍥р偓妤呭磻閹捐桅闁告洦鍨扮粻娑㈡煏婵犲繒鐣辨繛鍛哺濮婃椽宕崟闈涘壉濠碘槅鍋勯崯鏉戭嚕婵犳碍鍋勯柛娑橈功缁夎埖淇婇妶蹇曞埌闁哥噥鍨堕、鎾愁吋婢跺鎷洪梺鍛婄箓鐎氼厽鍒婃總鍛婄厱闁规崘娉涢弸娑欘殽閻愭彃鏆欐い顐ｇ矒閸┾偓妞ゆ帒瀚粻鏍ㄧ箾閸℃ɑ灏紒鐙欏洦鐓欓悗娑欘焽缁犳挾鎮鈧濠氬磼濞嗘劗銈板銈嗘肠閸涱喖搴婇梺瑙勬緲閸欐捇宕堕浣镐缓缂備礁顑堝▔鏇㈡偩濞差亝鐓熼柣鏂挎憸閹冲啴鎮楀鐓庢珝闁诡喚鏌夐妵鎰板箳閹捐泛甯楅柣鐔哥矋缁挸鐣峰鍫熷亜闁绘挸瀹妷鈺傜厱鐎光偓閳ь剟宕戦悙鍝勭柧婵犲﹤鐗婇悡鏇㈡煙閻愵剦娈旈柟宄邦儏鍗遍柟闂寸劍閳锋帒霉閿濆牜娼愰柛瀣█閺屾稒鎯旈鑲╀桓閻庤娲樼换鍐箚閺冨牆惟闁挎繂鍊告禍?),
        ]
        db.add_all(msgs)
        await db.commit()

        mock_response = {
            "role": "assistant",
            "content": json.dumps({
                "summary": "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴妤€浜惧銈庝簻閸熸潙鐣疯ぐ鎺濇晪闁告侗鍨版慨娲⒒娴ｄ警娼掗柛鏇炵仛閻ｅ墎绱撴担鎻掍壕婵犮垼娉涙径鍥磻閹捐崵宓侀柛顭戝枛婵骸顪冮妶蹇撶槣闁搞劏娉涢锝嗗閺夋嚦銊╂煥閺傚灝鈷旀い鏃€娲熷娲偡闁箑娈堕梺绋款儑閸犳牠濡撮崒鐐茶摕闁靛濡囬崢閬嶆煟鎼搭垳绉甸柛瀣崌閹虫捇宕稿Δ浣哄幐闁诲繒鍋熼崑鎾剁矆閸愵亞纾肩紓浣诡焽濞插鈧娲栫紞濠囥€佸▎鎴濇瀳閺夊牃鏂侀崑鎾诲箻椤旂晫鍘介梺缁樻煥閹芥粓鎯岀€ｎ亖鏀介柍鈺佸暞閸婃劗鈧娲橀〃濠囧箖閳哄懎鍨傛い鎰╁灪閻ｎ剚淇婇悙顏勨偓銈夊储瑜版帒绀夐柟瀛樼箘閺嗭附鎱ㄥ璇蹭壕闂佺硶鏂侀崜婵堟崲濠靛绀冮柣鎰靛墾缁辨ê鈹戦悩娈挎殰缂佽鲸娲熷畷鎴﹀箣閿曗偓绾惧綊鏌″搴′簼闁哄棙绮撻弻锝夊箛椤掍焦鍎撶紓浣瑰姈椤ㄥ﹪寮婚悢鍏肩劷闁挎洍鍋撻柡瀣ㄥ€濋弻锝夘敇閻旂儤鍣ч梺瀹狀潐閸ㄥ潡骞冮埡鍛煑濠㈣泛顭Σ閬嶆⒒娴ｄ警鐒炬い鎴濇瀹曟繂鈻庨幘瀹犳憰閻熸粍鍨圭划璇测槈閵忊剝娅滈梺鍛婁緱閸撴繈宕洪崨顔剧瘈缁剧増菤閸嬫捇鎼归鐔哥亞闂備焦鎮堕崝蹇撯枖濞戭澁缍栭煫鍥ㄦ⒒缁♀偓濠殿喗锕╅崜娑㈡晬濠婂啠鏀芥い鏃€鏋绘笟娑㈡煕韫囨棑鑰跨€规洘鍨块獮妯肩磼濡桨鐢婚梻鍌欑贰閸欏繑淇婇崶顒€绀夌€瑰嫭澹嬮弨浠嬫煟閹邦剙绾фい銉у仱閺屾盯寮埀顒勩€冩繝鍥ラ柛娑欐綑閽冪喖鏌曟径娑橆洭闁告ê宕埞鎴︽倷閺夋垹浠搁梺鎸庢处閸嬪﹤鐣峰┑瀣亜闁稿繐鐨烽幏?,
                "actions": [],
                "memories": [
                    {"category": "preference", "content": "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為〃鍛粹€﹂妸鈺佺妞ゆ巻鍋撶€殿喖娼″鍝勑ч崶褏浼堝┑鐐板尃閸パ冪€┑鐘绘涧閻楀啴宕戦幘鑽ゅ祦闁割煈鍠栨慨搴☆渻閵堝繒绱扮紒顔界懃椤曪綁顢曢敃鈧粈鍐┿亜椤撶儐鍎忕紓宥咃躬楠炲啴鍩℃笟鍥ф櫊濡炪倖姊婚崢褎绔熼崼銏㈢＝闁稿本鐟х拹浼存煕鐎ｎ亜顏紒顔芥閵囨劙骞掗幋锝嗘啺闁诲骸绠嶉崕鍗灻洪敃鍌氱；婵せ鍋撻柡灞界Ч婵＄兘濡烽妷銉ь儓濠电姰鍨奸～澶娒哄鍛潟闁规崘顕х壕鍏肩箾閸℃ê鐏ュ┑陇妫勯—鍐Χ閸愩劌顬堥梺纭呮珪閿氶柣锝囧厴楠炲洭鎮ч崼婵呯敾闂傚倷绶￠崣蹇曠不閹存績鏋旀い鎰堕檮閳锋垿鏌涘☉姗堟敾濠㈣泛瀚伴弻娑氣偓锝庡亜濞搭喚鈧娲忛崕鎶藉焵椤掑﹦绉甸柛鐘愁殜閹繝寮撮姀锛勫幐闂佹悶鍎崕杈ㄤ繆閸忕⒈娈介柣鎰懖閹寸偟鈹嶅┑鐘叉搐閻顭跨捄鐚村姛濞寸厧鑻埞鎴︻敊绾攱鏁惧┑锛勫仒缁瑩鐛繝鍥ㄦ櫢闁绘ê寮閺屾稑鈽夐崡鐐差潾闂佺顫夊ú妯兼崲濠靛牆鏋堟俊顖涙た濞兼垿姊虹粙娆惧剰闁硅櫕锕㈤獮鍡涘礋椤栵絾鏅梺缁樺姇閻°劌鈻嶅鍫熲拺缂備焦锚婵洭鏌熺喊鍗炰喊鐎规洘锕㈤崺鈧い鎺嗗亾妞ゎ亜鍟存俊鍫曞幢濡儤娈梻浣告憸婵敻宕濋弴銏犵厺鐎广儱顦崘鈧銈嗘尵閸犳捇宕㈡禒瀣棅妞ゆ劑鍨烘径鍕箾閸欏澧紒鍌涘笩椤﹀綊鏌＄仦鍓с€掗柍褜鍓ㄧ紞鍡涘磻閸涱厾鏆︾€光偓閸曨剛鍘靛銈嗘⒒閸嬫捇寮抽渚囨闁绘劘鎻懓璺ㄢ偓娈垮櫘閸撶喐淇婇悜鑺ユ櫆缂備焦顭囩粔楣冩⒒閸屾艾鈧兘鎳楅崼鏇炵疇闁规儳鐡ㄥ▍鐘裁归悩宸剾闁轰礁妫濋弻锛勪沪鐠囨彃濮庣紓浣插亾濠㈣埖鍔栭悡鐔兼煛閸屾稑顕滈柟鎻掓憸缁辨帡鍩﹂埀顒勫磻閹剧粯鈷掑〒姘ｅ亾闁逞屽墰閸嬫盯鎳熼娑欐珷閻庣數纭堕崑鎾舵喆閸曨剛锛橀梺鍛婃⒐閸ㄧ敻顢氶敐澶婇唶闁哄洨鍋熼娲⒑缂佹ê鐏ユ俊顐ｇ懇钘熼柕鍫濐槹閳锋帡鏌涚仦鍓ф噮闁告柨绉归弻鐔碱敊閼测晛鐓熼悗瑙勬礃濞茬喖銆佸璺虹劦妞ゆ巻鍋撴い鏇秮瀵濡烽妷褍骞愬┑鐐存尰閼规儳煤閵娾晛绀?},
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
        assert "闂傚倸鍊搁崐鎼佸磹閹间礁纾圭€瑰嫭鍣磋ぐ鎺戠倞鐟滃繘寮抽敃鍌涚厽闁靛繈鍩勯悞鍓х棯閸撗呭笡缂佺粯鐩獮瀣倻閸℃瑥濮辨繝鐢靛仦閸ㄦ儼褰滃┑鈩冨絻閻楀﹪濡甸崟顖ｆ晝妞ゆ劑鍨洪悘鎾剁磽? in memories[0].content
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

_EXTRACT_PROMPT = """闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎺嶇劍椤斿洭姊绘担鍛婅础闁稿簺鍊濆畷鐢告晝閳ь剟鍩ユ径濞㈢喖鏌ㄧ€ｎ兘鍋撴繝姘拺闁革富鍘兼禍鐐箾閸忚偐鎳囬柛鈹惧亾濡炪倖甯掗崐褰掑汲椤掑嫭鐓涢悘鐐额嚙閳ь剚绻堥悰顔界瑹閳ь剟鐛幒妤€绠ｆ繝闈涙煀閹寸偘绻嗛柣鎰典簻閳ь剚鍔欏鎻掆攽鐎ｎ亞顦у┑顔姐仜閸嬫挾鈧鍠栭…宄邦嚕閹绢喗鍋勫瀣捣閻涱噣姊绘担绋款棌闁稿鎳愮紓鎾淬偅閸愩劎锛涢梺鍦亾缁剁偤寮崼婵嗙獩濡炪倖妫冨Λ鍧楁偨婵犳碍鈷掑ù锝囧劋閸も偓婵犫拃鍛珪闁告帗甯￠、娑㈡倷閼碱剨绱梻浣圭湽閸ㄥ綊骞夐敓鐘冲亗闁绘柨鍚嬮悡蹇涚叓閸パ嶆敾妞ゎ偄锕弻娑㈡偄妞嬪海顔掗梺鍝勭焿缁绘繈宕洪埀顒併亜閹哄秶顦︽い鏇憾閹鈽夊▎妯煎姺闂佸憡眉缁瑥顫忓ú顏勭閹兼番鍩勫鍨攽閻愬樊妲规繛鑼枛楠炲棛浠︾憴锝嗙€婚梺瑙勫劤椤曨參宕㈤崨濠勭閺夊牆澧介崚浼存煙閼恒儳鐭婇柣鈽嗗弮濮婄粯鎷呮搴濊缂備焦褰冩晶浠嬪箲閵忋倕閱囨繝闈涚墛濞堟儳鈹戦濮愪粶闁稿鎸婚妵鍕閳╁喚妫冮悗瑙勬礀瀹曨剟鍩㈡惔銈囩杸濠电姴鍊锋竟鏇㈡⒑鐟欏嫬鍔跺┑顔哄€濋崺?JSON闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍛婄秶濡わ絽鍟宥夋⒑缁嬫鍎忔い鎴濐樀瀵鈽夊Ο閿嬵潔闂佸憡顨堥崑鐔哥椤栨粎纾藉ù锝呮惈鏍￠梺鍝勮閸旀垿鍨鹃敂鐐磯闁靛绠戠壕顖炴⒑缂佹ê鐏﹂拑閬嶆煙閻戞垝鎲炬慨濠冩そ瀹曨偊濡烽妷锔锯偓濠氭⒑閸︻厸鎷￠柛瀣工閿曘垺绗熼埀顒€顫忓ú顏勭閹艰揪绲块悾闈涒攽閻愰鍤嬬紒鐘冲灴閸┿垹顓兼径濠傚祮闂佺粯顭囬弫鎼佹晬濠靛鈷戦柛鎾村絻娴滄繄绱掔拠鑼ч柟顔瑰墲缁轰粙宕ㄦ繝鍕箰闂佽绻掗崑娑欐櫠閽樺铏光偓娑欙供濞堜粙鏌ｉ幇顒佲枙闁稿骸绻橀弻宥囨喆閸曨偆浼岄悗瑙勬礀閻栧吋淇婇幖浣肝ㄩ柕澶堝労濡劙姊婚崒姘偓鎼佸磹妞嬪海鐭嗗〒姘ｅ亾妤犵偛顦甸弫鎾绘偐閸愯弓鐢婚柣鐔哥矋閺屻劑鎮鹃悜钘夌闁挎洍鍋撶紒鐘差煼閺屾盯骞橀懠璺哄帯闂佺粯甯掑鈥愁潖濞差亜鎹舵い鎾跺仜婵″搫顪冮妶鍐ㄥ闁硅櫕锚閻ｅ嘲顫滈埀顒勫春閳ь剚銇勯幒鎴濐仾闁稿鍓濈换婵囩節閸屾碍娈堕柡浣哥墦閹鈻撻崹顔界彯闂佺顑呴敃銈夋偩闁垮闄勭紒瀣仢瀹撳棝姊虹紒妯荤叆闁汇劍绻堝畷鎴﹀箻缂佹ê浠洪梺鍛婄☉閿曪箓宕㈤柆宥嗏拺闁圭瀛╅ˉ鍡樸亜閺囧棗娲ㄥ畵浣逛繆閵堝嫰妾峰ù婊勭矒閻擃偊宕堕妸锔绢槬闂佸搫顑嗗鑽ゆ閹烘挻缍囬柕濞垮劤閻熸彃鈹戦悙闈涘付缂佺粯蓱娣囧﹪骞栨担鑲濄劑鏌曟径娑㈡闁搞倕鐗撳?
{
  "summary": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢铏圭＜闁靛繒濮甸悘鍫㈢磼閻愵剙鍔ゆい顓犲厴瀵鎮㈤悡搴ｎ槶閻熸粌绻掗弫顔尖槈閵忥紕鍘介梺瑙勫劤閻°劎绮堥崘顏嗙＜缂備焦顭囧ú瀵糕偓瑙勬礀瀹曨剝鐏冮梺鍛婂姇閸熴劑宕规禒瀣摕婵炴垯鍨瑰Λ姗€鎮归崶銊ョ祷濠殿噯绠撳娲传閸曨厾鍔圭紓鍌氱С缁舵艾顕ｉ锕€纾兼繝濠傚绾绢垶姊洪棃娴ゆ盯宕ㄩ鐐电暰濠电姴鐥夐弶搴撳亾濡や焦鍙忛柣鎴ｆ绾惧鏌熼悧鍫熺凡缁炬儳顭烽弻鐔煎礈瑜忕敮娑㈡煃闁垮鐏撮柡宀嬬秮楠炴﹢宕橀懠顒佇炴繝鐢靛仩閸嬫劙宕伴弽顓炶摕婵炴垶鐟х弧鈧梺鍛婂姉閸嬫捇鎮鹃崼鏇熲拺鐎规洖娲ㄧ敮娑欎繆椤愩垹鏆為柟渚垮姂閸┾偓妞ゆ帒瀚悡蹇涙煕椤愶絿绠栭柛锝堟铻栭柣妯哄级閸犳ɑ鎱ㄦ繝鍐┿仢鐎规洘锕㈠畷锝嗗緞鐎ｎ亜澹嶉梻鍌欒兌椤牓鏁冮妶澶嗏偓锕傛倻閻ｅ苯绁︽繝鐢靛Т濞层倗绮堢€ｎ偁浜滈柟瀛樼箓缂嶆牜绱掗妸銉吋婵﹪缂氶妵鎰板箳閹存粌鏋堥梻浣规偠閸斿孩鏅跺Δ鍐焿鐎广儱鐗勬禍褰掓煙閻戞ɑ灏甸柛妯绘崌閹嘲顭ㄩ崟顓犵厜閻庤娲樼划宀勫煡婢舵劕顫呴柣妯虹－閳ь剦鍓熷楦裤亹閹烘搫绱甸梻鍌氬缁夊綊宕洪埀顒併亜閹达絾纭堕柛鏂跨Ф缁辨帞绱掑Ο鑲╃杽閻庤娲栭悥鍏间繆閹间礁唯闁靛鍎幐鍕攽閻樺灚鏆╅柛瀣洴椤㈡岸顢橀悢绋垮伎闂佸湱铏庨崳顕€寮崟顖涚厱婵炴垵宕悘鐘炽亜閵夛附鐨戠紒杈ㄦ尰閹峰懘鎳栭埄鍐ㄧ伌鐎规洩缍€缁犳盯寮埀顒勫矗韫囨柧绻嗛柕鍫濆€告禍鎯р攽閳藉棗浜濇い銊ユ缁顓兼径瀣偓鐑芥煟閹寸儐鐒介柛姗€浜跺铏圭磼濡崵鍙嗛梺鎼炲€栭悧鏇㈩敊韫囨稑唯闁冲搫鍋嗗鎸庣節閵忥絽鐓愰柛鏃€鐗犻幃锟犳偄閸涘﹤寮垮┑掳鍊愰崑鎾翠繆椤愶綆娈曠紒鍌氱Т椤劑宕楅悩鍨殌妞ゎ厹鍔戝畷銊╊敇濠靛棭妫滅紓?,
  "actions": ["闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗霉閿濆浜ら柤鏉挎健濮婃椽顢楅埀顒傜矓閻㈢纾婚柨鐔哄У閻撴瑩鏌熼婊冾暭妞ゃ儱顦伴〃銉╂倷椤忓嫮浼堥梺鍝勮嫰缁夌懓鐣烽锕€绀嬫い鎰枎娴滃墽鎲搁悧鍫濈瑨缂佺嫏鍥ㄧ厵闂傚倸顕崝宥夋煃闁垮绗掗棁澶愭煥濠靛棙鍣洪悹鎰ㄥ墲缁绘繈鍩€椤掍胶顩烽悗锝庡亞閸橀亶姊洪崫鍕偓钘夆枖閺囥垺鍊堕梺顒€绉甸悡鍐喐濠婂牆绀堟慨妯挎硾缁€鍕喐閻楀牆绗掗柣顓燁殜閺屾盯骞囬棃娑欑亾閻庤鎸风欢姘跺蓟閳ユ剚鍚嬮幖绮光偓宕囶啈闂備胶绮幐鍫曞磿閻㈢绠栨俊銈呮噺閺呮煡骞栫划鍏夊亾閼碱剛娉垮┑锛勫亼閸婃洜鈧稈鏅犻獮鎰板箹娴ｅ摜鍘撮梺纭呮彧闂勫嫰宕戦幇鐗堝仯闁搞儱娲ら崯鈺冩閿濆鈷掑ù锝呮啞閹叉悂鏌涢敐鍐ㄥ姦鐎规洘鍨剁换婵嬪炊瑜忛悾鍝勨攽閳藉棗鐏ラ柕鍡忓亾闂佸搫顑呴柊锝夊蓟閻斿吋鍊锋い鎺嶈兌缁嬪洦绻?],
  "memories": [
    {"category": "preference|habit|decision|knowledge", "content": "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙５闁逞屽墾缁犳挸鐣锋總绋课ㄩ柨鏃囧Г閻濇牠姊绘担鐟邦嚋婵炲弶鐗犲畷鎰板箹娴ｅ摜锛滈梺闈浤涢崟顐ｇ€鹃梻濠庡亜濞诧箓骞愰幘顔煎嚑閹兼番鍔嶉悡蹇涚叓閸パ屽剰闁逞屽墯閻楃娀骞冮悙鐑樺殐闁宠鍎虫禍鐐殽閻愯尙浠㈤柛鏃€纰嶆穱濠囶敃閵忋垻鍔Δ鐘靛仜缁绘濡甸幇鏉跨闁圭虎鍨辩€氬ジ姊绘笟鈧鑽も偓闈涚焸瀹曪絾鎯旈妸锕€鈧灝螖閿濆懎鏆為柛濠傜仛缁绘盯骞嬮悙鑼懖濠电偛鎳庨敃锕傚焵椤掑喚娼愭繛鍙壝—鍐寠婢跺本娈鹃梺鍦劋椤ㄥ棝宕愰悜鑺ョ厸濠㈣泛顑呴悘锝夋煕閺嶃劎澧柍瑙勫灴閹瑧鈧稒锚闂夊秹姊虹化鏇熸珔闁哥喐娼欓悾鐑藉箣閿曗偓缁犵粯绻涢敐搴″幐缂併劌顭峰娲箰鎼达絿鐣电紓浣虹帛閸旀瑩濡撮崨鎼晢闁稿本绮庨敍婊堟煛婢跺﹦澧愰柡鍛⊕缁傛帗娼忛埞鎯т壕閻熸瑥瀚粈鈧梺缁樼墪閵堟悂濡存担鑲濇梹鎷呴悷閭︹偓鎾剁磽娴ｅ壊鍎忛柣蹇旂箞钘熷鑸靛姈閳锋帡鏌涚仦鍓ф噮妞わ讣绠撻弻鐔访圭€Ｑ冧壕閻℃帊鐒﹀浠嬪极閸岀偞鍋╃€光偓婵犲啴鏁滃┑鐘垫暩閸嬫稑螞濞嗘挸鍨傞悹楦挎閺嗭箓鏌＄仦璇插姕闁绘挻娲熼弻宥夊煛娴ｅ憡娈堕梺鎰佸灡濞茬喖寮?}
  ]
}

闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煟閵忋埄鐒剧紒鎰殜閺岀喖骞嶉纰辨毉闂佺顑戠换婵嬪蓟閺囩喓鐝舵い鏍殔娴滈箖姊虹粙娆惧剱闁瑰憡鎮傞敐鐐测攽鐎ｎ偄浜楅柟鑲╄ˉ濡狙囧箯椤愶附鐓熼幖娣€ゅ鎰箾閸欏澧辩紒杈╁仦缁绘繈宕堕妷銏犱壕濞达絿纭跺Σ鍫ユ煏韫囧ň鍋撻弬銉ヤ壕闁绘垼濮ら崐鍨箾閹寸儐浼嗛柟杈鹃檮閸?- summary 闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煟閵忋埄鐒剧紒鎰殜閺岀喖鏌囬敃鈧崝鎺撶箾瀹割喕绨荤紒鐙呯秮閺屻劑寮崶顭戞濠电偛鐗婇崹鍨潖濞差亜绀堥柟缁樺笂缁ㄧ厧鈹戦悙鎻掔骇闁挎洏鍨归悾鐑藉箣閿曗偓閻撴盯鏌涚仦鍓х煂闁伙箑鐗撳濠氬磼濮樺崬顤€缂備礁顑嗙敮锟犲箖濮椻偓閸╋繝宕ㄩ鎯у箺闂備胶鎳撻顓㈠磿閹扮増鍊垮ù鐘差儐閻撶喖鏌ｉ弮鍌氬妺闁搞倐鍋撻梻浣哥枃椤宕归崸妤€绠栭柍鍝勬噹缁犵敻鏌熼悜妯肩畱缂佽鲸鍨舵穱濠囨倷椤忓嫧鍋撹閳ь剟娼ч惌鍌氱暦閺夎鏃堝礃閳轰礁绨ユ繝鐢靛仦閸垶宕归崷顓犱笉闁挎繂顦伴悡鐔兼煙闁箑骞楃紓宥嗗灴閺岋綁濡搁敃鈧悘瀛樻叏婵犲懏顏犵紒顔界懃閳诲酣骞嗚婢瑰姊绘担鐑樺殌闁硅绻濋獮鍐磼閻愬弶妲梺闈涱檧缁犳垹娆㈤悙鐑樼厵闂侇叏绠戞晶鐗堛亜閺冣偓鐢€愁潖濞差亜宸濆┑鐘插閻ｅジ姊虹粙娆惧剱闁告梹鐟ラ悾鐑藉箣閿曗偓缁犲鎮归崶銊ョ祷鐎规挸妫濋弻鐔搞偊閹稿海褰х紓浣稿€哥粔鐑藉Φ閹版澘绠抽柟鎹愭硾楠炴姊绘担鍝ョШ闁稿锕畷婊冣槈濞嗘埈娴勫┑鐐村灟閸ㄦ椽宕?- memories 闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极閹剧粯鍋愰柛鎰紦閻㈢粯淇婇悙顏勨偓鏍偋濡ゅ啰鐭欓柟鐐湽閳ь剙鎳樺畷锝嗗緞瀹€鈧惁鍫ユ⒒閸屾氨澧涘〒姘殜閹偤骞嗛‖锛勬嚀椤劑宕ㄩ鍏肩暚闂備線娼уΛ娆戞暜閹烘缍栨繝闈涱儐閺呮煡鏌涘☉鍗炲妞ゃ儲宀稿铏规嫚閸欏鏀銈庡亜椤︻垳鍙呴梺鍐叉惈閸熸壆绮堟繝鍋綊鏁愰崨顓ф闂佹悶鍊栧ú鏍箒闂佺粯锚濡﹪宕曞☉銏＄厸濞达絿顭堥弳锝夋煛鐏炶濡奸柍瑙勫灴瀹曞崬顫滈崱姗堢磼濠碉紕鍋戦崐鏍箰閸濄儳绀婂┑鐘插亞濞兼牜绱撴担鑲℃垶鍒婄€靛摜纾兼繛鎴烇供閸庢劗绱撳鍛ⅵ婵﹥妞介幃鐑芥偋閸繃娈樺┑鐘垫暩閸嬫盯鏁冮妶澶樻晪闁挎繂顦儫闂佸疇妗ㄩ懗鍫曘€侀崨瀛樷拺缂備焦锚婵洨绱掔€ｎ亜顏紒杈╁仦缁楃喖鍩€椤掑嫭鍋樻い鏃堟暜閸嬫捇鏁愭惔鈩冪亶闂佺顑嗛崝娆撳蓟濞戙垹绠涙い鎾跺仧缁佸嘲螖閻橀潧浠﹂柛銊ㄥ煐缁岃鲸绻濋崶銊モ偓閿嬨亜韫囨挸顏ら柛瀣崌瀵粙鈥栭浣衡姇缂佹鍠栭崺鈧い鎺戝閺嬩線鏌熼幑鎰靛殭閸烆垶姊虹€圭姵銆冮柤鍐茬埣瀹曟繈鏁冮埀顒勨€旈崘顔嘉ч柛鈩冾殔濞兼垿姊虹粙娆惧剱闁圭懓娲璇测槈閵忊€充簽婵炶揪绲介幗婊勭閳轰緡娓婚柕鍫濋楠炴牗绻涘ù瀣珖缂侇喛顕ч埥澶娢熼柨瀣垫綌婵犵妲呴崹鎶藉煕閸惊锝夊醇閺囩喓鍘介梺缁樻煥閹芥粓鎯屾繝鍥ㄢ拺閻㈩垼鍠氱粔顔筋殽閻愭彃鏆為柕鍫秮瀹曟﹢鍩￠崘銊バ﹂梺璇查缁犲秹宕曢崡鐐嶆稑鈽夐姀鐘插亶闂備緡鍓欑粔鐢告偂閻旂厧绠归柟纰卞幖閻忥絿绱掓径鎰锭闂囧绻濇繝鍌涘櫣濞寸姍鍛＜妞ゆ柨澧界敮娑㈡倵娴ｅ啫浜归柍褜鍓氱粙鎺椻€﹂崶顒€鍌ㄦい蹇撶墛閳锋垿鏌涢幘鏉戠祷濞存粍绻勭槐鎺楊敊婵傜寮伴梺璇″灠閼活垶鍩㈡惔銈囩杸濠电姴鍟弶鎼佹⒒娴ｅ搫浠洪柛搴や含婢规洟顢橀姀鐘殿啈闂佺粯顭囩划顖炴偂濞嗘垟鍋撻悷鏉款伀濠⒀勵殜瀹曟娊鎮滃Ο闀愮盎闂佹寧姊归崕鎶姐€傛總鍛婄厵妞ゆ牗绋掗ˉ鍫ユ煛娴ｇ懓濮嶇€规洟浜堕崺锟犲磼濠婂應妲堥梻鍌氬€搁崐鎼佸磹閹间礁纾圭€瑰嫭鍣磋ぐ鎺戠倞妞ゆ帒顦伴弲顏堟⒑閸濆嫮鈻夐柛妯恒偢瀹曞綊宕掑锝嗘杸闂佺鏈划鐘绘倿妤ｅ啯鐓曢柕濞垮劚閳ь剙鐏濋～蹇撁洪宥嗘櫌闂侀€炲苯澧扮紒顔芥楠炴﹢顢欓悡搴ｂ偓顓㈡⒑缁嬭法鐏遍柛瀣仱閹ょ疀閹绢垱鏂€闂佺粯鍔欏褎绂嶉悙顒傜闁告侗鍘介ˉ銏ゆ煛瀹€瀣М妤犵偞锕㈠畷妯好圭€ｎ亙澹曟繝鐢靛У閼归箖鎮為崹顐犱簻闁瑰搫妫楁禍鍓х磽娴ｅ搫孝缂佸鎳撻悾鐑藉即閵忥紕鍔堕悗骞垮劚濡绂嶉崡鐐╂斀闁绘顕滃銉╂煕濡鍔ら悡銈嗐亜韫囨挻鍣烘繛鍛矋缁绘繈濮€閿濆棛銆愬銈嗗灥濞差厼鐣烽姀銈嗙劶鐎广儱妫岄幏娲偡濠婂懎顣奸悽顖涘笚缁傚秵瀵肩€涙鍘遍梺瑙勫劤椤曨厼煤閹绢喗鐓涘ù锝呮憸瀛濆銈嗘尭閸氬顕ラ崟顓涘亾閿濆骸澧?- 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮诲☉妯锋斀闁告洦鍋勬慨銏ゆ⒑濞茶骞楅柟鐟版喘瀵鏁愭径濠勵吅濠电姴鐏氶崝鏍礊濡ゅ懏鈷戦梺顐ゅ仜閼活垱鏅堕鈧弻鐔兼惞椤愵剝鈧法鈧鍣崑濠傜暦濮椻偓椤㈡瑩鎳栭埡瀣簥濠电姵顔栭崰妤呮晝閵忋垺鍏滈柟闂寸閼歌绻涘顔荤凹闁抽攱甯掗妴鎺戭潩閿濆懍澹曟繝鐢靛仒閸栫娀宕堕敐鍌氫壕闁挎洖鍋嗛弫鍥煏韫囧﹥顎嗛柟绋垮暣濮婃椽宕ㄦ繝鍐槱闂佹悶鍔戞禍璺虹暦閹版澘鍨傛い鏃€鑹剧紞濠囧箖閳轰緡鍟呮い鏃傚帶婢瑰姊绘担铏瑰笡闁圭鐖煎畷鏇㈡嚑椤掍礁搴婂┑鐐村灟閸ㄥ湱绮婚敐澶嬬厽闁瑰瓨绻冮ˉ鐘绘煕閺冨牊鏁辩紒缁樼箞閸╂盯鍩€椤掍焦濯撮柛婵勫劙缁辨瑩姊绘担鍛婃儓濠㈣泛娲畷婊冣攽鐎ｎ亞顔嗛梺鍛婄☉閻°劑藟閸喓绠鹃柟瀵稿仜缁楁帒霉濠婂懎浜剧紒缁樼箞濡啫鈽夐崡鐐插闁诲氦顫夐幐椋庢濮樿泛绠栨俊銈呮噺閺呮煡骞栫划鐟板⒉闁诲繐绉瑰铏圭矙濞嗘儳鍓炬繛瀛樼矋缁诲牊淇婇悽绋跨妞ゆ牗鑹鹃崬銊╂⒑濮瑰洤鐏叉繛浣冲洤鏄ラ悘鐐缎掗弨?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涚€ｃ劌鈧繈寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閹肩偛濡奸柛濠傛健瀵鈽夐姀鈺傛櫇闂佹寧绻傚Λ娑⑺囬妷銉㈡斀妞ゆ梹顑欏鎰版煟閹垮嫮绡€鐎殿喖顭烽弫鎰緞婵犲嫮娼夐梻浣规偠閸庮垶宕曢鈧畷鎴﹀箻鐠囪尙鍔﹀銈嗗笒鐎氼參鎮￠弴銏″€甸柨婵嗛娴滄繈鎮樿箛锝呭籍闁哄苯绉归幐濠冨緞濡亶锕傛⒑娴兼瑧鎮奸柛蹇斆悾鐑藉醇閺囩偟鍘搁梺鍛婂姦娴滄粓鎮欐繝鍕＝闁稿本鑹鹃埀顒佹倐瀹曟劙鎮滈懞銉モ偓鍧楁煥閺囩偛鈧爼鍩€椤掆偓閸熸潙鐣烽妸銉桨闁靛牆鎳忛崰妯活殽閻愯尙效妞ゃ垺鐟╁畷婊嗩槻妞?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓鍝ョ矆閸喐鍙忔俊顖涘绾墽鐥幆褜鐓奸柡灞剧☉閳藉宕￠悙鍏哥敾闂備礁鎼Λ娆戝垝閹捐钃熼柨婵嗩槸缁秹鏌涚仦缁㈡畷閻庢碍鐩鐑樻姜閹殿噮妲梺鎸庢处娴滎亜顕ｇ拠娴嬫闁靛繒濮堥妸锔轰簻闁哄啫娲ら崥褰掓煛閸℃﹩娈曠紒缁樼〒閳ь剚绋掗…鍥儗婵犲嫮纾界€广儱鎷戦煬顒傗偓娈垮枛椤兘寮幘缁樺亹闁肩⒈鍓欓埀顒傚仱濮婃椽宕崟顓炩叡闂佽桨鐒﹂幃鍌氼嚕椤愶箑鍐€妞ゎ剦鍓氬Λ鍐箖閳哄懏顥堟繛鎴烆殕濠⑩偓闂傚倷鐒﹂幃鍫曞礉鐎ｎ剙鍨濇繛鍡楁禋閸ゆ洖鈹戦悩宕囶暡闁哄懏褰冮…鍧楁嚋閻㈢偣鈧帞绱掔€ｎ亞绠版い顏勫暣婵″爼宕卞Δ鈧鎴︽⒑缁嬫鍎愰柟鍛婃倐閸╃偤骞嬮敃鈧悘鎶芥煠绾板崬澧伴柣鎾存崌濮婃椽宕崟顒佹嫳闂佺儵鏅╅崹璺虹暦濞差亝鏅搁柣妯垮皺閿涙粌鈹戦悩璇у伐閻庢凹鍓熷畷褰掓焼瀹ュ棌鎷绘繛杈剧导鐠€锕傚绩閻楀牏绠鹃柛娑卞枟缁€瀣殽閻愭潙鐏寸€规洘鍎奸ˇ鎾煛閸☆參妾ǎ鍥э躬椤㈡稑鈽夐崡鐐插婵犵鍓濋悡锛勭不閺嵮屾綎?0闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎺嶇劍椤斿洭姊绘担鍛婅础闁稿簺鍊濆畷鐢告晝閳ь剟鍩ユ径濞㈢喖宕楅崗鑲╂殾闂傚倷绀侀幉鈥趁洪敃鍌氱；闁糕剝绋戦拑鐔兼煕椤愮姴鍔滈柣鎾跺枛楠炴牠骞栭鐐典化缂備礁顦遍弫濠氬蓟濞戞埃鍋撻敐搴濈凹妞ゃ儯鍨介弻娑㈠煘閸喚浼堥悗娈垮櫘閸ｏ絽鐣烽幒鎳虫棃鍩€椤掍胶顩查柣鎰靛墻濞堜粙鏌ｉ幇顖氱毢濞寸姰鍨介弻娑㈠籍閳ь剛鍠婂鍡欌攳濠电姴娴傞弫鍐煥濠靛棗顒㈤柣銈勭窔濮婅櫣娑甸崨顔惧涧闂佽崵鍠嗛崝鎴炰繆閻㈢绠涢柡澶庢硶椤斿﹪姊虹憴鍕婵炲鐩悰顕€骞囬悧鍫氭嫽婵炶揪绲肩拃锕傛倿妤ｅ啯鍋犳慨妯煎帶娴滄壆鈧娲橀崝娆忣嚕閹绢喗鍊婚柛鈩冾殕椤撳潡姊洪懡銈呅ｅù婊€绮欏畷婵囨償閿濆拋妫?- 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢鍏尖拻閻庣數顭堟俊浠嬫⒑缁嬫鍎嶉柛濠冪箞瀵寮撮悢铏诡啎闂佸壊鐓堥崰鏍ㄦ叏鐠鸿　鏀介柣鎰摠鐏忣厽銇勯鐘插幋鐎殿喛顕ч埥澶娢熼崗鍏肩暦闂備線鈧偛鑻晶瀵糕偓瑙勬礃閸ㄧ敻鍩ユ径濠庢僵闁告瑦顭囬悷婵嬫⒒娴ｇ儤鍤€妞ゆ洦鍘介幈銊╂偨缁嬭法鐛ラ梺瑙勫婢ф宕愰崼鏇熺厽闁归偊鍘肩徊濠氭煃闁垮顥堥柡灞界Ч閹兘骞嶉褋鍨介弻宥囨喆閸曨偆浼岄梺璇″枓閺呯姴鐣烽敐鍡楃窞閻庯綆鍋勯埀顒勵棑缁辨捇宕掑▎鎺戝帯婵犳鍠氶弫鎼佸极椤斿槈鏃堝川椤撳浄绠撻弻娑㈠即閵娿儳浠╅梺鍛婂姀閸嬫捇姊绘笟鈧褑鍣归梺鍛婃处閸嬪懘鎮甸鈧濠氬磼濞嗘劗銈伴悗瑙勬礈閺佽鐣锋导鏉戠疀妞ゆ棁妫勬惔濠囨⒑閸撴彃浜栭柛搴や含缁寮介鐔蜂画濠电偛妫楃换鎰邦敂椤忓嫧鏀芥い鏍ㄥ嚬閸ょ喓绱掓潏銊ョ闁逞屽墾缂嶅棝宕㈤悾灞惧厹闁割偅娲橀悡鐔兼煃鏉炴壆鍔嶉柟鐧哥悼缁?婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾剧粯绻涢幋娆忕労闁轰礁顑嗛妵鍕箻鐠虹儤鐎鹃梺鍛婄懃缁绘﹢寮婚悢铏圭＜闁靛繒濮甸悘宥夋⒑閸濆嫭鍣虹紒璇茬墦瀵寮撮姀鐘诲敹濠电姴鐏氶崝鏍懅婵犵鍓濋〃鍛村箠韫囨洘宕叉繝闈涱儏椤懘鏌ㄥ┑鍡橆棤闁靛棙鍔曢—鍐Χ閸℃浠村┑鐐叉▕閸欏啫鐣峰ú顏勵潊闁靛牆鎳愰惈鍕⒑缁嬫寧婀版い銊ユ噺缁傚秹鎮欓澶嬵啍闂佺粯鍔樼亸娆愮閵忋倖鐓曢柡鍐ｅ亾缁炬澘绉电粚杈ㄧ節閸ヨ埖鏅濋梺鎸庣箓鐎涒晠鎮挎笟鈧幃妤冩喆閸曨剛锛橀梺鎼炲妺缁瑩鎮伴鈧獮鎺楀箠閾忣偅鈷愰柟宄版噽閸栨牠寮撮悙鏉款棜闂備礁澹婇悡鍫ュ磻閸℃瑧涓嶅Δ锝呭暞閻撴瑩鎮楀☉娆樼劷缂佺姵锕㈤弻銊モ槈濡す銈囩磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽绛嬫缂?闂?- 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈攻閸欏繘鏌ｉ幋婵愭綗闁逞屽墮閸婂湱绮嬮幒鏂哄亾閿濆簼绨介柛鏃撶畱椤啴濡堕崱妤€娼戦梺绋款儐閹瑰洭寮诲☉銏″亜闂佸灝顑呮禒鎾⒑缁洘鏉归柛瀣尭椤啴濡堕崱妤€娼戦梺绋款儐閹稿墽妲愰幘鎰佸悑闁告粌鍟抽崥顐⑽旈悩闈涗粶闁哥噥鍋夐悘鎺楁煟閻樺弶绌块悘蹇旂懅缁綁鎮欑€靛摜鐦堥梺姹囧灲濞佳勭瑜旈弻娑氣偓锝庡亝瀹曞矂鏌熼鍡欑瘈濠殿喒鍋撻梺闈涚墕濡矂骞忓ú顏呪拺闁告繂瀚埀顒€鐖煎畷鏇㈠箵閹哄棙鐎洪梺鍛婄☉閻°劑鎮￠弴銏＄厽闁哄洦姘ㄩˇ锕傛煟韫囥儳鎮肩紒杈ㄥ浮椤㈡瑧鍠婃潏鈺佹倯婵°倗濮烽崑鐐垫暜閹烘洜浜欏┑鐐舵彧缁蹭粙骞栭锔惧祦闁割偅绺鹃弨浠嬫煟濡櫣浠涢柡鍡忔櫅閳规垿顢欑喊鍗炴闂侀€炲苯澧柛鎴濈秺瀹曟粌鈽夐姀鐘崇€銈嗘磵閸嬫挾鈧娲樼划宥夊箯閸涘瓨鎯為柣褍鎽滄惔濠囨⒒閸屾瑦绁版い鏇熺墵瀹曞綊宕奸弴妯峰亾閸岀偞鏅濋柛灞句亢琚濇俊鐐€栭崝褔姊介崟顖涘亗婵炲棙鍨熼崑鎾绘偡閺夋浼冮梺绋款儏閿曨亜鐣烽弴銏犵疀闁绘鐗忛崣鍡椻攽閻愭潙鐏﹂柣鐔村劜閹便劑宕奸妷锔惧幍閻庣懓瀚晶妤呭吹閸ヮ剚鐓欓柣鎾虫捣缁夎櫣鈧娲樼划鎾荤嵁閸ヮ剙鐓涘ù锝嗗絻娴滅偓绻濋棃娑欙紞婵炲吋鐗犻弻娑樷攽閸℃褰呴悷婊勬煥閻ｇ兘骞嗛柇锔叫╂俊鐐€ら崜娆撴偋閹捐钃熼柨婵嗘閸庣喖鏌曡箛鏇炐㈡慨锝呯墛缁绘稓鈧稒顭囬惌瀣磼鐠囨彃顏柛鎺撳笒椤繈顢橀悢铏剐ら梻渚€娼ц噹闁告侗鍨遍～宀勬⒒閸屾瑧鍔嶉柟顔肩埣瀹曟洖顭ㄩ崼婵嗙獩濡炪倖鐗楃粙鎺楊敊閹寸偟绡€缁炬澘顦辩壕鍧楁煕鐎ｎ偄鐏寸€规洘鍔欏浠嬵敇閻旇渹缃曢梻浣筋潐瀹曟﹢顢氳婢规洜鎲撮崟顏嗙畾闂侀潧鐗嗛幊搴ㄥ汲閻斿吋鐓熸い鎾跺仦椤ユ粓鏌嶇憴鍕仸鐎垫澘瀚禒锔炬媼瀹曞洨姊緈ories 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄У瑜板啴婀侀梺鎸庣箓濞层劑濡存繝鍥ㄧ厸閻庯綆浜炴晥闂佸搫琚崝宀勫煘閹达箑骞㈤柍鍝勫€愰敃鍌涒拺缂備焦蓱鐏忎即鏌ㄩ弴妯虹伈鐎殿喖顭烽崹楣冨箛娴ｅ憡鍊梺纭呭亹鐞涖儵鍩€椤掆偓绾绢參顢欓幇鐗堚拻濞达絽鎲￠幆鍫熴亜閹存繂顏繛鍡愬灩椤繄鎹勬ウ鎸庢啺闂備胶绮弻銊╂儍濠靛鍑犻柡鍐ㄧ墛閻撴洘銇勯鐔风仴闁哄鍠栭弻锝堢疀閺冣偓瀹曞本鎱?""


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
                            user_answer = user_response.get("answer", "缂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙闁诡垳鍋ら獮鏍庨鈧俊濂告煟椤撶噥娈滄鐐寸墪鑿愭い鎺嗗亾濠德ゅ亹缁辨帡骞囬褎鐣风紓浣虹帛閻╊垶鐛€ｎ亖鏋庨煫鍥ㄦ礀婵爼姊?)
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

Add the following under the `### 闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃秹锝炲┑瀣櫇闁稿矉濡囩粙蹇旂節閵忥絽鐓愰柛鏃€娲滅划濠氬冀椤撶喓鍘卞銈嗗姧缁插墽绮堥埀顒傜磼閻愵剙鍔ゆ繛灏栤偓鎰佹綎婵炲樊浜堕弫鍡涙煃瑜滈崜娑氬垝閺冨牆绠绘い鏃囨閸撶懓鈹戞幊閸婃洟骞婅箛娑欏亗婵炲棙鍨圭壕濂告倵閿濆簼绨藉ù鐘灪閵囧嫰骞掔€ｎ亞浠奸梺瀹狀潐閸ㄥ潡銆佸☉妯锋婵炲棗绻愰弨顓㈡⒒娴ｇ瓔鍤冮柛鐘崇墱缁辩偞绻濋崶鈺佺ウ婵炴挻鍩冮崑鎾搭殽閻愭潙娴鐐差儏閳规垿骞囬鐟颁壕闁圭虎鍠楅埛鎺懨归敐鍛暈闁诡垰鐗婃穱濠囶敃閿濆孩鐤侀悗?section in `Agent.md`:

```markdown
- recall_memory闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍏煎€绘慨妤€妫欓悾鐑芥⒑閹肩偛鈧洟鎯岄崒鐐茶摕婵炴垯鍨圭粻缁樹繆閵堝倸浜鹃梺纭呮珪閸旀瑨妫熷銈嗙墱閸嬬偤鎮￠悢鐓庣闁圭⒈鍘奸悘锝囩磼婢跺本鏆柡灞剧洴閹晠骞囨担鍦澒闂佽姤顭囬崰鏍蓟濞戙垹鐒洪柛鎰典簴婵洭姊虹紒妯诲碍闁哥喍鍗抽獮澶岀矙濞嗗墽鍙嗛梺鍓插亝缁诲嫰藝椤撶偐鏀介柣鎰綑閻忕喖鏌涢妸銉﹁础缂侇喖顭烽幃銏ゅ礂閼测晛骞楁繝寰锋澘鈧劙宕戦幘缁樼厽婵°倐鍋撻柨鏇樺劦瀹曟碍绻濋崶褏顔掑銈嗘⒒閺咁偊宕㈤崡鐐╂斀闁绘劖娼欓悘锕傛煥閺囥劌浜扮€规洘绻堥幃銏ゅ箹閻愭壆鐩庨梻浣瑰閺屻劑骞栭锕€绀夐柨鏃€鍨濈换鍡樸亜閹扳晛鐏柛銈呮处閵囧嫰濮€閳╁啰顦版繝娈垮枓閸嬫捇姊洪弬銉︽珔闁哥噥鍨跺畷鎰版煥鐎ｎ剛鐦堢紒鍓у钃辨い顐躬閺屾稓鈧綆浜濋崵鍥煙椤栨艾顏い銏＄☉椤繈鎮℃惔銏╁悪濠碉紕鍋戦崐鏍礉瑜忕划濠氬箣濠靛洨鍑藉┑鐘垫暩婵即宕归悡搴樻灃婵炴垯鍨洪弲婵嬫煥閺囩偛浜為柡浣告处缁绘稑顔忛鑽ゅ嚬闂佹娊鏀遍崹鍧楀蓟閿濆绠涢梻鍫熺☉閳峰绻濋姀锝庢綈闁挎洏鍨藉璇测槈濞嗘垹鐦堥梺绋胯閸婃宕ョ€ｎ亶娓婚柕鍫濆暙閻忣亪鏌ㄥ鑸靛亗闁靛牆妫庢禍婊堢叓閸ャ劍灏伴柛锝勭矙閺屾稑顫滈埀顒佺鐠轰警娼栭柧蹇氼潐閸犲棝鏌涢弴銊ヤ簻濠殿喓鍨荤槐鎺楀礈瑜戝鎼佹煕濞嗗苯浜鹃梻浣侯焾閿曘倝鎮洪妸褎宕叉繝闈涱儐閸嬨劑姊婚崼鐔衡棩缂侇喖鐖煎铏圭磼濮楀棙鐣堕梺鎸庢处娴滄粓鎮鹃悿顖樹汗闁圭儤鍨甸悗顓烆渻閵堝棙鈷掗柛瀣尭閳绘挻銈ｉ崘鈹炬嫼缂佺虎鍘奸幊蹇氥亹瑜忕槐鎺楀箵閹烘挸浠撮梺璇″枛濞硷繝宕洪埀顒併亜閹烘垵顏柍閿嬪灴閹嘲鈻庤箛鎿冧患闂佸憡鏌ｉ崐妤呭焵椤掑喚娼愭繛璇х畵瀹曟粌顫濇潏鈺冪効闂佸湱鍎ら崵姘洪宥嗘櫆闂佸憡渚楁禍婵堚偓姘偢濮婂宕掑顑藉亾閹间焦鍋嬪┑鐘插閻瑩鏌熼悜姗嗘濠㈣泛艌閺嬪酣鏌熼柇锔跨敖缂佺姵宀稿铏圭磼濡搫顫嶅┑鐐插悑閻熝呭垝椤撯槅妲鹃梺閫炲苯澧い鏃€鐗犲畷顖烆敃閿曗偓閻愬﹦鎲歌箛娴板洭寮跺▎鐐瘜闂侀潧鐗嗗Λ娑欐櫠椤掍焦鍙忔俊顖滎焾婵倿鏌熼鈧粻鏍嵁閸℃凹妾ㄥ┑鐐存尭椤兘寮婚弴銏犻唶婵犻潧娴傚Λ銈嗙節閳封偓鐏炶棄顫紓浣介哺鐢偤鍩€椤掑﹦绉甸柛瀣閹﹢骞橀鐣屽幍濡炪倖姊婚悡顐︻敂閸モ晙绨烽梻鍌欑閹测剝绗熷Δ鍛獥婵娉涢崒銊╂⒑椤掆偓缁夌敻鍩涢幋鐘冲枑闁绘鐗嗙粭鎺懨瑰鈧崡鎶藉蓟濞戙垹绠婚悗闈涙啞閸掓盯姊烘潪鎵槮缂佸鎸抽、姗€宕楅悡搴ｇ獮闁诲函缍嗛崜娆撶嵁濡ゅ懏鈷戦柛锔诲幖閸斿鈹戦悙璇у伐闁伙絿鍏樺鎾閳藉棙顥堟繝鐢靛仦閸ㄩ潧鐣烽鈧埢鎾诲Ω閵夘喗瀵岄梺闈涚墕濡瑧澹曢悽鍛婄厱閻庯綆鍋呯亸鐢告煃瑜滈崜姘额敊閺嶎厼绐楁慨妯挎硾閺嬩線鎮归崶褍妫樻繛鎴欏灩缁€鍐煏婵炲灝鐏い顐㈢Ч濮婃椽宕烽鐐插闂佽鎮傜粻鏍春閳ь剚銇勯幒鍡椾壕闂侀潧鐗忛…鍫ワ綖韫囨洜纾兼俊顖濐嚙椤庢捇鏌ｉ悢鍝ユ噧閻庢哎鍔嶇粋鎺曨槻闁宠鍨块幃娆撴濞戞ü绮繝鐢靛仜閻ㄧ兘鍩€椤掆偓绾绢參寮抽敂鐣岀瘈闂傚牊绋掑婵堢磼閳锯偓閸嬫捇姊绘担瑙勫仩闁稿孩绮撳畷銊╊敇閻愭劖娲栭埞鎴︽晬閸曨偂鏉梺绋匡攻閻楁洟顢欒箛鏃傜瘈婵﹩鍓涢敍娑㈡⒑閻熸澘鈷旂紒顕呭灦閹繝寮撮悙鈺傛杸闂佺粯锚瀵墎绮婇埡鍌欑箚妞ゆ劧绲介悘鈺冪磼鏉堛劌娴い銏″哺瀹曘劑顢橀悙娈垮晥闂佽楠搁悘姘熆濡皷鍋撳鐓庢灍缂佸倹甯￠弫鍐磼濮樿京鏆伴柣鐔哥矊妤犳瓕顣鹃梺鎼炲劀閳ь剟寮ㄦ禒瀣厽闁归偊鍨伴悡鎰喐閹跺﹤鎳愮壕濂告煠閼规澘鐓愭い銉ヮ樀閺屻劑寮村Ο铏逛紙閻庤娲╃换婵嬪箖濞嗗浚鍚嬮煫鍥ㄦ礈琚﹀┑鐘殿暯閸撴繈骞冮崒鐐叉瀬闁稿瞼鍋涚粈鍫㈡喐濠婂牆鐤幖娣妽閳锋帒霉閿濆牊顏犻柕鍡楋躬閺屽秷顧侀柛鎾寸懅婢规洟顢橀悩鍏哥瑝濠殿喗顭堥崺鏍偂閺囥垺鍊甸柨婵嗛娴滄繄鈧娲栭張顒勩€冮妷鈺傚€烽柛娆忣槸椤︹晠姊洪悷鏉挎Щ闁硅櫕锚閻ｇ兘濡搁敂鍓х槇闁硅偐琛ラ崜婵嗏枍婵犲洦鈷掗柛灞捐壘閳ь剙鍢查湁闁搞儜鍛闂佸壊鐓堥崑鍛村矗韫囨稒鐓涘璺侯儏濞堫喗绻涘顔荤凹闁哄懏绮撻弻锝夊箛闂堟稑顫╅柟鍏兼綑閿曨亜顫忓ú顏勭闁圭粯甯婄花鎾⒑缁嬫寧鍞夊ù婊庡墰閸掓帡宕奸妷銉э紲濠电偞鍨堕〃鍫㈢不濮橆剦娓婚柕鍫濇婢ь剟鏌よぐ鎺旂暫妤犵偛鍟撮獮瀣晜閽樺鍋撻崹顐ｅ弿婵☆垳鍘х敮璺侯熆瑜庨幐鎶藉蓟閿涘嫪娌柛鎾楀嫬鍨辨俊銈囧Х閸嬫稑煤椤撶偟鏆︽俊銈呮噹娴肩娀鏌曟径鍫濆姎婵絽鐗撳濠氬磼濞嗘埈妲梺鍦拡閸嬪嫯鐏嬪┑掳鍊曢崯顖氱暦閸欏鍙忔俊鐐额嚙娴滈箖鎮楀▓鍨灈妞ゎ參鏀辨穱濠囧箹娴ｈ倽銊╂煏韫囧﹥顫婃繛鍏兼⒐缁绘繄鍠婂Ο娲绘綉闂佹悶鍔嬮崡鎶藉箖濡　鏀介悗锝呯仛閺呮粌顪冮妶鍡樺蔼闁搞劍妞藉畷鎴﹀焺閸愵亞鐦堟繝鐢靛Т閸婃悂顢旈埡鍛畾闁绘柨鍚嬮埛鎴︽煙閼测晛浠滈柛鏂哄亾闂備礁鎲″ú锕傚磻閸℃稑围闁割偅娲橀埛鎺楁煕鐏炲墽鎳呯紒鎰⒐缁绘稒鎷呴崘鍙夘棞婵炲拑缍佸缁樼瑹閳ь剟鍩€椤掑倸浠滈柤娲诲灡閺呭爼骞橀鐣屽幈闂佸疇顫夐崕铏閻愵兛绻嗛柣鎰典簻閳ь剚鐗滈弫顔界節閸曨剦鍋ㄩ梺璺ㄥ枔婵敻宕愰崹顔氬綊鎮╁顔煎壉闂佺粯鎸搁崯浼村箟缁嬫鐓ラ柛顐ｇ箘椤︻厼鈹戦悙鍙夘棞濡ょ姴绻橀幊鎾诲锤濡や讲鎷哄銈嗗坊閸嬫挾绱掓径濠庡殶濠㈣娲樼换婵嗩潩椤撶姴甯鹃梻浣稿閸嬪懐鎹㈤崘顔奸棷闁绘垼濮ら悡鍐喐濠婂牆绀堟慨妯块哺閺嗘粓鏌嶉妷銉э紞闁哄棴闄勭换婵囩節閸屾凹浠炬繝娈垮灡閹告娊寮婚敐澶嬪亜闁告繂瀚烽弳顓炩攽椤曞棛鍒版繛灞傚€濋崺鐐哄箣閿旇棄鈧兘鏌ら幖浣规锭婵炴嚪鍛＝濞达絿鎳撶徊缁樼箾绾绡€闁搞劑绠栭弫鍐磼濮樿泛鏁归梻渚€娼чˇ顓㈠磿閻㈢鏋佹繝濠傚缁♀偓闂佹眹鍨藉褍鐡繝鐢靛仩椤曟粎绮婚幘璇茬畺闁跨喓濮撮崡鎶芥煟閺冨洦顏犳い鏃€娲熷铏瑰寲閺囩偛鈷夐梺鎸庢皑缁辨帒螖娴ｅ摜顑傜紓浣介哺鐢繝鐛径灞稿亾閿濆骸澧伴柡鍡欏█閺屻倝骞愭惔鈥愁潚闂佸搫鏈惄顖涗繆閻戣棄绠ｆ繝闈涚唵閵夆晜鐓曟慨妯煎帶娴滄粓鎽堕弽顓熺厽婵せ鍋撴繛浣冲嫮顩烽柟鐑樻⒒绾惧ジ鏌ら幖浣规锭闁告繃妞介弻鏇㈠幢閺囩媭妲梺瀹犳椤︻垵鐏掗梻浣哥仢椤戞劕顭囬弮鈧换婵嬫偨闂堟稐绮跺┑鈽嗗亝閻熴劑骞楅锔藉仩婵ǚ鍋撻柛鏇ㄥ幘閻﹀牓姊哄Ч鍥х伈婵炰匠鍕浄闁冲搫鎳忛悡娆愮箾閼奸鍞虹紒銊ф櫕缁辨帗娼忛埡浣锋闂佺硶鏂侀崑鎾愁渻閵堝棗绗傞柤鍐插缁骞嗚閻斿棝鎮规潪鎷岊劅闁稿孩鍔楃槐鎺楀焵椤掑倵鍋撻敐搴″幋闁?- save_memory闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍏煎€绘慨妤€妫欓悾鐑芥⒑閹肩偛鈧洟鎯岄崒鐐茶摕闁绘梻鍎ら崰鍡涙煕閺囥劌浜滄い顐㈡处缁绘稓鈧稒顭囬惌濠冪節閳ь剟鏌嗗鍛枀闂佸憡绋戦敃銉╁磿閻斿吋鐓ユ繝闈涙瀹告繈鏌ｉ幘瀛橆棃婵﹥妞藉畷銊︾節鎼淬垻鏆梻浣侯焾椤戝棝宕濆▎蹇ｅ殨闁靛濡囬々鐑芥倵閿濆骸浜為柛姗€浜跺娲棘閵夛附鐝旈梺鍝ュ枍閸楁娊鐛繝鍥х妞ゆ牗绋撻崢鐢告⒑閸︻厾甯涢悽顖氭喘瀹曟垿濮€閳╁啫寮挎繝鐢靛Т閸婂綊骞嗛崼銉﹀亗闁靛牆娲ㄧ壕钘壝归敐鍜佹綘妞ゅ繐鐗嗛悡婵嬬叓閸ャ劎鈯曢柍閿嬪灴閺屾稑鈽夊鍫熸暰闂佺粯鎸堕崕宕囨閹烘挸绶為悘鐐村劤濞堝矂姊烘导娆戞偧闁稿繑锚閻ｇ兘顢曢敃鈧粈瀣煏婵犲繐鐦滄繛鍏兼濮婄粯绗熼埀顒€顭囪閹广垽骞掗幘鏉戝伎闂佸搫顦伴崺鍫ュ吹閺囥垺鐓熼柟杈剧到琚氶梺缁樻尰閻熲晠寮婚妶澶婃嵍妞ゆ挾鍎愰弳顓㈡偡濠婂嫬惟闁告侗鍨抽敍婊堟⒑閸涘﹦鎳冩い锔垮嵆婵￠潧鈹戠€ｎ偆鍘遍梺瀹狀潐閸庤櫕绂嶉悙顑跨箚闁绘劦浜滈埀顒佺墱閺侇喗绻濋崟顒夊仺闂佽法鍠撴慨鐢稿磹閸啔褰掓偐瀹割喖鍓遍梺缁樻尰閻燂箓濡甸崟顖氱睄闁搞儴娉涘▓顓㈡倵鐟欏嫭灏俊顐ｎ殜閸╃偤骞嬮敃鈧悞娲煕閹般劍娅呴柍褜鍓氶崝鏇㈠煘閹达箑鐒洪柛鎰ㄦ櫅閳ь剚鍔欓弻鈩冩媴缁嬫寧娈婚梺绯曟杹閸嬫挸顪冮妶鍡楀潑闁稿鎹囬弻宥夋寠婢舵ɑ歇濡炪倧绠掗～澶愬箞閵婏妇绡€闁稿本绋掗崕鎾绘煛娴ｅ摜澧﹂柡灞剧洴婵＄兘骞嬪┑鍡樼亾闂佽瀛╂繛濠傤潖閾忚瀚氶柟缁樺俯閸斿姊洪崨濠傜伇妞ゎ偄顦辩划瀣吋閸涱亝鏂€闂佸壊鍋侀崹濠氭偂閺冨牊鐓涘璺猴功婢ф垿鏌涢弬鎸庢崳鐎殿啫鍥х劦妞ゆ帒瀚埛鎴︽煙閼测晛浠滈柛鏂哄亾闂備礁鎲℃笟妤呭垂閸楃偐鏋旈柛婵嗗閺€浠嬫煥濞戞ê顏╁ù婊冦偢閺屾稒绻濋崘顏勨拰闂佽鍟崶褏顔掗柣鐘叉穿鐏忔瑩鏁嶅▎蹇婃斀閹烘娊宕愰弴銏犵柈濞寸厧鐡ㄩ崕妤呮煕閳╁喚娈㈤柣鏂挎閹綊宕崟顐⑩枏闂佸壊鍋呴幆濠囨晲婢跺﹪鍞堕梺闈涱檧婵″洭宕㈤悽鍛娾拺閻犲洠鈧磭鈧鏌涘鍐ㄦ殶缂佲偓婵犲洦鈷戦柛婵勫劚閺嬫梹銇勯鐐靛ⅵ闁炽儲妫冨畷姗€顢欓崲澹洦鐓曢悘鐐插⒔閳洟鏌ｅ┑鍕缂佽鲸鎸婚幏鍛村传閸曟埊缍侀弻鐔兼偡閻楀牆鏋犻梺璇″枙閸楁娊銆佸璺虹劦妞ゆ帒瀚畵渚€鏌熼悜妯烘闁哄啫鐗嗛悞鍨亜閹哄秶顦﹂柛鏃€妫冨濠氬磼濞嗘垵濡介柣搴ｇ懗閸愮偓缍庢繝鐢靛У閼归箖鎮块悙顑句簻闁规澘澧庨悾杈╃磼閳ь剚寰勯幇顓犲幗闂佺鎻徊鍊燁暱闂備焦濞婇弨閬嶅垂閸噮娼栧┑鐘宠壘闁卞洭鏌ｉ弮鍥モ偓鈧┑顔兼搐椤啴濡堕崘銊ュ缂備緡鍠楅幑鍥ь嚕鐠囨祴妲堟繛鍡樺灩閻﹀牓姊洪幖鐐插姤闁糕晜鐗犺棢闁哄稁鍘介埛鎴︽煟閻旂顥嬮柣锝庡弮閺屾盯濡搁妷褏楔闂佹寧绻勯崑娑㈠煘閹寸姭鍋撻敐搴濈敖妞ゆ挸鍚嬬换娑欐綇閸撗呅滈梺鍝勬噹瀵墎绮╅悢鐓庡嵆闁绘劏鏅滈弬鈧梻浣虹帛閸旀牕顭囧▎鎾村€堕柨鏂款潟娴滄粓鐓崶椋庡闂侇収鍨遍妵鍕閳╁喚妫冮悗瑙勬磸閸旀垿銆佸▎鎾村仼閻忕偠妫勯埢蹇涙⒒閸屾艾鈧兘鎳楅崜浣稿灊妞ゆ牜鍋愰埀顒婄畵瀹曠厧鈹戦崘鈺冣偓娲⒑閹稿海绠撴い锔垮嵆瀹曟垿顢旈崼鐔哄帗閻熸粍绮撳畷婊堟偄婵傚缍庡┑鐐叉▕娴滄粌顔忓┑鍡忔斀闁绘ɑ褰冮銈呪攽椤斿吋鍠樻慨濠勫劋鐎电厧鈻庨幋鐘橈絾绻涚€涙鐭ゅù婊庝簻閻ｅ嘲煤椤忓嫮鍔﹀銈嗗笂闂勫秵绂嶅鍫熺厵闁告繂瀚ˉ婊兠瑰鍐ㄢ挃缂佽鲸鎸婚幏鍛存惞閻熸壆顐奸梻浣瑰瀹€鎼佸蓟閿濆鏅查柛娑卞幗浜涢梺鍓х帛閻楃娀寮诲☉妯锋闁告鍋涚猾宥夋⒑閸濄儱浠滈柣鏍帶椤繐煤椤忓拋妫冨┑鐐村灦濮樸劑鎮炬ィ鍐┾拺闁告稑锕ョ亸鎵磼鐠囨彃鈧潡宕?ask_user 缂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙闁诡垳鍋ら獮鏍庨鈧俊濂告煟椤撶噥娈滄鐐寸墪鑿愭い鎺嗗亾濠德ゅ亹缁辨帡骞囬褎鐣风紓浣虹帛閻╊垶鐛€ｎ亖鏋庨煫鍥ㄦ礀婵爼姊绘担鑺ャ€冪紒鈧担璇ユ椽濡舵径濠勫幋闂佺鎻梽鍕磻閹邦喒鍋撶憴鍕婵炴潙鍊垮鎶芥晸閻樻枼鎷?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涚€ｃ劌鈧繈寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閹肩偛濡奸柛濠冩倐閸╃偤骞嬮敃鈧壕鍏兼叏濮楀棗澧绘俊顐㈢焸濮婄儤娼幍顕呮М闂佹寧娲︽禍顏勵嚕鐠囨祴妲堥柕蹇曞閵娾晜鐓ユ繝闈涙閸ｈ銇勯鈧ˇ鎵崲濠靛棌鏋旈柛顭戝枤娴狀參姊洪悷鐗堝暈濠电偛锕獮鍐晸閻欌偓閺佸啴鏌ㄩ弴妤€浜鹃梺缁樺姇閿曪箓骞夐崨濠冨劅闁靛鍎抽澶愭⒑閹稿海绠撴い锔垮嵆閹繝寮撮姀锛勫幗闂佸搫鍊搁悘婵嗏枔閳哄懏顥婃い鎺戭槸婢ф挳鏌″畝瀣？濞寸媴濡囬幏鐘诲箵閹烘繄鈧娊姊绘担鍝ユ瀮婵☆偄瀚拌棟妞ゆ牜鍋涢悡婵嬪箹濞ｎ剙濡肩紒鐙呯秮閺岋綁骞囬鐔虹▏闂佸搫妫崑濠傤潖婵犳艾纾兼慨姗嗗厴閸嬫挻顦版惔锝囩劶婵炴挻鍩冮崑鎾搭殽閻愬樊妯€闁轰焦鎹囬幃鈺呮嚑椤掑啸闂傚倷绀侀幖顐⒚洪姀銈呭瀭闁革富鍘炬稉宥夋煟濡鍤欑紒鐘茬秺閺岀喓鍠婇崡鐐茬闂佸憡蓱閻╊垶寮婚埄鍐╁闂傚牃鏅為崥顐︽⒑閸濆嫮鐏遍柛鐘崇墵閵嗕礁螖閸涱厾顦板銈嗘尵婵潧袙閸ヮ剚鈷掑ù锝呮啞閹牓鏌￠崼顐㈠閻撱倝鏌ｉ弮鍫闁哄棴绠撻弻娑樜旈崘銊㈠亾閿濆绫嶉柛顐ｇ箘閸旓箑顪冮妶鍡楃瑨閻庢凹鍓熼幃鐐哄垂椤愮姳绨婚梺鐟版惈缁夊爼宕濆澶嬬厱濠电姴鍟慨鍫ユ煏閸パ冾伃濠殿喒鍋撻梺鐐藉劚閸熷潡骞楅棃娑辨富闁靛牆鍟悘顏嗏偓鍏夊亾闁归棿绀侀弰銉╂煃瑜滈崜姘跺Φ閸曨垰绠抽柛鈩冦仦婢规洟姊绘担椋庝覆缂佹彃娼″畷妤€螣鐠佸磭绠氶梺缁樺灱濡嫬鏁梺鐟板悑閻ｎ亪宕瑰ú顏勭厱闁圭儤顨嗛悡鍐喐濠婂牆绀堥柕濞у懐顦梺绯曞墲缁嬫垹绮堥崼鐔虹闁糕剝蓱鐏忣厾绱?
  - preference闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍏煎€绘俊顖濇閸旂鈹戦悙鑼癁闁哄懐濞€瀵寮撮悢铏诡啎闂佺粯鍔﹂崜姘舵偟閺冨牊鈷戦柛婵嗗閸庡海绱掗懜闈涘摵鐎殿喖顭峰鎾閻樿鏁规繝鐢靛Т閻忔岸宕濋弽顐ゆ噮缂傚倸鍊搁崐鐑芥嚄閼搁潧鍨旈悗鐢殿焾缁躲倝鏌涜椤ㄥ懘鎮為崹顐犱簻闁圭儤鍨甸埀顒€缍婂畷鐢稿焵椤掑嫭鐓熼幖娣灮閻擃垶鏌涘Δ浣糕枙濠碘剝鎸冲畷鎺楁倷鐎涙ɑ鐝栭梻浣侯焾閺堫剛绮欓幋锕€鐒垫い鎺嗗亾闁诲繑绻堥崺鐐哄箣閿旇棄浜归梺鍦帛瀹稿宕戦幘缁樺仺缂佸娉曢崫妤佺箾鐎电孝妞ゆ垵妫濋幃锟犲即閵忊€斥偓鍫曟煟閹邦厼绲婚柍閿嬫閺屽秹顢涘☉娆戭槹闂佸搫鐭夌紞鈧紒鐘崇洴閺佹劙宕ㄩ鍙ュ缂?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涚€ｃ劌鈧繈寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閹肩偛濡奸柛濠傛健瀵鏁愭径濠庢綂闂侀潧绻嗛弲婵嬪礉閹间焦鈷戦柛娑橈工閻忊晛鈹戦悙鈺佷壕闂備礁鎼懟顖滅矓闂堟侗鐒芥い蹇撶墕缁狀垳鈧厜鍋撳┑鐘插€归弳顓㈡⒒閸屾瑧顦﹂柟纰卞亰椤㈡牠宕ㄧ€涙鍘愰梺鎸庣箓椤︻垶鎷戦悢鍏肩厸闁搞儵顥撶壕鍧楁煟閵堝倸浜炬繝鐢靛Х閺佸憡鎱ㄩ幘顔肩９闁归棿绀侀悡鏇烆熆閼搁潧濮堥柍閿嬪灴閺岀喓绮欓幐搴㈠闯闂佸疇妫勯ˇ杈╂閹烘挸绶為悗锝庡亜閸炲姊虹化鏇熸澓闁稿孩褰冮銉╁礋椤栨氨鐤€濡炪倖甯掗崑鍡涘疮鐎ｎ剛纾介柛灞剧懅閸斿秶绱掔€ｎ偅宕屾鐐诧躬楠炴﹢寮堕幋顓炴闂備礁缍婇崑濠囧礈閿曗偓閵嗘帗绻濆顓犲帾闂佸壊鍋呯换鍕不閹惰姤鐓熼柨婵嗙墔閸氼偊鏌嶈閸撴岸顢欓弽顓炵獥闁哄秲鍔嶅▍鐘诲箹鏉堝墽鍒伴柛銊︾箖缁绘盯宕卞Ο鍝勵潕缂備讲妾ч崑鎾绘⒒娴ｈ鍋犻柛搴灦瀹曟繄浠﹂崜褜娲搁悷婊呭鐢鍩涢幋锔界厵妞ゆ牕妫楃€氼噣銆呮导瀛樷拺缂佸顑欓崕蹇涙煙閾忣偓鑰块柕鍡曠閳诲氦绠涢敐鍛€┑鐘灱濞夋盯顢栭崶顒€鍌?闂?  - habit闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍏煎€绘慨妤€妫欓悾鐑芥⒑閹肩偛鈧洟鎳熼婵堜簷闂備焦瀵х换鍌炲箠鎼淬劌鍑犻柕鍫濐槹閻撴稑霉閿濆懏鍟炴い銉ｅ灲閺屸€崇暆鐎ｎ剛袦閻庢鍣崜鐔肩嵁閹邦厽鍎熼柕蹇曞У閻庨箖姊婚崒娆戭槮缁剧虎鍘鹃崚鎺楊敍濮ｎ厽妞介幃銏ゆ偂鎼淬倖鎲伴梻浣瑰缁诲倿骞夊鈧幃銏㈢矙鐠恒劎鐛紓鍌欑椤戝棛鈧瑳鍥х？闁瑰墽绮埛鎺懨归敐澶樻濞戞捁灏欑槐鎺楁偐閸愯尙浼岄梺鍝勮嫰閿曨亪寮幇顓炵窞濠电姴鎳忛幉浼存⒒娴ｈ櫣甯涙慨濠傤煼閸╂盯宕奸妷銉︾€悗骞垮劚椤︿即鎮￠妷锔剧瘈闂傚牊绋掗ˉ鐐烘煕閿濆牊顥夐棁澶愭煟閹捐櫕鎹ｅ褋鍨荤槐?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涚€ｃ劌鈧繈寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閹肩偛濡奸柛濠傤煼閸┾偓妞ゆ帒鍠氬鎰箾閸欏澧悡銈夋煏婵炵偓娅呯痪顓涘亾婵犳鍠楅…鍫ュ春閺嶎厽鍋傛繛鎴烇供閻斿棝鎮规潪鎷岊劅闁稿骸绻橀弻锝堢疀閹剧紟褔鏌″畝瀣？闁逞屽墾缂嶅棙绂嶉鍫濈煑闁告洦鍨遍悡娑㈡倶閻愬灚娅曢弫鍫ユ⒑缁洘鏉归柛鎾寸箞楠炲繘宕ㄩ弶鎴濈獩婵犵數濮撮崰姘跺船鐟欏嫮绡€闁汇垽娼ф禒婊勩亜閺囥劌骞楅柟渚垮姂閹粙宕ㄦ繝鍐╃彣婵犵绱曢崑鎴﹀磹閵堝鍌ㄩ柣鎾冲瘨閻掍粙鏌ㄩ悢鍝勑㈢紒鐘靛У缁绘繃绻濋崒婊冾杸濡炪們鍎遍悧濠勬崲濞戙垹绠ｉ柣鎰閸ㄥ潡鐛繝鍌楁瀻闁归偊鍠氶惁鍫ユ⒑濮瑰洤鐏叉繛浣冲嫮顩锋繝濠傚娴滄粎鎲告径鎰；闁瑰墽绮埛鎺楁煕鐏炴崘澹樻い蹇婃櫊閹顫濋悡搴㈢亾闂?闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅悷婊冪箻楠炴垿濮€閵堝懐鐤€濡炪倖妫佸Λ鍕償婵犲洦鈷戠憸鐗堝笒娴滀即鏌涢悩鎰佹當闁伙絿鍏樺濠氬Ψ閿旀儳骞嶉梺璇插缁嬫帡鈥﹂崶鈺冧笉闁靛濡囩粻?闂?  - decision闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍏煎€绘俊顖濇娴犲ジ姊洪崫鍕棞婵☆偅绻堝濠氭偄閸忓皷鎷婚柣搴ㄦ涧婢瑰﹤危椤曗偓濮婂宕掑顑跨敖闂佹悶鍔岄悥鐓庮嚕鐠囨祴妲堟俊顖炴敱閺傗偓闂備礁鎲″ú锕傚磻閸曨剚鍙忛柡鍥ュ灪閳锋垿鏌涘┑鍕姎闁哄閰ｉ弻鐔哄枈閸楃偘鍠婂┑鐘亾濞撴埃鍋撴慨濠冩そ楠炴劖鎯旈敐鍥╂殼婵犵數鍋炲娆撳磹閸ф绠栭柣鎰暘閸嬪懘鏌涢幇銊︽珖闁告ɑ鎮傞弻锝嗘償椤栨稈鍋撻妷鈺佺鐟滃秹藟濮樿京纾介柛灞捐壘閳ь剚鎮傚畷鎰板箹娴ｅ摜锛欓梺缁樺灱婵倝宕愰崸妤佺叆闁哄倸鐏濋埛鏃堟煟椤撶喓鎳囬柡宀€鍠栭幃婊冾潨閸℃鏆﹂梻浣侯焾椤戝懘顢栭崱娑樜﹂柛鏇ㄥ灠缁犲鎮归搹瑙勭＊闁挎繂妫庢禍?婵犵數濮烽弫鍛婃叏閹绢喗鍎夊鑸靛姇缁狙囧箹鐎涙ɑ灏ù婊堢畺閺岋繝宕堕妷銉т患缂佺偓鍎冲﹢閬嶆儉椤忓牜鏁囬柣鎰綑濞呫倝姊洪悷鏉挎毐闁活厼鍊搁～蹇曠磼濡顎撻梺鍛婄☉閿曘儵宕曢幘鏂ユ斀闁宠棄妫楁禍婵嬫煟閳哄﹤鐏犻柣锝夋敱鐎靛ジ寮堕幋婵嗘暏婵＄偑鍊栭幐楣冨磻閻斿吋鍋╅柣鎴烆焽缁犻箖鎮楅悽娈跨劸鐎涙繂顪冮妶鍡楃仴闁瑰啿绻樺畷鏇㈩敃閿旇В鎷绘繛鎾村焹閸嬫挻绻涙担鍐叉硽閸ヮ剦鏁囬柕蹇曞Х閿涚喖姊虹憴鍕姸婵☆偄瀚伴幃鐐哄垂椤愮姳绨婚梺鍦劋閸ㄧ敻寮冲▎鎾寸厱婵﹩鍓氱拹锛勭磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽敃浣烘闂佽瀛╅鏍闯椤曗偓瀹曟娊鏁愰崨顖涙闂佸湱鍎ら崵鈺呭箳閹存梹鐎婚梺璇″瀻閸愮偓浜ら梻鍌欑閻ゅ洭锝炴径鎰瀭闁秆勵殔閺勩儵鏌曟径鍡樻珔妤犵偑鍨烘穱濠囧Χ閸屾矮澹曠紓鍌欒兌婵儳鐣烽悽鍨潟闁规儳顕悷褰掓煕閵夋垵瀚禍楣冩⒒娴ｈ姤銆冩繛鏉戞喘椤㈡俺顦规い銏″哺閺佹劙宕卞▎妯荤カ闂佽鍑界徊浠嬫倶濮樿泛鐤炬繝闈涱儐閳锋垿鏌熺粙鎸庢崳缂佺姵鎸绘穱濠囶敃椤愩垹绫嶉悗?闂?  - knowledge闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍏煎€绘俊顖濐嚙閺嗘姊哄畷鍥ㄥ殌缂佸鏁搁幑銏犫槈濮楀棗鏅犲銈嗘⒒缁垶宕板鑸碘拺閺夌偞澹嗛ˇ锔姐亜閹存繃鍠橀柛鈹惧亾濡炪倖甯掗崰姘焽閹邦厾绠鹃柛娆忣槺婢ь亪鎮￠妶澶嬬厪濠电偟鍋撳▍鍡涙煕鎼淬埄娈曠紒缁樼洴瀹曞崬螣鐠囨煡鐎洪梻浣侯焾閿曪箓寮繝姘摕闁靛鍎弨浠嬫煕閳╁啩绶遍柍褜鍓氶〃鍫ュ焵椤掍緡鍟忛柛锝忕悼缁寮介鐐舵憰濠电偞鍨堕敃鈺侇焽閳哄倶浜滈柟鍝勭Ф椤︼箓鏌＄€ｎ剙鈻堟慨濠冩そ瀹曨偊宕熼鐘插Ы缂傚倸鍊哥粔宕囨濮樿泛违濞达綀鍊介悢鍝ョ懝妞ゆ牗绮屽鎶芥⒒娴ｅ憡鍟為柛鏃€鍨垮畷婵堜沪閼恒儲鐦庣紓?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴妤€浜惧銈庝簻閸熸潙鐣疯ぐ鎺濇晪闁告侗鍨版慨娲⒒娴ｄ警娼掗柛鏇炵仛閻ｅ墎绱撴担鎻掍壕婵犮垼娉涙径鍥磻閹捐崵宓侀柛顭戝枛婵骸顪冮妶蹇撶槣闁搞劏娉涢锝嗗閺夋嚦銊╂煥閺傚灝鈷旀い鏃€娲熷娲偡闁箑娈堕梺绋款儑閸犳牠濡撮崒鐐茶摕闁靛濡囬崢閬嶆⒑缂佹◤顏勵嚕閸泙澶婎煥閸曗晙绨诲銈嗘尨閸撴繄娑甸崼鏇熺厵闁荤喐婢橀顓㈡煙椤曞懎娅嶇€殿喖鐖奸獮瀣攽閹邦厽绁紓鍌氬€搁崐鎼佸磹瀹勬噴褰掑炊椤掑鏅╂繝鐢靛Т濞诧箓宕愰崸妤佺叆闁哄洨鍋涢埀顒€鎽滅划濠氭倷閻戞鍘繝鐢靛仧閸嬫挸鈻嶉崨顖滅＜闁绘ê鍟块埢鏇㈡煛瀹€鈧崰鎾诲焵椤掍胶鈯曟い顓炴处娣囧﹪宕堕浣哄幈闁诲函缍嗛崑鍛焊閻㈠憡鐓欏瀣瀛濆銈嗘煥缁绘﹢銆佸▎鎾崇闁稿繗鍋愯ぐ瀣⒒閸屾艾鈧绮堟笟鈧畷銉р偓锝庡墰閻牓鏌熺紒銏犳灈闁汇倗鍋撶换婵囩節閸屾凹浠奸梺鎼炲妽閺屻劑鍩為幋锕€纾兼慨姗嗗幖閺嗗牓姊虹紒妯诲暗闁哥姵鐗犲濠氭偄鐞涒€充壕闁汇垺顔栭悞楣冩煃瑜滈崜姘舵偋閻樿崵宓侀悗锝庡枟閸婇攱绻涢崼鐔奉嚋缂佷緡鍋呯换婵嗏枔閸喗鐏嶉梺闈涙处閻╊垰鐣烽幋锕€绠婚悗娑櫭?闂?- 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮诲☉妯锋斀闁告洦鍋勬慨銏ゆ⒑濞茶骞楅柟鐟版喘瀵鏁愭径濠勵吅濠电姴鐏氶崝鏍礊濡ゅ懏鈷戦梺顐ゅ仜閼活垱鏅堕鈧弻鐔兼惞椤愵剝鈧法鈧鍣崑濠傜暦閹烘鍊烽柡澶嬪灣閹綁姊虹拠鑼闁稿鐩獮澶愭晸閻樺弶鐎梺鍓茬厛閸嬪棛寮ч埀顒勬⒑濮瑰洤鐏叉繛浣冲洤鐓濋柛顐ゅ枔缁犳儳霉閿濆懎鏆遍柛姘埥澶娢熼柨瀣垫綌闂備線娼х换鎺撴叏閻戠瓔鏁婇柟杈鹃檮閳锋垹绱撴担骞库偓鐐哄箣閻樼數鐒鹃梺鍝勵槹閸わ箓鏁愭径濠囧敹闂侀潧顧€婵″洭宕㈤悽鍛娾拺閻犲洠鈧磭鈧鏌涘鍐ㄦ殶缂佲偓婵犲洦鈷掑ù锝呮啞鐠愶繝鏌￠崪浣镐簼闁逛究鍔戝畷褰掝敃閵堝倹鏁靛┑鐘垫暩婵潙煤閿曞倸纾归柣鎴ｅГ閻撴瑧绱撴担濮戭亪宕告繝鍥ㄧ厱閻庯綆鍋呭畷宀€鈧娲滈…鍫ｇ亙闂佸憡鍔戦崝搴ㄥΧ閿曞倹鈷掑〒姘ｅ亾闁逞屽墰閸嬫盯鎳熼娑欐珷濞寸厧鐡ㄩ悡娆撴煙缂佹ê绗氶柟鑼焾闇夐柣娆忔噽閻ｇ數鈧娲樼划蹇浰囬鈧弻锟犲焵椤掑嫭鎯炴い鎰╁€楅惁鍫ユ⒑濮瑰洤鐏叉繛浣冲啰鎽ュ┑鐘垫暩閸嬫盯鎯囨导鏉戠９婵°倕鍟崹婵嗏攽閻樺疇澹樼紒鐘冲▕閺岀喖骞嗚缂嶄胶绱掗妸銉吋婵﹥妞藉畷顐﹀礋椤撳濞€閺屾稒鎯旈妸銈嗗枤闂佺硶鏂侀崑鎾愁渻閵堝棗绗傜紒鍨涒偓鏂ユ灁婵☆垵鍋愮壕?婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾剧粯绻涢幋娆忕労闁轰礁顑嗛妵鍕箻鐠虹儤鐎鹃梺鍛婄懃缁绘﹢寮婚悢铏圭＜闁靛繒濮甸悘宥夋⒑閸濆嫭鍣虹紒璇茬墦瀵寮撮姀鐘诲敹濠电姴鐏氶崝鏍懅婵犵鍓濋〃鍛村箠韫囨洘宕叉繝闈涱儏椤懘鏌ㄥ┑鍡橆棤闁靛棙鍔曢—鍐Χ閸℃浠村┑鐐叉▕閸欏啫鐣峰ú顏勵潊闁靛牆鎳愰惈鍕⒑缁嬫寧婀版い銊ユ噺缁傚秹鎮欓澶嬵啍闂佺粯鍔樼亸娆愮閵忋倖鐓曢柡鍐ｅ亾缁炬澘绉电粚杈ㄧ節閸ヨ埖鏅濋梺鎸庣箓鐎涒晠鎮挎笟鈧幃妤冩喆閸曨剛锛橀梺鎼炲妺缁瑩鎮伴鈧獮鎺楀箠閾忣偅鈷愰柟宄版噽閸栨牠寮撮悙鏉款棜闂備礁澹婇悡鍫ュ磻閸℃瑧涓嶅Δ锝呭暞閻撴瑩鎮楀☉娆樼劷缂佺姵锕㈤弻銊モ槈濡す銈囩磼鏉堛劌绗氭繛鐓庣箻婵℃悂濡烽绛嬫缂?闂?- 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮诲☉妯锋斀闁告洦鍋勬慨銏ゆ⒑濞茶骞楅柟鐟版喘瀵鏁愭径濠勵吅濠电姴鐏氶崝鏍礊濡ゅ懏鈷戦梺顐ゅ仜閼活垱鏅堕鈧弻鐔兼惞椤愵剝鈧法鈧鍣崑濠傜暦閹烘鍊烽柡澶嬪灣閹綁姊虹拠鑼闁稿鐩獮澶愭晸閻樺弶鐎梺鍓茬厛閸嬪棛寮ч埀顒勬⒑濮瑰洤鐏叉繛浣冲洤鐓濋柛顐ゅ枔缁犳儳霉閿濆懎鏆遍柛姘埥澶娢熼柨瀣垫綌闂備線娼х换鎺撴叏閻戠瓔鏁婇柟杈鹃檮閳锋垹绱撴担鐧镐緵闁绘帟濮ら妵鍕晲閸曨厾鐓撻悗瑙勬礃閸ㄥ潡鐛鈧幊婊堟濞戞瑧鈧參姊绘担鍛婂暈婵炶绠撳畷銏＄鐎ｎ亞鐤呭┑鐐叉閹稿鎮￠悢鑲╁彄闁搞儯鍔嶇亸鐢电磼閻樺磭鍙€闁哄矉缍侀幃銏犫攽閸℃ɑ鎮欑紓浣插亾闁糕剝绋掗悡娆撴煟閹寸儑渚涙繛鍫熸礋閺岋繝宕ㄩ钘夆偓鎰版煛瀹€瀣埌閾伙綁鏌涘┑鍡楊伀濡ょ姴娲幃妤冩喆閸曨剙纰嶇紓浣割槺閹虫捇锝炶箛鎾佹椽顢旈崪浣诡棃婵犵數鍋為崹鍏肩椤掑嫬鐭楁慨妯垮煐閳锋帡鏌涚仦鎹愬妞ゅ繆鏅犻幃妤€顫濋悡搴♀拫闂佺硶鏂傞崹浠嬬嵁濡吋瀚氶柡灞诲劚閺佸綊姊绘担鍛婃儓婵炲眰鍔戝畷浼村箻鐠囨彃鍋嶉梺姹囧灩閹诧繝鎮￠悢鍏肩厽婵☆垰鎼痪褏绱掗埀顒€鐣濋崟顒傚帗閻熸粍绮撳畷婊冣攽閸″繑鐎洪梺鍝勬储閸ㄦ椽宕愰崼鏇熺厱妞ゆ劗濮撮悘顔剧棯閹规劖顥夐棁澶愭煥濠靛棭妲规繛鎳峰啠鏀芥い鏃傛嚀娴滅偓绻濈喊澶岀？闁稿鍋涢…鍥р枎閹惧磭顔戝┑鐘诧工閹冲酣宕瑰┑鍥╃闁糕剝锚婵洨绱掗崜浣镐槐闁哄瞼鍠栧鍓佹崉閵娿倗椹抽梻浣告惈閹锋垹绱炴担鍓叉綎闁惧繐婀辩壕鍏间繆椤栨碍绂嬪ù婊呭仦缁旂喖寮撮姀鈺傛櫍闂侀潧绻掓慨鍨綇閸儲鈷戠紓浣光棨椤忓棗顥氭い鎾跺Х娑撳秴螖閿濆懎鏆為柣鎾卞劜缁绘繈妫冨☉娆樻！闂侀潻缍€濞咃絿妲愰幒妤€鐒垫い鎺嗗亾闁伙絾绻堝畷鐔碱敆閸屾艾绠為梻鍌欐祰椤宕曢幎绛嬫晪妞ゆ挾濮锋稉宥夋煛瀹ュ骸骞楅柛濠勬暬濮婂宕奸悢琛℃（闂佺顑冮崹濠氬焵椤掑喚娼愭繛鎻掔箻瀹曟繃鎯旈妸銉у姦濡炪倖甯婇懗鍫曞煀閺囥垺瀚呴弶鍫涘妿缁犻箖鏌涘☉鍗炴灓濠⒀冪仛閹便劍绻濋崘鈹夸虎閻庤娲樼划鎾荤嵁閹捐绠崇€广儱鎷嬪Λ婊呯磽閸屾艾鈧悂宕愰崫銉х煋闁哄鍤﹀☉妯锋斀闁糕剝鐟﹀▓楣冩⒑濮瑰洤鐏╅柟璇х節瀵彃顭ㄩ崼鐔哄幈闂佸湱鍋撻〃鍛村箯閹寸姵顫曢柡灞诲劜閳锋垿鎮归崶銊ョ祷闁搞倛浜槐鎾愁吋閸涱噮妫＄紓浣稿€哥粔鐟扮暦婵傜鍗抽柣鎰暜缁辩敻鏌ｆ惔锛勭暛闁稿酣浜惰棟濞寸厧鐡ㄩ崑鍌炴煕閹板吀绨奸柛鐘冲姈缁绘繃绻濋崒婊冾暫缂備讲鍋撻柛灞剧〒缁犻箖鏌熺€电鍓冲〒姘⊕缁绘盯骞橀幇浣哄悑闂佸搫鐬奸崰鏍箖濠婂喚娼ㄩ柛鈩冾焽閺嗐儳绱撻崒娆掑厡濠殿喚鏁婚幃锟犳晸閻樿尪鎽曢梺鍝勬祫缁辨洟鎮块埀顒勬煟鎼搭垳绉靛ù婊勭墵瀹曟垿骞樼拠鎻掑祮闂佺粯顭囬弫鎼佹倿閸忚偐绡€闁靛骏绲介悡鎰版煕閺冣偓濞叉粎鍒掓繝姘闁兼亽鍎抽崢鐢告⒑鐠団€崇仯濠⒀勵殜钘熷鑸靛姈閻撶喖鏌熼悜妯虹仼濞寸姵鐩弻鏇㈠炊瑜嶉顓燁殽閻愬樊鍎旈柟顔界懃椤斿繘顢欓崗鑲╂澓缂傚倸鍊搁崐宄邦渻閹烘埈娓婚柟鐑橆殔绾偓闂佽鍎煎Λ鍕嫅閻旇　鍋撻獮鍨姎闁绘绮岄‖濠囧Ω閳哄倵鎷洪梺鍛婄☉閿曘儳浜告导瀛樼厽闁绘柨寮跺▍鍛存煟閿濆洤鍘存い銏＄洴閹瑩鎳犻澶婃暥闂傚倷绀侀崥瀣娴犲纾块梺顒€绉寸粈鍫ユ煏婵炲灝鍔存繛鎾愁煼閺屾洟宕煎┑鍥舵￥婵犫拃鍥︽喚闁哄本绋撻埀顒婄秵閸撴瑦绂掓潏鈹惧亾?- 闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾缁愭鏌熼柇锕€鏋涢柛銊︾箞楠炴牕菐椤掆偓閻忣亝绻涢崨顖毿ｅǎ鍥э躬婵″爼宕ㄩ鍏碱仩缂傚倷鑳舵慨闈涱熆濡法浜欓梻浣瑰缁诲倿骞婃惔銊ユ辈婵炲棙鎸婚悡娑㈡倵閿濆倹娅囩紒鎰閺岋紕浠﹂悙顒傤槹閻庤娲滈崢褔鍩為幋锕€绠涙い鎾愁檧婵″洨妲愰幘瀛樺闁告繂瀚烽埀顒佹尵缁辨挸顓奸崟顓犵崲閻庢鍠栭…鐑藉极閹邦厼绶炲┑鐐╂媰閸パ咁啇闁哄鐗嗘晶鐣屽閸啔褰掓偂鎼淬垹鏋犲┑?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂磋閳ь剨绠撻、妤呭礋椤愩倧绱遍梻浣告啞濞诧箓宕愮€ｎ€㈡椽顢旈崨顔界彇濠电偠鎻紞鈧い顐㈩樀瀹曟娊鎮滈懞銉㈡嫽婵炶揪绲藉﹢鍗烇耿娴犲鐓曢柍杞扮椤忣厾鈧娲栫紞濠囥€侀弮鍫濋唶婵犻潧鐗炵槐閬嶆⒒娴ｇ儤鍤€闁告艾顑夐幃浼存儍?闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹潡顢氶埀顒勫蓟閻旂厧绀堝ù锝囧劋閹叉﹢姊烘潪鎵槮闁挎洦浜濠氭偄閸忚偐鍔烽梺鎸庢磵閸嬫捇鏌＄€ｎ剙鏋戦柕鍥у椤㈡洟鏁愰崱娆樻О缂傚倷鑳剁划顖滄崲閸惊娑㈠礃閵娿垺顫嶉梺鍛婎殘閸嬫稒绔熸径鎰拻?recall_memory 闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涙繝鍛厫闁逛究鍔岃灒闁圭娴烽妴鎰磼閻愵剙鍔ゆ繛纭风節瀵鎮㈤悡搴ｇ暰闂佺粯顨呴悧婊兾涢崟顖涒拺闁告繂瀚銉╂煕鎼淬垹鈻曢柛鈹惧亾濡炪倖宸婚崑鎾绘煕濡崵鐭掔€规洘鍨块獮妯肩磼濡厧甯楅柣鐔哥矋缁挸鐣峰鍫熷亜闁绘挸瀛╁Σ顒勬⒑闁偛鑻晶顖炴煏閸パ冾伃妤犵偞甯￠獮瀣攽閸愩劋澹曢悷婊呭鐢帒效閺屻儲鐓冮柛婵嗗閸ｆ椽鏌ｉ幘瀵告噰闁哄睙鍡欑杸闁挎繂鎳嶇花濂告煟韫囨挾绠抽柡浣割煼瀵濡堕崥銈嗘そ椤㈡棃宕橀埡浣圭亾闂傚倷鑳堕幊鎾跺椤撶喓绠鹃柍褜鍓氶妵鍕閳藉棙鐣烽梺鐟板槻閹虫ê鐣峰鍏犲湱鈧綆浜欐竟鏇炩攽閻愭潙鐏熼柛銊︽そ閸╂盯骞嬮敂鐣屽幈濠电娀娼уΛ妤咁敂鐎涙ü绻嗛柟缁樺笒閹垹绱掔紒妯尖姇鐎垫澘瀚埀顒婄秵閸嬪棝藝椤撶姷纾藉〒姘搐閺嬫稒銇勯鐘插幋闁绘侗鍠栬灒闁兼祴鏅濋敍婊冣攽閳藉棗鐏ｉ柛妯犲喚鍤曢柧蹇ｅ亞缁♀偓闂佹眹鍨藉褎绂掗敃鍌涚厱闁靛鍎抽崺锝夋煃閵夘垳鐣电€规洖鐖奸、妤佹媴缁洖浜鹃柛顐ｆ礃閳锋垶銇勯幒鍡椾壕缂備礁顦遍弫濠氬箖閿熺姴鍗抽柕蹇ョ磿閸樻悂姊虹粙鎸庢拱缂侇喖鏈粋鎺戭煥閸曨厾顔曢柣蹇曞仜閸婃悂鍩€椤掍緡娈滄鐐差樀楠炴﹢顢欓懞銉︾彇闂備胶顭堥張顒€顫濋妸鈺婃晩闁归偊鍠氱壕钘夈€掑顒佹悙闁哄鍊濋弻鐔兼惞椤愶絽闉嶉梺鍝勬噹閻栫厧顕ｆ繝姘ㄩ柨鏃€鍎抽獮鍫ユ⒒娴ｈ櫣甯涢柡灞诲姂楠炴牠顢曢敐鍥舵祫闂備緡鍓欑粔鐢告偂濞戞埃鍋撻崗澶婁壕闁诲函缍嗛崜娑溾叺濠碉紕鍋戦崐鎴﹀垂濞差亝鏅俊鐐€ら崢褰掑礉閹存繄鏆︽慨妞诲亾濠碘剝鎮傛俊鐑藉箛椤撶偟浼屽┑顔硷功缁垶骞忛崨瀛樺殟闁靛绲洪崑鎾诲礃椤旇В鎷婚梺鍛婃处閸嬪棙鏅ラ柣搴ゎ潐濞叉﹢宕濋弴銏犵厴闁瑰濮崑鎾绘晲鎼粹€愁潻缂備椒绶ょ粻鎾诲蓟閿濆棙鍎熸い鏍ㄧ矌鏍″┑鐐茬摠缁酣宕戦妶鍜佸殨鐎规洖娲犻崑鎾绘晲鎼粹剝鐏嶉梺缁樻尰缁嬫垿鈥︾捄銊﹀磯闁绘碍娼欐慨娑欑箾鐎电袨闁搞劏娅ｉ幑銏犫槈閵忕娀鍞跺┑鐐村灦閿氬┑顕嗙畱閳规垿顢欑涵閿嬫暰濠碉紕鍋犲Λ鍕偩閻戣棄惟闁挎柨澧介惁鍫ユ⒑缁嬫寧婀扮紒顔惧█瀹曟洜浠︾憴锝嗘杸闂佺粯锚閻忔岸寮抽埡鍛厱閻庯綆鍋勬慨宥団偓瑙勬礃閸ㄥ潡鐛鈧顒勫Ψ閿旇姤婢?```

- [x] **Step 2: Add few-shot example for memory**

Add the following as a new example after existing examples in `Agent.md`:

```markdown
### 缂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂寸绾剧懓顪冪€ｎ亜顒㈠┑顖氥偢閺岋紕浠︾拠鎻掑缂佺偓鍎抽…鐑藉蓟閻旂厧绠查柟浼存涧濞堫厾绱撴担鍝勭彙闁搞儯鍔庨崢浠嬫⒑瑜版帒浜伴柛妯兼櫕缁辩偤骞嬮悙顏冪盎闂侀潧顦崕娲磿韫囨稒顥?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍏煎€绘俊顖濐嚙閺嗘姊哄畷鍥ㄥ殌缂佸鏁搁幑銏犫槈濮楀棗鏅犲銈嗘⒒缁垶宕板鑸碘拺閺夌偞澹嗛ˇ锕傛煥閺囥劋閭€殿喛顕ч埥澶愬閻樻牓鍔嶉妵鍕籍閸パ冩優闂佽桨鐒﹂悧鐘差潖閸濆嫅褔宕惰閸嬫捇骞囬弶璺紱闂佺懓澧界划顖炲煕閹烘嚚褰掓晲閸噥浠╅梺闈涙閿曨亪寮诲☉銏犵閻庨潧鎽滈悿鍕⒑鐠団€虫灓闁稿繑锕㈤妴浣糕槈閵忊€斥偓鐑芥煠閼测晝绀嬮柡鍥ュ灪閳锋垿姊洪銈呬粶闁兼椿鍨遍弲鍓佲偓娑櫳戦崣?
闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴妤€浜惧銈庝簻閸熸潙鐣疯ぐ鎺濇晪闁告侗鍨版慨娲⒒娴ｄ警娼掗柛鏇炵仛閻ｅ墎绱撴担鎻掍壕婵犮垼娉涙径鍥磻閹捐崵宓侀柛顭戝枛婵骸顪冮妶蹇撶槣闁搞劏娉涢? "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涚€ｃ劌鈧繈寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閹肩偛濡奸柛濠冩倐濠€渚€姊洪幐搴ｇ畵闁瑰啿閰ｅ鎶藉棘濡數鎳撻…銊╁礃椤忓柊銊╂⒑閸濆嫭婀扮紒瀣灴閹儳鈹戠€ｎ亞鍔﹀銈嗗笒鐎氼剛澹曟繝姘厽闁归偊鍓氶幆鍫㈢棯閸撗呭笡缂佺粯绻堝Λ鍐ㄢ槈閸楃偛澹夐梻浣虹帛閹搁箖宕伴幇顓犫攳濠电姴娲ゅ洿闂佺鏈惌顔界珶閺囥垺鈷掑ù锝堟鐢稒銇勯妸銉﹀殗闁轰礁鍟撮、鏃堝醇濠靛牏鏆梻浣圭湽閸ㄥ鈥﹂崼銏笉濠电姵纰嶉悡娑㈡煕鐏炰箙顏堝礉濠婂嫨浜滄い鎰╁灮鏁堝┑顔硷攻濡炰粙骞冮悜钘夌骇閹煎瓨鎸荤€垫牗淇婇悙顏勨偓鏍暜濡ゅ嫨浜归柛鎰靛櫘閺佸﹪鐓崶銊р槈閸烆垶姊洪幐搴㈩梿婵℃ぜ鍔庨懞杈ㄧ節濮橆厸鎷洪梺鍦焾鐎涒晝澹曢悽鍛婄厱閻庯綆鍋呯亸鐢告煃瑜滈崜姘额敊閺嶎厼绐楅柡宥冨妽濞呯娀骞栨潏鍓у埌闁搞劍绻冪换娑㈠幢濡搫顫庣紓浣叉閸嬫捇姊绘担瑙勫仩闁稿寒鍨跺畷婵堜沪閸撗屾锤閻熸粎澧楃敮妤呭煕閹达附鐓欐い鏍ф鐎氼噣銆呮导瀛樷拺缂佸顑欓崕蹇涙煙閾忣偓鑰挎鐐插暣閹粙宕ㄦ繝鍐╊仧闂備胶绮摫闁哄銈搁獮蹇涙惞閸︻厾锛濋梺绋挎湰閻熝囧礉瀹ュ棎浜滄い鎾跺仦閸犳﹢鏌熼姘拱缂佺粯绻堝畷姗€顢旈崱鈺佹櫗闂備浇宕垫慨鏉戔枖瑜斿畷銊╊敍濞戞瑯鍟呴梻鍌欒兌缁垶骞愰崼鏇炵９婵犻潧顑呴拑鐔兼煟閺冨洦顏犻柣顓熺懇閺屾盯鈥﹂幋婵囩亾濠碘€冲级濠㈡﹢鍩為幋锔藉€烽柤纰卞墮椤も偓婵＄偑鍊戦崝灞轿涘┑瀣祦闁割偁鍎辨儫闂侀潧顦€涒晛螞閸愵喖鏄ラ柍褜鍓氶妵鍕箳閹存繍浠鹃梺绋款儏椤戝鎮￠锕€鐐婇柕濠忓椤︻參姊哄ú璇插箹婵☆偅顨婇垾锔炬崉閵婏箑纾柣鐐寸▓閳ь剚鍓氬鎾绘煟閻斿摜鐭屽褎顨堥弫顔嘉旈崨顓狅紱闂佸綊鍋婇崢瑙勭濠婂牊鐓涢柛鎰╁妼閳ь剙鎽滈弫顔炬崉鐞涒剝鏂€濡炪倖鏌ㄩ妶鎼佸矗閸曨剚鍙忓┑鐘叉噺椤忕娀鏌熸搴♀枅闁搞劑绠栭幖褰掝敃閵堝嫭鍠氭繝纰夌磿閸嬫垿宕愰幋锕€绀夌€光偓閸曨剙浜遍梺鍦亾閸撴岸宕甸弴鐔翠簻闁规媽娉涢惁婊堟煛娴ｅ壊鍎旈柡灞界Х椤т線鏌涢幘璺烘灈濠碘€崇摠閹峰懐鍖栭弴鐔衡偓濠氭⒑閸︻厼浜炬繛鍏肩懇閹倿宕熼鍌滅槇闂侀潧楠忕徊鍓ф兜閹€鏀介柛灞剧⊕椤ュ牏鈧娲橀悷锔剧矉閹烘柡鍋撻敐搴′簮闁归绮换娑欐綇閸撗冾嚤闁荤姭鍋撻柨鏇炲€哥紒鈺呮煟濡も偓閻楀繒绮婚幆褜鐔嗛悹杞拌閸庢垶绻涢崣澶嬪唉闁哄备鍓濋幏鍛矙閹稿孩顔掑┑鐘茬棄閵堝懐鍘紓浣规⒒閸犳牠寮崘顔肩劦妞ゆ巻鍋撻悡銈嗐亜閹捐泛浠ч柡鍡畵閺屻劌鈹戦崱姗嗘缂備礁澧庨崑銈夊箖濮椻偓閹瑩宕ｆ径濠冩畼闂備浇顕х换鎰涘┑鍡╂綎缂備焦蓱婵挳鏌ц箛鏇熷殌缂佹せ鈧剚娓婚柕鍫濋楠炴牠鏌ｅΔ浣瑰磳闁靛棔绀侀～婵嬪箛娴ｅ厜鏋岄梺璇叉唉椤煤韫囨稑鍨傚ù鐘差儑瀹撲焦鎱ㄥ璇蹭壕濡炪們鍨洪悷鈺呭箰婵犲啫绶為柛鈩冦仦婢规洟姊哄Ч鍥х仼闁硅绻濋幃锟犳偄閸忚偐鍘介梺鍝勫暙閸婂摜鏁捄濂界懓顭ㄩ崨顓ф毉婵烇絽娲ら敃顏堢嵁閹捐绠抽柡鍐ㄥ€愰妸鈺傗拺閻犲洠鈧櫕鐏嗙紓渚囧枟閻熲晠濡存担绯曟婵☆垶鏀遍～宥呪攽閻愬弶顥滅紒缁樺浮閺佸秹骞樼紒妯煎幗闁瑰吋鐣崐銈咁焽閹邦厾绠鹃柛娆忣槺閻帞鈧娲橀〃鍛扮亽闁荤姳绀佺壕顓犵不濮樿埖鈷戠憸鐗堝笚閿涚喖鏌ｉ幒鐐电暤鐎殿喗褰冮…銊╁醇閻斿搫骞楅梻浣瑰缁诲倿骞婇幘鍨涘亾濮橆厼顥嬬紒杈ㄥ浮閹崇娀顢楅埀顒傛暜閸洘鐓冮悷娆忓閻忔挳鏌熼鐣屾噰鐎殿喖鐖奸獮瀣偐鏉堫煈鏁囬梻鍌氬€烽懗鍫曞箠閹捐绠熼柨鐔哄Т缁犳牠鏌涘畝鈧崑娑㈠几娓氣偓閺屾盯骞囬棃娑欑亪闁搞儱鐡ㄧ换婵嬪閿濆棛銆愰梺鎸庢穿缁犳捇骞?

闂?save_memory(category="preference", content="闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墰缁鎮╅懡銈呭絼闂佹悶鍎崝搴ㄥ煀閺囥垺鐓曢幖娣焺濞堟洟鏌曢崶褍顏€殿噮鍓熷畷褰掝敊鐟欏嫬鐦辩紓鍌氬€烽懗鑸垫叏闂堟党娑㈠礃椤旇壈鎽曞┑鐐村灦閻喖鈻介鍫熺厱闁圭偓銇涢崑鎾翠繆閹绘帞澧㈢紒杈ㄦ尰閹峰懐绮欏▎鐐闂備胶顭堥鍥窗閺嶎厼鏄ラ柍褜鍓氶妵鍕箳閸℃ぞ澹曠紓鍌欒兌婵绮旈悷鎵殾闁哄洨鍠愮紞鍥煃鐟欏嫬鍔ゅù婊呭亾閹便劌螣閻撳骸浠樺┑鐐叉噹缁夊綊寮婚悢纰辨晬婵炲棙鍨垫俊浠嬫⒑鐠団€崇仭婵☆偄鍟穱濠囧箹娴ｈ娅嗛梺璇″瀻閸愵亶鍞舵繝鐢靛Х閺佹悂宕戦悩璇茬妞ゅ繐妫楃欢銈吤归悩宸剰缂佺姷鍎ょ换婵囩節閸屾凹浠惧┑鐐叉噽婵炩偓闁哄本娲濈粻娑欑節閸愩劍鐝伴梻浣侯焾椤戝棝骞戦崶褏鏆﹂柣鎴犵摂閺佸洨鎲歌箛娑樼闁归棿鐒﹂埛鎴︽⒒閸喓銆掑褋鍨洪妵鍕敇閻愰潧鈪靛銈冨灪瀹€鎼佸极閹邦厼绶炲┑鐘插閸熷淇婇悙顏勨偓鏍涙笟鈧畷鎴﹀箛闁附鏅╅梺鍦劋閸╁牆銆掓繝姘厪闁割偅绻冮ˉ鐐烘煃闁垮濮嶉柡灞剧⊕閹棃濮€閻橆偅鐏嗛梻浣烘嚀閸㈣尙鎹㈤幒妤€鐒垫い鎺戯功缁夌敻鏌涢悩鎰佹疁闁糕晜鐩獮瀣晜閻ｅ苯骞嶇紓鍌欑椤戝棛鈧瑳鍥х闁挎繂顦伴悡鍐煢濡警妯堟俊顖楀亾闂備礁鎼悮顐﹀磹閺囩姴寮查梺鑽ゅТ濞测晝浜稿▎鎰浄妞ゆ挾濮风壕钘壝归敐鍥剁劸闁逞屽墮閹芥粎鍒掗弮鍫熷仭闁规鍠楀▓楣冩⒑闂堟侗鐓┑鈥虫川瀵囧焵椤掑嫭鈷戦柛娑橈攻婢跺嫰鏌涢妸鈺€鎲炬い銏℃尭椤撳吋寰勭€Ｑ勫濠电偠鎻徊鍧椻€﹂崼銉ョ畺闁瑰瓨绶烽悷閭︾叆闁逞屽墰閸掓帒鈻庤箛鏇熸闂佸搫娲㈤崹褰掓嫅閻斿吋鐓忓鑸电〒閻ｅ崬霉閻樻瑥娲﹂埛鎴︽煟閻斿憡绶查柍閿嬫⒒缁辨帡顢氶崨顓犱桓闂佺硶鏅滈惄顖炵嵁閹烘嚦鏃€鎷呴崫鍕疄闂備浇顕х换鎺楀磻濞戞瑦娅犲ù鐘差儏閻撯偓闂佸搫娲ㄦ慨椋庡閻ｅ备鍋撻獮鍨姎婵☆偅顨婇幃姗€骞橀鐣屽幐閻庡厜鍋撻悗锝庡墰琚﹂梻浣芥〃閻掞箓宕濆▎蹇曟殾婵せ鍋撳┑鈩冩倐婵＄兘顢欓悾宀€校濠电姴鐥夐弶搴撳亾濡や焦鍙忛柣鎴ｆ绾惧鏌ｉ幇顒備粵闁哄棙绮撻弻銊╂偄閸濆嫅銉р偓瑙勬尫缁舵岸寮婚悢鍏煎€绘慨妤€妫欓悾鍓佺磽娴ｅ搫顎撶紒鏌ョ畺婵＄敻宕熼姘鳖啋闁荤姾娅ｉ崕銈呪枍閳哄懏鈷戦柛鎰级閹牓鏌涙繝鍛惞缂?)
闂?婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｅΟ娆惧殭缂佺姴鐏氶妵鍕疀閹炬惌妫炵紓浣界堪閸婃繈寮婚敃鈧灒闁绘艾顕粈鍡椻攽閻愭潙鐏︽い顓炲€垮顕€宕煎┑鍡欑崺婵＄偑鍊栭幐楣冨磻濞戞瑧顩查柤鍝ユ暩缁♀偓闂佹眹鍨藉褎绂掗敃鍌涚厱闁靛鍎遍。鎶芥煕閻樿宸ユい鎾冲悑瀵板嫭绻濋崟鍨濆┑鐘垫暩婵挳鏁冮妶鍥ｅ亾濮樸儱濡界紒鍌氱Т椤劑宕奸悢鍝勫箰闂備礁鎲￠崝褏寰婇懞銉ь洸闁诡垎灞惧瘜闂侀潧鐗嗗Λ妤呮倶閿曞倹鐓熼柣鏂垮级濞呭懘鏌ｉ敐鍥у幋濠碉紕鍏橀崺鈩冩媴閸濆嫧鍋撻悙宸富闁靛牆妫楃粭鍌炴煠閸愯尙鍩ｇ€规洩缍佸畷鍗烆渻缂佹ɑ鏉搁梻浣虹帛閸旀牕顭囧▎鎾村€堕柨鏇炲€归悡鐔兼煟閺冣偓缁诲倸煤閵堝洨涓嶉柣鎴炃滄禍婊堟煏閸繃绁╅柛鏃€婀絬ser(type="confirm", question="闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涚€ｃ劌鈧繈寮婚弴鐔虹闁绘劦鍓氶悵鏃堟⒑閹肩偛濡奸柛濠冩倐閸╃偤骞嬮敃鈧壕鍏兼叏濮楀棗澧绘俊顐㈢焸濮婄儤娼幍顕呮М闂佹寧娲︽禍顏勵嚕鐠囨祴妲堥柕蹇曞閵娾晜鐓ユ繝闈涙閸ｈ銇勯鈧ˇ鎵崲濠靛棌鏋旈柛顭戝枤娴狀參姊洪悷鐗堝暈濠电偛锕獮鍐晸閻欌偓閺佸啴鏌ㄩ弴妤€浜鹃梺缁樺姇閿曪箓骞夐崨濠冨劅闁靛鍎抽澶愭⒑閹稿海绠撴い锔垮嵆閹繝寮撮姀锛勫幗闂佸搫鍊搁悘婵嗏枔閳哄懏顥婃い鎺戭槸婢ф挳鏌″畝瀣？濞寸媴濡囬幏鐘诲箵閹烘繄鈧娊姊绘担鍝ユ瀮婵☆偄瀚拌棟妞ゆ牜鍋涢悡婵嬪箹濞ｎ剙濡肩紒鐙呯秮閺岋絽螣鐠囪尙绁风紓鍌氱Т濡稓妲愰幘璇茬＜婵﹩鍏橀崑鎾诲箹娴ｅ摜锛欓梺鍛婄缚閸庢娊鎯岄幘缁樼厽闁靛繒濮甸崯鐐烘煛閸涱喚绠為柡灞炬礉缁犳盯寮撮悜鍡忓亾瀹€鍕厱闁靛牆妫欑粈瀣煛瀹€鈧崰鎾舵閹烘嚦鐔告姜閺夊灝鐏佸┑鐘垫暩閸嬫盯鎯冮悜钘夌柧婵犲﹤鐗嗘闂佸憡娲﹂崹鎵不濞戙垺鐓冮弶鐐村椤斿鏌涚€ｎ偅灏摶鏍煕濞戝崬骞橀柣銈呮噹椤啴濡堕崨顖滎唶闂佺娅曢崝妤€顕ｈ閸┾偓妞ゆ帒瀚埛鎴︽⒒閸喓娲撮柣娑欑矌缁辨帡骞撻幒鎴旀寖濠电偞鍨归弫璇茬暦濠婂棭妲剧紒鎯у⒔閸樠団€︾捄銊﹀磯闁绘碍娼欐慨娑㈡⒑閹稿海鈽夌紒澶婄埣閸┾偓妞ゆ帊绶￠崯蹇涙煕閻曚礁浜扮€规洘鍎奸ˇ瀛樸亜閿旇姤绶叉い顏勫暣婵″爼宕卞▎蹇ｆ椒缂備胶鍋撳妯肩矓瑜版帒绠栨俊銈呮媼閺佸棝鏌涢弴銊ュ幋闁归攱妞藉娲川婵犲啫闉嶉悷婊勬緲閸燁垳绮嬪澶婂唨妞ゆ挾鍠撻崢閬嶆⒑闂堟侗鐒鹃柛搴＄－缁柨煤椤忓懐鍘甸悗瑙勬礀濞层倖绂掓潏顭戞闁绘劖鐓￠崣鍕煙瀹曞洤浠卞┑锛勬焿椤﹀弶顨ラ悙鏉戝婵﹦绮幏鍛喆閸曨偂鍝楅梻浣侯焾鐎垫帡宕圭捄铏规殾婵犻潧妫崥瀣煕閵夘垰顩柛鎾卞姂濮婃椽骞愭惔銏㈩槬闂佺锕ょ紞濠囧箖閿熺姵鍋勯柛婵勫劤閻﹀牓姊洪崜鑼帥闁稿瀚幈銊╁炊閵娧咁啎闂佸憡渚楅崢鐐櫏闂備礁鎼径鍥礈濠靛绠柛娑欐綑娴肩娀鏌曟径瀣闁稿﹥娲熷﹢渚€姊虹紒妯兼噧闁硅櫕鍔欓幃楣冨垂椤愶絽寮挎繝鐢靛Т閹冲酣宕ヨぐ鎺撶厓鐟滄粓宕滃▎鎾村€舵慨妯挎硾缁犳牠鏌涘畝鈧崑鐐哄磹閸偆绠剧€瑰壊鍠曠花濂告煃闁垮绗掗棁澶愭煥濠靛棙鍣洪柛鐔哄仱閺屾盯鎮㈤崫鍕闂佸搫琚崐婵嬪箖閻戣棄绾ч幖瀛樻尰鐎垫牠姊绘担绋挎倯婵＄偠濮ょ粋宥夊醇閺囩偟鐤囬梺鍝勭▉閸樺ジ鎮″☉銏＄厱閻忕偠顕ч埀顒佺墱缁辩偛螖娴ｉ绠氶梺缁樺姦娴滄粓鍩€椤掍胶澧垫鐐村姍瀹曞ジ寮撮悙鑼偓顓㈡⒑闂堚晛鐦滈柛姗€绠栭幆宀勫幢濞戞瑧鍘遍悗鍏夊亾闁逞屽墴瀹曟垿鎮欓悜妯轰簵闂佸搫娲ㄩ崰鍡樼濠婂牊鐓欓柡澶婄仢椤ｆ娊鏌熼鍨汗缂佽鲸甯￠幃鈺冪驳绾應鍋撻崸妤佺厸鐎光偓鐎ｎ剛鐦堥悗瑙勬礀瀹曨剝鐏掑┑鐐跺皺缁垶藟閸儲鈷掑ù锝呮啞閹牓鏌ｉ鈧妶绋跨暦娴兼潙鍐€妞ゆ挾鍋熼悾鍝勨攽閻樿宸ラ柛姘耿閹垽宕楅崗鐓庡姃闂備線娼荤€靛矂宕㈡禒瀣惞闁告劑鍔夐弨浠嬫煟濡櫣浠涢柡鍡忔櫊閺屾稓鈧綆鍋嗗ú瀛橆殽閻愯鏀婚柟顖涙閺佹劙宕掑顐㈩棜婵犳鍠楅敃鈺呭储閻ｅ本顐介柛娆忣槶娴滄粍銇勯幇鈺佺伄缂佺姾灏欑槐鎺旂磼濡偐鐣靛銈庡亝缁诲牓銆佸Δ鍛＜闁绘劙娼х粈鍫ユ⒒閸屾艾鈧嘲霉閸ヮ剨缍栧鑸靛姇缁犳氨鈧厜鍋撻柛鏇ㄥ亜閸嬪秹姊洪悷鎵憼閻㈩垳鍋ゅ浼村磼濮橈絾鏂€闂佺粯锚閻忔岸寮抽埡鍛厱閻庯綆鍓欐禒杈┾偓瑙勬礀濠€閬嶅箲閸曨剛鐟规い鏍ㄧ〒缁嬩胶绱撻崒姘偓鐑芥倿閿曚焦鎳岄梻浣告啞閻熴儳鎹㈤幇鐗堢畳闂備胶顭堢换鎰板触鐎ｎ剛绀婇柟杈鹃檮閻撶喖鏌熼悜妯虹仼濞寸姵鐩弻鏇㈠炊瑜嶉顓燁殽閻愭潙娴€规洖宕—鍐箚瑜滃Λ婊堟⒒閸屾艾鈧兘鎳楅崼鏇椻偓锕傚醇閵夛附娅囬梺闈涱槴閺呮稓绮婚弽顓熺厱鐎光偓閳ь剟宕戦幋锕€鐒垫い鎴ｆ硶椤︼附銇勯锝囩畺闁挎稒鍔曢埞鎴﹀炊閵婏妇褰ｉ梻鍌氬€风欢姘跺焵椤掑倸浠滈柤娲诲灡閺呭爼顢氶埀顒勫蓟閿濆鏅查柛銉戝啫绠ｅ┑鐘殿暜缁辨洟宕楀Ο璁崇箚闂佸灝顑嗛崕鐔兼煏韫囧﹥顎嗛柟宄邦煼濮婃椽鏌呴悙鑼跺濠⒀冨⒔缁辨挸顓奸崨顕呮＆閻庤娲樼划宀勫煝鎼淬劌绠荤€规洖娲ㄩ弳?)
闂?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴妤€浜惧銈庝簻閸熸潙鐣疯ぐ鎺濇晪闁告侗鍨版慨娲⒒娴ｄ警娼掗柛鏇炵仛閻ｅ墎绱撴担鎻掍壕婵犮垼娉涙径鍥磻閹捐崵宓侀柛顭戝枛婵骸顪冮妶蹇撶槣闁搞劏娉涢锝嗗閺夋嚦銊╂煥閺傚灝鈷旀い鏃€娲熷娲偡闁箑娈堕梺绋款儑閸犳牠濡撮崒鐐茶摕闁靛濡囬崢閬嶆椤愩垺澶勬慨濠傤煼閹瞼鈧綆鍠楅悡蹇涙煕閵夋垵鍠氭导鍐倵濞堝灝娅橀柛锝忕秮瀹曟椽鍩€椤掍降浜滈柟鐑樺灥椤忔挳鏌℃担绋款仾缂佺粯鐩畷鍗炍熺拠鑼暡闂?闂?save_memory
闂?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓鍝ョ不閺嶎厽鐓曟い鎰剁稻缁€鈧紒鐐劤濞硷繝寮婚悢鐓庣畾闁绘鐗滃Λ鍕磼閹冣挃缂侇噮鍨抽幑銏犫槈閵忕姷顓洪梺鍝勫暊閸嬫捇鏌? "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柛娑橈功缁犻箖鏌嶈閸撴氨鎹㈠☉娆愬闁告劕寮堕幖鎰棯閸撗勫殌闁宠鍨块幃鈺冣偓鍦Т椤ユ繈姊哄Ч鍥р偓妤呭磻閹捐桅闁告洦鍨扮粻娑㈡煏婵犲繒鐣辨繛鍛哺濮婃椽宕崟闈涘壉濠碘槅鍋勯崯鏉戭嚕婵犳碍鍋勯柛娑橈功缁夎埖淇婇妶蹇曞埌闁哥噥鍨堕、鎾愁吋婢跺鎷洪梺鍛婄箓鐎氼厽鍒婃總鍛婄厱闁规崘娉涢弸娑欘殽閻愭彃鏆欐い顐ｇ矒閸┾偓妞ゆ帒瀚粻鏍ㄧ箾閸℃ɑ灏伴柛銈咁儐缁绘盯宕奸悢濂夊殝濡炪們鍎遍ˇ闈涱潖缂佹ɑ濯撮悷娆忓娴犫晠姊虹粙鍖℃敾闁绘绮撳顐︻敋閳ь剟寮幘缁樺亹闁肩⒈鍓涢弳顐︽⒑閼姐倕鏋戦柣鐔村劤閳ь剚鍑归崳锝夊箖閻ゎ垬浜归柟鐑樻尵閸樻捇鎮峰鍕煉鐎规洘绮撻幃銏ゆ偂楠烆兙鍎甸弻娑樼暆閳ь剟宕戦悙鍝勭柧婵犲﹤鐗婇悡鏇㈡煙閻愵剦娈旈柟宄邦儏鍗遍柟闂寸劍閳锋帒霉閿濆牜娼愰柛瀣█閺屾稒鎯旈姀掳浠㈤悗瑙勬礃缁矂鍩㈡惔銊ョ闁哄啫鍋嗛崯宥夋⒒閸屾艾鈧悂宕愰悜鑺ュ殑闁割偅娲嶉埀顒婄畵瀹曞ジ濡烽妷銉у綁婵＄偑鍊栫敮鎺斺偓姘煎弮瀹曟垿鏁撻悩宕囧帾闂佸壊鍋呯换鍐矚閸喒鏀芥い鏃傚帶閺嗛亶妫佹径鎰厽闁规崘娅曢幑锝夋煙閻ｅ苯鈻堥柡宀嬬秮楠炴鈧稒顭囬ˇ銊╂⒑闁稓鈹掗柛鏂跨焸閿濈偛顭ㄩ崼婵嗚€垮┑掳鍊愰崑鎾淬亜椤愵偂閭慨濠冩そ瀹曠兘顢橀悤浣锋埛缂傚倸鍊哥粔宕囨濮橆剦鍤曞┑鐘宠壘閻掓椽鏌涢幇銊︽珔妞ゅ孩鎹囬弻锝夋偄閸濄儲鍣ч柣搴㈠嚬閸撴稒绔熼弴銏犵闁告瑥鍊瑰Λ鍐箖閳哄懏顥堟繛鎴烆殘閹规洘淇婇悙顏勨偓鏍垂閻㈡潌鍥偨閸涘﹤浠掑銈嗘磵閸嬫挾鈧娲栭悥濂搞€佸Δ浣哥窞閻庯綆鍋呴悵婊勭節閻㈤潧袨闁搞劎鍘ч埢鏂库槈閵忊€充画闂佸啿鎼幊搴ㄦ偂濞戙垺鐓曢悘鐐插⒔閻本銇勯弮鈧ú鐔奉潖濞差亝鍋￠梺顓ㄧ畱濞堝爼姊虹粙娆惧剳闁稿鍊濆畷鍝勨槈閵忕姷顔婇梺鐟扮摠濮婂綊寮埀顒佷繆閻愵亜鈧牕煤瀹ュ纾婚柟鎯у绾惧ジ鏌ｅΟ铏癸紞濠⒀呮暬閺屾洟宕遍弴鐙€妲銈庡亝缁捇宕洪埀顒併亜閹烘垵顏€规挷绶氶弻鈥愁吋閸愩劌顬夋繝娈垮灡閹告娊寮诲☉妯锋斀闁告洦鍋勬慨璺衡攽閳ュ啿绾ч柟绋垮暱椤繒绱掑Ο璇差€撻梺鍛婄☉閿曘劎娑甸埀顒勬⒒娴ｄ警鐒剧紒銊︽そ瀹曟劕鈹戠€ｎ剙绁﹂梺褰掑亰閸樺墽寮ч埀顒€鈹戦鍡欐偧妞ゎ厼鐗嗙叅闁冲搫鎯ら崶顒€钃熼柕澶涘瘜濮婃寧绻濋姀锝呯厫闁告梹鐗犻幃锟犲即閵忋垹褰勯梺鎼炲劘閸斿繑绔熷Ο濂界懓顭ㄩ崘顏喰ㄩ梺鍝勭焿缂嶄線鐛▎鎾崇闁靛ě鍌氬缂傚倸鍊峰ù鍥ㄣ仈閸濄儲鏆滄俊銈呮嫅缂嶆牠鏌熸潏鍓х暠闁告劏鍋撻柣鐔哥矊缁夊爼鎮幆褜鍚嬪璺侯儏閳ь剛鏁婚幃宄扳枎韫囨搩浠剧紓浣插亾闁告劏鏂傛禍婊堟煏婵炲灝鍔电€规悶鍎甸弻锝夋晲閸パ冨箣闂佽鍠掗崜婵嬪箚閺傝鐔虹磼濡粯绶梻鍌氬€风粈浣圭珶婵犲洤纾婚柛鈩冪☉缁愭鏌熸导鏉戜喊闁轰礁娲よ灃闁挎繂鎳庨弳鐐烘煃闁垮绗掗棁澶愭煥濠靛棙鍣洪柛鐔哄仱閹綊骞囬崜浣虹槇闂佸搫鏈粙鎺楀箚閺傚簱妲堟俊顖氬槻娴滅偓淇婇妶鍛櫣闁哄鐒﹂妵鍕棘閹稿寒娼旈梺鍝勫暙閻楀棝鎮為崹顐犱簻闁圭儤鍨甸鈺呮煟閹惧绠橀柍褜鍓欑粻宥夊磿闁单鍥敍濠婂懐鐒奸柣搴秵閸嬩焦绂嶅鍫熺厸鐎广儱鍟俊鍧楁煃缂佹ɑ宕岄柡宀€鍠庨悾锟犳焽閿旀儳鎮戦梻浣告惈閻寰婃ィ鍐ㄧ畾闁哄啫鐗嗛～鍛存煃閸ㄦ稒娅呮い顐㈢焸濮婃椽鎸婃径濠冩婵＄偛鐡ㄩ幃鍌涗繆閻㈢绀嬫い鏃€鍎抽弫銉╂⒒娴ｅ憡鍟炴繛璇х畵瀹曘垺銈ｉ崘鐐櫓闂佸搫娲㈤崹娲煕閹达附鐓曢柟鐐綑缁茶霉濠婂嫮澧甸柡灞剧洴婵℃悂鈥﹂幋鐐电Х缂傚倷绀侀崐鍦暜閿熺姰鈧礁鈽夐姀鈥斥偓鐑芥倵閻㈡鐒鹃悽?

闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴妤€浜惧銈庝簻閸熸潙鐣疯ぐ鎺濇晪闁告侗鍨版慨娲⒒娴ｄ警娼掗柛鏇炵仛閻ｅ墎绱撴担鎻掍壕婵犮垼娉涙径鍥磻閹捐崵宓侀柛顭戝枛婵骸顪冮妶蹇撶槣闁搞劏娉涢? "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柟闂磋閳ь剨绠撻、妤呭礋椤愩倧绱遍梻浣告啞濞诧箓宕愮€ｎ€㈡椽顢旈崨顔界彇濠电偠鎻紞鈧い顐㈩樀瀹曟娊鎮滈懞銉㈡嫽婵炶揪绲藉﹢鍗烇耿娴犲鐓曢柍杞扮椤忣厾鈧娲栫紞濠囥€侀弮鍫濋唶婵犻潧鐗炵槐閬嶆⒒娴ｇ瓔娼愰柛搴㈠▕椤㈡岸顢橀悩鍏哥瑝婵°倧绲介崯顖炴偂濞嗘挻鍊甸柣銏☆問閻掓儳霉閻欏懐鐣甸柡宀嬬秮楠炴﹢宕￠悙鎻掝潥闂備線娼уú銈団偓姘嵆閻涱喚鈧綆浜栭弨浠嬫煕閵夋垵瀚锋禒顓㈡⒒閸屾瑧顦﹂柟纰卞亰楠炲﹥鎯旈妸锕€浜繝闈涘€婚…鍫㈢不閺嶎厽鐓冮柛婵嗗閸ｅ綊鏌涢妸銉モ偓褰掑Φ閸曨垰绠涢柍杞拌兌娴煎嫰鎮峰鍛暭闁圭鍟块～蹇涙惞鐟欏嫬鐝伴梺鍝勮閸庡崬顕ｉ弶搴撴斀闁绘劖婢樼亸鍐煕閵夋垵鎳愰弸鈧梻鍌欐祰濞夋洟宕伴幘瀛樺弿闁汇垻顭堢壕濠氭煃閸濆嫭鍣洪柍閿嬪灦閵囧嫰骞掗崱妞惧缂傚倷绀侀ˇ閬嶅极婵犳艾绠栭柍銉︽灱濡插牓鏌曡箛銉х？闁告﹢浜跺铏规喆閸曨剛鍑℃繝鈷€鍐╂崳缂侇喗鐟х槐鎺懳熼懖鈺婂晭闂備礁鎲℃笟妤呭储婵傜姹查柣鏃囨绾惧ジ寮堕崼娑樺缂佹甯￠幗鍫曞冀椤撶喓鍘撻悷婊勭矒瀹曟粓鎮㈡搴㈡闂佽澹嗘晶妤呭磻閿熺姵鈷戞い鎾卞妿閻ｈ鲸绻涢崼顐喊婵﹥妞藉畷銊︾節閸愵煈妲遍梻浣侯焾椤戝棛鏁垾宕囨殾闁靛／鈧崑鎾绘晲鎼粹剝鐏嶉梺缁樻尰濞茬喖寮婚敓鐘茬倞闁靛鍎遍‖鍫澪旈悩闈涗沪閽冨崬菐閸パ嶈含鐎规洩绲惧鍕節閸曨亞绀夊┑鐘愁問閸犳牠鏁冮敃鍌氱？闁靛牆鎷嬮悞鑺ャ亜韫囨挾澧曠紒鐘劜閵囧嫰寮崒姘粯濡炪値鍓欓ˇ鎵崲濠靛鍋ㄩ梻鍫熷垁閻愮儤鐓曢柕濠忛檮閵囨繈鏌℃担绋挎殻濠殿喒鍋撻梺闈涚墕閸熺娀宕?

闂?recall_memory(query="闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹潡顢氶埀顒勫蓟閿濆憘鐔封枎閹勵唲闂備焦鐪归崐妤呭磻閹捐埖宕叉繛鎴欏灩楠炪垺淇婇婵囶仩濞寸姾鍋愮槐鎾存媴閸濆嫅锝嗕繆椤愩垹鏆ｇ€殿喛顕ч埥澶婎潩椤愶絽濯伴梻浣告啞閹稿棝鍩€椤掆偓鍗遍柛顐犲灮绾捐棄霉閿濆浂鐒炬い锝嗗▕閺屾稓鈧綆鍓欓弸娑㈡煕閳规儳浜炬俊鐐€栧濠氬磻閹惧墎纾奸柣妯垮皺鏁堥悗瑙勬礃濞叉ê顭囪箛娑樼厴闁诡垎鍌氼棜婵犳鍠楅…鍥储瑜嶉埢宥咁吋婢跺鍘靛銈嗙墬閻熝囧礉瀹ュ鐓欐い鏍ㄧ⊕椤ュ牆鈹戦埄鍐╁€愰柡浣稿€块獮鍡氼槻缂佺姷澧楃换婵嬫偨闂堟稐鍝楅梺瑙勬た娴滅偟妲愰悙鍝勭劦妞ゆ帊闄嶆禍婊勩亜閹扳晛鐒烘俊鑼劋缁绘盯宕遍幇顒備紙閻庤娲╃徊鎯ь嚗閸曨垰閱囨繝濠傛噽濞?)
闂?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸ゅ嫰鏌涢锝嗙缂佺姷濞€閺岀喖宕滆鐢盯鏌涙繝鍛厫闁逛究鍔岃灒闁圭娴烽妴鎰磼閻愵剙鍔ゆ繛纭风節瀵鎮㈤悡搴ｇ暰闂佺粯顨呴悧婊兾涢崟顖涒拺闁告繂瀚銉╂煕鎼淬垹鈻曢柛鈹惧亾濡炪倖宸婚崑鎾绘煕濡崵鐭掔€规洘鍨块獮妯肩磼濡厧甯楅柣鐔哥矋缁挸鐣峰鍫熷亜闁兼祴鏅涚粊锕傛椤愩垺澶勬繛鎻掔Ч瀹曟垿骞樼紒妯绘珳闁硅偐琛ラ崜婵嬫倶閸垻纾藉ù锝呮惈閻濓繝鏌涢妷锝呭濞寸媭鍨跺铏规嫚閳ュ啿绠洪柣銏╁灡鐢绌辨繝鍥ч敜婵°倓鑳堕崢?闂?闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极瀹ュ绀嬫い鎺嶇劍椤斿洭姊绘担铏瑰笡闁告梹娲熼、姘额敇閻樺吀绗夋俊銈忕到閸燁垶鎮￠崘顏呭枑婵犲﹤鐗嗙粈鍫熸叏濡潡鍝虹€?闂?闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓鍝ョ不閺嶎厽鐓曟い鎰剁稻缁€鈧紒鐐劤濞硷繝寮婚悢鐓庣畾闁绘鐗滃Λ鍕磼閹冣挃缂侇噮鍨抽幑銏犫槈閵忕姷顓洪梺鍝勫暊閸嬫捇鏌? "闂傚倸鍊搁崐宄懊归崶顒夋晪鐟滃秹婀侀梺缁樺灱濡嫮绮婚悩缁樼厵闁硅鍔﹂崵娆戠磼閻橀潧鏋涙慨濠佺矙瀹曞爼顢楅埀顒侇攰闂備礁婀辨晶妤€顭垮Ο鑲╃焼闁告劏鏂傛禍婊堟煛閸愩劌鈧摜鏁崼鏇熺厽閹兼惌鍠栧顕€鏌熼鐓庢Щ妞ゎ厹鍔戝畷銊╊敇瑜庡В澶愭⒑濮瑰洤鐒洪柛銊╀憾閵嗗啯绻濋崶褎妲┑鐐村灟閸ㄥ湱鐚惧澶嬬厱妞ゆ劑鍊曢弸鏃堟煕濮楀棔閭慨濠冩そ瀹曟粓骞撻幒宥囧嚬缂傚倷娴囬褏鈧凹鍙冨鏌ュ醇閺囩儐娼婇梺闈涚箞閸ㄥ鏁嶅鍫熲拺缂備焦锕╅悞楣冩倶韫囨梻鎳呯紒顔芥煥鐓ゆい蹇撴噽閸樻悂鏌ｈ箛鏇炰户妞ゎ厼鐗婇弲鍫曟嚑椤掑倻锛滈梺鍝勫暙閸婃悂寮告惔銊︾厓闁荤喐婢橀弳锝団偓瑙勬礀缂嶅﹪銆佸▎鎾村仭濡绀侀ˉ姘舵⒒娓氣偓濞佳囨偋閸℃蛋鍥敍閻愭潙娈濋悷婊呭鐢鎮￠弴鐔翠簻闁规澘澧庣粙鑽ょ磼閳ь剟宕奸妷锔惧幈濠电偛妫欓崝鏍х暦瀹€鍕厸閻忕偛澧藉ú鏉戔攽閿涘嫬鍘存鐐差儏閳规垿宕遍埡鈧槐婵囩節绾版ɑ顫婇柛瀣嚇瀹曞綊宕归鍛稁?
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
        {"role": "user", "content": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｅΟ娆惧殭缂佺姴鐏氶妵鍕疀閹炬惌妫炵紓浣界堪閸婃繈寮婚悢铏圭煓闁割煈鍣崝澶愭⒑閸涘﹦鎳冪紒缁橈耿瀵鎮㈤搹鍦紲闂侀潧绻掓慨鐢告倶閸儲鐓?},
        {"role": "assistant", "content": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｅΟ娆惧殭缂佺姴鐏氶妵鍕疀閹炬惌妫炵紓浣界堪閸婃繈寮婚悢铏圭煓闁割煈鍣崝澶愭⒑閸涘﹦鎳冪紒缁橈耿瀵鎮㈤搹鍦紲闂侀潧绻掓慨鐢告倶閸儲鐓曢柕澶堝劤閹界姷绱掔紒妯笺€掗柍褜鍓涢弫鎼佲€﹂崼婵堟懃濠碉紕鍋戦崐鏍垂闂堟党娑樷攽閸♀晛娈ㄩ梺鍝勮閸庢椽寮崱娑欑厓鐟滄粓宕滈悢鍑よ€垮〒姘ｅ亾婵﹥妞介獮鎰償閿濆洨鏆ら梻浣虹帛椤ㄥ棛鍒掑畝鍕ㄢ偓锕傚炊椤掆偓缁犳稒銇勯弬鍨挃闁挎稒绮撳铏圭磼濡浚浜畷顖滄崉閵娧呯暥闂佸湱鍎ら〃鍡浰夐崱妤婄唵闁兼悂娼ф慨鍫ユ煟閹捐泛鏋戦柟渚垮妼铻栭柍褜鍓欒灋婵°倓鑳堕々鍙夌節婵犲倸骞橀柣鐔煎亰閻撱儵鏌涘☉鍗炲箳濠㈣娲滅槐鎾存媴閾忕懓绗￠梺鐑╂櫓閸ㄥ爼鎮伴閿亾閿濆骸鏋熼柛濠勫厴閹鎮藉▓璺ㄥ姼閻庢鍠楁繛濠傤潖缂佹ɑ濯撮柧蹇曟嚀缁椻€愁渻閵堝啫濡奸柟鍐叉唉閻忓鈹戦悩璇у伐闁绘妫欓、濠囨⒒娴ｅ憡璐″褎顨呴…鍨潨閳ь剟骞嗙仦杞挎棃鍩€椤掑嫧鈧妇鎹勯妸锕€纾梺鎯х箰濠€閬嶅礉缁嬪簱鏀介柣鎰摠缂嶆垿鎮楀顓熺凡妞ゎ偄绻愮叅妞ゅ繐鎷嬪Λ鍐ㄢ攽閻愭潙鐏卞瀛樼摃閸婃挳姊婚崒娆掑厡妞ゎ厼鐗嗛～婵嬫晜閻ｅ矈娲稿銈嗗笒鐎氼參宕靛澶婄骇闁割偅纰嶅▍鍡涙倵濮橆厼鍝洪柟顕€鏀遍幏鍛槹鎼搭喗袦缂傚倸鍊哥粔鎾晝椤忓嫷鍤曟い鎰剁畱缁犳盯鏌℃径搴㈢《闁稿﹦鍋涢—鍐Χ鎼粹€斥拻闂佸摜濮甸幑鍥х暦閺囥垺鍤戞い鎺嶇鎼村﹤鈹戦悙鏉戠仧闁搞劌缍婇弻瀣炊椤掍胶鍘介梺鍝勫暙閻楁粌螞閹存緷褰掓偂鎼达絿鍔┑?},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    """Long conversations should have older messages compressed."""
    messages = [{"role": "system", "content": "System prompt"}]
    # Add 20 user/assistant pairs
    for i in range(20):
        messages.append({"role": "user", "content": f"闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴妤€浜惧銈庝簻閸熸潙鐣疯ぐ鎺濇晪闁告侗鍨版慨娲⒒娴ｄ警娼掗柛鏇炵仛閻ｅ墎绱撴担鎻掍壕婵犮垼娉涙径鍥磻閹捐崵宓侀柛顭戝枛婵骸顪冮妶蹇撶槣闁搞劏娉涢锝嗗閺夋嚦銊╂煥閺傚灝鈷旀い鏃€娲熷娲偡闁箑娈堕梺绋匡攻閸ㄧ敻锝炲┑瀣垫晞闁冲搫顑囩粔顔锯偓瑙勬礀閵堝憡淇婇悜鑺ユ櫆闁诡垎鍐杽婵犵绱曢崑鎴﹀磹閺嶎厼绀夐柟杈剧畱绾惧綊鏌￠崶銉ョ仼闁告垹濮烽埀顒€绠嶉崕鍗灻洪妸褍顥?{i}"})
        messages.append({"role": "assistant", "content": f"闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极閹剧粯鍋愰柤鑹板煐閹蹭即姊绘担鑺ョ《闁哥姵鎸婚幈銊╁箻椤旇棄浠鹃梺缁樺姦閸撴稓寮ч埀顒佺節閻㈤潧孝闁稿﹥鎮傞、鏃堫敂閸涱垳顔曢梺鍛婁緱閸ㄧ増鐗庣紓鍌欒兌缁垳鎹㈤崘顏呭床婵犻潧顑呯壕鍏肩節婵犲倸鏋ら柡鍡╁亰濮婄粯鎷呴搹鐟扮闂佸憡姊瑰ú鐔煎极閸愵噮鏁傞柛顐ｇ箚閹芥洟姊洪幐搴ｇ畵妞わ富鍨崇划璇测槈濞嗗秳绨婚梺鐟版惈缁夌兘顢欐径鎰厸閻庯綆鍋嗛幊鍐煃?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ラ梺钘夊暟閸犳牠寮婚弴鐔虹闁绘劦鍓氶悵锕傛⒑鏉炴壆顦﹂悗姘嵆瀵鈽夊Ο閿嬵潔闂佸憡顨堥崑鐐烘倶瀹ュ應鏀介柣鎰级閸ｈ棄鈹戦悙鈺佷壕闂備礁鎼惌澶屽緤閸婄喓浜介梻浣稿悑缁佹挳寮插☉姘辩當闁跨喓濮甸埛鎴犵磼鐎ｎ亝鍋ユい搴㈩殘缁辨帗寰勬繝鍕ㄩ悗娈垮枦椤曆囧煡婢舵劕顫呴柣妯诲絻缁侇噣姊绘笟鈧褔鈥﹂崼銉ョ？濞寸厧鐡ㄩ崵瀣亜韫囨挾澧涢柍閿嬪灴閺岀喖鎳栭埡浣风捕闂侀€炲苯澧い銊ユ閹广垹鈽夐姀鐘靛姦濡炪倖甯掔€氼參鎮″▎鎰╀簻闁哄啫娲ゆ禍鍦磼婢跺孩顏犻柍褜鍓濋～澶娒洪弽顓熷亯闁稿繘妫跨换鍡樻叏濠靛棛鐒炬俊鏌ョ畺濮婄儤瀵煎▎鎴犘滄繛瀛樼矎濞夋盯锝炶箛鎾佹椽顢旈崨顓濈暗闂佺澹堥幓顏嗗緤閼测晛鍨濋柣銏犳啞閳锋垿鏌熼懖鈺佷粶濠碘€冲悑缁绘稓浜搁弽銈呬壕闁归绀佸▓銊ヮ渻閵堝棗濮傞柛鈺佸瀹曘儳鈧綆鍠楅悡鏇熺箾閹存繂鑸归柣蹇婂墲缁绘盯宕奸悢鍝ヮ槹濠殿喖锕ュ浠嬪蓟閸涘瓨鍊烽柤鑹版硾椤忣厽绻濋埛鈧崘鎯ф闂侀€炲苯澧い鏃€鐗犲畷鎶筋敋閳ь剙鐣烽幋鐐电瘈闁告剬鍛暰闂備礁鍚嬮幃鍌氼焽瑜忓▎銏ゆ倷濞村鏂€闂佺粯蓱瑜板啴顢旈幘顔界厱婵﹩鍓氶崵鍥煛瀹€瀣ɑ闁诡垱妫冮弫鎰板幢濡や胶鏆氶梻浣筋嚙鐎涒晠宕欒ぐ鎺戝偍濠靛倻纭堕埀顒婄畵瀹曞綊顢欓妷褍鏋涢柟顔瑰墲閹棃鏁愰崶鈺傛啠婵犵數濮烽弫鎼佸磻濞戞鐔哥節閸愵亶娲稿┑鐘绘涧椤戝懘鎮￠弴銏＄厵閻庣數顭堟禍鐓幟瑰鍕煉闁哄瞼鍠栭幊婊堫敆閳ь剚淇婇悡搴唵鐟滃秴顕ｉ崼鏇炍﹂柛鏇ㄥ灡閺呮繈鏌涚仦璇测偓鏍夐弽顐ょ＝?0闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴姘辩Т闂佹悶鍎洪崜锕傚极閸愵喗鐓ラ柡鍥殔娴滃墽绱撴担鎻掍壕闂佸壊鍋嗛崰鎾跺姬閳ь剟姊婚崒姘卞缂佸鎸婚弲鍫曞閵堝棛鍘藉銈嗘尵閸犳劕鐣峰畝鍕厸鐎光偓鐎ｎ剛袦濡ょ姷鍋涢澶愬极閹版澘骞㈤柍鍝勫亞濡嫮绱撻崒姘偓鐑芥嚄閼稿灚鍙忛柣銏犵仛閺嗘粍淇婇妶鍛櫣濡楀懘姊洪崨濠冨闁搞劋鍗冲畷姗€鍩€椤掑嫭鈷戦梻鍫熶緱濡插爼鏌涙惔顔兼珝鐎规洘鍨块獮妯侯熆閸曨剚顥堢€规洘锕㈤、鏃堝幢濞嗗繐笑濠电姷鏁告慨浼村垂婵傜鏄ラ柡宥庡幖缁€澶愭煛瀹ュ骸骞楅柛瀣€块弻锟犲炊閵夈儳浠鹃梺缁樻尰閻╊垶寮诲☉姘勃闁告挆鍛帎闂備礁鎲￠弻銊╊敄閸℃瑦宕叉繛鎴欏灩瀹告繃銇勯幘璺烘珡婵☆偆鍋涢—鍐Χ鎼粹€崇哗闂佺楠搁…鐤閻庤娲栧ú銊у閸忕浜滈柡鍐ㄦ搐琚氶悗瑙勬礀閻ジ鍩€椤掍緡鍟忛柛鐘崇墵閳ワ箑鐣￠幍顔芥婵犻潧鍊婚…鍫濇暜闂備焦瀵уú宥夊磻閹剧粯鐓熺憸宥団偓姘煎幘閹广垹鈹戠€ｎ亶娼婇梺鎸庣箓濡盯濡撮幇顒夋富闁靛牆绻掗悾鍐差渻鐎涙ɑ鍊愬┑锟犳涧閳诲酣骞樼€涙ê鍔掓俊鐐€栭崝鎴﹀磹濡ゅ拋鏁婇柡鍥ュ灪閻撶喖骞栧ǎ顒€鐏柍顖涙礃閵囧嫰顢橀悙鏉戞灎闂佽鍨伴張顒傛崲濠靛绀冪憸蹇曠不濮橆剦娓婚柕鍫濇婵呯磽瀹ュ懏顥滈柍缁樻崌瀵噣宕奸悢铚傜暗闂備線娼ч悧鍡浰囨导瀛樺亗婵炴垶鍩冮崑鎾荤嵁閸喖濮庨梺鍝ュ櫏閸嬪懏绌辨繝鍥ㄥ殐闁冲搫鍟伴敍婊堟⒑閸涘﹥灏紒鈧担鍦浄鐟滄棃寮诲鍫闂佸憡鎸婚悷褏鍒掔拠宸悑濠㈣泛锕﹂敍鐔兼⒒娓氬洤澧紒澶嬫尦閹潡顢氶埀顒勫蓟閿濆憘鐔封枎閹勵唲缂?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # System prompt should be preserved
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"

    # Should have a summary message
    assert any("婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ラ梺钘夊暟閸犳牠寮婚弴鐔虹闁绘劦鍓氶悵锕傛⒑鏉炴壆顦﹂悗姘嵆瀵鈽夊Ο閿嬵潔闂佸憡顨堥崑鐐烘倶瀹ュ應鏀介柣鎰级閸ｈ棄鈹戦悙鈺佷壕闂備礁鎼惌澶屽緤閸婄喓浜介梻浣稿悑缁佹挳寮插☉姘辩當闁跨喓濮甸埛鎴犵磼鐎ｎ亝鍋ユい搴㈩殘缁辨帗寰勬繝鍕ㄩ悗娈垮枦椤曆囧煡婢舵劕顫呴柣妯诲絻缁侇噣姊绘笟鈧褔鈥﹂崼銉ョ？濞寸厧鐡ㄩ崵瀣亜韫囨挾澧涢柍閿嬪灴閺岀喖鎳栭埡浣风捕闂侀€炲苯澧い銊ユ閹广垹鈽夐姀鐘靛姦濡炪倖甯掔€氼參鎮? in m.get("content", "") for m in result)

    # Recent messages should be preserved (last 12 non-system messages = 6 pairs)
    assert len(result) <= 14  # system + summary + 12 recent


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    """The most recent messages should be kept intact."""
    messages = [{"role": "system", "content": "System prompt"}]
    for i in range(20):
        messages.append({"role": "user", "content": f"濠电姷鏁告慨鐑藉极閸涘﹥鍙忛柣鎴ｆ閺嬩線鏌熼梻瀵割槮缁炬儳顭烽弻锝夊箛椤掍焦鍎撻梺鎼炲妼閸婂潡寮婚敐澶婎潊闁绘ê鍟块弳鍫ユ⒑缁嬫鍎忔い鎴濇嚇閸╃偤骞嬮敂钘変汗闂佸湱绮敮妤€鈻撻鐑嗘富?{i}"})
        messages.append({"role": "assistant", "content": f"闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓鍝ョ不閺嶎厽鐓曟い鎰剁稻缁€鈧紒鐐劤濞硷繝寮婚悢鐓庣畾闁绘鐗滃Λ鍕磼閹冣挃缂侇噮鍨抽幑銏犫槈閵忕姷顓洪梺鍝勫暊閸嬫捇鏌?{i}"})

    mock_response = {
        "role": "assistant",
        "content": "闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋為悧鐘汇€侀弴銏℃櫇闁逞屽墴閹潡顢氶埀顒勫蓟閿濆憘鐔封枎閹勵唲闂備焦鐪归崐妤呭磻閹捐埖宕叉繝闈涙川缁♀偓闂佺鏈喊宥夋倶閺囥垺鈷戦柛蹇撳悑缁跺弶绻涚涵椋庣瘈鐎殿喖顭锋俊鎼佸Ψ閵忊槅娼旀繝纰樻閸垳鎷冮敂鐣岊浄闂侇剙绉甸埛鎴犵磼鐎ｎ偒鍎ラ柛搴㈠姍閺岀喖鎮烽悧鍫濇灎濡ょ姷鍋涢崯鎾箰婵犲啫绶為柛鈩冾焽娴滄牠姊绘担鍛婅础妞ゎ厼鐗忛埀顒佺▓閺呯姴顕ｉ幎鑺ュ€烽柣鎴炃氶幏缁樼箾鏉堝墽绉い銉︽尰缁嬪鎳犻鍌滐紳闂佺鏈粙鎺楁儍閹达附鐓曢柟鐑樻尭缁楁帡鏌嶇拠鏌ュ弰妤犵偞顭囬幑鍕惞楠炲灝浜版繝鐢靛Т閻ュ寮舵惔鎾充壕闁圭増婢樼壕濠氭煙閸撗呭笡闁硅櫕宀搁弻銊モ攽閸℃﹩妫ょ紓浣哄█缁犳牠寮诲☉銏犵労闁告劦浜濋崳褎绻涚€涙鐭掔紒鐘崇墵瀵?,
    }

    with patch("app.services.context_compressor.chat_completion", new_callable=AsyncMock, return_value=mock_response):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    # Last message should be the most recent assistant reply
    assert result[-1]["content"] == "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弴鐐测偓鍝ョ不閺嶎厽鐓曟い鎰剁稻缁€鈧紒鐐劤濞硷繝寮婚悢鐓庣畾闁绘鐗滃Λ鍕磼閹冣挃缂侇噮鍨抽幑銏犫槈閵忕姷顓洪梺鍝勫暊閸嬫捇鏌?19"
```

- [x] **Step 2: Run tests to verify they fail**

Run: `cd student-planner && python -m pytest tests/test_conversation_compression.py -v`
Expected: FAIL 闂?`ImportError: cannot import name 'compress_conversation_history'`

- [x] **Step 3: Add compress_conversation_history to context_compressor.py**

Append to `app/services/context_compressor.py`:

```python
from app.agent.llm_client import chat_completion as _chat_completion

_SUMMARIZE_PROMPT = """闂傚倸鍊搁崐鎼佸磹瀹勬噴褰掑炊瑜忛弳锕傛煕椤垵浜濋柛娆忕箻閺屸剝寰勭€ｎ亝顔呭┑鐐叉▕娴滃爼寮崶顒佺厓閻犺櫣鍎ら幆鍫熴亜閿旂偓鏆柣娑卞枛铻ｉ柛蹇曞帶閻濅即姊洪崨濠勬噧妞わ箓浜堕崺鈧?-3闂傚倸鍊搁崐鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极閹剧粯鍋愰柛鎰紦閻㈠姊绘担鐟邦嚋缂佽鍊胯棟妞ゆ牗绮岄ˉ姘舵煕瑜庨〃鍡涙偂濞嗘垹纾藉ù锝夋涧閻忊晠鏌＄€ｎ剙鏋涢柡灞剧⊕閹棃鍩ラ崨顓濈矗闂傚倸娲らˇ鐢稿蓟閿濆憘鐔兼倻濡攱鐏嗛梻浣侯焾妤犲摜鎹㈤幒鏃€顫曢柟鐑橆殕閸嬫劙鏌涢幇顖氱毢濞寸厧鐭傚娲传閸曨噮娼堕梺绋匡攻閻楃娀鐛崼銉ノ╅柍杞拌兌閻も偓婵＄偑鍊栭崹鐓幬涢崟顒傤洸闁绘劦鍏涚换鍡涙煏閸繂鈧憡绂嶆ィ鍐┾拺鐎规洖娲ㄧ敮娑欎繆椤愩垹鏆為柟渚垮姂閸┾偓妞ゆ帒瀚悡鐔镐繆椤栨粌鍔嬫い銉︾矌缁辨挸顓奸崪鍐惈濡ょ姷鍋涢崯鎾春閿熺姴妞藉ù锝堫潐濞呮捇姊绘担铏瑰笡闁圭鎲￠〃銉╁箹娓氬﹦绋忛梺鍦劋濮婅崵澹曟禒瀣厱閻忕偛澧介幊鍛存煕閺傝法校闁靛洤瀚版俊鎼佸Ψ閿曗偓濞堟螖閻橀潧浠滈柨鏇ㄤ邯閻涱噣宕堕鈧痪褔鎮归幁鎺戝濠殿噯闄勬穱濠囨倷椤忓嫧鍋撻弽顐ｆ殰闁圭儤顨呯壕鍦喐閻楀牆绗掓慨瑙勭叀閺屽秹宕崟顐熷亾閼哥數顩叉繝濠傜墛閻撳繘鐓崶銊︾妞ゅ孩鎹囧Λ鍛搭敆婢跺﹤鈷嬮梺鍝勭灱閸犳牠銆佸☉妯锋瀻闁瑰瓨绻傞‖澶岀磽閸屾瑧顦﹂柛濠傛贡閺侇噣鎮欓崫鍕姦濡炪倖甯掗敃锔剧矓闂堟耽鐟邦煥閸涱厺妲愰柦妯荤箞閺屾洘绻涢悙顒佺彆闂佹娊鏀遍崹鍧楀蓟濞戞ǚ妲堟慨妤€鐗婇。鑲╃磽娴ｅ摜鍩ｅù婊冪埣瀵鈽夊Ο閿嬬€婚棅顐㈡处缁嬫垵顕ｆ导瀛樺€甸悷娆忓婢跺嫰鏌涢妸銊︾【闁伙絿鍏樺畷濂稿即閵婏附娅屽┑鐐舵彧缁蹭粙骞栭銈嗘殰濡わ絽鍟埛鎺懨归敐鍫燁仩闁靛棗锕弻娑㈠箻鐎靛摜鐤勯梺闈涙閸熸潙鐣烽妸鈺佺骇闁瑰濮存慨锔戒繆閻愵亜鈧牕顔忔繝姘；闁规儳顕粻楣冩倶韫囨梻澧ら柛瀣尭閻ｇ兘宕堕妸锔诲晭闂傚倷娴囬～澶愬磿閻撳宫娑㈠礋椤撶姳绗夐梺鑽ゅ枑閸ｇ銇愰幒鎾存珳闂佹悶鍎崝灞解枔瀹€鍕拺闂侇偆鍋涢懟顖涙櫠娴煎瓨鐓曢煫鍥ㄦ瀭椤忓牞缍栭煫鍥ㄦ媼濞差亶鏁傜€广儱妫欏▍鍥⒒娴ｇ懓顕滅紒璇插€哥叅闁靛繈鍊曢悞鍨亜閹哄秶顦︾紒妞﹀懐纾奸弶鍫涘妼濞搭噣鏌熼瑙勬珕婵炵厧绻橀崺锟犲礃椤忓嫬绠氶梻鍌氬€风粈渚€骞栭锔藉剹濠㈣泛鐬肩粈濠傘€掑锝呬壕閻庢鍣崑濠囩嵁閸ヮ剙绾ч柛顭戝枦閳ь剙鐏濋埞鎴︽倷閸欏妫￠梺鍛婃⒐濞叉牠鍩㈤幘鍦杸闁哄洨濮烽敍婵嬫⒑缁嬫寧婀伴柣鐔濆泚鍥晜閻愵剙鏋戦梺鍝勵槹椤戞瑥螣閳ь剟鎮楃憴鍕┛缂佺粯绻堥悰顔芥償閵婏箑鐧勬繝銏ｆ硾閻ジ寮抽鈶╂斀闁绘劕妯婇崵鐔封攽椤旇姤灏︽い銏＄墵瀹曘劑顢欓悡搴☆潑闂傚倸鍊搁崐鐑芥倿閿旈敮鍋撶粭娑樺幘閸濆嫷鍚嬪璺猴功閿涙盯姊洪悷鏉库挃缂侇噮鍨堕幃锟犳偄閸忚偐鍘甸梺璇″瀻閸涱喗鍠栫紓鍌欒閸嬫捇鎮楅敐搴℃灍闁绘挻鐩幃姗€鎮欓幓鎺嗘寖闂侀潧妫欑敮锟犲蓟瀹ュ牜妾ㄩ梺鍛婃尪閸斿海妲愰悙鍝勫耿婵炴垶顭囬敍娑㈡⒑缁洖澧茬紒瀣浮瀹曟垿宕掑☉鏍︾盎闂佸搫绉查崝搴ㄦ儗瀹€鈧惀顏堝箚瑜嬮崑銏ゆ煛鐏炵偓绀冪紒缁樼洴瀹曞綊顢欓崣銉﹀亝婵犵數濮幏鍐幢濡ゅ啯顕楃紓鍌欐祰妞村摜鏁垾宕囨殾闁圭儤鍨熷Σ鍫熶繆椤栨稒顫楅柣褌绶氬缁樻媴閾忓箍鈧﹪鏌￠崒娆戠獢鐎规洘鍨块獮姗€骞囨担鐟扮槣闂備線娼ч悧鍡椢涘Δ鍐當闁稿瞼鍋為悡鐘绘煕閹邦垰鐨洪柛鈺嬬秮閺屾盯鍩為崹顔句紙閻庢鍠楅幐铏叏閳ь剟鏌ㄥ☉妯侯仼妤犵偛鐗婃穱濠囨倷椤忓嫧鍋撻弽顓炵闁硅揪绠戠壕褰掓煛閸ャ儱鐏╅柛鎴犲█閺岀喐娼忔ィ鍐╊€嶉梺缁樻尰閻燂箓濡甸崟顖氬唨闁靛ě浣插亾閹烘鐓欓柛鎰絻閺嗭絾淇婇锛勫妽鐎垫澘瀚伴獮鍥敇閻樻彃姹插┑鐘垫暩婵炩偓婵炰匠鍏炬稑鈻庨幘宥咁槸椤劑宕熼鐙€鍟庨梻浣稿閸嬩線宕硅ぐ鎺戠厺闁割偁鍎查悡娑㈡倶閻愬灚娅曢崯绋款渻閵囧崬鍊荤粣鏃堟煛鐏炲墽顬肩紒鐘崇洴瀵噣宕掑☉妯虹仭闂傚倷鑳堕、濠傗枍閺囶潿鈧啯绻濋崒婊勬婵犻潧鍊婚…鍫ュ础閹惰姤鐓熼柟閭﹀墮閹胶绱掓潏銊х煁缂佺粯绻勯崰濠偽熷ú缁樼秹闂備焦鎮堕崝瀣础閸愯尙鏆﹂柕澹偓閸嬫捇鏁愭惔鈥茬盎闂佹悶鍔嶉弻銊╁煘閹达箑纾兼慨姗嗗幖閺嗗牓姊虹紒妯诲碍缂佺粯锕㈠璇测槈閵忊晜鏅濋梺鎸庣箓濞层劑鎮鹃棃娑辨富闁靛牆鎳忕粋瀣煕鐎ｎ亷韬€殿喛顕ч埥澶愬閳ュ厖绨婚梻浣告啞閸垶宕愰弴鐔奉嚤闁规壆澧楅埛鎺楁煕閵夋垵鏈埢鍫ユ⒑閸濆嫮鐒跨紒韫矙閿濈偛顭ㄩ崼婵嗚€垮┑锛勫仜婢т粙鎯勬惔鈾€鏀介柣鎰皺閹界姷绱掗濂稿弰鐎规洘鍨块獮姗€鎳滈棃娑樼哎婵犵數鍋為崹顖炲垂閸︻厾涓嶉柨婵嗩槹閻撶喖鏌熼柇锕€澧婚柛銈囧枛閺屾稑鈻庤箛鏃戞＆濠殿喖锕ㄥ▍锝囨閹烘埈娼ㄩ柛鈩冾焽閺嗐儵姊虹拠鎻掝劉闁活収鍣ｅ畷锟犲礃閼碱剚娈惧┑鐐叉▕娴滄粓鎮為崹顐犱簻闁瑰搫绉瑰宄懊瑰鍕煉闁哄瞼鍠撻埀顒傛暩椤牊绂掑鍕╀簻闁哄洨鍠撻惌宀€绱掓潏銊ョ瑲闁瑰嘲鎳庨悾锟犲级鐠恒劊鍋栭梻鍌欑閹碱偊寮甸鈧叅闁绘棃顥撻弳锕傛煕濡ゅ啫鈧綁寮崼婵堝姦濡炪倖甯掔€氼剙效閺屻儲鐓熼柟閭﹀墻閸ょ喓绱掗悩鑽ょ暫闁哄矉缍侀獮姗€鎼归锝呴棷缂傚倷鑳舵慨鎯х暦閻㈢鐒垫い鎺戝枤濞兼劖绻涘ù瀣珖缂佽京鍋為幏鍛存焻濞戞氨鐣鹃梻浣圭湽閸娿倝宕归悡骞絾绻濆顓涙嫼闂佸憡绻傜€氼參宕抽幎鑺ョ厸闁告侗鍠氶惌宀勬煙楠炲灝鐏╅柍钘夘槸椤繈鏁愰崨顒€顥氶梻浣圭湽閸ㄦ椽顢欓弽顓熷€块柛鎾楀嫬浠忛梺闈涱槴閺呮粓鍩涢幋鐘电＜閻庯綆鍋掗崕銉╂煕鎼淬垹濮嶉柡宀€鍠栧畷銊︾節閸愩劉鍋撻幇鐗堢厱闁崇懓鐏濋崝婊呪偓鍨緲鐎氫即鐛崶顒夋晢濞撴艾娲﹂ˉ銈夋⒒娴ｈ棄鍚瑰┑顔肩仛缁傚秵绂掔€ｎ亞顦悗鍏夊亾闁告洍鏂侀崑鎾诲磼閻愭潙鈧粯淇婇婵嗕汗妞ゆ梹娲熼弻锝嗘償閵忊懇濮囧銈庡幖濞差參骞嗙仦鍓х瘈闁搞儯鍔庨崢鐢告煟閻樺弶鍘傞柛娑卞灲缁辩數绱撻崒姘偓鎼佸磹瑜版帒绠查柛銉墮缁犵娀鏌ｉ幇顒佹儓閸烆垶姊洪幐搴㈢５闁稿鎸鹃埀顒侇問閸犳牕顭囬垾鎰佹綎闁惧繗顫夐崗婊堟煕濞戝崬骞橀柛鏃傚厴濮婃椽宕ㄦ繝鍐弳闂佸搫鐗滈崜娑氬垝?""


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
        summary = response.get("content", "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍛婄秶濡わ絽鍟宥夋⒑缁嬫鍎忔い鎴濇嚇閸╃偤骞嬮敂钘変汗闂傚鍋掗崣鈧柟鑸殿殔閳规垿鎮欓弶鎴犱户闂佺硶鏅涚€氭澘顕ｉ锕€鐐婃い鎺嶈兌閸橆亪妫呴銏″婵炲弶鐗曢悺顓㈡⒒娴ｈ櫣甯涚紒璇插暣閺佸啴濮€閻欌偓濞兼牠鏌ц箛鎾磋础缁炬儳鍚嬫穱濠囶敍濠靛棗鎯為梺鍛婄懃濡鈥旈崘顔嘉ч柛鎰╁妼椤牓姊绘担绋跨盎缂佽弓绮欓幃楣冩倻閼恒儱浠洪梺鍛婄☉閿曘倖绂嶉崷顓犵＝闁稿本鐟ч崝宥夋煥濮橆優褰掓偑閳ь剟宕圭捄渚綎婵炲樊浜滅粻褰掓煟閹邦厼绲诲┑顔肩焸濮婃椽宕ㄦ繝鍐弳濠电偞鎸抽ˉ鎾诲礆閹烘挾绡€婵﹩鍓欓崬銊ヮ渻閵堝棙灏甸柛鐘虫崌瀹曘垽鎮介崨濞炬嫼闂侀潻瀵岄崢鍓ф暜濞戙垺鍋ㄦい鏍ㄧ矊娴犻亶鏌℃担鍝バ㈡い鎾冲悑瀵板嫮鈧綆鍓欓獮宥夋⒒娴ｈ棄浜归柍宄扮墦瀹曟粌鈻庨幘鎵佸亾閸屾稓闄勯柛娑橈功閸樼敻鎮楅悷鏉款伀濠⒀勵殜瀹曟娊鎮滃Ο闀愮盎闂佹寧姊归崕鎶姐€傛總鍛婄厵妞ゆ牗绋掗ˉ鍫ユ煛娴ｇ懓濮嶇€规洖宕灃濞达綀妗ㄧ花顕€姊婚崒姘偓鎼佸磹閹间礁纾瑰瀣捣閻棗銆掑锝呬壕濡ょ姷鍋涢ˇ鐢稿极閹剧粯鍋愰柛鎰紦閻㈢粯淇婇悙顏勨偓鏍偋濠婂牆纾绘繛鎴欏灩閸ㄥ倿鏌涘畝鈧崑鐐烘偂濞嗘挻鐓欐い鏍ㄧ矊椤ｅ吋銇勯妷銉█闁哄矉绱曢埀顒婄岛閺呮繄绮ｉ弮鍫熺厸閻忕偟鍋撶粈瀣偓瑙勬礈閸樠囧煘閹达箑绠涙い鎾筹紡閸ャ劉鎷?)
    except Exception:
        summary = "闂傚倸鍊搁崐鎼佸磹閹间礁纾归柣鎴ｅГ閸婂潡鏌ㄩ弮鍫熸殰闁稿鎸剧划顓炩槈濡娅ч梺娲诲幗閻熲晠寮婚悢鍛婄秶濡わ絽鍟宥夋⒑缁嬫鍎忔い鎴濇嚇閸╃偤骞嬮敂钘変汗闂傚鍋掗崣鈧柟鑸殿殔閳规垿鎮欓弶鎴犱户闂佺硶鏅涚€氭澘顕ｉ锕€鐐婃い鎺嶈兌閸橆亪妫呴銏″婵炲弶鐗曢悺顓㈡⒒娴ｈ櫣甯涚紒璇插暣閺佸啴濮€閻欌偓濞兼牠鏌ц箛鎾磋础缁炬儳鍚嬫穱濠囶敍濠靛棗鎯為梺鍛婄懃濡鈥旈崘顔嘉ч柛鎰╁妼椤牓姊绘担绋跨盎缂佽弓绮欓幃楣冩倻閼恒儱浠洪梺鍛婄☉閿曘倖绂嶉崷顓犵＝闁稿本鐟ч崝宥夋煥濮橆優褰掓偑閳ь剟宕圭捄渚綎婵炲樊浜滅粻褰掓煟閹邦厼绲诲┑顔肩焸濮婃椽宕ㄦ繝鍐弳濠电偞鎸抽ˉ鎾诲礆閹烘挾绡€婵﹩鍓欓崬銊ヮ渻閵堝棙灏甸柛鐘虫崌瀹曘垽鎮介崨濞炬嫼闂侀潻瀵岄崢鍓ф暜濞戙垺鍋ㄦい鏍ㄧ矊娴犻亶鏌℃担鍝バ㈡い鎾冲悑瀵板嫮鈧綆鍓欓獮宥夋⒒娴ｈ棄浜归柍宄扮墦瀹曟粌鈻庨幘鎵佸亾閸屾稓闄勯柛娑橈功閸樼敻鎮楅悷鏉款伀濠⒀勵殜瀹曠敻宕堕浣哄幍濡炪倖姊婚弲顐︽儗婵犲洦鎳氶柨婵嗘川绾捐棄霉閿濆洦顏熷〒姘☉闇夐柣妯荤懃濞诧箓鍩涢幒妤佺厱閻忕偛澧介幊鍡涙煕韫囨挾鐒搁柡宀€鍠栭幖褰掝敃閿濆懐锛撻梻浣筋嚃閸犳顪冮懞銉ょ箚闁归棿绀侀悡娑樏归敐鍕劅婵¤尙鍏樺缁樻媴閸涘﹥鍎撳┑鐐茬湴閸ㄨ棄鐣烽崷顓熷枂闁告洖鐏氶弫顖炴⒒閸屾艾鈧兘鎳楅崼鏇炵疇闁圭偓妞块弫瀣亜閹捐泛鏋戦柛娆忕箻閺岋綁濮€閵忊晜姣岄梺绋款儐閹告悂锝炲┑瀣垫晢濠㈣泛鑻幃鎴︽⒒娴ｅ憡鎯堥柡鍫墮鐓ゆ俊顖欒閸ゆ鏌涢弴銊モ偓鐘绘偄閸忓吋鍎梻渚囧亝缁嬫垹鈧絻灏欑槐鎾诲磼濮橆兘鍋撴搴㈠闁哄被鍎辩壕?

    summary_msg = {
        "role": "user",
        "content": f"[婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ラ梺钘夊暟閸犳牠寮婚弴鐔虹闁绘劦鍓氶悵锕傛⒑鏉炴壆顦﹂悗姘嵆瀵鈽夊Ο閿嬵潔闂佸憡顨堥崑鐐烘倶瀹ュ應鏀介柣鎰级閸ｈ棄鈹戦悙鈺佷壕闂備礁鎼惌澶屽緤閸婄喓浜介梻浣稿悑缁佹挳寮插☉姘辩當闁跨喓濮甸埛鎴犵磼鐎ｎ亝鍋ユい搴㈩殘缁辨帗寰勬繝鍕ㄩ悗娈垮枦椤曆囧煡婢舵劕顫呴柣妯诲絻缁侇噣姊绘笟鈧褔鈥﹂崼銉ョ？濞寸厧鐡ㄩ崵瀣亜韫囨挾澧涢柍閿嬪灴閺岀喖鎳栭埡浣风捕闂侀€炲苯澧い銊ユ閹广垹鈽夐姀鐘靛姦濡炪倖甯掔€氼參鎮″▎鎰╀簻闁哄啫娲ゆ禍鍦磼婢跺孩顏犻柍褜鍓濋～澶娒洪弽顓熷亯闁稿繘妫跨换鍡樻叏濠靛棛鐒炬俊鏌ョ畺濮婄儤瀵煎▎鎴犐戝┑锛勫仩濡嫰锝炶箛娑欐優閻熸瑥瀚弸鍌炴⒑閸涘﹥澶勯柛瀣缁﹥顦版惔锝囷紲闂佸憡鎸嗛崱姗嗏偓妤呮⒑閸涘﹦鎳冮柛鐔告尦閹即顢欓挊澶岀獮闂佸綊鍋婇崢鍏肩闁秵鈷戦柛鎾村絻娴滄劙鏌熼崘鍙夊枠鐎?{summary}",
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

- [x] **Step 7: Commit**

```bash
cd student-planner
git add app/services/context_compressor.py app/agent/loop.py tests/test_conversation_compression.py
git commit -m "feat: add sliding window conversation compression"
```

---

### Task 10: Update AGENTS.md 闂?Mark Plan 4 Progress

**Files:**
- Modify: `AGENTS.md`

- [x] **Step 1: Update progress in AGENTS.md**

Update the Plan 4 line and current status:

```markdown
- [ ] Plan 4: Memory + 婵犵數濮烽弫鍛婃叏閻戣棄鏋侀柟闂寸绾惧鏌ｉ幇顒佹儓闁搞劌鍊块弻娑㈩敃閿濆棛顦ョ紓浣哄С閸楁娊寮婚悢鍏尖拻閻庣數顭堟俊浠嬫⒑閸濆嫭鍣虹紒璇茬墦瀵濡搁妷銏℃杸闂佺硶鍓濋敋缂佹劖绋撶槐鎾存媴閸濆嫅锝嗕繆椤愩垹鏆ｇ€殿喛顕ч埥澶娢熼柨瀣垫綌婵犵數鍋涘Λ娆撳礉濡ゅ啰鐭欓柛銉戔偓閺€浠嬫煃閽樺顥滃ù婊勭箞閺屻劑寮村Ο铏逛紙閻庢鍠涢褔鍩ユ径鎰潊闁绘ɑ鐗撻崝鎴﹀蓟閺囷紕鐤€濠电姴鍊搁埛澶愭⒑缂佹绠扮紒鐘虫尭椤繐煤椤忓嫬绐涙繝鐢靛Т閸婂宕濇导瀛樷拺缂佸顑欓崕鎰版煙閻熺増鎼愭い顐㈢箳缁辨帒螣鐠囧樊鈧捇姊洪懞銉冾亪藝椤栫偛绠氶柣鎰劋閳锋垹绱掔€ｎ偒鍎ラ柛搴㈠姉缁辨帞鈧綆鍋勯悘閬嶆煟韫囨搩鍎旈柡宀嬬稻閹棃濡搁敂浠嬫暘闂備胶顢婇婊呮崲濠靛鏅?0 婵?task闂?```

Update "闂傚倸鍊搁崐宄懊归崶褏鏆﹂柣銏㈩焾缁愭鏌熼柇锕€鏋涢柛銊︾箞楠炴牕菐椤掆偓閻忣亝绻涢崨顖毿ｅǎ鍥э躬婵″爼宕ㄩ鍏碱仩缂傚倷鑳舵慨鎶藉础閹惰棄钃熸繛鎴炃氬Σ鍫熸叏濡も偓閻楀﹪寮幆褉鏀介柣鎰级閸ｈ棄鈹戦悙鈺佷壕闂備礁鎼惌澶屽緤閸婄喓浜介梻浣虹帛閸ㄦ儼褰滈梺鍝勵儐閻熴儵鍩為幋锔藉€烽柣鎴烇公缁辩敻姊洪崨濠庢畷濠电偛锕ら锝嗙節濮橆儵鈺呮煏婢跺牆鐏柡鍌楀亾闂傚倷鑳剁涵鍫曞礈濠靛鏅繝鐢靛仜閹冲矂宕愬┑鍡╂綎缂備焦顭囩弧鈧柟鑲╄ˉ閳ь剚鏋奸幏濠氭⒒娴ｅ憡鍟為柟鎼佺畺瀹曚即寮借閸ゆ洖鈹戦悩宕囶暡闁稿瀚伴弻褑绠涢幘纾嬬闂佷紮缍€濞夋盯鍩為幋锔藉€烽柡澶嬪灩娴犳悂鏌﹂崘顔绘喚闁哄被鍔岄埥澶娢熸径瀵″洦鐓涚€光偓鐎ｎ剛鐦堥梺绯曟杹閸? to reflect Plan 4 completion.

- [x] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with Plan 4 completion status"
```
