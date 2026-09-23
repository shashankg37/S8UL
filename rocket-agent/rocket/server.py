"""Local WebSocket bridge for the Rocket ADK agent."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Uvicorn does not load project .env files itself. Load it before importing the
# agent, because LiteLlm reads GROQ_API_KEY when ``root_agent`` is constructed.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from .agent import root_agent

LOGGER = logging.getLogger(__name__)
APP_NAME = "rocket"
USER_ID = "desktop-user"

app = FastAPI(title="Rocket local agent bridge")
sessions = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=sessions)


async def _ensure_session(session_id: str) -> None:
    if await sessions.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id) is None:
        await sessions.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)


def _event_text(event) -> str:
    return "".join(part.text for part in (getattr(event.content, "parts", None) or []) if part.text)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    await _ensure_session(session_id)
    try:
        while True:
            payload = await websocket.receive_json()
            text = payload.get("text") if isinstance(payload, dict) else None
            if not isinstance(text, str) or not text.strip():
                await websocket.send_json({"type": "state", "state": "error"})
                await websocket.send_json({"type": "response", "text": "Please send a non-empty text message."})
                continue

            await websocket.send_json({"type": "state", "state": "thinking"})
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=text)]),
            ):
                if event.get_function_calls():
                    await websocket.send_json({"type": "state", "state": "tool_running"})
                if event.is_final_response():
                    response = _event_text(event)
                    if response:
                        await websocket.send_json({"type": "state", "state": "success"})
                        await websocket.send_json({"type": "response", "text": response})
    except WebSocketDisconnect:
        LOGGER.info("Rocket desktop client disconnected: %s", session_id)
    except Exception:
        LOGGER.exception("Rocket WebSocket request failed")
        try:
            await websocket.send_json({"type": "state", "state": "error"})
            await websocket.send_json({"type": "response", "text": "Rocket could not complete that request."})
        except RuntimeError:
            pass
