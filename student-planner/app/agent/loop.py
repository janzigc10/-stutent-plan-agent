import json
import uuid
from typing import Any, AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.guardrails import (
    GuardrailViolation,
    check_consecutive_ask_user,
    check_max_loop_iterations,
    check_max_retries,
    check_unknown_tool,
)
from app.agent.llm_client import AsyncOpenAI, chat_completion, chat_completion_stream
from app.agent.prompt import build_system_prompt
from app.agent.tool_executor import execute_tool
from app.agent.tools import TOOL_DEFINITIONS
from app.models.agent_log import AgentLog
from app.models.conversation_message import ConversationMessage
from app.models.user import User
from app.services.context_compressor import compress_conversation_history, compress_tool_result

KNOWN_TOOLS = {tool["function"]["name"] for tool in TOOL_DEFINITIONS}
MAX_ITERATIONS = 20
VALID_ASK_TYPES = {"confirm", "select", "review"}
_SCHEDULE_IMPORT_KEYWORDS = (
    "上传",
    "文件",
    "file_id",
    "图片",
    "截图",
    "照片",
    "excel",
    "xlsx",
    "xls",
    "导入",
)
_COURSE_CONTEXT_KEYWORDS = (
    "课表",
    "课程",
    "日历",
    "两门课",
)
_COURSE_VIEW_KEYWORDS = (
    "查看",
    "看看",
    "看下",
    "看一下",
    "查一下",
    "查查",
    "有哪些",
    "有什么课",
    "列出",
    "现在课表",
)
_COURSE_EDIT_KEYWORDS = (
    "改成",
    "改为",
    "改名",
    "改一下",
    "修正",
    "纠正",
    "合并",
    "重复",
    "删掉",
    "删除",
    "保留",
    "优化成一门",
    "错别字",
)
_COURSE_DISAMBIGUATION_KEYWORDS = (
    "哪两门",
    "具体是哪两门",
    "删掉其中一门",
    "合并成一门",
    "确认一下具体",
)


def _normalize_ask_type(result: dict[str, Any]) -> str:
    ask_type = result.get("type")
    if ask_type not in VALID_ASK_TYPES:
        return "review"

    options = result.get("options")
    has_options = isinstance(options, list) and len(options) > 0
    has_data = result.get("data") is not None

    if ask_type == "confirm" and not has_options and not has_data:
        return "review"

    return ask_type


def _to_persisted_tool_summary(tool_name: str, tool_result_content: str) -> str:
    if tool_result_content.startswith("[TOOL_SUMMARY:"):
        return tool_result_content
    return f"[TOOL_SUMMARY:{tool_name}:v1] {tool_result_content}"


def _build_course_routing_hint(
    user_message: str,
    history_messages: list[ConversationMessage],
) -> str | None:
    compact_message = (user_message or "").strip().lower().replace(" ", "")
    if not compact_message:
        return None

    if any(keyword in compact_message for keyword in _SCHEDULE_IMPORT_KEYWORDS):
        return None

    mentions_course_context = any(keyword in compact_message for keyword in _COURSE_CONTEXT_KEYWORDS)
    wants_to_view_courses = mentions_course_context and any(
        keyword in compact_message for keyword in _COURSE_VIEW_KEYWORDS
    )
    wants_to_edit_courses = mentions_course_context and any(
        keyword in compact_message for keyword in _COURSE_EDIT_KEYWORDS
    )

    last_assistant_message = next(
        (
            str(message.content)
            for message in reversed(history_messages)
            if message.role == "assistant" and message.content
        ),
        "",
    )
    is_course_followup = bool(last_assistant_message) and any(
        keyword in last_assistant_message for keyword in _COURSE_DISAMBIGUATION_KEYWORDS
    )

    if wants_to_edit_courses or is_course_followup:
        return (
            "这是当前数据库里已有课程的管理请求，不是重新导入课表。"
            "不要要求用户重新上传文件，也不要只做寒暄。"
            "先调用 `list_courses` 查看现有课程。"
            "如果用户是在纠正 OCR/导入错字、统一课程名或合并重复课程，"
            "先用 `ask_user` 确认最终保留方案，再调用 `update_course` 修改要保留的课程，"
            "必要时调用 `delete_course` 删除重复或错误记录。"
        )

    if wants_to_view_courses:
        return (
            "这是查看当前课表的请求。"
            "直接调用 `list_courses` 查看现有课程，不要要求用户上传文件。"
        )

    return None


def _is_course_followup_message(
    user_message: str,
    history_messages: list[ConversationMessage],
) -> bool:
    compact_message = (user_message or "").strip().lower().replace(" ", "")
    if not compact_message:
        return False
    if any(keyword in compact_message for keyword in _SCHEDULE_IMPORT_KEYWORDS):
        return False

    last_assistant_message = next(
        (
            str(message.content)
            for message in reversed(history_messages)
            if message.role == "assistant" and message.content
        ),
        "",
    )
    return bool(last_assistant_message) and any(
        keyword in last_assistant_message for keyword in _COURSE_DISAMBIGUATION_KEYWORDS
    )


def _should_handle_course_merge_locally(
    user_message: str,
    history_messages: list[ConversationMessage],
) -> bool:
    compact_message = (user_message or "").strip().lower().replace(" ", "")
    if not compact_message:
        return False
    if any(keyword in compact_message for keyword in _SCHEDULE_IMPORT_KEYWORDS):
        return False

    merge_keywords = ("优化成一门", "合并成一门", "还是两门课", "重复课程", "重复的课")
    if any(keyword in compact_message for keyword in merge_keywords):
        return True
    return _is_course_followup_message(user_message, history_messages)


def _match_courses_from_text(user_text: str, courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for course in courses:
        course_name = str(course.get("name") or "").strip()
        if course_name and course_name in user_text:
            matches.append(course)
    return matches


def _build_course_merge_plan(courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for course in courses:
        key = (
            course.get("weekday"),
            course.get("start_time"),
            course.get("end_time"),
            course.get("location") or "",
            course.get("week_start"),
            course.get("week_end"),
            course.get("week_pattern") or "all",
        )
        grouped.setdefault(key, []).append(course)

    plans: list[dict[str, Any]] = []
    for (weekday, start_time, end_time, location, week_start, week_end, week_pattern), group in grouped.items():
        if len(group) < 2:
            continue

        distinct_names = sorted({str(course.get("name") or "").strip() for course in group if course.get("name")})
        if not distinct_names:
            continue
        canonical_name = max(distinct_names, key=lambda value: (len(value), value))
        keeper_candidates = sorted(
            group,
            key=lambda course: (
                str(course.get("name") or "").strip() != canonical_name,
                str(course.get("id") or ""),
            ),
        )
        keeper = keeper_candidates[0]
        delete_ids = [
            str(course.get("id") or "")
            for course in group
            if str(course.get("id") or "") != str(keeper.get("id") or "")
        ]
        rename_to = canonical_name if str(keeper.get("name") or "").strip() != canonical_name else None
        if not delete_ids and rename_to is None:
            continue

        plans.append(
            {
                "weekday": weekday,
                "start_time": start_time,
                "end_time": end_time,
                "location": location or None,
                "week_start": week_start,
                "week_end": week_end,
                "week_pattern": week_pattern,
                "current_names": distinct_names,
                "keep_course_id": str(keeper.get("id") or ""),
                "keep_name": canonical_name,
                "rename_to": rename_to,
                "delete_ids": delete_ids,
            }
        )

    return sorted(
        plans,
        key=lambda item: (
            item.get("weekday") or 999,
            str(item.get("start_time") or ""),
            str(item.get("end_time") or ""),
            str(item.get("week_pattern") or ""),
            str(item.get("keep_name") or ""),
        ),
    )


def _is_confirmed_answer(answer: str) -> bool:
    normalized = (answer or "").strip().lower()
    if not normalized:
        return False
    negative_prefixes = ("不", "先不", "取消", "等等", "no")
    if any(normalized.startswith(prefix) for prefix in negative_prefixes):
        return False
    positive_prefixes = ("确认", "好", "可以", "行", "是", "yes", "ok")
    return any(normalized.startswith(prefix) for prefix in positive_prefixes)


async def _run_course_merge_shortcut(
    user_message: str,
    user: User,
    session_id: str,
    db: AsyncSession,
    history_messages: list[ConversationMessage],
) -> AsyncGenerator[dict[str, Any], str | None]:
    selected_names_text = user_message
    if not _is_course_followup_message(user_message, history_messages):
        selected_names_text = yield {
            "type": "ask_user",
            "ask_type": "review",
            "question": "你想合并的是哪两门课？请直接把课程名发给我，我来按当前课表里的记录帮你收口。",
            "options": [],
            "data": None,
        }
        selected_names_text = (selected_names_text or "").strip()
        if not selected_names_text:
            message_id = str(uuid.uuid4())
            text = "好的，等你把要合并的课程名发给我后，我再帮你处理。"
            yield {"type": "text", "message_id": message_id, "content": text}
            await _save_message(db, session_id, "assistant", text)
            yield {"type": "done"}
            return

    yield {"type": "tool_call", "name": "list_courses", "args": {}}
    list_result = await execute_tool("list_courses", {}, db, user.id)
    yield {"type": "tool_result", "name": "list_courses", "result": list_result}
    await _save_message(
        db,
        session_id,
        "assistant",
        _to_persisted_tool_summary("list_courses", compress_tool_result("list_courses", list_result)),
        is_compressed=True,
    )
    await _log_step(db, user.id, session_id, 1, "list_courses", {}, list_result)

    matched_courses = _match_courses_from_text(selected_names_text, list_result.get("courses", []))
    merge_plan = _build_course_merge_plan(matched_courses)
    if not merge_plan:
        message_id = str(uuid.uuid4())
        text = "我先查了当前课表，但还没定位到可以直接合并的重复记录。你可以把要保留的课程名再明确发我一次。"
        yield {"type": "text", "message_id": message_id, "content": text}
        await _save_message(db, session_id, "assistant", text)
        yield {"type": "done"}
        return

    review_data = {
        "plans": [
            {
                "weekday": item["weekday"],
                "start_time": item["start_time"],
                "end_time": item["end_time"],
                "location": item["location"],
                "week_start": item["week_start"],
                "week_end": item["week_end"],
                "week_pattern": item["week_pattern"],
                "current_names": item["current_names"],
                "keep_name": item["keep_name"],
                "delete_count": len(item["delete_ids"]),
            }
            for item in merge_plan
        ],
        "count": len(merge_plan),
    }
    confirm_answer = yield {
        "type": "ask_user",
        "ask_type": "review",
        "question": "我准备把这些重复课程合并成每个时段 1 条记录。确认后我就直接处理。",
        "options": ["确认", "取消"],
        "data": review_data,
    }
    if not _is_confirmed_answer(str(confirm_answer or "")):
        message_id = str(uuid.uuid4())
        text = "好的，我先不改。你后面想继续的话，直接告诉我保留哪个课程名就行。"
        yield {"type": "text", "message_id": message_id, "content": text}
        await _save_message(db, session_id, "assistant", text)
        yield {"type": "done"}
        return

    step = 1
    for item in merge_plan:
        rename_to = item.get("rename_to")
        keep_course_id = str(item.get("keep_course_id") or "")
        if rename_to and keep_course_id:
            update_args = {"course_id": keep_course_id, "name": rename_to}
            yield {"type": "tool_call", "name": "update_course", "args": update_args}
            update_result = await execute_tool("update_course", update_args, db, user.id)
            yield {"type": "tool_result", "name": "update_course", "result": update_result}
            step += 1
            await _save_message(
                db,
                session_id,
                "assistant",
                _to_persisted_tool_summary("update_course", compress_tool_result("update_course", update_result)),
                is_compressed=True,
            )
            await _log_step(db, user.id, session_id, step, "update_course", update_args, update_result)

        for course_id in item.get("delete_ids", []):
            delete_args = {"course_id": course_id}
            yield {"type": "tool_call", "name": "delete_course", "args": delete_args}
            delete_result = await execute_tool("delete_course", delete_args, db, user.id)
            yield {"type": "tool_result", "name": "delete_course", "result": delete_result}
            step += 1
            await _save_message(
                db,
                session_id,
                "assistant",
                _to_persisted_tool_summary("delete_course", compress_tool_result("delete_course", delete_result)),
                is_compressed=True,
            )
            await _log_step(db, user.id, session_id, step, "delete_course", delete_args, delete_result)

    merged_names = "、".join(dict.fromkeys(item["keep_name"] for item in merge_plan))
    message_id = str(uuid.uuid4())
    text = f"已经帮你把重复课程合并好了，当前保留的是：{merged_names}。"
    yield {"type": "text", "message_id": message_id, "content": text}
    await _save_message(db, session_id, "assistant", text)
    yield {"type": "done"}


async def run_agent_loop(
    user_message: str,
    user: User,
    session_id: str,
    db: AsyncSession,
    llm_client: AsyncOpenAI,
) -> AsyncGenerator[dict[str, Any], str | None]:
    """Run the agent loop and yield frontend events."""
    system_prompt = await build_system_prompt(user, db)

    history_result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.timestamp)
    )
    history_messages = history_result.scalars().all()

    messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    for message in history_messages:
        messages.append({"role": message.role, "content": message.content})

    course_routing_hint = _build_course_routing_hint(user_message, history_messages)
    if course_routing_hint:
        messages.append({"role": "system", "content": course_routing_hint})

    messages.append({"role": "user", "content": user_message})
    await _save_message(db, session_id, "user", user_message)

    if _should_handle_course_merge_locally(user_message, history_messages):
        shortcut = _run_course_merge_shortcut(user_message, user, session_id, db, history_messages)
        try:
            event = await shortcut.__anext__()
            while True:
                if event["type"] == "ask_user":
                    user_response = yield event
                    event = await shortcut.asend(user_response)
                else:
                    yield event
                    event = await shortcut.__anext__()
        except StopAsyncIteration:
            pass
        return

    tool_history: list[str] = []
    error_count: dict[str, int] = {}
    step = 0

    for iteration in range(MAX_ITERATIONS):
        check_max_loop_iterations(iteration, MAX_ITERATIONS)
        response: dict[str, Any] | None = None
        response_message_id = str(uuid.uuid4())
        streamed_deltas: list[str] = []
        try:
            async for stream_event in chat_completion_stream(
                llm_client,
                messages,
                tools=TOOL_DEFINITIONS,
            ):
                event_type = stream_event.get("type")
                if event_type == "content_delta":
                    delta = str(stream_event.get("delta") or "")
                    if not delta:
                        continue
                    streamed_deltas.append(delta)
                    continue

                if event_type == "response":
                    response = stream_event.get("response")
        except Exception:
            if streamed_deltas:
                raise
            response = await chat_completion(llm_client, messages, tools=TOOL_DEFINITIONS)
            response_message_id = str(uuid.uuid4())

        if response is None:
            raise RuntimeError("chat completion stream finished without a response payload")

        if "tool_calls" not in response:
            text = response.get("content", "") or "".join(streamed_deltas)
            if text:
                for delta in streamed_deltas:
                    yield {
                        "type": "text_delta",
                        "message_id": response_message_id,
                        "delta": delta,
                    }
                yield {
                    "type": "text",
                    "message_id": response_message_id,
                    "content": text,
                }
                await _save_message(db, session_id, "assistant", text)
            yield {"type": "done"}
            return

        messages.append(response)

        for tool_call in response["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args_str = tool_call["function"]["arguments"]
            tool_call_id = tool_call["id"]

            try:
                tool_args = json.loads(tool_args_str)
            except json.JSONDecodeError:
                tool_args = {}

            try:
                check_unknown_tool(tool_name, KNOWN_TOOLS)
                if tool_name == "ask_user":
                    check_consecutive_ask_user(tool_history + [tool_name])
                else:
                    check_consecutive_ask_user(tool_history)
                check_max_retries(tool_name, error_count)
            except GuardrailViolation as exc:
                tool_result = {"error": exc.message, "suggestion": exc.suggestion}
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )
                if exc.user_visible:
                    yield {"type": "error", "message": exc.message}
                continue

            yield {"type": "tool_call", "name": tool_name, "args": tool_args}

            if tool_name == "ask_user":
                result = await execute_tool(tool_name, tool_args, db, user.id)
                ask_type = _normalize_ask_type(result)
                user_response = yield {**result, "type": "ask_user", "ask_type": ask_type}
                if user_response is None:
                    user_response = "纭"
                tool_result_content = json.dumps({"user_response": user_response}, ensure_ascii=False)
            else:
                result = await execute_tool(tool_name, tool_args, db, user.id)
                tool_result_content = compress_tool_result(tool_name, result)
                if "error" in result:
                    error_count[tool_name] = error_count.get(tool_name, 0) + 1
                yield {"type": "tool_result", "name": tool_name, "result": result}
                await _save_message(
                    db,
                    session_id,
                    "assistant",
                    _to_persisted_tool_summary(tool_name, tool_result_content),
                    is_compressed=True,
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_result_content,
                }
            )

            step += 1
            tool_history.append(tool_name)
            await _log_step(db, user.id, session_id, step, tool_name, tool_args, result)

    yield {"type": "error", "message": "Agent loop reached the maximum number of iterations."}
    yield {"type": "done"}


async def _save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    *,
    is_compressed: bool = False,
) -> None:
    message = ConversationMessage(
        session_id=session_id,
        role=role,
        content=content,
        is_compressed=is_compressed,
    )
    db.add(message)
    await db.commit()


async def _log_step(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    step: int,
    tool_name: str,
    tool_args: dict[str, Any],
    tool_result: dict[str, Any],
) -> None:
    log = AgentLog(
        user_id=user_id,
        session_id=session_id,
        step=step,
        tool_called=tool_name,
        tool_args=tool_args,
        tool_result=tool_result,
    )
    db.add(log)
    await db.commit()
