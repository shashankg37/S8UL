"""Qt-native WebSocket client for Rocket's local backend protocol."""

from __future__ import annotations

import json
import logging

from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWebSockets import QWebSocket

from config import BACKEND_WS_URL, RECONNECT_DELAY_MS

LOGGER = logging.getLogger(__name__)


class WSClient(QObject):
    """Reconnects in Qt's event loop; no background thread touches widgets."""

    state_changed = Signal(str)
    response_received = Signal(str)
    connected = Signal()
    disconnected = Signal()

    def __init__(self, url: str = BACKEND_WS_URL, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._url = QUrl(url)
        self._should_reconnect = False
        self._socket = QWebSocket()
        self._reconnect_timer = QTimer(self)
        self._reconnect_timer.setSingleShot(True)
        self._reconnect_timer.timeout.connect(self._open)
        self._socket.connected.connect(self._on_connected)
        self._socket.disconnected.connect(self._on_disconnected)
        self._socket.textMessageReceived.connect(self._on_message)
        self._socket.errorOccurred.connect(self._on_error)

    def start(self) -> None:
        self._should_reconnect = True
        self._open()

    def stop(self) -> None:
        self._should_reconnect = False
        self._reconnect_timer.stop()
        self._socket.close()

    def send_text(self, text: str) -> bool:
        text = text.strip()
        if not text:
            return False
        if self._socket.state() != QAbstractSocket.SocketState.ConnectedState:
            LOGGER.warning("Rocket backend is disconnected; message was not sent.")
            return False
        self._socket.sendTextMessage(json.dumps({"text": text}))
        return True

    def _open(self) -> None:
        if self._should_reconnect and self._socket.state() == QAbstractSocket.SocketState.UnconnectedState:
            LOGGER.info("Connecting to Rocket backend at %s", self._url.toString())
            self._socket.open(self._url)

    def _on_connected(self) -> None:
        self._reconnect_timer.stop()
        self.connected.emit()

    def _on_disconnected(self) -> None:
        self.disconnected.emit()
        if self._should_reconnect:
            self._reconnect_timer.start(RECONNECT_DELAY_MS)

    def _on_error(self, _error) -> None:
        LOGGER.warning("Rocket WebSocket error: %s", self._socket.errorString())

    def _on_message(self, raw_message: str) -> None:
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError:
            LOGGER.warning("Ignored malformed backend message: %r", raw_message)
            return

        message_type = message.get("type")
        if message_type == "state" and isinstance(message.get("state"), str):
            self.state_changed.emit(message["state"])
        elif message_type == "response" and isinstance(message.get("text"), str):
            self.response_received.emit(message["text"])
        else:
            LOGGER.warning("Ignored unknown backend message: %r", message)
