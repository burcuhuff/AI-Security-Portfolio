#server/tools/read_document.py
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def read_document(document_id: str) -> dict [str,str]:
    """
    Read the contents of an enterprise document.

    Args:
        document_id: Filename of the document to read.

    Returns:
        Document metadata and content.

    Raises:
        ValueError: If the document ID is invalid.
        FileNotFoundError: If the document does not exist.
    """

    document_id = document_id.strip()

    if not document_id:
        raise ValueError("document_id cannot be empty")

    # Prevent path traversal such as ../../secret.txt
    if Path(document_id).name != document_id:
        raise ValueError("Invalid document_id")

    file_path = (DATA_DIR / document_id).resolve()

    # Ensure the resolved file remains inside DATA_DIR
    if file_path.parent != DATA_DIR.resolve():
        raise ValueError("Document path is outside the allowed data directory")

    if file_path.suffix != ".txt":
        raise ValueError("Only .txt documents are supported")

    if not file_path.is_file():
        raise FileNotFoundError(f"Document not found: {document_id}")

    content = file_path.read_text(encoding="utf-8")

    return {
        "document_id": file_path.name,
        "name": file_path.stem,
        "content": content,
    }