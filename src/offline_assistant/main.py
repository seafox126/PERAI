from __future__ import annotations

import json
import os
from pathlib import Path

from .assistant import OfflineAssistant
from .intent_resolver import IntentResolver
from .modules.calendar_module import CalendarModule
from .modules.email_module import EmailModule
from .modules.file_module import FileModule
from .modules.music_module import MusicModule
from .modules.system_module import SystemModule
from .router import CommandRouter


def build_assistant(data_dir: Path, file_index_root: Path | None = None) -> OfflineAssistant:
    resolver = IntentResolver(
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        ollama_url=os.getenv("OLLAMA_URL", "http://127.0.0.1:11434"),
    )
    router = CommandRouter(
        calendar_module=CalendarModule(data_dir / "calendar.json"),
        music_module=MusicModule(Path(os.getenv("MUSIC_DIR", str(Path.home() / "Music")))),
        file_module=FileModule(
            data_dir / "file_index.db",
            file_index_root or Path(os.getenv("FILE_INDEX_ROOT", str(Path.cwd()))),
        ),
        email_module=EmailModule(
            os.getenv("EMAIL_IMAP_HOST"),
            os.getenv("EMAIL_USERNAME"),
            os.getenv("EMAIL_APP_PASSWORD"),
        ),
        system_module=SystemModule(),
    )
    return OfflineAssistant(resolver=resolver, router=router)


def run_cli() -> None:
    data_dir = Path(os.getenv("ASSISTANT_DATA_DIR", "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    assistant = build_assistant(data_dir)
    wake_word = os.getenv("WAKE_WORD")

    print("Offline assistant ready. Type 'exit' to quit.")
    while True:
        text = input("> ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        result = assistant.handle_transcript(text, wake_word=wake_word)
        if result is None:
            print("null")
            continue
        print(json.dumps({"intent": result.intent, "parameters": result.parameters, "message": result.message}))


if __name__ == "__main__":
    run_cli()
