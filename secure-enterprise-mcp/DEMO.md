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

