# Rocket Desktop Pet

This is the PySide6 mascot frontend. It connects only to Rocket's local
WebSocket bridge; it contains no agent logic or shell execution.

## Install and run

```powershell
cd rocket-mascot
py -3.11 -m pip install PySide6
py main.py
```

## Run with the local agent

In one PowerShell window, start the backend from its project folder:

```powershell
cd C:\Users\shash\Documents\ChatGPT\Rocket\rocket-agent
.\.venv\Scripts\python.exe -m uvicorn rocket.server:app --host 127.0.0.1 --port 8000
```

Then start the mascot from another window (or with `launch_rocket.vbs`).
Double-click Rocket, enter a message, and press Enter. Replies appear in a
temporary bubble near the sprite. The mascot dims while the backend is
unavailable and retries every two seconds.

The endpoint is configured by `BACKEND_WS_URL` in `config.py`.

Put Rocket's transparent PNG at `assets/sprite.png`. The window automatically
fits it into a 5 cm square while preserving its aspect ratio. Adjust
`PET_SIZE_CM` and `CORNER_MARGIN_PX` in `config.py` to change its default size
or lower-right placement. Qt recognizes `@2x`/`@3x` image scale metadata when
present.

Rocket is static while idle. Set `IDLE_BOB_AMPLITUDE_PX` above `0` in
`config.py` only if you want to restore the optional idle bob.

Press `Ctrl+Shift+Q` anywhere in Windows to exit Rocket. The hotkey is defined
in `hotkey.py`; `config.py` contains its user-facing label.

## Start with Windows

`launch_rocket.vbs` starts Rocket without a console window. A shortcut to it
can be placed in the Windows Startup folder so Rocket starts after you sign in.
The launcher uses `.venv\\Scripts\\pythonw.exe` when present, otherwise it
uses `pythonw.exe` from your Windows PATH.

## Future animated states

The state names and public `set_state(name)` interface are in
`mascot.py` (`Mascot.set_state`). Replace the static loader in
`Mascot._load_static_sprite`, then add the state-specific QMovie/frame-sequence
selection at the marked `Future seam` comment in `Mascot.set_state`.

For example, `mascot.set_state("thinking")` currently logs the transition and
does not change the static artwork.
