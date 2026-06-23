from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def run() -> int:
    try:
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QApplication

        from tony.ui.main_window import MainWindow
    except Exception as exc:
        print(f"Could not import UI: {exc}")
        return 0

    screenshots = ROOT / "docs" / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication(sys.argv)
    MainWindow.speak_startup = lambda self: None
    window = MainWindow()
    window.resize(1280, 720)
    window.show()

    def capture() -> None:
        pixmap = window.grab()
        pixmap.save(str(screenshots / "dashboard.png"))
        window.close()
        app.quit()

    QTimer.singleShot(750, capture)
    app.exec()
    print(f"Saved UI screenshot: {screenshots / 'dashboard.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
