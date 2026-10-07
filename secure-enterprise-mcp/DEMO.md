# DEMO

Install dependencies:
```
python -m pip install -r requirements.txt
```

Run as an analyst with search and read access:
```
DEMO_USER=analyst python -m client.agent
```

Run as a restricted user with search-only access:
```
DEMO_USER=restricted_user python -m client.agent
```

The restricted user can discover matching documents but is denied access to
document contents.


### Tests

Run the security tests with:
```
python -m pytest -q
```
        TEST EVIDENCE VISUAL
    Authorization
    ├── allowed authorization
    └── denied authorization

    Trust Boundary
    ├── trusted search isolation
    ├── path traversal protection
    └── quarantine isolation


    allowed   → requested operation was authorized
    denied    → authorization rejected it
    passed    → positive security invariant was verified
    blocked   → prohibited boundary crossing was prevented

```
(.venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % python -m pytest -q -rP
.....                                                                                                                 [100%]
========================================================== PASSES ===========================================================
_____________________________________ test_allowed_authorization_writes_security_event ______________________________________
--------------------------------------------------- Captured stdout call ----------------------------------------------------

Allowed authorization audit event:
{
  "timestamp": "2026-09-22T17:18:14.915774+00:00",
  "user_id": "analyst",
  "tool_name": "read_enterprise_document",
  "outcome": "allowed",
  "details": {
    "required_scopes": [
      "documents.read"
    ]
  },
  "event_type": "authorization_decision",
  "resource_id": null
}
______________________________________ test_denied_authorization_writes_security_event ______________________________________
--------------------------------------------------- Captured stdout call ----------------------------------------------------

Denied authorization audit event:
{
  "timestamp": "2026-09-22T17:18:14.920785+00:00",
  "user_id": "restricted_user",
  "tool_name": "read_enterprise_document",
  "outcome": "denied",
  "details": {
    "missing_scopes": [
      "documents.read"
    ]
  },
  "event_type": "authorization_decision",
  "resource_id": null
}
________________________________________ test_search_only_returns_trusted_documents _________________________________________
--------------------------------------------------- Captured stdout call ----------------------------------------------------

Trust boundary search result:
{
  "security_property": "trusted_search_isolation",
  "outcome": "passed",
  "trusted_results": [
    {
      "document_id": "trusted.txt",
      "name": "trusted"
    }
  ],
  "quarantine_results": []
}
______________________________________ test_path_traversal_into_quarantine_is_rejected ______________________________________
--------------------------------------------------- Captured stdout call ----------------------------------------------------

Path traversal protection result:
{
  "security_property": "path_traversal_protection",
  "outcome": "blocked",
  "requested_resource": "../quarantine/untrusted.txt",
  "reason": "Invalid document_id"
}
5 passed in 1.50s
(.venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % 
```

## Audit Test with Trust Boundary and Approval Store

      Human approved:
      finance_report.txt
              ↓
      partner@example.com

      Agent attempts:
      finance_report.txt
              ↓
      attacker@example.com

              BLOCKED
                ↓
          audit evidence
                ↓

      Agent uses exact approved action
                ↓
              CONSUMED

```
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % touch .gitignore
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % grep -qxF 'logs/' .gitignore || echo 'logs/' >> .gitignore
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % python - <<'PY'
from server.security.approval import ApprovalStore, ApprovalError

store = ApprovalStore()

request = store.create(
    principal_id="analyst",
    tool_name="send_enterprise_document",
    document_id="finance_report.txt",
    destination="partner@example.com",
)

store.approve(
    request.approval_id,
    decided_by="security_operator",
)

# Simulate destination substitution / exfiltration attempt.
try:
    store.consume(
        approval_id=request.approval_id,
        principal_id="analyst",
        tool_name="send_enterprise_document",
        document_id="finance_report.txt",
        destination="attacker@example.com",
    )
except ApprovalError as exc:
    print(f"Blocked expected attack: {exc}")

# Original approved action remains valid after the blocked mismatch.
store.consume(
    approval_id=request.approval_id,
    principal_id="analyst",
    tool_name="send_enterprise_document",
    document_id="finance_report.txt",
    destination="partner@example.com",
)

print(f"Demo approval lifecycle completed: {request.approval_id}")
PY
Blocked expected attack: Approval destination does not match request.
Demo approval lifecycle completed: apr_94cc454ba6894d7bbebd2ef64fac8d25
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % python - <<'PY'
import json
from pathlib import Path

source = Path("logs/mcp_audit.jsonl")
destination = Path("examples/sample_audit.jsonl")

events = [
    json.loads(line)
    for line in source.read_text(encoding="utf-8").splitlines()[-4:]
]

sample_timestamps = [
    "2026-10-07T18:00:00+00:00",
    "2026-10-07T18:00:30+00:00",
    "2026-10-07T18:01:00+00:00",
    "2026-10-07T18:01:10+00:00",
]

for event, timestamp in zip(events, sample_timestamps):
    event["timestamp"] = timestamp

    if "approval_id" in event.get("details", {}):
        event["details"]["approval_id"] = "apr_demo"

destination.parent.mkdir(parents=True, exist_ok=True)

with destination.open("w", encoding="utf-8") as file:
    for event in events:
        file.write(json.dumps(event) + "\n")

print(f"Wrote {destination}")
PY
Wrote examples/sample_audit.jsonl
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % cat examples/sample_audit.jsonl
{"timestamp": "2026-10-07T18:00:00+00:00", "user_id": "analyst", "tool_name": "send_enterprise_document", "outcome": "pending", "details": {"approval_id": "apr_demo", "destination": "partner@example.com", "expires_at": "2026-10-07T18:05:00+00:00"}, "event_type": "approval_request", "resource_id": "finance_report.txt"}
{"timestamp": "2026-10-07T18:00:30+00:00", "user_id": "analyst", "tool_name": "send_enterprise_document", "outcome": "approved", "details": {"approval_id": "apr_demo", "destination": "partner@example.com", "decided_by": "security_operator"}, "event_type": "approval_decision", "resource_id": "finance_report.txt"}
{"timestamp": "2026-10-07T18:01:00+00:00", "user_id": "analyst", "tool_name": "send_enterprise_document", "outcome": "blocked", "details": {"approval_id": "apr_demo", "destination": "partner@example.com", "reason": "destination_mismatch", "approved_destination": "partner@example.com", "attempted_destination": "attacker@example.com"}, "event_type": "approval_consumption", "resource_id": "finance_report.txt"}
{"timestamp": "2026-10-07T18:01:10+00:00", "user_id": "analyst", "tool_name": "send_enterprise_document", "outcome": "consumed", "details": {"approval_id": "apr_demo", "destination": "partner@example.com"}, "event_type": "approval_consumption", "resource_id": "finance_report.txt"}
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % 
```

    18:00:00  approval requested
              expires 18:05:00

    18:00:30  security_operator approves

    18:01:00  agent attempts destination substitution
              partner@example.com → attacker@example.com
              BLOCKED

    18:01:10  exact approved action is consumed
              SUCCESS

````
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp %
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % python -m pytest -q
........................                                                                                              [100%]
24 passed in 1.52s
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % 

```
