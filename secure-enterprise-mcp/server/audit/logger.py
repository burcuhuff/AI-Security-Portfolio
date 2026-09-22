#server/audit/logger.py
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
    Write a structured MCP tool audit event.

    Security events intentionally contain metadata rather than
    sensitive document contents or credentials.

    Args:
        user_id: Authenticated or simulated principal identifier.
        tool_name: MCP tool being invoked.
        outcome: Result such as "allowed" or "denied".
        details: Optional non-sensitive contextual metadata.
        event_type: What security relevant event occured
        resource_id: Which objct/data item was affected
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

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")