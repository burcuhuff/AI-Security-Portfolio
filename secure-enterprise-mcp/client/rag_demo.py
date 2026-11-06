"""Live Bedrock demo through MCP. Run only with synthetic documents."""
import argparse
import asyncio
import json
import os
import sys
from mcp import Client, StdioServerParameters

async def run(query: str) -> int:
    # Explicit allowlist: do not forward unrelated application secrets.
    keys = ('DEMO_USER', 'BEDROCK_MODEL_ID', 'AWS_REGION', 'AWS_PROFILE',
            'AWS_CONFIG_FILE', 'AWS_SHARED_CREDENTIALS_FILE',
            'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN',
            'AWS_CONTAINER_CREDENTIALS_RELATIVE_URI')
    env = {key: os.environ[key] for key in keys if key in os.environ}
    env.setdefault('DEMO_USER', 'restricted_user')
    params = StdioServerParameters(command=sys.executable, args=['-m', 'server.mcp_server'], env=env)
    async with Client(params) as client:
        result = await client.call_tool('answer_enterprise_question', {'query': query})
        if result.is_error:
            print('RAG request failed or was denied.', file=sys.stderr)
            for block in result.content:
                print(block, file=sys.stderr)
            return 1
        if result.structured_content is not None:
            print(json.dumps(result.structured_content, indent=2))
        else:
            for block in result.content:
                if getattr(block, 'text', None):
                    print(block.text)
        return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query')
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.query)))
