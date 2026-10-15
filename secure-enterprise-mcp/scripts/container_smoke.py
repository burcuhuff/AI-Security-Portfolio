#secure-enterprise-mcp/scripts/container_smoke.py
"""
Checks the packaged demo's allowed and denied request paths.
Launches fresh containers. 
Checks the JSON events on stderr and the result on stdout, then removes its own containers. 
"""

import json
import subprocess
import uuid

IMAGE = "secure-enterprise-mcp:local"

def check_identity(user: str, expected_read: str) -> None:
    name = f"mcp-smoke-{uuid.uuid4().hex[:12]}"

    try:
        result = subprocess.run(
            [
                "docker", "run", "--name", name,
                "-e", f"DEMO_USER={user}",
                IMAGE,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"{user}: container failed\n{result.stdout}\n{result.stderr}"
            )

        events = []
        for line in result.stderr.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if isinstance(event, dict):
                if event.get("event_type") == "authorization_decision":
                    events.append(event)

        actual = [
            (event["user_id"], event["tool_name"], event["outcome"])
            for event in events
        ]
        expected = [
            (user, "search_enterprise_documents", "allowed"),
            (user, "read_enterprise_document", expected_read),
        ]

        if actual != expected:
            raise RuntimeError(f"{user}: unexpected audit decisions: {actual}")

        document_returned = "\nDocument:\n" in result.stdout
        read_failed = "\nRead tool failed:\n" in result.stdout

        if expected_read == "allowed":
            if not document_returned or read_failed:
                raise RuntimeError(f"{user}: expected a successful document read")
        else:
            if document_returned or not read_failed:
                raise RuntimeError(f"{user}: expected the read to be denied")
            if "documents.read" not in result.stdout:
                raise RuntimeError(f"{user}: missing expected denial reason")

        print(f"PASS: {user} — search allowed, read {expected_read}")

    finally:
        subprocess.run(
            ["docker", "rm", "-f", name],
            capture_output=True,
            timeout=15,
        )


if __name__ == "__main__":
    check_identity("analyst", "allowed")
    check_identity("restricted_user", "denied")