#server/audit/logger.py
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_DIR = Path(__file__).resolve().parents[2] / "logs"
AUDIT_FILE = AUDIT_DIR / "mcp_audit.jsonl"


def log_security_event(
    *,
    event_type: str,
    outcome: str,
    user_id: str | None = None,
    tool_name: str | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Write a structured security audit event to a JSONL file and stderr.

    If the file write fails, exception occurs first

    Security events intentionally contain metadata rather than
    sensitive document contents or credentials.

    Args:
        event_type: Security relevant event category.
        outcome: Result such as "allowed", "denied", or "blocked".
        user_id: Authenticated or simulated principal identifier.
        tool_name: MCP tool associated with the event, when applicable.
        resource_id: Object or data item affected by the event.
        details: Optional non sensitive contextual metadata.
    """

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "tool_name": tool_name,
        "outcome": outcome,
        "details": details or {},
        "event_type": event_type,
        "resource_id": resource_id,
    }

    serialized_event = json.dumps(event)

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(serialized_event + "\n")

    # stderr copy makes successful audit writes visible to container log collection
    # flush=True sends the event immediately
    print(serialized_event, file=sys.stderr, flush=True)