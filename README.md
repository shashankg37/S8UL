# Rocket desktop pet

Open `project.godot` with Godot 4.2+ and run it. Rocket uses a transparent, frameless, always-on-top window; drag the mascot to reposition it, then click it to open the compact menu.

The Chat action sends a JSON `POST` request to the `agent_endpoint` in `rocket_settings.json`. Its default is `http://127.0.0.1:8000/chat`, with a `{"message":"…"}` body. The bridge only calls the existing Python service: it does not edit, start, or otherwise alter `rocket-agent`. Update that endpoint/body adapter in `Main.gd` only if your existing service exposes a different HTTP contract.

Included actions: Chat, Tools, Settings, About, and Exit.
