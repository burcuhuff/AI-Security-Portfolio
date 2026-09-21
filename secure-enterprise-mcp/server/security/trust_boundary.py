# secure-enterprise-mcp/server/security/trust_boundary.py
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

TRUSTED_DOCUMENTS_DIR = DATA_DIR / "trusted"
QUARANTINE_DIR = DATA_DIR / "quarantine"


def resolve_trusted_document(document_id: str) -> Path:
    """
    Resolve a document identifier strictly within the trusted repository.

    Documents outside the trusted repository, including quarantined
    documents, cannot be resolved through this function.
    """

    document_id = document_id.strip()

    if not document_id:
        raise ValueError("document_id cannot be empty")

    # Reject directory traversal or nested paths.
    if Path(document_id).name != document_id:
        raise ValueError("Invalid document_id")

    file_path = (TRUSTED_DOCUMENTS_DIR / document_id).resolve()

    if file_path.parent != TRUSTED_DOCUMENTS_DIR.resolve():
        raise ValueError("Document path is outside the trusted repository")

    if file_path.suffix != ".txt":
        raise ValueError("Only .txt documents are supported")

    return file_path