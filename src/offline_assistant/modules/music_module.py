from __future__ import annotations

from pathlib import Path


class MusicModule:
    SUPPORTED = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}

    def __init__(self, music_dir: Path) -> None:
        self.music_dir = music_dir

    def execute(self, parameters: dict) -> str:
        query = str(parameters.get("query", "")).strip().lower()
        if not query:
            return "Which playlist?"
        if not self.music_dir.exists():
            return "No results."

        matches = []
        for path in self.music_dir.iterdir():
            if path.suffix.lower() in self.SUPPORTED and query in path.stem.lower():
                matches.append(path)

        if not matches:
            return "No results."

        # Playback hook intentionally omitted for local player preference.
        return f"Playing {matches[0].name}."
