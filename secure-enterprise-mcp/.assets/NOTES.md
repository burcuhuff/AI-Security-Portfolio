## NOTES

### Docker setup

- .dockerignore
- dockerfile

```
FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app \
    && mkdir /app/logs \
    && chown app:app /app/logs

COPY client/ ./client/
COPY server/ ./server/
COPY data/trusted/ ./data/trusted/

USER app

CMD ["python", "-m", "client.agent"]
```


| Instruction | Purpose | Result |
|-----------|---------|:------:|
| `FROM` | Supplies Linux and Python 3.13 independently of my Mac’s virtual environment | ✅ |
| `WORKDIR` | Runs commands from /app, so Python can find the project modules | ✅ |
| `ENV` | Avoids bytecode files and makes the client’s printed output appear promptly | ✅ |
| Dependency `COPY`+`RUN`| Installs dependencies before copying application code, allowing reuse of that build layer. `RUN` executes while building the image | ✅ |
| User and director setup| Creates a non-root runtime user with permission to write audit logs | ✅ |
| Application `COPY`| Includes the client, server, policy, and trusted sample documents| ✅ |
| `USER`| Runs the application as app | ✅ |
| `CMD`| Starts the client, which launches its MCP server subprocess and defines what starts when the container runs| ✅ |

```
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % docker system df                                               
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          0         0         0B        0B
Containers      0         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     2         0         16.38kB   16.38kB

```

```(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % docker build -t secure-enterprise-mcp:local .```

```
[+] Building 32.0s (13/13) FINISHED                                                                     docker:desktop-linux
 => [internal] load build definition from dockerfile                                                                    0.0s
 => => transferring dockerfile: 528B                                                                                    0.0s
 => [internal] load metadata for docker.io/library/python:3.13-slim-bookworm                                            1.6s
 => [internal] load .dockerignore                                                                                       0.0s
 => => transferring context: 200B                                                                                       0.0s
 => [1/8] FROM docker.io/library/python:3.13-slim-bookworm@sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979  7.2s
 => => resolve docker.io/library/python:3.13-slim-bookworm@sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979  0.0s
 => => sha256:29d8700fe216d98a8d918ecf891265355e2ca697f9c11e8290d00813caaed60d 250B / 250B                              0.1s
 => => sha256:aded561bdc17f79b65ec824282d38146fac0eb9d8951b9a7a4ca462bbea8c21d 14.89MB / 14.89MB                        1.5s
 => => sha256:29a6e787b2e07b2b8a2c88b600812f9f7588374cf74e6f17d696695c8984d900 3.34MB / 3.34MB                          3.0s
 => => sha256:7fd1ebe418b5079d4aa36f416af9b143d127bc75b0155d71cb5fd559b5e04d39 28.25MB / 28.25MB                        5.0s
 => => extracting sha256:7fd1ebe418b5079d4aa36f416af9b143d127bc75b0155d71cb5fd559b5e04d39                               1.1s
 => => extracting sha256:29a6e787b2e07b2b8a2c88b600812f9f7588374cf74e6f17d696695c8984d900                               0.1s
 => => extracting sha256:aded561bdc17f79b65ec824282d38146fac0eb9d8951b9a7a4ca462bbea8c21d                               0.7s
 => => extracting sha256:29d8700fe216d98a8d918ecf891265355e2ca697f9c11e8290d00813caaed60d                               0.0s
 => [internal] load build context                                                                                       0.0s
 => => transferring context: 22.58kB                                                                                    0.0s
 => [2/8] WORKDIR /app                                                                                                  0.3s
 => [3/8] COPY requirements.txt .                                                                                       0.0s
 => [4/8] RUN pip install --no-cache-dir -r requirements.txt                                                           15.8s
 => [5/8] RUN groupadd --gid 10001 app     && useradd --uid 10001 --gid app --no-create-home app     && mkdir /app/log  0.3s 
 => [6/8] COPY client/ ./client/                                                                                        0.0s 
 => [7/8] COPY server/ ./server/                                                                                        0.0s 
 => [8/8] COPY data/trusted/ ./data/trusted/                                                                            0.0s 
 => exporting to image                                                                                                  6.6s 
 => => exporting layers                                                                                                 3.1s 
 => => exporting manifest sha256:50dbc0371a389d0b0672d001e0dba78d5439fc88d011d1b3e972bfb29c97546c                       0.0s
 => => exporting config sha256:159f6089eae3f0ed94e12eb044234a0346712cef99e78be31dab7105553f38ef                         0.0s
 => => exporting attestation manifest sha256:0a105b4441f721e1ba2c5a7e56f3e851d23d90000aa62d9e822f4d925cd9fdac           0.0s
 => => exporting manifest list sha256:00ab6d8341e3fe71697553e58c443a689612b7ebbd570c9aa27fa1fd4ebefe79                  0.0s
 => => naming to docker.io/library/secure-enterprise-mcp:local                                                          0.0s
 => => unpacking to docker.io/library/secure-enterprise-mcp:local                                                       3.4s
 ```

 ``` (venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % docker system df ```
 ```                            
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          1         0         281.3MB   281.3MB (99%)
Containers      0         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     14        0         281.4MB   281.4MB
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % 
```

| Part | Purpose |
|-----------|------|
|```--name``` | Gives each container a name for inspection|
|```-e DEMO_USER=...``` | Sets the demo identity at runtime|
| ```secure-enterprise-mcp:local```|Selects the image we just built |

The image stays the same, the runtime configuration changes. Each container starts the client, which launches the server inside that same container. When the client finishes, the container stops—expected for this one-shot workflow.

``` (venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % docker run --name mcp-analyst -e DEMO_USER=analyst secure-enterprise-mcp:local```
```
Connected to server.

Available tools:
-> search_enterprise_documents
-> read_enterprise_document

Search result:
{'result': [{'document_id': 'normal_document.txt', 'name': 'normal_document'}]}

Document:
Quarterly Security Review

The security engineering team completed its quarterly review
of enterprise AI integrations.

The review covered identity management, authorization,
audit logging, least privilege, and tool access controls.

MCP servers should enforce authorization independently
from instructions generated by an AI model.
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % 
```

```docker run --name mcp-restricted -e DEMO_USER=restricted_user secure-enterprise-mcp:local```

```
Connected to server.

Available tools:
-> search_enterprise_documents
-> read_enterprise_document

Search result:
{'result': [{'document_id': 'normal_document.txt', 'name': 'normal_document'}]}
[10/11/26 15:44:50] INFO     Tool 'read_enterprise_document'       server.py:444
                             failed: "Error executing tool                      
                             read_enterprise_document: Access                   
                             denied. Missing required scopes:                   
                             ['documents.read']"                                

Read tool failed:
type='text' text="Error executing tool read_enterprise_document: Access denied. Missing required scopes: ['documents.read']" annotations=None meta=None
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % 

```

```
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % docker cp mcp-analyst:/app/logs/mcp_audit.jsonl /tmp/mcp-analyst-audit.jsonl
Successfully copied 501B (transferred 2.05kB) to /tmp/mcp-analyst-audit.jsonl
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % docker cp mcp-restricted:/app/logs/mcp_audit.jsonl /tmp/mcp-restricted-audit.jsonl
Successfully copied 515B (transferred 2.56kB) to /tmp/mcp-restricted-audit.jsonl
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % cat /tmp/mcp-analyst-audit.jsonl
{"timestamp": "2026-10-11T15:32:12.220068+00:00", "user_id": "analyst", "tool_name": "search_enterprise_documents", "outcome": "allowed", "details": {"required_scopes": ["documents.search"]}, "event_type": "authorization_decision", "resource_id": null}
{"timestamp": "2026-10-11T15:32:12.327600+00:00", "user_id": "analyst", "tool_name": "read_enterprise_document", "outcome": "allowed", "details": {"required_scopes": ["documents.read"]}, "event_type": "authorization_decision", "resource_id": null}
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % cat /tmp/mcp-restricted-audit.jsonl
{"timestamp": "2026-10-11T15:44:49.947691+00:00", "user_id": "restricted_user", "tool_name": "search_enterprise_documents", "outcome": "allowed", "details": {"required_scopes": ["documents.search"]}, "event_type": "authorization_decision", "resource_id": null}
{"timestamp": "2026-10-11T15:44:50.048398+00:00", "user_id": "restricted_user", "tool_name": "read_enterprise_document", "outcome": "denied", "details": {"missing_scopes": ["documents.read"]}, "event_type": "authorization_decision", "resource_id": null}
(venv) burcu@Burcus-MacBook-Pro secure-enterprise-mcp % 

```


| Step | Build next  | Focuses on |
|---|---|---|
| **1. Container observability** | Emit audit events to stderr while retaining the JSONL file | Application logs, audit evidence, and troubleshooting |
| **2. CI workflow** | Automate tests, image build, and allowed/denied smoke checks | How a change becomes a validated artifact |
| **3. Small AWS deployment with Terraform** | Publish to ECR and run the demo as an on-demand ECS/Fargate task | IAM, networking, image registry versus compute, IaC, and cleanup |
| **4. Local Kubernetes exercise** | Run the same image as a Job; inspect status, logs, and an intentional failure | Pods, Jobs, resource limits, and debugging |

- For now I'll keep AWS usage bounded and avoid a standing EKS cluster. 

- For now, I'll keep stdio wokload - the HTTP transport, a database, and outbound approval integration remain later product steps. 

## An HR document service where users can access permitted information and request controlled exports, with traceable decisions.

| Information | Proposed home | Purpose |
|---|---|---|
| HR documents/datasets | Private object storage, such as S3 | Durable content storage |
| Document permissions, ownership, approval requests | Application database | Shared, durable business state |
| Security audit events | Centralized, access-controlled logging destination | Evidence across users, instances, and restarts |
| Temporary execution files | Isolated execution environment | Disposable working data |

- For the first AWS deployment, we can collect container output centrally. For sensitive exports later, we should design durable recording of the approval and execution intent, including what happens when logging or delivery fails.
- The product needs richer events, not document contents in logs
Our current event says a scope check was allowed or denied. “Authorization allowed” does not prove the document was successfully read or sent.
The product should distinguish:
    - Decision: Who requested which action, against which document, and why it was allowed or denied?
    - Execution: Did that action succeed, fail, or remain pending?
    - Correlation: Which request, approval, and document version connect those events?
- Useful fields would include an event ID, request ID, authenticated user ID, organization ID if applicable, document ID/version, action, outcome, and approval ID. Your current resource_id: null shows one gap we would address.
- We should also remove the demo client’s document-content printing before introducing HR data. Logs need restricted access, defined retention, and protection against modification; credentials, tokens, and unnecessary personal information should stay out of them.

## PLAN as of 1015/26:
1. CI: automate tests, image build, and authorization checks.
2. AWS + Terraform: publish the image and run an on-demand task with centralized logs.
3. Local Kubernetes: run the same demo as a Job, inspect its Pod and logs, set resource requests/limits, and troubleshoot an intentional failure.
4. Product expansion: Auth0, document-level permissions, durable approvals, and controlled exports.

- Kubernetes is an interview learning milestone here, not yet a product requirement. A Job fits our current demo because it runs and exits. A Deployment becomes relevant later for a continuously running HTTP MCP service.
- We’ll also cover how local Kubernetes concepts map to EKS, while being precise that this exercise gives you local Kubernetes hands-on experience—not production EKS ownership.