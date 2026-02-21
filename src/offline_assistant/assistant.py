from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .intent_resolver import IntentResolver
from .router import CommandRouter
from .models import IntentResult


@dataclass
class AssistantResponse:
    intent: str
    parameters: dict
    message: str


class OfflineAssistant:
    """High-level orchestration for one-turn memory and deterministic routing."""

    def __init__(self, resolver: IntentResolver, router: CommandRouter) -> None:
        self.resolver = resolver
        self.router = router
        self._pending_file_result: Optional[str] = None

    def handle_transcript(self, transcript: str, wake_word: str | None = None) -> AssistantResponse | None:
        intent = self.resolver.resolve(transcript, wake_word=wake_word)
        if intent is None:
            return None

        intent = self._resolve_short_term_references(intent)
        message = self.router.route(intent)

        # One-turn context: valid only for the immediately next interaction.
        if intent.intent == "file_find" and message not in {"Not found.", "Which file?"}:
            self._pending_file_result = message
        else:
            self._pending_file_result = None

        return AssistantResponse(intent=intent.intent, parameters=intent.parameters, message=message)

    def _resolve_short_term_references(self, intent: IntentResult) -> IntentResult:
        if intent.intent == "file_open_last":
            if self._pending_file_result:
                remembered_path = self._pending_file_result
                self._pending_file_result = None
                return IntentResult("file_open", {"path": remembered_path})
            return IntentResult("unknown", {})
        return intent
