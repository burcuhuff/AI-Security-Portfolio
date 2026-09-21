#server/tools/read_document.py
from server.security.trust_boundary import resolve_trusted_document


def read_document(document_id: str) -> dict[str, str]:
    """
    Read a document from the trusted enterprise repository.
    """

    file_path = resolve_trusted_document(document_id)

    if not file_path.is_file():
        raise FileNotFoundError(f"Document not found: {document_id}")

    content = file_path.read_text(encoding="utf-8")

    return {
        "document_id": file_path.name,
        "name": file_path.stem,
        "content": content,
    }