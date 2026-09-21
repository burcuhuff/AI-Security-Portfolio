#server/tools/search_documents.py
from server.security.trust_boundary import TRUSTED_DOCUMENTS_DIR


def search_documents(query: str) -> list[dict]:
    """
    Search trusted enterprise documents for matching text.

    Quarantined or otherwise untrusted documents are intentionally
    excluded from search.
    """

    query = query.lower().strip()
    results = []

    for file_path in TRUSTED_DOCUMENTS_DIR.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")

        if query in content.lower():
            results.append(
                {
                    "document_id": file_path.name,
                    "name": file_path.stem,
                }
            )

    return results