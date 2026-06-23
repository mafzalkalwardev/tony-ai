from tony.core.command_parser import CommandParser
from tony.core.safety import SafetyLevel, SafetySystem


def classify(text: str):
    parsed = CommandParser().parse(text)
    return SafetySystem().classify(text, parsed.intent)


def test_screen_record_needs_approval():
    assert classify("screen record karo").level == SafetyLevel.NEEDS_APPROVAL


def test_actions_record_needs_approval():
    assert classify("actions record karo").level == SafetyLevel.NEEDS_APPROVAL


def test_last_macro_replay_needs_approval():
    assert classify("last macro replay karo").level == SafetyLevel.NEEDS_APPROVAL


def test_recording_stop_is_safe():
    assert classify("recording band karo").level == SafetyLevel.SAFE


def test_pyautogui_replay_requires_approval():
    assert SafetySystem().classify("pyautogui replay", "replay_macro").level == SafetyLevel.NEEDS_APPROVAL

