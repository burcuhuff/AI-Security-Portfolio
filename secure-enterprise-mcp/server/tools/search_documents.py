#server/tools/search_documents.py
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def search_documents(query: str) -> list[dict]:
    """
    Search local enterprise documents for text matching the query.
    Returns document metadata rather than document contents.
    """

    query = query.lower().strip()
    results = []

    for file_path in DATA_DIR.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")

        if query in content.lower():
            results.append(
                {
                    "document_id": file_path.name,
                    "name": file_path.stem,
                }
            )

    return results