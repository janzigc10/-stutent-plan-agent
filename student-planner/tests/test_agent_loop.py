from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.agent.loop import run_agent_loop
from app.models.conversation_message import ConversationMessage
from app.models.course import Course
from app.models.user import User
from tests.conftest import TestSession


def stream_response_chunks(*, response: dict, deltas: list[str] | None = None):
    async def _generator():
        for delta in deltas or []:
            yield {"type": "content_delta", "delta": delta}
        yield {"type": "response", "response": response}

    return _generator()


@pytest.mark.asyncio
async def test_simple_text_response(setup_db):
    """LLM returns text without tool calls and loop ends immediately."""
    mock_client = AsyncMock()

    with patch("app.agent.loop.chat_completion_stream") as mock_chat_completion_stream:
        mock_chat_completion_stream.return_value = stream_response_chunks(
            response={"role": "assistant", "content": "Hello there."},
            deltas=["Hello ", "there."],
        )

        async with TestSession() as db:
            user = User(id="u1", username="test", hashed_password="x")
            db.add(user)
            await db.commit()

            events = []
            generator = run_agent_loop("hi", user, "session-1", db, mock_client)
            async for event in generator:
                events.append(event)

            assert any(event["type"] == "text_delta" for event in events)
            assert any(event["type"] == "text" for event in events)
            assert any(event["type"] == "done" for event in events)
            text_event = next(event for event in events if event["type"] == "text")
            assert text_event["content"] == "Hello there."


@pytest.mark.asyncio
async def test_tool_call_then_text(setup_db):
    """LLM calls a tool, gets result, then responds with text."""
    mock_client = AsyncMock()
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
                            "function": {"name": "list_courses", "arguments": "{}"},
                        }
                    ],
                }
            )
        return stream_response_chunks(
            response={"role": "assistant", "content": "You currently have no courses."},
            deltas=["You currently ", "have no courses."],
        )

    with patch("app.agent.loop.chat_completion_stream", side_effect=mock_chat_completion_stream):
        async with TestSession() as db:
            user = User(id="u2", username="test2", hashed_password="x")
            db.add(user)
            await db.commit()

            events = []
            generator = run_agent_loop("what courses", user, "session-2", db, mock_client)
            async for event in generator:
                events.append(event)

            types = [event["type"] for event in events]
            assert "tool_call" in types
            assert "tool_result" in types
            assert "text_delta" in types
            assert "text" in types
            assert "done" in types


@pytest.mark.asyncio
async def test_streamed_text_emits_delta_before_final_text(setup_db):
    mock_client = AsyncMock()

    with patch("app.agent.loop.chat_completion_stream") as mock_chat_completion_stream:
        mock_chat_completion_stream.return_value = stream_response_chunks(
            response={"role": "assistant", "content": "Streaming works."},
            deltas=["Streaming ", "works."],
        )

        async with TestSession() as db:
            user = User(id="u2b", username="test2b", hashed_password="x")
            db.add(user)
            await db.commit()

            events = []
            generator = run_agent_loop("check stream", user, "session-2b", db, mock_client)
            async for event in generator:
                events.append(event)

            first_delta_index = next(i for i, event in enumerate(events) if event["type"] == "text_delta")
            final_text_index = next(i for i, event in enumerate(events) if event["type"] == "text")
            assert first_delta_index < final_text_index
            assert events[final_text_index]["content"] == "Streaming works."


@pytest.mark.asyncio
async def test_ask_user_event_preserves_event_type(setup_db):
    """ask_user events expose event type separately from confirm/select/review mode."""
    mock_client = AsyncMock()
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
                                "name": "ask_user",
                                "arguments": '{"question": "Confirm?", "type": "confirm", "options": ["Yes", "No"]}',
                            },
                        }
                    ],
                }
            )
        return stream_response_chunks(response={"role": "assistant", "content": "Continue."})

    with patch("app.agent.loop.chat_completion_stream", side_effect=mock_chat_completion_stream):
        async with TestSession() as db:
            user = User(id="u3", username="test3", hashed_password="x")
            db.add(user)
            await db.commit()

            generator = run_agent_loop("help me", user, "session-3", db, mock_client)
            event = await generator.__anext__()
            assert event["type"] == "tool_call"

            ask_event = await generator.__anext__()
            assert ask_event["type"] == "ask_user"
            assert ask_event["ask_type"] == "confirm"


@pytest.mark.asyncio
async def test_ask_user_without_options_or_data_defaults_to_review(setup_db):
    """ask_user confirm without options/data should degrade to free-text review mode."""
    mock_client = AsyncMock()
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
                                "name": "ask_user",
                                "arguments": '{"question": "Provide period times", "type": "confirm"}',
                            },
                        }
                    ],
                }
            )
        return stream_response_chunks(response={"role": "assistant", "content": "Received."})

    with patch("app.agent.loop.chat_completion_stream", side_effect=mock_chat_completion_stream):
        async with TestSession() as db:
            user = User(id="u4", username="test4", hashed_password="x")
            db.add(user)
            await db.commit()

            generator = run_agent_loop("help me", user, "session-4", db, mock_client)
            event = await generator.__anext__()
            assert event["type"] == "tool_call"

            ask_event = await generator.__anext__()
            assert ask_event["type"] == "ask_user"
            assert ask_event["ask_type"] == "review"


@pytest.mark.asyncio
async def test_continue_message_can_reuse_persisted_list_course_summary(setup_db):
    mock_client = AsyncMock()
    llm_call_count = 0
    session_id = "session-delete-continue"
    target_course_id = "course-target"

    def mock_chat_completion_stream(client, messages, tools=None):
        nonlocal llm_call_count
        llm_call_count += 1
        if llm_call_count == 1:
            return stream_response_chunks(
                response={
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_list",
                            "type": "function",
                            "function": {"name": "list_courses", "arguments": "{}"},
                        }
                    ],
                }
            )
        if llm_call_count == 2:
            return stream_response_chunks(
                response={"role": "assistant", "content": "Found matching course options."},
                deltas=["Found matching ", "course options."],
            )
        if llm_call_count == 3:
            summaries = [
                str(message.get("content") or "")
                for message in messages
                if message.get("role") == "assistant"
                and str(message.get("content") or "").startswith("[TOOL_SUMMARY:list_courses:v1] ")
            ]
            assert summaries, "second turn did not include list_courses summary"
            latest_summary = summaries[-1]
            assert target_course_id in latest_summary
            assert "Hall-305" in latest_summary
            return stream_response_chunks(
                response={
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_delete",
                            "type": "function",
                            "function": {
                                "name": "delete_course",
                                "arguments": '{"course_id": "course-target"}',
                            },
                        }
                    ],
                }
            )
        return stream_response_chunks(
            response={"role": "assistant", "content": "Deleted the Hall-305 course."},
            deltas=["Deleted ", "the Hall-305 course."],
        )

    with patch("app.agent.loop.chat_completion_stream", side_effect=mock_chat_completion_stream):
        async with TestSession() as db:
            user = User(id="u6", username="test6", hashed_password="x")
            db.add(user)
            db.add_all(
                [
                    Course(
                        id=target_course_id,
                        user_id="u6",
                        name="NLP",
                        location="Hall-305",
                        weekday=3,
                        start_time="08:30",
                        end_time="10:05",
                    ),
                    Course(
                        id="course-other",
                        user_id="u6",
                        name="NLP",
                        location="Hall-324",
                        weekday=4,
                        start_time="08:30",
                        end_time="10:05",
                    ),
                ]
            )
            await db.commit()

            first_round_events = []
            generator = run_agent_loop(
                "Please delete NLP in Hall-305",
                user,
                session_id,
                db,
                mock_client,
            )
            async for event in generator:
                first_round_events.append(event)

            second_round_events = []
            generator = run_agent_loop("continue", user, session_id, db, mock_client)
            async for event in generator:
                second_round_events.append(event)

            first_types = [event["type"] for event in first_round_events]
            assert first_types[:2] == ["tool_call", "tool_result"]
            assert "text_delta" in first_types
            assert first_types[-2:] == ["text", "done"]

            second_types = [event["type"] for event in second_round_events]
            assert "tool_call" in second_types
            delete_call = next(
                event
                for event in second_round_events
                if event["type"] == "tool_call" and event["name"] == "delete_course"
            )
            assert delete_call["args"] == {"course_id": target_course_id}

            message_result = await db.execute(
                select(ConversationMessage)
                .where(ConversationMessage.session_id == session_id)
                .order_by(ConversationMessage.timestamp)
            )
            stored_messages = list(message_result.scalars().all())
            persisted_summaries = [
                message
                for message in stored_messages
                if message.role == "assistant"
                and message.is_compressed
                and message.content.startswith("[TOOL_SUMMARY:list_courses:v1] ")
            ]
            assert persisted_summaries