from typing import Any, cast

import anthropic
from anthropic.types import MessageParam

from app.config import settings

_MODEL = "claude-sonnet-5"


class AssistantNotConfiguredError(Exception):
    pass


def ask_claude(system: str, content: str | list[dict[str, Any]]) -> str:
    """Sends one message to Claude and returns its text reply.

    Stateless by design (Phase 7a) -- no persisted conversation history,
    one question in, one answer out. Raises AssistantNotConfiguredError
    if no API key is set, rather than silently failing on the API call.
    """
    if not settings.anthropic_api_key:
        raise AssistantNotConfiguredError

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=system,
        messages=[cast(MessageParam, {"role": "user", "content": content})],
    )
    return "".join(block.text for block in message.content if block.type == "text")
