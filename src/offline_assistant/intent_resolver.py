from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

from .types import IntentResult


class IntentResolver:
    def __init__(self, ollama_model: str = "llama3.1:8b", ollama_url: str = "http://127.0.0.1:11434") -> None:
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url.rstrip("/")

    def resolve(self, transcript: str, wake_word: str | None = None) -> IntentResult | None:
        text = transcript.strip().lower()
        if not text:
            return None

        if wake_word:
            ww = wake_word.strip().lower()
            if text == ww:
                return IntentResult("wake_acknowledge", {})
            if text.startswith(f"{ww} "):
                text = text[len(ww) :].strip()
                if not text:
                    return IntentResult("wake_acknowledge", {})

        deterministic = self._deterministic(text)
        if deterministic:
            return deterministic

        return self._ollama_fallback(text)

    def _deterministic(self, text: str) -> IntentResult | None:
        if text in {"yes?", "go ahead", "listening"}:
            return IntentResult("wake_acknowledge", {})

        add_event = re.match(r"(?:add|create) event (.+?) (?:on|at) (.+)", text)
        if add_event:
            return IntentResult("calendar_add_event", {"title": add_event.group(1), "when": add_event.group(2)})

        if text.startswith("list events"):
            return IntentResult("calendar_list_events", {})

        if text.startswith("remove event "):
            return IntentResult("calendar_remove_event", {"title": text.removeprefix("remove event ").strip()})

        if text.startswith("play "):
            return IntentResult("music_play", {"query": text.removeprefix("play ").strip()})

        if text.startswith("find file "):
            return IntentResult("file_find", {"query": text.removeprefix("find file ").strip()})

        if text.startswith("index files"):
            return IntentResult("file_index", {})

        if text in {"open it", "open last file", "open that file"}:
            return IntentResult("file_open_last", {})

        if text in {"read unread emails", "read unread email"}:
            return IntentResult("email_unread", {})

        if text in {"shutdown", "restart", "lock"}:
            return IntentResult("system_action", {"action": text})

        return None

    def _ollama_fallback(self, text: str) -> IntentResult:
        prompt = (
            "Extract intent and parameters as strict JSON with keys intent and parameters. "
            "No prose. Unknown requests must return {\"intent\":\"unknown\",\"parameters\":{}}.\n"
            f"User text: {text}"
        )
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.ollama_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            raw = body.get("response", "{}")
            if isinstance(raw, dict):
                parsed = raw
            else:
                parsed: dict[str, Any] = json.loads(raw)
            intent = str(parsed.get("intent", "unknown"))
            parameters = parsed.get("parameters", {}) if isinstance(parsed.get("parameters", {}), dict) else {}
            return IntentResult(intent=intent, parameters=parameters)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
            return IntentResult(intent="unknown", parameters={})
