# Offline Productivity Assistant (Python + Ollama)

A local-first assistant implementation using **Python** with optional **Ollama** fallback.

## What this does
- Deterministic intent parsing first.
- Optional Ollama fallback (`/api/generate`) when deterministic rules miss.
- Always routes through structured intent output.
- Domain modules expose `execute(parameters: dict) -> str`.
- Supports both:
  - Text CLI mode
  - Offline voice mode (mic input + local whisper STT + local TTS)

## Modules
- Calendar: JSON-backed add/list/remove (`calendar.json`).
- File: SQLite index/search/open (`file_index.db`) with one-turn `open it` memory (immediate next turn only).
- Music: local file matching for playback selection.
- Email: unread subjects via IMAP with offline-safe responses.
- System: deterministic action responses (shutdown/restart/lock).

## Text mode
```bash
PYTHONPATH=src python -m offline_assistant.main
```

## Voice mode (offline)
Install local dependencies:
```bash
pip install numpy sounddevice pyttsx3 faster-whisper
```

Run voice loop:
```bash
PYTHONPATH=src python -m offline_assistant.voice --record-seconds 4
```

Voice mode behavior:
- Records microphone audio for a short fixed turn window.
- Transcribes with local `faster-whisper` on CPU.
- Routes transcript through deterministic parser + optional Ollama fallback.
- Speaks back the module response using local TTS (`pyttsx3`).

## Ollama setup (optional)
Start Ollama locally and pull a model:
```bash
ollama serve
ollama pull llama3.1:8b
```

Then run assistant with defaults (or set env vars below).

## Optional environment variables
- `WAKE_WORD`
- `OLLAMA_URL` (default `http://127.0.0.1:11434`)
- `OLLAMA_MODEL` (default `llama3.1:8b`)
- `WHISPER_MODEL` (default `base`)
- `MUSIC_DIR`
- `FILE_INDEX_ROOT` (default current working directory)
- `EMAIL_IMAP_HOST`
- `EMAIL_USERNAME`
- `EMAIL_APP_PASSWORD`
- `ASSISTANT_DATA_DIR` (default `data`)

## Example commands
- `index files`
- `find file budget`
- `open it`
- `add event team sync at monday 10am`
- `list events`
- `remove event team sync`
- `play lofi`
- `read unread emails`
- `shutdown`
