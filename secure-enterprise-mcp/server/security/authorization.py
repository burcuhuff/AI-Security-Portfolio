# server/security/authorization.py
from collections.abc import Iterable

from mcp.server.mcpserver.exceptions import ToolError

from server.security.policy import get_tool_policy


def authorize_tool(tool_name: str, user_scopes: Iterable[str]) -> None:
    """
    Authorize access to an MCP tool based on its required scopes.

    Raises:
        ToolError: If the caller lacks one or more required scopes.
        ValueError: If the requested tool has no governance policy.
    """

    policy = get_tool_policy(tool_name)

    required_scopes = set(policy.get("required_scopes", []))
    granted_scopes = set(user_scopes)

    missing_scopes = required_scopes - granted_scopes

    if missing_scopes:
        raise ToolError(
            f"Access denied. Missing required scopes: "
            f"{sorted(missing_scopes)}"
        )