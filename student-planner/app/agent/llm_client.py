from typing import Any

from openai import AsyncOpenAI

from app.config import settings


def create_llm_client() -> AsyncOpenAI:
    """Create an OpenAI-compatible async client for provider-switched backends."""
    return AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )


async def chat_completion(
    client: AsyncOpenAI,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Call the LLM and normalize the response into a serializable dict."""
    kwargs: dict[str, Any] = {
        "model": settings.llm_model,
        "messages": messages,
        "max_tokens": settings.llm_max_tokens,
        "temperature": settings.llm_temperature,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = await client.chat.completions.create(**kwargs)
    message = response.choices[0].message

    result: dict[str, Any] = {"role": "assistant", "content": message.content}
    if message.tool_calls:
        result["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in message.tool_calls
        ]

    return result