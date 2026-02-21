from __future__ import annotations

from types import SimpleNamespace

from offline_assistant import voice


class _FakeTTS:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def say(self, text: str) -> None:
        self.spoken.append(text)

    def runAndWait(self) -> None:
        return None


class _FakeWhisper:
    def transcribe(self, _path: str, vad_filter: bool = True):
        assert vad_filter is True
        return [SimpleNamespace(text="hello world")], None


def test_voice_runtime_can_be_constructed_without_real_audio_stack(monkeypatch) -> None:
    fake_tts = _FakeTTS()

    fake_sd = SimpleNamespace(rec=lambda *args, **kwargs: None, wait=lambda: None)
    fake_pyttsx3 = SimpleNamespace(init=lambda: fake_tts)

    monkeypatch.setattr(voice, "_load_optional_dependencies", lambda: (None, fake_sd, fake_pyttsx3))
    monkeypatch.setattr(voice, "_load_whisper_model", lambda _size: _FakeWhisper())

    runtime = voice.VoiceAssistantRuntime()
    runtime.speak("Listening.")

    assert fake_tts.spoken == ["Listening."]
