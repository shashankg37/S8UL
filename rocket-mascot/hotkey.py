"""Windows-only global hotkey support with no third-party dependency."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import logging

from PySide6.QtCore import QAbstractNativeEventFilter, QCoreApplication

from config import GLOBAL_EXIT_HOTKEY

LOGGER = logging.getLogger(__name__)

WM_HOTKEY = 0x0312
HOTKEY_ID = 1
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
VK_Q = 0x51


class GlobalExitHotkey(QAbstractNativeEventFilter):
    """Registers Ctrl+Shift+Q and asks Qt to exit when Windows sends it."""

    def __init__(self) -> None:
        super().__init__()
        self._registered = False

    def register(self) -> bool:
        self._registered = bool(
            ctypes.windll.user32.RegisterHotKey(
                None, HOTKEY_ID, MOD_CONTROL | MOD_SHIFT, VK_Q
            )
        )
        if self._registered:
            LOGGER.info("Press %s to exit Rocket", GLOBAL_EXIT_HOTKEY)
        else:
            LOGGER.warning(
                "%s is already in use; Rocket's global exit hotkey is disabled.",
                GLOBAL_EXIT_HOTKEY,
            )
        return self._registered

    def unregister(self) -> None:
        if self._registered:
            ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID)
            self._registered = False

    def nativeEventFilter(self, event_type, message):
        if event_type == b"windows_generic_MSG":
            native_message = wintypes.MSG.from_address(int(message))
            if native_message.message == WM_HOTKEY and native_message.wParam == HOTKEY_ID:
                LOGGER.info("Global exit hotkey triggered")
                QCoreApplication.quit()
                return True, 0
        return False, 0
