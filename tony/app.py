from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from tony.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

