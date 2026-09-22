<p align="center">
  <img src="./.assets/ai-security-portfolio.png"
       alt="AI Security Portfolio"
       width="220">
</p>

<p align="center">
  <strong>
    AI Security & Privacy Engineering Portfolio.
  </strong>
</p>

<p align="center">
  <strong>
    Hands on work across AI security, privacy engineering, secure backend architecture, and enterprise AI systems.
  </strong>
</p>

<p align="center">
  <a href="./secure-enterprise-mcp/README.md">Secure Enterprise MCP</a> •
  <a href="./privacy-hr-pipeline/README.md">Privacy Engineering Portfolio</a> •
  <a href="./capstone/README.md">UC Berkeley MIDS Capstone</a>
</p>

# 

The projects range from production oriented security architecture developed during
my UC Berkeley MIDS capstone to independent implementations exploring secure MCP
tool access, privacy engineering, trust boundaries, sandboxed execution, identity,
authorization, and governance controls.

Each project is documented separately with its architecture, security goals,
implementation decisions, and technical design.


## 1. Secure Enterprise MCP 

A security focused MCP (Model Context Protocol) implementation that explores how enterprise capabilities
can be exposed to AI agents while enforcing controls independently of model behavior.

- **Current security controls:** trusted and quarantined data boundaries,
  scope based authorization, declarative tool policy, fail closed governance,
  path traversal protection, and security audit events
- **Architecture:** MCP client/server over stdio with separate identity,
  authorization, policy, and trusted-data layers
- **Tech stack:** Python, MCP SDK 2.x, YAML

➡️ **[Explore Secure Enterprise MCP](./secure-enterprise-mcp/README.md)**


## 2. Privacy Engineering Portfolio

Independent privacy and security engineering work exploring practical controls
for enterprise systems, including:

- Privacy-aware architecture
- Threat modeling
- Identity and access controls
- Data protection
- Secure system design
- Privacy engineering principles

➡️ **[View the Privacy Engineering Documentation](./privacy-hr-pipeline/README.md)**


## 3. UC Berkeley MIDS Capstone — Secure Agent Execution Architecture

Security and backend architecture developed as part of the UC Berkeley MIDS
capstone project for a platform that executed browser-based AI agent workloads.

My contributions included:

- Sandboxed execution of user-submitted agent code
- Docker-based isolation on EC2
- Auth0 identity integration
- User-scoped S3 storage
- Secret-gated internal services
- Rate limiting and API security
- Execution metadata and evaluation infrastructure

➡️ **[View the Capstone Documentation](./capstone/README.md)**

---
