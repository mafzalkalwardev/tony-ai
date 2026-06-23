from pathlib import Path

from tony.core.safety import SafetyLevel, SafetySystem
from tony.tools.vision_tool import VisionTool
from tony.tools.window_tool import WindowTool


def test_observe_screen_needs_approval():
    decision = SafetySystem().classify("Tony screen dekho", "observe_screen")

    assert decision.level == SafetyLevel.NEEDS_APPROVAL


def test_analyze_screen_needs_approval():
    decision = SafetySystem().classify("Tony kya issue hai screen par", "analyze_screen")

    assert decision.level == SafetyLevel.NEEDS_APPROVAL


def test_sensitive_window_is_blocked_for_analysis():
    tool = WindowTool()

    assert tool.check_if_sensitive_window("Bank payment login")
    assert tool.check_if_sensitive_window("project .env - VS Code")


def test_screenshot_path_is_local_only(tmp_path):
    vision = VisionTool(screenshot_dir=tmp_path)
    path = str(tmp_path / "screen.png")

    assert Path(path).is_relative_to(tmp_path)
    assert "http://" not in path
    assert "https://" not in path
    assert str(vision.screenshot_dir) == str(tmp_path)
