from __future__ import annotations


class SystemModule:
    def execute(self, parameters: dict) -> str:
        action = parameters.get("action")
        if action == "shutdown":
            return "Shutdown queued."
        if action == "restart":
            return "Restart queued."
        if action == "lock":
            return "Locking system."
        return "Unknown system action."
