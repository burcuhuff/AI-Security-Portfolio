# Read-only RAG: local handoff

Run from `secure-enterprise-mcp` in your existing virtual environment.
No AWS resources are created by these commands.

## 1. Install and verify

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

## 2. Verify denial without AWS setup

```bash
DEMO_USER=restricted_user python -m client.rag_demo 'What is the incident response process?'
```

Expected: missing `documents.read`, no model invocation, exit status 1.

## 3. Verify no-evidence behavior without AWS setup

```bash
DEMO_USER=analyst python -m client.rag_demo 'volcanoes'
```

Expected: `insufficient_evidence`, no model invocation, exit status 0.

## 4. Configure the live model using your existing local AWS profile

```bash
aws sso login --profile mcp-sandbox
aws sts get-caller-identity --profile mcp-sandbox
export AWS_PROFILE=mcp-sandbox
export AWS_REGION=us-east-1
```

The following model was verified with this project in us-east-1 on November 5,
2026. Availability and permissions must still be checked for another account.

```bash
export BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
```

The application requires explicit model and region configuration.
Do not paste credentials, tokens, or SSO cache files into chat.

Then:

```bash
DEMO_USER=analyst python -m client.rag_demo 'What is the incident response process?'
```

This is a paid model invocation. Only synthetic corpus text and the question are
sent. Inspect the answer against the cited files and record the result in the
walkthrough evaluation table. The model may return invalid JSON or unsupported
claims: response validation handles some errors; answer quality requires review.

## Troubleshooting boundaries

- Missing required scope: application policy, not AWS IAM.
- No evidence: query/retrieval, not a model access failure.
- Configuration error: check model ID and region settings.
- Credential/access error: check local SSO session and model invocation permission.
- Invalid response: inspect the recorded error type and revise/test the contract;
  do not remove authorization or citation checks to make the demo pass.

The tool intentionally suppresses raw provider errors. If an AWS error needs
further diagnosis, reproduce a harmless synthetic request directly with the AWS
SDK/CLI in your local environment. Do not enable sensitive payload logging.


## 5. Container verification (passed November 5, 2026; no AWS credentials needed)

Run from secure-enterprise-mcp with Docker Desktop running:

```bash
docker build -t secure-enterprise-mcp:local .
python scripts/container_smoke.py
```

The existing smoke script verifies the original search/read demo for both identities.
It does not test live RAG generation. Verify the new early-stop paths separately:

```bash
docker run --rm -e DEMO_USER=restricted_user secure-enterprise-mcp:local python -m client.rag_demo 'What is the incident response process?'
docker run --rm -e DEMO_USER=analyst secure-enterprise-mcp:local python -m client.rag_demo volcanoes
```

Expected: first exits 1 with a missing-read-scope denial; second exits 0 with
insufficient_evidence. Both audit model_invoked=false. No AWS credentials are
passed into these containers. These checks do not prove live Bedrock invocation
from a container or from Fargate.
