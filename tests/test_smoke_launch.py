import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from tony.ui.main_window import MainWindow


def test_smoke_launch_main_window(monkeypatch):
    monkeypatch.setattr(MainWindow, "speak_startup", lambda self: None)
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    assert window.input is not None
    assert window.voice_button.text() == "Push to Talk"
    assert window.wake_mode_button.text() == "Wake Mode"
    assert window.status.text()

    window.close()
