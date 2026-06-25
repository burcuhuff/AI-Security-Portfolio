# Secure Agent Execution Platform

> A security first backend architecture for safely executing untrusted, user submitted AI agent scripts in a shared multi-tenant environment.

This is a personal documentation of the backend and security architecture I designed and built as part of the [Agent IQ capstone project](https://www.ischool.berkeley.edu/projects/2025/agent-iq-build-and-test-ai-agents-scale) at UC Berkeley's Master of Information and Data Science (MIDS) program, Fall 2025.

Advising Faculty on reviews and feedback: Prof. Daniel Aranki

---

## The problem I was solving

Agent IQ is a platform where users upload and run their own AI agent scripts, testing how well agents navigate websites, complete tasks, and behave across different models and configurations.

The core security question I had to answer: **how do you let users run arbitrary, untrusted code in a shared platform without exposing your infrastructure, leaking credentials to user scripts, or allowing one user to access another user's data?**

This is not a hypothetical threat model. It is the actual attack surface of any platform that executes user submitted code. I identified this risk early in the project, proposed the sandboxed architecture, and built it end-to-end.

---

## Threat model

Before writing a line of implementation code, I defined the threats I was designing against:

| Threat | Risk | Mitigation |
|---|---|---|
| User script reads env vars / credentials | Full infrastructure compromise | Restricted Node VM — no env access |
| User script persists malicious state | Cross-request contamination | Ephemeral containers — destroyed after each run |
| Direct sandbox invocation bypassing API | Unauthorized execution | Shared secret auth between services |
| User accesses another user's data | Multi-tenant data breach | userId-scoped S3 keys via Auth0 identity |
| Client-side AWS access | Credential exposure | All storage proxied through backend — no direct client access |
| Secrets in source control | Long-term credential leakage | Env vars only; `.gitignore` enforced from day one |
| Uncontrolled script input | Injection / privilege escalation | Server-side input validation before sandbox invocation |
| Unbounded executor access | Lateral movement risk | Rate limiting on custom script executor |

---

## Architecture

```
User (browser)
    │
    ▼
Frontend (Next.js / Vercel)
    │  — no direct AWS or sandbox access —
    ▼
Backend API  (Node.js / TypeScript / EC2)
    │  Auth0 JWT validation
    │  Input validation
    │  Run lifecycle management
    │
    ├──────────────────────┐
    ▼                      ▼
Sandbox Executor       Amazon S3
(Node/Express / EC2)   userId-scoped keys
    │  shared secret    Auth0 identity binding
    │  header auth
    ▼
Sandbox Runner
(ephemeral Docker container)
    │  restricted Node VM
    │  no env vars, no host access
    │  explicit config injection only
    ▼
Run result → Backend API → S3 → Databricks analytics
```

---

## What I built — component by component

### 1. Backend API (Node.js / TypeScript)

The central orchestration layer. Every security control in the system flows through here.

- Exposes endpoints for workflow execution, script submission, run status, and result retrieval
- Validates all inputs server side before triggering any downstream execution
- Manages full run lifecycle: unique run ID generation, status tracking (pending → running → completed / failed), metadata capture
- Routes authenticated requests to the sandbox executor — frontend never touches the sandbox directly
- Proxies all S3 operations — no AWS credentials or direct cloud access exposed to clients
- Integrates robots.txt analysis to enforce ethical agent crawling behavior

### 2. Sandbox Executor (Node/Express on EC2)

The internal execution gateway, not exposed to users.

- Accepts POST requests from the backend only
- Authenticates every request via a shared secret header, unauthorized callers are rejected before any execution begins
- Validates inputs and prepares execution context
- Launches a fresh Docker container per request: one run, one container, no shared state

### 3. Sandbox Runner (ephemeral Docker container)

Where user code actually runs, fully isolated.

- Ephemeral: created per execution request, destroyed on completion
- Executes user scripts inside a restricted Node VM
  - No access to environment variables
  - No access to host filesystem
  - No access to credentials or internal network
- Receives only explicitly passed configuration (model, device type, stealth mode, proxy settings)
- Stateless by design — eliminates persistence risk between runs

**Why this matters:** a user submitting a malicious script cannot read secrets, cannot affect other users' runs, and cannot persist anything beyond their own result payload.

### 4. Identity and Multi-Tenancy (Auth0 + Amazon S3)

Every user action is identity bound from authentication through to storage.

- Auth0 handles authentication; user identity derived from the Auth0 `sub` field
- Every S3 object (runs, profiles, project configs) is keyed under `userId`
- Users can only retrieve their own data, access is enforced at the storage key level, not just in application logic
- Supports multiple profiles per user, each tagged with `userId`, `profileId`, and `profileLabel`
- Logical multi-tenancy enforced at every layer: API, storage key structure, and query patterns

### 5. Rate Limiting

Applied to the custom script executor endpoint specifically, the highest risk surface in the platform.

- Prevents abuse of the execution environment through script flooding or resource exhaustion
- Enforced server side, independent of frontend controls

### 6. Operational Security Policy

On day one of the project, before any application code was written, I created a `CONTRIBUTOR_ATTESTATION.md` and drafted the project's security and privacy guidelines. These covered:

- **Data minimization:** use synthetic/demo accounts; no PII in logs or traces
- **Secrets management:** no tokens committed to source control; env vars only; monthly rotation
- **Log retention:** runtime logs deleted within 30 days; deletions logged
- **Incident tracking:** material risks reported within 48 hours
- **Project close-out:** token revocation, log wipe, verified deletion before project archival

This wasn't a compliance exercise. It was a recognition that a platform handling user submitted code and agent traces has real data exposure risk, and that operational hygiene matters as much as architectural controls.

### 7. Analytics Pipeline (Databricks)

- Execution logs written to S3 as structured JSON per run
- Loaded into Databricks as queryable datasets
- Metrics: success rate by model and configuration, latency distributions (p50 / p90 / p99), performance across task types, impact of stealth mode and proxy settings
- Cross account S3 integration required careful credential scoping

---

## Security decisions I made and why

**Ephemeral containers over a persistent sandbox process.**
A persistent sandbox could theoretically be more efficient, but it creates state persistence risk. A compromised or misbehaving script could affect subsequent runs. Per-request container lifecycle was the safer design.

**Shared secret between backend and executor, not open network access.**
The executor runs on EC2 but is not publicly accessible. The shared secret ensures that even if the network perimeter were breached, the executor would reject unauthenticated calls.

**userId-scoped S3 keys, not application layer filtering.**
Relying only on application logic to filter results is a single point of failure. Keying data by userId at the storage layer means a bug in query logic cannot leak another user's data — the keys don't overlap.

**Input validation before sandbox invocation, not inside it.**
Validating inside the sandbox would mean untrusted code has already been partially initialized. Validating at the API layer stops malformed or malicious inputs before they reach the execution environment.

---

## Stack

Node.js · TypeScript · Docker · AWS EC2 · Amazon S3 · Auth0 · Databricks · GitHub Actions CI

---

## Context

This architecture was my individual contribution to the Agent IQ capstone. The security design, threat modeling, sandbox architecture, multi-tenancy, operational security policy, was entirely my own work.

The broader platform included a frontend UI built by a teammate. The full project is documented at the [Berkeley I School project page](https://www.ischool.berkeley.edu/projects/2025/agent-iq-build-and-test-ai-agents-scale).

- Deployed repo: [mqustar/agent-readiness-score-ui](https://github.com/mqustar/agent-readiness-score-ui)
- Original Berkeley org repo: [UC-Berkeley-I-School/w210-fall25-agent-nav-sim](https://github.com/UC-Berkeley-I-School/w210-fall25-agent-nav-sim)

---

*Burcu Huffman · UC Berkeley MIDS '25 · AI Security & Privacy Engineering*
