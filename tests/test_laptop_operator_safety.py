from tony.core.command_parser import CommandParser
from tony.core.safety import SafetyLevel, SafetySystem


def classify(text: str):
    parsed = CommandParser().parse(text)
    return SafetySystem().classify(text, parsed.intent)


def test_npm_install_needs_approval():
    assert classify("npm install").level == SafetyLevel.NEEDS_APPROVAL


def test_project_analyze_is_safe():
    assert classify("project analyze karo").level == SafetyLevel.SAFE


def test_screenshot_needs_approval():
    assert classify("screenshot lo").level == SafetyLevel.NEEDS_APPROVAL


def test_external_url_needs_approval():
    safety = SafetySystem()
    assert safety.classify("https://example.com", "open_external_url").level == SafetyLevel.NEEDS_APPROVAL


def test_localhost_opening_is_safe():
    assert classify("localhost 3000 kholo").level == SafetyLevel.SAFE


def test_env_reading_is_blocked():
    assert classify(".env read karo").level == SafetyLevel.BLOCKED
