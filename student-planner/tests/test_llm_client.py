from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.llm_client import chat_completion, create_llm_client
from app.config import settings


def test_create_llm_client_uses_settings():
    client = create_llm_client()

    assert str(client.base_url) == f"{settings.llm_base_url}/"
    assert client.api_key == settings.llm_api_key


@pytest.mark.asyncio
async def test_chat_completion_text_response():
    mock_message = MagicMock()
    mock_message.content = "你好！有什么可以帮你的？"
    mock_message.tool_calls = None

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await chat_completion(mock_client, [{"role": "user", "content": "你好"}])

    assert result["role"] == "assistant"
    assert result["content"] == "你好！有什么可以帮你的？"
    assert "tool_calls" not in result


@pytest.mark.asyncio
async def test_chat_completion_tool_call():
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_123"
    mock_tool_call.function.name = "list_courses"
    mock_tool_call.function.arguments = "{}"

    mock_message = MagicMock()
    mock_message.content = None
    mock_message.tool_calls = [mock_tool_call]

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await chat_completion(
        mock_client,
        [{"role": "user", "content": "我有什么课"}],
        tools=[{"type": "function", "function": {"name": "list_courses"}}],
    )

    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["function"]["name"] == "list_courses"
