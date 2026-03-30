"""Test that the agent loop compresses tool results in conversation history."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.loop import run_agent_loop
from app.models.user import User


@pytest.mark.asyncio
async def test_loop_compresses_large_tool_result(setup_db):
    from tests.conftest import TestSession

    async with TestSession() as db:
        user = User(id="loop-comp-1", username="loopcomp", hashed_password="x")
        db.add(user)
        await db.commit()

        large_result = {
            "slots": [
                {
                    "date": f"2026-04-{day:02d}",
                    "weekday": "周一",
                    "free_periods": [
                        {"start": "08:00", "end": "22:00", "duration_minutes": 840}
                    ],
                    "occupied": [],
                }
                for day in range(1, 8)
            ],
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
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "get_free_slots",
                                "arguments": json.dumps(
                                    {"start_date": "2026-04-01", "end_date": "2026-04-07"}
                                ),
                            },
                        }
                    ],
                }

            tool_message = next(message for message in messages if message.get("role") == "tool")
            content = tool_message["content"]
            assert "free_periods" not in content
            assert "7 个空闲段" in content
            return {"role": "assistant", "content": "已经整理好了这段空闲时间。"}

        with patch("app.agent.loop.chat_completion", side_effect=mock_chat_completion):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                generator = run_agent_loop("帮我看看这周空闲时间", user, "test-session", db, AsyncMock())
                try:
                    event = await generator.__anext__()
                    while True:
                        events.append(event)
                        if event["type"] == "done":
                            break
                        event = await generator.__anext__()
                except StopAsyncIteration:
                    pass

        tool_result_events = [event for event in events if event.get("type") == "tool_result"]
        assert len(tool_result_events) == 1
        assert "slots" in tool_result_events[0]["result"]