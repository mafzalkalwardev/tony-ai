import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from tony.ui.main_window import MainWindow


def test_main_window_imports_without_crashing(monkeypatch):
    monkeypatch.setattr(MainWindow, "speak_startup", lambda self: None)
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    assert window.windowTitle() == "Tony AI"
    assert window.advanced_tabs.isVisible() is False
    assert window.voice_button.text() == "Push to Talk"

    window.close()
