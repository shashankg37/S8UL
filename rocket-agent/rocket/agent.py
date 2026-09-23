import os
import platform
import subprocess
from google.adk.agents import Agent
from .permissions import check_permission
from google.adk.models.lite_llm import LiteLlm
from .memory import remember, recall
from .web import web_search


def get_system_info() -> dict:
    """Returns basic information about the computer."""
    return {
        "operating_system": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }


def list_files(path: str) -> str:
    """Lists the files and folders inside a directory."""
    try:
        items = os.listdir(path)

        if not items:
            return f"The folder '{path}' is empty."

        result = []

        for item in items:
            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                result.append(f"[FOLDER] {item}")
            else:
                result.append(f"[FILE] {item}")

        return "\n".join(result)

    except Exception as e:
        return f"Could not access '{path}': {e}"

def launch_application(application: str) -> str:
    """Launches an approved Windows application."""

    allowed_apps = {
        "chrome": "chrome",
        "notepad": "notepad",
        "calculator": "calc",
        "cmd": "cmd",
    }

    app = application.lower().strip()

    if app not in allowed_apps:
        return (
            f"I can't launch '{application}'. "
            f"Allowed applications are: {', '.join(allowed_apps.keys())}"
        )

    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "", allowed_apps[app]],
            shell=False
        )

        return f"Successfully launched {application}."

    except Exception as e:
        return f"Failed to launch {application}: {e}"

root_agent = Agent(
    name="rocket",
    model=LiteLlm(
        model="groq/qwen/qwen3.8-27b",
        api_key=os.getenv("GROQ_API_KEY"),
    ),
    description="Rocket is a personal AI desktop companion.",
    instruction="""
You are Rocket, the user's personal AI desktop companion.

Personality:
- Friendly
- Helpful
- Concise
- Slightly playful

You help with:
- Learning
- Coding
- AI/ML projects
- Research
- Productivity
- Planning
- Computer tasks

You have tools that allow you to inspect the user's computer.
You have persistent memory.

Use remember when the user explicitly asks you to remember useful
information.

Use recall when previous information would help answer the user.

Choose short categories such as:
- preferences
- projects
- goals
- notes

Do not store sensitive information unless the user explicitly asks you to.

You must check permissions before performing actions.

Permission levels:
- safe: action can be performed
- ask: user confirmation is required
- block: action must not be performed

Never bypass the permission system.

For launching applications:

1. Check the permission for "launch_application".
2. If permission is "safe", use launch_application.
3. Only launch applications supported by the tool.
4. Never invent a successful launch.

You have access to a live web search tool.

Use web_search when:
- the user asks for current information
- the user asks about recent events
- the user asks for the latest version of something
- your knowledge may be outdated
- the user explicitly asks you to search the web

Do not use web search for simple questions that you can answer reliably without it.

When using web search, base your answer on the returned search results.
Do not invent information or sources.

Use tools when appropriate.

IMPORTANT:
- You may inspect files and folders.
- Do not claim to have performed an action unless you actually performed it.
- Never delete, modify, or execute anything unless a tool explicitly allows it.
- Ask for confirmation before potentially destructive actions.
""",
    tools=[
    get_system_info,
    list_files,
    remember,
    recall,
    check_permission,
    launch_application,
    web_search,
    ],
)