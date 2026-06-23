from tony.voice import voice_setup


def test_voice_setup_detects_missing_packages_gracefully(monkeypatch):
    def fake_find_spec(name):
        if name == "faster_whisper":
            return None
        return object()

    monkeypatch.setattr(voice_setup.importlib.util, "find_spec", fake_find_spec)
    missing = voice_setup.check_voice_dependencies()

    assert "faster-whisper" in missing


def test_voice_setup_status_has_install_command(monkeypatch):
    monkeypatch.setattr(voice_setup, "check_voice_dependencies", lambda: ["faster-whisper"])
    monkeypatch.setattr(voice_setup, "check_microphone_available", lambda: (False, "No mic"))

    status = voice_setup.get_voice_setup_status()

    assert status.ok is False
    assert status.install_command == "python -m pip install -r requirements.txt"
    assert "No mic" in status.as_text()
