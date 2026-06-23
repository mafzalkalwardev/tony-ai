from tony.core.command_parser import CommandParser
from tony.core.safety import SafetyLevel, SafetySystem


def classify(text: str):
    parsed = CommandParser().parse(text)
    return SafetySystem().classify(text, parsed.intent)


def test_password_record_is_blocked():
    assert classify("password record karo").level == SafetyLevel.BLOCKED


def test_bulk_sms_is_blocked():
    assert classify("bulk SMS bhejo").level == SafetyLevel.BLOCKED


def test_live_voice_setting_defaults_to_off():
    import json
    from pathlib import Path

    settings = json.loads(Path("config/settings.json").read_text(encoding="utf-8"))
    assert settings["live_voice_enabled"] is False


def test_stop_live_voice_is_safe():
    assert classify("live listening stop karo").level == SafetyLevel.SAFE
