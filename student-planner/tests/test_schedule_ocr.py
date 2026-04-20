import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.schedule_ocr import parse_schedule_image
from app.services.schedule_parser import RawCourse

MOCK_LLM_RESPONSE = json.dumps(
    {
        "image_week": 3,
        "courses": [
            {
                "name": "高等数学",
                "teacher": "张老师",
                "location": "教学楼A301",
                "weekday": 1,
                "period": "1-2",
                "weeks": "1-16周",
            },
            {
                "name": "线性代数",
                "teacher": "李老师",
                "location": "教学楼B205",
                "weekday": 3,
                "period": "1-2",
                "weeks": "1-16周",
            },
        ],
    },
    ensure_ascii=False,
)


@pytest.mark.asyncio
async def test_parse_image_returns_raw_courses() -> None:
    mock_response = {"role": "assistant", "content": MOCK_LLM_RESPONSE}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png")
    assert len(courses) == 2
    assert all(isinstance(course, RawCourse) for course in courses)


@pytest.mark.asyncio
async def test_parse_image_extracts_fields() -> None:
    mock_response = {"role": "assistant", "content": MOCK_LLM_RESPONSE}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png")
    gaoshu = next(course for course in courses if course.name == "高等数学")
    assert gaoshu.weekday == 1
    assert gaoshu.period == "1-2"
    assert gaoshu.teacher == "张老师"
    assert gaoshu.location == "教学楼A301"
    assert gaoshu.week_start == 1
    assert gaoshu.week_end == 16
    assert gaoshu.week_pattern == "all"
    assert gaoshu.week_text == "第1-16周"


@pytest.mark.asyncio
async def test_parse_image_handles_llm_error() -> None:
    mock_response = {"role": "assistant", "content": "抱歉，我无法识别这张图片"}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png")
    assert courses == []


@pytest.mark.asyncio
async def test_parse_image_handles_missing_weeks() -> None:
    response_data = json.dumps(
        [
            {
                "name": "体育",
                "teacher": None,
                "location": "操场",
                "weekday": 5,
                "period": "7-8",
                "weeks": None,
            }
        ],
        ensure_ascii=False,
    )
    mock_response = {"role": "assistant", "content": response_data}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png")
    assert len(courses) == 1
    assert courses[0].week_start == 1
    assert courses[0].week_end == 18
    assert courses[0].week_pattern == "all"
    assert courses[0].week_text == "第1-18周"


@pytest.mark.asyncio
async def test_parse_image_can_infer_odd_or_even_from_fallback_week_number() -> None:
    response_data = json.dumps(
        [
            {
                "name": "自然语言处理",
                "teacher": "",
                "location": "",
                "weekday": 3,
                "period": "1-2",
                "weeks": "",
            }
        ],
        ensure_ascii=False,
    )
    mock_response = {"role": "assistant", "content": response_data}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png", fallback_week_number=3)
    assert len(courses) == 1
    assert courses[0].week_pattern == "odd"
    assert courses[0].week_text == "第1-18周(单周)"


@pytest.mark.asyncio
async def test_parse_image_can_infer_odd_or_even_from_image_week_field() -> None:
    response_data = json.dumps(
        {
            "image_week": 4,
            "courses": [
                {
                    "name": "机器人流程自动化",
                    "teacher": "",
                    "location": "",
                    "weekday": 3,
                    "period": "3-4",
                    "weeks": "",
                }
            ],
        },
        ensure_ascii=False,
    )
    mock_response = {"role": "assistant", "content": response_data}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png")
    assert len(courses) == 1
    assert courses[0].week_pattern == "even"
    assert courses[0].week_text == "第1-18周(双周)"


@pytest.mark.asyncio
async def test_parse_image_supports_fenced_json_and_array_period() -> None:
    response_data = """```json
[
  {
    "name": "自然语言处理",
    "teacher": "",
    "location": "",
    "weekday": 3,
    "period": [1, 2],
    "weeks": ""
  }
]
```"""
    mock_response = {"role": "assistant", "content": response_data}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png")

    assert len(courses) == 1
    assert courses[0].period == "1-2"
    assert courses[0].weekday == 3


@pytest.mark.asyncio
async def test_parse_image_supports_chinese_weekday_text() -> None:
    response_data = json.dumps(
        [
            {
                "name": "大学生就业指导",
                "teacher": "",
                "location": "",
                "weekday": "周三",
                "period": "第9-10节",
                "weeks": "",
            }
        ],
        ensure_ascii=False,
    )
    mock_response = {"role": "assistant", "content": response_data}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png")

    assert len(courses) == 1
    assert courses[0].weekday == 3
    assert courses[0].period == "9-10"


@pytest.mark.asyncio
async def test_parse_image_supports_odd_even_weeks_text() -> None:
    response_data = json.dumps(
        [
            {
                "name": "机器学习",
                "teacher": "",
                "location": "",
                "weekday": 4,
                "period": "5-6",
                "weeks": "1-18周(双周)",
            }
        ],
        ensure_ascii=False,
    )
    mock_response = {"role": "assistant", "content": response_data}
    with patch(
        "app.agent.schedule_ocr._vision_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        courses = await parse_schedule_image(b"fake-image-bytes", "image/png")

    assert len(courses) == 1
    assert courses[0].week_start == 1
    assert courses[0].week_end == 18
    assert courses[0].week_pattern == "even"
    assert courses[0].week_text == "第1-18周(双周)"
