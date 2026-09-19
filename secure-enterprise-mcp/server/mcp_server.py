#server/mcp_server.py
import os

from mcp.server import MCPServer

from server.security.auth import authenticate_user
from server.security.authorization import authorize_tool
from server.tools.read_document import read_document
from server.tools.search_documents import search_documents


mcp = MCPServer("Secure Enterprise MCP")

DEMO_USER = os.getenv("DEMO_USER", "restricted_user")
CURRENT_USER = authenticate_user(DEMO_USER)

CURRENT_USER_SCOPES = {
    "documents.search",
    #"documents.read",
}


@mcp.tool()
def search_enterprise_documents(query: str) -> list[dict]:
    """
    Search enterprise documents for text matching the query.
    """
    authorize_tool(
        "search_enterprise_documents",
        CURRENT_USER.scopes,
    )

    return search_documents(query)


@mcp.tool()
def read_enterprise_document(document_id: str) -> dict[str, str]:
    """
    Read an enterprise document.
    """
    authorize_tool(
        "read_enterprise_document",
        CURRENT_USER.scopes,
    )

    return read_document(document_id)

if __name__ == "__main__":
    mcp.run()