# secure-enterprise-mcp/tests/test_trust_boundary.py
import pytest
import json
import server.security.trust_boundary as trust_boundary
import server.tools.search_documents as search_module
from server.tools.read_document import read_document


def configure_test_directories(tmp_path, monkeypatch):
    trusted_dir = tmp_path / "trusted"
    quarantine_dir = tmp_path / "quarantine"

    trusted_dir.mkdir()
    quarantine_dir.mkdir()

    monkeypatch.setattr(
        trust_boundary,
        "TRUSTED_DOCUMENTS_DIR",
        trusted_dir,
    )

    monkeypatch.setattr(
        trust_boundary,
        "QUARANTINE_DIR",
        quarantine_dir,
    )

    monkeypatch.setattr(
        search_module,
        "TRUSTED_DOCUMENTS_DIR",
        trusted_dir,
    )

    return trusted_dir, quarantine_dir


def test_search_only_returns_trusted_documents(tmp_path, monkeypatch):
    trusted_dir, quarantine_dir = configure_test_directories(
        tmp_path,
        monkeypatch,
    )

    (trusted_dir / "trusted.txt").write_text(
        "Enterprise authorization policy",
        encoding="utf-8",
    )

    (quarantine_dir / "untrusted.txt").write_text(
        "QUARANTINE SECRET TEST",
        encoding="utf-8",
    )

    trusted_results = search_module.search_documents("authorization")
    quarantine_results = search_module.search_documents(
        "QUARANTINE SECRET TEST"
    )

    print(
        "\nTrust boundary search result:"
    )
    print(
        json.dumps(
            {
                "security_property": "trusted_search_isolation",
                "outcome": "passed",
                "trusted_results": trusted_results,
                "quarantine_results": quarantine_results,
            },
            indent=2,
        )
    )

    assert trusted_results == [
        {
            "document_id": "trusted.txt",
            "name": "trusted",
        }
    ]

    assert quarantine_results == []


def test_path_traversal_into_quarantine_is_rejected(
    tmp_path,
    monkeypatch,
):
    configure_test_directories(tmp_path, monkeypatch)

    with pytest.raises(
        ValueError,
        match="Invalid document_id",
    ) as exc_info:
        read_document("../quarantine/untrusted.txt")

    print("\nPath traversal protection result:")
    print(
        json.dumps(
            {
                "security_property": "path_traversal_protection",
                "outcome": "blocked",
                "requested_resource": "../quarantine/untrusted.txt",
                "reason": str(exc_info.value),
            },
            indent=2,
        )
    )


def test_quarantined_document_is_not_readable_as_trusted(
    tmp_path,
    monkeypatch,
):
    _, quarantine_dir = configure_test_directories(
        tmp_path,
        monkeypatch,
    )

    (quarantine_dir / "untrusted.txt").write_text(
        "Untrusted content",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError):
        read_document("untrusted.txt")
        print("\nQuarantine isolation result:")
        print(
            json.dumps(
                {
                    "security_property": "quarantine_isolation",
                    "outcome": "blocked",
                    "requested_resource": "untrusted.txt",
                    "reason": str(exc_info.value),
                },
                indent=2,
            )
        )