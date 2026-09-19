# server/security/policy.py
# responsible for loading and interpreting server/security/tool-policy.yaml
from pathlib import Path
from typing import Any

import yaml


POLICY_FILE = Path(__file__).resolve().parent / "tool-policy.yaml"


def load_tool_policy() -> dict[str, Any]:
    """
    Load the MCP tool governance policy from YAML.
    """

    with POLICY_FILE.open("r", encoding="utf-8") as file:
        policy = yaml.safe_load(file)

    if not isinstance(policy, dict) or "tools" not in policy:
        raise ValueError("Invalid tool policy: missing 'tools' section")

    return policy


def get_tool_policy(tool_name: str) -> dict[str, Any]:
    """
    Return governance policy for a specific MCP tool.
    """

    policy = load_tool_policy()
    tools = policy["tools"]

    if tool_name not in tools:
        raise ValueError(f"No policy defined for tool: {tool_name}")

    return tools[tool_name]