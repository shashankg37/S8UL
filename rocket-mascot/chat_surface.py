"""Tiny input and response windows used by the mascot, not a chat UI."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QLabel, QLineEdit

from config import RESPONSE_BUBBLE_DURATION_MS


class ChatInput(QLineEdit):
    submitted = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setPlaceholderText("Ask Rocket…")
        self.setFixedWidth(300)
        self.setStyleSheet("QLineEdit { background: #18243a; color: white; border: 1px solid #5b8cff; border-radius: 8px; padding: 8px; }")
        self.returnPressed.connect(self._submit)

    def open_near(self, mascot) -> None:
        self.move(mascot.x() - self.width() + mascot.width(), mascot.y() - self.height() - 8)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def _submit(self) -> None:
        text = self.text().strip()
        if text:
            self.submitted.emit(text)
            self.clear()
            self.hide()


class ResponseBubble(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWordWrap(True)
        self.setMaximumWidth(320)
        self.setStyleSheet("QLabel { background: #18243a; color: white; border: 1px solid #5b8cff; border-radius: 8px; padding: 10px; }")
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    def show_response(self, text: str, mascot) -> None:
        self.setText(text)
        self.adjustSize()
        self.move(mascot.x() - self.width() + mascot.width(), mascot.y() - self.height() - 8)
        self.show()
        self.raise_()
        self._hide_timer.start(RESPONSE_BUBBLE_DURATION_MS)
