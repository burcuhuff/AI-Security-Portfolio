# client/agent.py
import os
import asyncio
import sys

from mcp import Client, StdioServerParameters


async def main() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "server.mcp_server"],
        env={
            "DEMO_USER": os.getenv("DEMO_USER", "restricted_user"),
        },
    )

    async with Client(server_params) as client:
        print("Connected to server.")

        tools = await client.list_tools()

        print("\nAvailable tools:")
        for tool in tools.tools:
            print(f"-> {tool.name}")

        search_result = await client.call_tool(
            "search_enterprise_documents",
            {"query": "authorization"},
        )

        print("\nSearch result:")
        print(search_result.structured_content)

        matches = search_result.structured_content["result"]

        if not matches:
            print("\nNo matching documents found.")
            return

        document_id = matches[0]["document_id"]

        read_result = await client.call_tool(
            "read_enterprise_document",
            {"document_id": document_id},
        )

        if read_result.is_error:
            print("\nRead tool failed:")
            for block in read_result.content:
                print(block)
            return

        print("\nDocument:")
        print(read_result.structured_content["content"])


if __name__ == "__main__":
    asyncio.run(main())