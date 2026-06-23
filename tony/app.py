from __future__ import annotations

import signal
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from tony.core.logging_config import setup_logging
from tony.ui.main_window import MainWindow


def main() -> None:
    setup_logging()
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, lambda *_args: app.quit())
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(250)
    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        app.quit()
