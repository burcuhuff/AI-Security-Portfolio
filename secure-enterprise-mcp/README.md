# Secure Enterprise MCP

A small security focused MCP project that demonstrates how enterprise tools can be exposed through Model Context Protocol while enforcing identity, least privilege, authorization, and declarative governance controls.

## Overview

This project implements a local MCP client and server that expose document search and document read capabilities. The focus is not just MCP connectivity, but the security controls around tool access.

## Why This Project

Enterprise MCP servers can expose sensitive internal capabilities to AI agents. This project explores how those capabilities can be protected through explicit policy, scope based authorization, and fail closed behavior rather than relying on the model to behave correctly.

## Architecture

The client connects to the MCP server over stdio. The server authenticates a simulated principal, checks tool requirements defined in policy, authorizes the request, and only then invokes the underlying document tool.

## Security Model

Authentication and authorization are kept separate. A simulated identity resolves to a principal with granted scopes, while each MCP tool declares its required scopes through a central policy file.

## MCP Tools

The current implementation exposes two MCP tools:

- `search_enterprise_documents` — searches document contents and returns matching document metadata.
- `read_enterprise_document` — returns the content of a specific document after authorization succeeds.

## Tool Governance Policy

Tool security requirements are defined declaratively in `tool-policy.yaml`, including risk level, required scopes, approval requirements, and audit requirements. Unknown tools fail closed if no policy exists.

## Running the Demo

The demo supports two simulated identities selected through `DEMO_USER`.

### Analyst

Has both `documents.search` and `documents.read` scopes, so both MCP tools succeed.

### Restricted User

Has only `documents.search`, so document discovery succeeds while document reading is denied by the server.

## Security Controls Demonstrated

The current MVP demonstrates least privilege, server side authorization, declarative tool policy, fail closed governance, path traversal protection, controlled subprocess environment propagation, and MCP tool error handling.

## Production Considerations

`DEMO_USER` is intentionally a local identity simulation, not production authentication. A production implementation would validate OAuth/OIDC or Microsoft Entra tokens and derive the principal and scopes from trusted identity claims.

## Roadmap

Planned extensions include audit logging, human approval for sensitive actions, an outbound document tool, indirect prompt-injection testing, exfiltration controls, and a formal threat model.

