from __future__ import annotations

import json
from pathlib import Path

from offline_assistant.main import build_assistant


def test_calendar_roundtrip(tmp_path: Path) -> None:
    assistant = build_assistant(tmp_path, file_index_root=tmp_path)

    add = assistant.handle_transcript("add event demo at friday 9am")
    assert add is not None
    assert add.intent == "calendar_add_event"
    assert add.message == "Event added."

    listing = assistant.handle_transcript("list events")
    assert listing is not None
    assert "demo @ friday 9am" in listing.message


def test_file_find_then_open_it(tmp_path: Path) -> None:
    target = tmp_path / "report.txt"
    target.write_text("hello", encoding="utf-8")

    assistant = build_assistant(tmp_path, file_index_root=tmp_path)
    index_res = assistant.handle_transcript("index files")
    assert index_res is not None
    assert index_res.intent == "file_index"

    found = assistant.handle_transcript("find file report")
    assert found is not None
    assert found.intent == "file_find"
    assert found.message.endswith("report.txt")

    opened = assistant.handle_transcript("open it")
    assert opened is not None
    assert opened.intent == "file_open"
    assert opened.message == "Opening report.txt."


def test_cli_output_shape(tmp_path: Path) -> None:
    assistant = build_assistant(tmp_path, file_index_root=tmp_path)
    out = assistant.handle_transcript("shutdown")
    assert out is not None
    payload = {"intent": out.intent, "parameters": out.parameters, "message": out.message}
    encoded = json.dumps(payload)
    assert '"intent": "system_action"' in encoded


def test_wake_word_only_acknowledges(tmp_path: Path) -> None:
    assistant = build_assistant(tmp_path, file_index_root=tmp_path)
    wake = assistant.handle_transcript("assistant", wake_word="assistant")
    assert wake is not None
    assert wake.intent == "wake_acknowledge"


def test_short_term_file_memory_is_one_use(tmp_path: Path) -> None:
    target = tmp_path / "invoice.pdf"
    target.write_text("hello", encoding="utf-8")

    assistant = build_assistant(tmp_path, file_index_root=tmp_path)
    assistant.handle_transcript("index files")
    found = assistant.handle_transcript("find file invoice")
    assert found is not None and found.intent == "file_find"

    first_open = assistant.handle_transcript("open it")
    assert first_open is not None
    assert first_open.intent == "file_open"

    second_open = assistant.handle_transcript("open it")
    assert second_open is not None
    assert second_open.intent == "unknown"


def test_short_term_memory_expires_after_one_followup_turn(tmp_path: Path) -> None:
    target = tmp_path / "draft.md"
    target.write_text("x", encoding="utf-8")

    assistant = build_assistant(tmp_path, file_index_root=tmp_path)
    assistant.handle_transcript("index files")
    found = assistant.handle_transcript("find file draft")
    assert found is not None and found.intent == "file_find"

    # A different turn consumes the one-turn context window.
    assistant.handle_transcript("list events")

    expired = assistant.handle_transcript("open it")
    assert expired is not None
    assert expired.intent == "unknown"
