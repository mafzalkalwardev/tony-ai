from tony.core.screen_context import ScreenContext
from tony.core.workflow_memory import WorkflowMemory


class FakeVision:
    def analyze_screenshot_basic(self):
        return {
            "active_window_title": "VS Code - tony-ai",
            "process_name": "Code.exe",
            "screenshot_path": "tony/logs/screenshots/example.png",
            "visible_text": "safe text",
            "sensitive": False,
            "note": "basic context only",
        }


def test_screen_context_stores_title_path_and_time(tmp_path):
    context = ScreenContext().capture_context(FakeVision(), workspace_path=tmp_path)

    assert context.active_window_title == "VS Code - tony-ai"
    assert context.screenshot_path.endswith("example.png")
    assert context.timestamp


def test_sensitive_keywords_detected():
    context = ScreenContext(active_window_title="Password manager")

    assert context.is_sensitive()


def test_env_secret_windows_flagged():
    context = ScreenContext(active_window_title=".env - VS Code")

    assert context.is_sensitive()


def test_screen_context_saves_to_memory(tmp_path):
    context = ScreenContext(active_window_title="VS Code", screenshot_path="tony/logs/screenshots/a.png", timestamp="now")
    memory = WorkflowMemory(tmp_path / "memory.db")

    context.save_to_memory(memory)

    assert (tmp_path / "memory.db").exists()
