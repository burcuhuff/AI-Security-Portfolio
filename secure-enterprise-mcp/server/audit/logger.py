#server/audit/logger.py
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_DIR = Path(__file__).resolve().parents[2] / "logs"
AUDIT_FILE = AUDIT_DIR / "mcp_audit.jsonl"


def log_tool_event(
    *,
    user_id: str,
    tool_name: str,
    outcome: str,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Write a structured MCP tool audit event.

    Args:
        user_id: Authenticated or simulated principal identifier.
        tool_name: MCP tool being invoked.
        outcome: Result such as "allowed" or "denied".
        details: Optional non-sensitive contextual metadata.
    """

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "tool_name": tool_name,
        "outcome": outcome,
        "details": details or {},
    }

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")