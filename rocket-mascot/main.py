"""Application entry point for the backend-free Rocket mascot frontend."""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from config import APP_NAME
from chat_surface import ChatInput, ResponseBubble
from hotkey import GlobalExitHotkey
from mascot import Mascot
from tray import RocketTray
from ws_client import WSClient


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)  # The tray owns the app lifetime.

    global_exit_hotkey = GlobalExitHotkey()
    app.installNativeEventFilter(global_exit_hotkey)
    global_exit_hotkey.register()
    app.aboutToQuit.connect(global_exit_hotkey.unregister)

    mascot = Mascot()
    mascot.place_initially()
    mascot.show()
    mascot.start_idle_bob()

    chat_input = ChatInput()
    response_bubble = ResponseBubble()
    client = WSClient(parent=app)
    mascot.open_chat_requested.connect(lambda: chat_input.open_near(mascot))
    chat_input.submitted.connect(client.send_text)
    client.state_changed.connect(mascot.set_state)
    client.response_received.connect(lambda text: response_bubble.show_response(text, mascot))
    client.connected.connect(lambda: (logging.info("Rocket backend connected"), mascot.set_connected(True), mascot.set_state("idle")))
    client.disconnected.connect(lambda: (logging.warning("Rocket backend disconnected; retrying"), mascot.set_connected(False)))
    app.aboutToQuit.connect(client.stop)
    client.start()

    tray = RocketTray(mascot, app)
    tray.show()
    if not tray.isSystemTrayAvailable():
        logging.warning("No system tray is available on this system.")

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
