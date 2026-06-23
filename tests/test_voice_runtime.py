from tony.voice.stt import SpeechToText
from tony.voice.stt import TranscriptionResult


def test_microphone_failure_returns_helpful_error(monkeypatch):
    stt = SpeechToText()

    def fail_record(*_args, **_kwargs):
        raise RuntimeError("No input device")

    monkeypatch.setattr(stt, "_record_temp_wav", fail_record)
    result = stt.transcribe_from_microphone()

    assert result.error
    assert "Microphone not detected" in result.error


def test_empty_transcript_returns_clear_message(monkeypatch, tmp_path):
    stt = SpeechToText()
    wav = tmp_path / "empty.wav"
    wav.write_bytes(b"fake")
    monkeypatch.setattr(stt, "_record_temp_wav", lambda **_kwargs: wav)
    monkeypatch.setattr(stt, "transcribe_file", lambda _path: TranscriptionResult("", "I could not hear a clear command. Please try again."))

    result = stt.transcribe_from_microphone()

    assert result.error == "I could not hear a clear command. Please try again."
