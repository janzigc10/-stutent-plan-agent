"""Test that the agent loop compresses tool results in conversation history."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.loop import run_agent_loop
from app.models.user import User


def stream_response_chunks(*, response: dict, deltas: list[str] | None = None):
    async def _generator():
        for delta in deltas or []:
            yield {"type": "content_delta", "delta": delta}
        yield {"type": "response", "response": response}

    return _generator()


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
                    "weekday": "Monday",
                    "free_periods": [
                        {"start": "08:00", "end": "22:00", "duration_minutes": 840}
                    ],
                    "occupied": [],
                }
                for day in range(1, 8)
            ],
            "summary": "7 free slots, 98 hours total",
        }

        call_count = 0

        def mock_chat_completion_stream(client, messages, tools=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return stream_response_chunks(
                    response={
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
                )

            tool_message = next(message for message in messages if message.get("role") == "tool")
            content = tool_message["content"]
            assert "free_periods" not in content
            assert "7" in content
            return stream_response_chunks(
                response={"role": "assistant", "content": "Summarized your availability."},
                deltas=["Summarized ", "your availability."],
            )

        with patch("app.agent.loop.chat_completion_stream", side_effect=mock_chat_completion_stream):
            with patch("app.agent.loop.execute_tool", new_callable=AsyncMock, return_value=large_result):
                events = []
                generator = run_agent_loop("check this week's availability", user, "test-session", db, AsyncMock())
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