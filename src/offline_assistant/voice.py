from __future__ import annotations

import argparse
import json
import os
import tempfile
import wave
from pathlib import Path
from typing import Any

from .main import build_assistant


class VoiceRuntimeError(RuntimeError):
    pass


def _load_optional_dependencies() -> tuple[Any, Any, Any]:
    try:
        import numpy as np
        import pyttsx3
        import sounddevice as sd
    except ImportError as exc:  # pragma: no cover - exercised in runtime environments
        raise VoiceRuntimeError(
            "Missing voice dependencies. Install: pip install numpy sounddevice pyttsx3 faster-whisper"
        ) from exc
    return np, sd, pyttsx3


def _load_whisper_model(model_size: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:  # pragma: no cover - exercised in runtime environments
        raise VoiceRuntimeError(
            "Missing speech-to-text dependency. Install: pip install faster-whisper"
        ) from exc

    return WhisperModel(model_size, device="cpu", compute_type="int8")


class VoiceAssistantRuntime:
    """Offline voice loop using local microphone + faster-whisper + local TTS."""

    def __init__(
        self,
        sample_rate: int = 16_000,
        channels: int = 1,
        whisper_model_size: str = "base",
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels

        np, sd, pyttsx3 = _load_optional_dependencies()
        self.np = np
        self.sd = sd

        self.tts = pyttsx3.init()
        self.whisper = _load_whisper_model(whisper_model_size)

    def _record_seconds(self, seconds: float) -> bytes:
        if seconds <= 0:
            raise ValueError("seconds must be positive")

        frame_count = int(self.sample_rate * seconds)
        audio = self.sd.rec(frame_count, samplerate=self.sample_rate, channels=self.channels, dtype="int16")
        self.sd.wait()

        if self.channels > 1:
            audio = audio.mean(axis=1, keepdims=True).astype("int16")

        return audio.tobytes()

    def _transcribe_pcm16(self, pcm16_bytes: bytes) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)

        try:
            with wave.open(str(wav_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(pcm16_bytes)

            segments, _ = self.whisper.transcribe(str(wav_path), vad_filter=True)
            text = " ".join(segment.text.strip() for segment in segments).strip().lower()
            return text
        finally:
            wav_path.unlink(missing_ok=True)

    def speak(self, text: str) -> None:
        self.tts.say(text)
        self.tts.runAndWait()


def run_voice_loop() -> None:
    parser = argparse.ArgumentParser(description="Offline voice loop for the assistant")
    parser.add_argument("--record-seconds", type=float, default=4.0, help="Audio capture duration per turn")
    parser.add_argument("--whisper-model", default=os.getenv("WHISPER_MODEL", "base"), help="faster-whisper model size")
    args = parser.parse_args()

    data_dir = Path(os.getenv("ASSISTANT_DATA_DIR", "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    assistant = build_assistant(data_dir)
    wake_word = os.getenv("WAKE_WORD")

    try:
        runtime = VoiceAssistantRuntime(whisper_model_size=args.whisper_model)
    except VoiceRuntimeError as exc:
        print(str(exc))
        return

    print("Voice mode ready. Press Ctrl+C to exit.")
    while True:
        print("Listening...")
        pcm_bytes = runtime._record_seconds(args.record_seconds)
        transcript = runtime._transcribe_pcm16(pcm_bytes)

        if not transcript:
            print("null")
            continue

        result = assistant.handle_transcript(transcript, wake_word=wake_word)
        if result is None:
            print("null")
            continue

        payload = {"intent": result.intent, "parameters": result.parameters, "message": result.message, "transcript": transcript}
        print(json.dumps(payload))
        runtime.speak(result.message)


if __name__ == "__main__":
    run_voice_loop()
