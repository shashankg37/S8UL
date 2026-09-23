"""The transparent, draggable Rocket desktop-pet window.

The sprite-loading boundary in ``_load_static_sprite`` is the intended place to
swap in a per-state QMovie or frame-sequence renderer later.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import QPoint, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QAction, QGuiApplication, QMouseEvent, QPixmap
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QMenu

from config import (
    ALWAYS_ON_TOP,
    CORNER_MARGIN_PX,
    IDLE_BOB_AMPLITUDE_PX,
    IDLE_BOB_DURATION_MS,
    PET_SIZE_CM,
    SPRITE_PATH,
    VALID_STATES,
)

LOGGER = logging.getLogger(__name__)


class Mascot(QLabel):
    """A single static sprite today, with a state interface for future art."""
    open_chat_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.state = "idle"
        self._drag_offset: QPoint | None = None
        self._home_position: QPoint | None = None
        self._bob: QPropertyAnimation | None = None
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity)

        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if ALWAYS_ON_TOP:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)

        self._load_static_sprite()

    def _load_static_sprite(self) -> None:
        """Load today's static image; replace this seam for animated states."""
        pixmap = QPixmap(str(SPRITE_PATH))
        if pixmap.isNull():
            raise FileNotFoundError(
                f"Rocket sprite was not found or could not be loaded: {SPRITE_PATH}"
            )

        # Qt reports a @2x/@3x image in device-independent units through DPR.
        # Fit the art into a physical 5 cm box while keeping its aspect ratio.
        screen = QGuiApplication.primaryScreen()
        dpi = screen.physicalDotsPerInch() if screen is not None else 96.0
        target_side = max(1, round((PET_SIZE_CM / 2.54) * dpi))
        scaled = pixmap.scaled(
            target_side,
            target_side,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
        self.setFixedSize(scaled.deviceIndependentSize().toSize())

    def set_state(self, name: str) -> None:
        """Set the visual state. Animation/state assets will plug in here later."""
        if name not in VALID_STATES:
            LOGGER.warning("Unknown Rocket state %r; keeping %s", name, self.state)
            return
        previous = self.state
        self.state = name
        LOGGER.info("Rocket state transition: %s -> %s", previous, name)
        # Future seam: select/start the QMovie or frame sequence for ``name`` here.

    def set_connected(self, is_connected: bool) -> None:
        """Dim the static sprite while the local backend is unavailable."""
        self._opacity.setOpacity(1.0 if is_connected else 0.45)

    def start_idle_bob(self) -> None:
        """Start the current static-sprite idle motion, if configured."""
        if IDLE_BOB_AMPLITUDE_PX <= 0 or self._home_position is None:
            return
        self.stop_idle_bob(reset_to_home=False)
        home = self._home_position
        self._bob = QPropertyAnimation(self, b"pos", self)
        self._bob.setDuration(IDLE_BOB_DURATION_MS)
        self._bob.setLoopCount(-1)
        self._bob.setStartValue(home)
        self._bob.setKeyValueAt(0.5, QPoint(home.x(), home.y() - IDLE_BOB_AMPLITUDE_PX))
        self._bob.setEndValue(home)
        self._bob.start()

    def stop_idle_bob(self, reset_to_home: bool = True) -> None:
        if self._bob is not None:
            self._bob.stop()
            self._bob.deleteLater()
            self._bob = None
        if reset_to_home and self._home_position is not None:
            self.move(self._home_position)

    def place_initially(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        self._home_position = self._clamp_position(
            QPoint(
                available.right() - self.width() + 1 - CORNER_MARGIN_PX,
                available.bottom() - self.height() + 1 - CORNER_MARGIN_PX,
            ),
            screen,
        )
        self.move(self._home_position)

    def _clamp_position(self, position: QPoint, screen=None) -> QPoint:
        if screen is None:
            screen = self._screen_for_point(position)
        if screen is None:
            return position
        geometry = screen.availableGeometry()
        amplitude = IDLE_BOB_AMPLITUDE_PX if IDLE_BOB_AMPLITUDE_PX > 0 else 0
        min_x = geometry.left()
        max_x = max(min_x, geometry.right() - self.width() + 1)
        min_y = geometry.top() + amplitude
        max_y = max(min_y, geometry.bottom() - self.height() + 1)
        return QPoint(
            max(min_x, min(position.x(), max_x)),
            max(min_y, min(position.y(), max_y)),
        )

    def _screen_for_point(self, point: QPoint):
        return QGuiApplication.screenAt(point) or self.screen() or QGuiApplication.primaryScreen()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.stop_idle_bob()
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            cursor = event.globalPosition().toPoint()
            screen = self._screen_for_point(cursor)
            if screen is not None:
                self._home_position = self._clamp_position(cursor - self._drag_offset, screen)
                self.move(self._home_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._drag_offset is not None:
            self._drag_offset = None
            self.start_idle_bob()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_chat_requested.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(QGuiApplication.quit)
        menu.addAction(exit_action)
        menu.exec(event.globalPos())
