from __future__ import annotations

from .types import IntentResult


class CommandRouter:
    def __init__(self, calendar_module, music_module, file_module, email_module, system_module) -> None:
        self.calendar_module = calendar_module
        self.music_module = music_module
        self.file_module = file_module
        self.email_module = email_module
        self.system_module = system_module

    def route(self, intent: IntentResult) -> str:
        if intent.intent == "wake_acknowledge":
            return "Listening."

        if intent.intent == "calendar_add_event":
            return self.calendar_module.execute({"action": "add", **intent.parameters})
        if intent.intent == "calendar_list_events":
            return self.calendar_module.execute({"action": "list"})
        if intent.intent == "calendar_remove_event":
            return self.calendar_module.execute({"action": "remove", **intent.parameters})

        if intent.intent == "music_play":
            return self.music_module.execute(intent.parameters)

        if intent.intent == "file_index":
            return self.file_module.execute({"action": "index"})
        if intent.intent == "file_find":
            return self.file_module.execute({"action": "find", **intent.parameters})
        if intent.intent == "file_open":
            return self.file_module.execute({"action": "open", **intent.parameters})

        if intent.intent == "email_unread":
            return self.email_module.execute(intent.parameters)

        if intent.intent == "system_action":
            return self.system_module.execute(intent.parameters)

        return "Unknown intent."
