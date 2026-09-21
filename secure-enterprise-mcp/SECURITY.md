# Security Model

Secure Enterprise MCP is designed around the principle that an AI model must
not be treated as a trusted security boundary.

Security-sensitive decisions such as identity resolution, authorization,
tool access, trust classification, and audit generation are enforced outside
the model at the MCP server and policy layers.

## Security Objectives

The current design aims to enforce the following properties:

1. MCP tools are accessible only when explicitly governed by policy.
2. Tool authorization is enforced server-side.
3. Users receive only the capabilities required by their granted scopes.
4. Unknown tools fail closed.
5. Trusted document tools cannot access quarantined content.
6. File identifiers cannot escape the trusted repository through path traversal.
7. Authorization decisions are auditable.
8. Security controls do not depend on the AI model following instructions.

## Security Design Principle

The core principle of the project is:

- The model may request an action, but the security architecture decides
whether that action is permitted.

- Identity, authorization, policy, trust classification, and auditability remain
outside the model's control.

## Trust Zones

The project currently defines two document trust zones.


### Trust Boundary

    UNTRUSTED / EXTERNAL

            │
            ▼

        QUARANTINE
            │
            │ future inspection / approval
            ▼

    TRUSTED ENTERPRISE DATA
            │
            ▼
        MCP TOOLS

- Crossing from quarantine into trusted storage is considered a trust-elevation
event and will eventually require inspection, policy enforcement, and
approval.

### Identity Model

- The current project uses simulated principals for local testing.

    restricted_user
    documents.search

    analyst
    documents.search
    documents.read

- The simulation exists to exercise authorization behavior without introducing
an external identity provider.

- Production authentication is intentionally out of scope for the current MVP.

- A production implementation would validate OAuth/OIDC or Microsoft Entra
tokens and derive the principal and scopes from trusted claims.

### Authorization Model

- Authorization is scope-based.

- Each MCP tool declares required scopes in tool-policy.yaml.

```
search_enterprise_documents:
  required_scopes:
    - documents.search

read_enterprise_document:
  required_scopes:
    - documents.read
```

- The server compares required scopes against the authenticated or simulated
principal's granted scopes before invoking the underlying tool.

- Authorization therefore occurs independently of:

    * model output
    * prompts
    * client instructions
    * document contents

### Fail-Closed Governance

- An MCP tool without a defined policy is rejected.

- The system does not interpret absence of policy as permission.

    Known tool + required scopes
    → ALLOW

    Known tool + missing scopes
    → DENY

    Unknown tool / missing policy
    → DENY

### Trusted Data Enforcement

- Document tools resolve files only inside the trusted repository.

- To cross the trusted repository boundary, a caller cannot use identifiers such as:
```
../quarantine/untrusted.txt
../../.env
```

### File-Type Policy

- The trusted repository currently supports .txt files only.

- This is intentional.

- Adding parsers for PDF, DOCX, HTML, and other formats increases the attack
surface and will be addressed as part of the inbound sandboxing phase.

- Future external document formats will first enter quarantine and be inspected
before any trusted representation is created.

### Audit and Security Observability

- Authorization decisions are written as structured JSONL security events.

```
{
  "timestamp": "2026-09-21T16:40:28.144936+00:00",
  "user_id": "analyst",
  "tool_name": "read_enterprise_document",
  "outcome": "allowed",
  "details": {
    "required_scopes": ["documents.read"]
  }
}
```

- Denied authorization events are also recorded.

- Audit events intentionally avoid storing complete document contents or other
unnecessary sensitive data.

- Generated audit logs are excluded from Git.

- The audit model will expand as additional trust-boundary events are introduced.

### Threats Addressed

The current implementation directly addresses:

#### Unauthorized tool use

Mitigation:
scope-based authorization and declarative tool policy.

#### Excessive privilege

Mitigation:
separate principals with least-privilege scope sets.

#### Unregistered tool exposure

Mitigation:
fail-closed tool governance.

#### Path traversal

Mitigation:
trusted-directory resolution and filename validation.

#### Untrusted document exposure

Mitigation:
physical separation between trusted and quarantine repositories.

#### Model-driven authorization bypass

Mitigation:
authorization is enforced independently by the MCP server.

### Threats Planned for Later Phases

The following are part of the project roadmap but are not yet fully
implemented:

    malicious external document ingestion
    sandboxed parsing and inspection
    indirect prompt injection
    tool-triggered data exfiltration
    outbound document export
    human approval for sensitive actions
    DLP-style policy checks
    promotion from quarantine to trusted storage
    richer audit and monitoring events
    
### Security Limitations

This project is a security engineering reference implementation, not a
production identity or document-processing platform.

Current limitations include:

    simulated authentication
    local stdio transport
    local filesystem storage
    no cryptographic audit-log integrity
    no production SIEM integration
    no external policy service
    no sandboxed document parser yet
    no malware scanning
    no production approval workflow
    trusted formats currently limited to text files

These limitations are documented intentionally so implemented protections are
not confused with planned capabilities.

