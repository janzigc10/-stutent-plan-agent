"""Parse schedule screenshots with a vision-capable LLM."""

from __future__ import annotations

import base64
import json
import re
from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.services.schedule_parser import RawCourse

_WEEK_RANGE_RE = re.compile(r"(\d+)\s*-\s*(\d+)\s*周")
_PERIOD_RANGE_RE = re.compile(r"(\d{1,2})\s*[-~～—–]\s*(\d{1,2})")
_WEEKDAY_TEXT_MAP = {
    "周一": 1,
    "星期一": 1,
    "周二": 2,
    "星期二": 2,
    "周三": 3,
    "星期三": 3,
    "周四": 4,
    "星期四": 4,
    "周五": 5,
    "星期五": 5,
    "周六": 6,
    "星期六": 6,
    "周日": 7,
    "周天": 7,
    "星期日": 7,
    "星期天": 7,
}

_PROMPT = (
    "这是一张大学课表的照片或截图。请提取所有课程信息，输出 JSON 数组。"
    "每个对象包含 name、teacher、location、weekday、period、weeks。"
    "weekday 使用 1-7（周一=1），period 使用字符串格式如 1-2（不要返回数组）。"
    "只输出 JSON 数组；如果不是课表或无法识别，输出 []。"
)


async def parse_schedule_image(image_bytes: bytes, mime_type: str) -> list[RawCourse]:
    response = await _vision_completion(image_bytes, mime_type)
    content = (response or {}).get("content")
    raw_items = _extract_json_array(content)
    if not raw_items:
        return []

    courses: list[RawCourse] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        weekday = _normalize_weekday(item.get("weekday"))
        period = _normalize_period(item.get("period"))
        if not name or weekday is None or period is None:
            continue
        week_start, week_end = _parse_weeks(item.get("weeks"))
        courses.append(
            RawCourse(
                name=str(name),
                teacher=_optional_str(item.get("teacher")),
                location=_optional_str(item.get("location")),
                weekday=weekday,
                period=period,
                week_start=week_start,
                week_end=week_end,
            )
        )
    return courses


async def _vision_completion(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    client = AsyncOpenAI(
        api_key=settings.vision_llm_api_key or settings.llm_api_key,
        base_url=settings.vision_llm_base_url or settings.llm_base_url,
    )
    encoded = base64.b64encode(image_bytes).decode("ascii")
    response = await client.chat.completions.create(
        model=settings.vision_llm_model,
        messages=[
            {"role": "system", "content": _PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请识别这张课表图片。"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                    },
                ],
            },
        ],
        max_tokens=settings.llm_max_tokens,
        temperature=0,
    )
    message = response.choices[0].message
    return {"role": "assistant", "content": message.content}


def _parse_weeks(weeks: Any) -> tuple[int, int]:
    if not weeks:
        return 1, 16
    match = _WEEK_RANGE_RE.search(str(weeks))
    if match is None:
        return 1, 16
    return int(match.group(1)), int(match.group(2))


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_json_array(content: Any) -> list[dict[str, Any]]:
    if content is None:
        return []

    text = str(content).strip()
    if not text:
        return []

    candidates = [text]
    if text.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        candidates.append(cleaned.strip())

    first_bracket = text.find("[")
    last_bracket = text.rfind("]")
    if first_bracket != -1 and last_bracket != -1 and first_bracket < last_bracket:
        candidates.append(text[first_bracket:last_bracket + 1].strip())

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]

    return []


def _normalize_weekday(value: Any) -> int | None:
    if isinstance(value, int) and 1 <= value <= 7:
        return value

    text = _optional_str(value)
    if text is None:
        return None

    if text.isdigit():
        numeric = int(text)
        if 1 <= numeric <= 7:
            return numeric
        return None

    return _WEEKDAY_TEXT_MAP.get(text)


def _normalize_period(value: Any) -> str | None:
    if isinstance(value, (list, tuple)) and len(value) == 2:
        try:
            start = int(value[0])
            end = int(value[1])
        except (TypeError, ValueError):
            return None
        if start <= 0 or end <= 0:
            return None
        low, high = sorted((start, end))
        return f"{low}-{high}"

    text = _optional_str(value)
    if text is None:
        return None

    normalized = (
        text.replace("第", "")
        .replace("节", "")
        .replace(" ", "")
        .replace("—", "-")
        .replace("–", "-")
        .replace("~", "-")
        .replace("～", "-")
    )
    match = _PERIOD_RANGE_RE.search(normalized)
    if match is None:
        return None

    start = int(match.group(1))
    end = int(match.group(2))
    low, high = sorted((start, end))
    return f"{low}-{high}"
