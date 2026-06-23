from __future__ import annotations

from collections import deque

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget


class AudioWaveformWidget(QWidget):
    def __init__(self, max_bars: int = 32) -> None:
        super().__init__()
        self.levels = deque([0.05] * max_bars, maxlen=max_bars)
        self.state = "Idle"
        self.setMinimumHeight(72)

    def set_level(self, level: float) -> None:
        self.levels.append(max(0.02, min(1.0, float(level))))
        self.update()

    def set_state(self, state: str) -> None:
        self.state = state
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#0f172a"))
        width = max(1, self.width())
        height = max(1, self.height())
        bar_width = max(3, width // (len(self.levels) * 2))
        gap = bar_width
        x = gap
        color = QColor("#38bdf8") if self.state not in {"Blocked", "Waiting for Approval"} else QColor("#f59e0b")
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        for level in self.levels:
            bar_height = max(4, int((height - 20) * level))
            y = (height - bar_height) // 2
            painter.drawRoundedRect(x, y, bar_width, bar_height, 3, 3)
            x += bar_width + gap
        painter.setPen(QColor("#e2e8f0"))
        painter.drawText(10, height - 8, self.state)

