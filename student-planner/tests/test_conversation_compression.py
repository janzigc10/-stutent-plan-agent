from unittest.mock import AsyncMock, patch

import pytest

from app.services.context_compressor import compress_conversation_history


@pytest.mark.asyncio
async def test_compress_short_history_unchanged():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，有什么可以帮你的？"},
    ]
    result = await compress_conversation_history(messages, AsyncMock(), max_messages=10)
    assert result == messages


@pytest.mark.asyncio
async def test_compress_long_history():
    messages = [{"role": "system", "content": "System prompt"}]
    for index in range(20):
        messages.append({"role": "user", "content": f"用户消息 {index}"})
        messages.append({"role": "assistant", "content": f"助手回复 {index}"})

    mock_response = {
        "role": "assistant",
        "content": "之前的对话中，用户发送了很多消息，助手也持续做了回复。",
    }

    with patch(
        "app.services.context_compressor.chat_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System prompt"
    assert any("之前的对话中" in message.get("content", "") for message in result)
    assert len(result) <= 14


@pytest.mark.asyncio
async def test_compress_preserves_recent_messages():
    messages = [{"role": "system", "content": "System prompt"}]
    for index in range(20):
        messages.append({"role": "user", "content": f"消息 {index}"})
        messages.append({"role": "assistant", "content": f"回复 {index}"})

    mock_response = {"role": "assistant", "content": "早期对话摘要"}

    with patch(
        "app.services.context_compressor.chat_completion",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await compress_conversation_history(messages, AsyncMock(), max_messages=12)

    assert result[-1]["content"] == "回复 19"