# secure-enerprise-mcp/tests/test_audit_logger.py
import json
import pytest
from mcp.server.mcpserver.exceptions import ToolError
import server.audit.logger as audit_logger
from server.security.authorization import authorize_tool


def read_events(audit_file):
    return [
        json.loads(line)
        for line in audit_file.read_text(encoding="utf-8").splitlines()
    ]


def test_allowed_authorization_writes_security_event(
    tmp_path,
    monkeypatch,
):
    audit_file = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        audit_logger,
        "AUDIT_FILE",
        audit_file,
    )

    authorize_tool(
        "read_enterprise_document",
        "analyst",
        {"documents.search", "documents.read"},
    )

    events = read_events(audit_file)

    assert len(events) == 1

    event = events[0]

    print("\nAllowed authorization audit event:")
    print(json.dumps(event, indent=2))

    assert event["event_type"] == "authorization_decision"
    assert event["outcome"] == "allowed"
    assert event["user_id"] == "analyst"
    assert event["tool_name"] == "read_enterprise_document"
    assert event["resource_id"] is None
    assert event["details"] == {
        "required_scopes": ["documents.read"]
    }

    assert "timestamp" in event

def test_denied_authorization_writes_security_event(
    tmp_path,
    monkeypatch,
):
    audit_file = tmp_path / "audit.jsonl"

    monkeypatch.setattr(
        audit_logger,
        "AUDIT_FILE",
        audit_file,
    )

    with pytest.raises(
        ToolError,
        match="Access denied",
    ):
        authorize_tool(
            "read_enterprise_document",
            "restricted_user",
            {"documents.search"},
        )

    events = read_events(audit_file)

    assert len(events) == 1

    event = events[0]

    print("\nDenied authorization audit event:")
    print(json.dumps(event, indent=2))

    assert event["event_type"] == "authorization_decision"
    assert event["outcome"] == "denied"
    assert event["user_id"] == "restricted_user"
    assert event["tool_name"] == "read_enterprise_document"
    assert event["resource_id"] is None
    assert event["details"] == {
        "missing_scopes": ["documents.read"]
    }

    assert "timestamp" in event