"""System-tray controls for the Rocket mascot."""

from __future__ import annotations

from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from config import APP_NAME, SPRITE_PATH


class RocketTray(QSystemTrayIcon):
    def __init__(self, mascot, parent=None) -> None:
        icon = QIcon(str(SPRITE_PATH))
        if icon.isNull():
            icon = QIcon(QPixmap(16, 16))
        super().__init__(icon, parent)
        self._mascot = mascot
        self.setToolTip(APP_NAME)

        menu = QMenu()
        self._toggle_action = QAction(menu)
        self._toggle_action.triggered.connect(self.toggle_mascot)
        menu.addAction(self._toggle_action)
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self._exit)
        menu.addAction(exit_action)
        self.setContextMenu(menu)
        self._refresh_toggle_label()

    def toggle_mascot(self) -> None:
        if self._mascot.isVisible():
            self._mascot.hide()
        else:
            self._mascot.show()
            self._mascot.raise_()
        self._refresh_toggle_label()

    def _refresh_toggle_label(self) -> None:
        self._toggle_action.setText(
            "Hide Rocket" if self._mascot.isVisible() else "Show Rocket"
        )

    def _exit(self) -> None:
        self._mascot.close()
        self.parent().quit()
