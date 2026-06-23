from tony.core.command_parser import CommandParser
from tony.core.safety import SafetyLevel, SafetySystem


def classify_voice(text: str):
    parsed = CommandParser().parse(text)
    return SafetySystem().classify(text, parsed.intent)


def test_voice_git_push_needs_approval():
    assert classify_voice("git push karo").level == SafetyLevel.NEEDS_APPROVAL


def test_voice_rm_rf_is_blocked():
    assert classify_voice("rm -rf").level == SafetyLevel.BLOCKED


def test_voice_repo_status_is_safe():
    assert classify_voice("repo status dikhao").level == SafetyLevel.SAFE


def test_risky_voice_command_needs_approval():
    assert classify_voice("Tony git push karo").level == SafetyLevel.NEEDS_APPROVAL


def test_blocked_voice_command_is_blocked():
    assert classify_voice(".env read karo").level == SafetyLevel.BLOCKED

