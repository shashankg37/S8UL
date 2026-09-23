from enum import Enum


class PermissionLevel(Enum):
    SAFE = "safe"
    ASK = "ask"
    BLOCK = "block"


PERMISSIONS = {
    "read_system": PermissionLevel.SAFE,
    "read_file": PermissionLevel.SAFE,
    "list_files": PermissionLevel.SAFE,

    "launch_application": PermissionLevel.SAFE,

    "create_file": PermissionLevel.ASK,
    "modify_file": PermissionLevel.ASK,
    "run_command": PermissionLevel.ASK,
    "delete_file": PermissionLevel.ASK,

    "shutdown": PermissionLevel.BLOCK,
}


def check_permission(action: str) -> str:
    """Returns the permission level for an action."""
    permission = PERMISSIONS.get(action, PermissionLevel.ASK)
    return permission.value