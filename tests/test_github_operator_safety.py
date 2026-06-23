from tony.core.command_parser import CommandParser
from tony.core.safety import SafetyLevel, SafetySystem


def classify(text: str):
    parsed = CommandParser().parse(text)
    return SafetySystem().classify(text, parsed.intent)


def test_git_push_needs_approval():
    assert classify("push karo").level == SafetyLevel.NEEDS_APPROVAL


def test_force_push_blocked():
    assert classify("force push karo").level == SafetyLevel.BLOCKED


def test_create_pr_needs_approval():
    assert classify("PR create karo").level == SafetyLevel.NEEDS_APPROVAL


def test_list_issues_safe():
    assert classify("issues dikhao").level == SafetyLevel.SAFE

