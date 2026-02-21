from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4


class CalendarModule:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def execute(self, parameters: dict) -> str:
        action = parameters.get("action")
        if action == "add":
            return self._add(parameters)
        if action == "list":
            events = self._read()
            if not events:
                return "No events."
            return " | ".join(f"{e['title']} @ {e['when']}" for e in events)
        if action == "remove":
            title = parameters.get("title", "")
            events = self._read()
            kept = [e for e in events if e["title"].lower() != str(title).lower()]
            self._write(kept)
            return "Event removed." if len(kept) != len(events) else "Not found."
        return "Unknown calendar action."

    def _add(self, parameters: dict) -> str:
        title = str(parameters.get("title", "")).strip()
        when = str(parameters.get("when", "")).strip()
        if not title or not when:
            return "Need title and date."
        events = self._read()
        events.append({"id": str(uuid4()), "title": title, "when": when})
        self._write(events)
        return "Event added."

    def _read(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, payload: list[dict]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
