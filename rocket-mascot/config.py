"""Small, centralized settings for the Rocket mascot."""

from pathlib import Path


APP_NAME = "Rocket Mascot"
BASE_DIR = Path(__file__).resolve().parent
BACKEND_WS_URL = "ws://127.0.0.1:8000/ws/rocket-desktop"
RECONNECT_DELAY_MS = 2_000
RESPONSE_BUBBLE_DURATION_MS = 6_000

# Replace this file with the transparent PNG supplied for Rocket.
SPRITE_PATH = BASE_DIR / "assets" / "s8ul.png"

ALWAYS_ON_TOP = True
IDLE_BOB_AMPLITUDE_PX = 4
IDLE_BOB_DURATION_MS = 2_800

# The mascot is constrained to this physical-size bounding box, preserving its
# original aspect ratio. At a typical 96-DPI display this is about 189 px.
PET_SIZE_CM = 4
CORNER_MARGIN_PX = 16

# Global Windows shortcut. This works even when Rocket does not have focus.
GLOBAL_EXIT_HOTKEY = "Ctrl+Shift+Q"

VALID_STATES = (
    "idle",
    "thinking",
    "tool_running",
    "success",
    "error",
    "sleeping",
)
