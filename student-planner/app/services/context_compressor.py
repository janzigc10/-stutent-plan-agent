"""Compression helpers for tool results and long conversation histories."""

import json

from app.agent.llm_client import chat_completion

_SMALL_THRESHOLD = 300
_SUMMARIZE_PROMPT = """请用 1 到 3 句话总结以下较早的对话内容，保留用户做了什么、确认了什么、表达了什么偏好。"""


def compress_tool_result(tool_name: str, result: dict) -> str:
    if "error" in result:
        return json.dumps(result, ensure_ascii=False)

    raw = json.dumps(result, ensure_ascii=False)
    if len(raw) < _SMALL_THRESHOLD:
        return raw

    compressor = _COMPRESSORS.get(tool_name)
    if compressor is not None:
        return compressor(result)

    return raw


async def compress_conversation_history(
    messages: list[dict],
    llm_client,
    max_messages: int = 12,
) -> list[dict]:
    system_messages = [message for message in messages if message.get("role") == "system"]
    conversation_messages = [message for message in messages if message.get("role") != "system"]

    if len(conversation_messages) <= max_messages:
        return messages

    cutoff = len(conversation_messages) - max_messages
    old_messages = conversation_messages[:cutoff]
    recent_messages = conversation_messages[cutoff:]

    old_text = "\n".join(
        f"{message.get('role', 'unknown')}: {message.get('content', '')}"
        for message in old_messages
        if message.get("content")
    )

    try:
        response = await chat_completion(
            llm_client,
            [
                {"role": "system", "content": _SUMMARIZE_PROMPT},
                {"role": "user", "content": old_text},
            ],
        )
        summary = response.get("content") or "早期对话摘要不可用。"
    except Exception:
        summary = "早期对话摘要生成失败。"

    summary_message = {
        "role": "user",
        "content": f"[之前的对话摘要] {summary}",
    }
    return system_messages + [summary_message] + recent_messages


def _compress_get_free_slots(result: dict) -> str:
    summary = result.get("summary")
    if summary:
        return f"[空闲时段查询结果] {summary}"

    slots = result.get("slots", [])
    free_count = sum(len(day.get("free_periods", [])) for day in slots)
    return f"[空闲时段查询结果] {len(slots)} 天，共 {free_count} 个空闲段"


def _compress_list_courses(result: dict) -> str:
    courses = result.get("courses", [])
    count = result.get("count", len(courses))
    names = ", ".join(course.get("name", "") for course in courses[:5] if course.get("name"))
    if names:
        return f"[课程列表] 共 {count} 门课：{names}"
    return f"[课程列表] 共 {count} 门课"


def _compress_list_tasks(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    completed_count = sum(1 for task in tasks if task.get("status") == "completed")
    return f"[任务列表] 共 {count} 个任务，其中 {completed_count} 个已完成"


def _compress_create_study_plan(result: dict) -> str:
    tasks = result.get("tasks", [])
    count = result.get("count", len(tasks))
    titles = ", ".join(task.get("title", "") for task in tasks[:3] if task.get("title"))
    if titles:
        return f"[学习计划] 已生成 {count} 个任务，包含：{titles}"
    return f"[学习计划] 已生成 {count} 个任务"


_COMPRESSORS = {
    "get_free_slots": _compress_get_free_slots,
    "list_courses": _compress_list_courses,
    "list_tasks": _compress_list_tasks,
    "create_study_plan": _compress_create_study_plan,
}