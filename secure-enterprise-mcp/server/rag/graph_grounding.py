"""Deterministic retrieval from a small, governed enterprise knowledge graph."""
from __future__ import annotations

import json
from pathlib import Path
import re

from server.rag.retrieval import Evidence, STOP_WORDS
from server.security import trust_boundary


GRAPH_FILE = "knowledge_graph.json"
MAX_GRAPH_BYTES = 64 * 1024
MAX_GRAPH_NODES = 200
MAX_GRAPH_EDGES = 500


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower())) - STOP_WORDS


def _load_graph() -> tuple[dict[str, dict], list[dict]]:
    """Load only the fixed graph file located inside the trusted corpus."""
    path = trust_boundary.TRUSTED_DOCUMENTS_DIR / GRAPH_FILE
    if not path.exists():
        return {}, []
    if path.is_symlink() or not path.is_file():
        raise ValueError("Knowledge graph must be a regular file")
    if path.resolve().parent != trust_boundary.TRUSTED_DOCUMENTS_DIR.resolve():
        raise ValueError("Knowledge graph is outside the trusted repository")

    raw = path.read_bytes()
    if len(raw) > MAX_GRAPH_BYTES:
        raise ValueError("Knowledge graph exceeds 64 KiB")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict) or set(payload) != {"nodes", "edges"}:
        raise ValueError("Invalid knowledge graph schema")
    nodes, edges = payload["nodes"], payload["edges"]
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Invalid knowledge graph collections")
    if len(nodes) > MAX_GRAPH_NODES or len(edges) > MAX_GRAPH_EDGES:
        raise ValueError("Knowledge graph exceeds demo limits")

    node_map: dict[str, dict] = {}
    for node in nodes:
        if not isinstance(node, dict) or set(node) != {"id", "label", "aliases"}:
            raise ValueError("Invalid knowledge graph node")
        if (not isinstance(node["id"], str) or not node["id"]
                or not isinstance(node["label"], str) or not node["label"]
                or not isinstance(node["aliases"], list)
                or any(not isinstance(alias, str) for alias in node["aliases"])):
            raise ValueError("Invalid knowledge graph node fields")
        if node["id"] in node_map:
            raise ValueError("Duplicate knowledge graph node")
        node_map[node["id"]] = node

    required_edge_fields = {"subject", "predicate", "object", "fact", "source_document"}
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != required_edge_fields:
            raise ValueError("Invalid knowledge graph edge")
        if any(not isinstance(edge[field], str) or not edge[field]
               for field in required_edge_fields):
            raise ValueError("Invalid knowledge graph edge fields")
        if edge["subject"] not in node_map or edge["object"] not in node_map:
            raise ValueError("Knowledge graph edge references an unknown node")
        # Provenance must resolve to a regular trusted text document.
        source = trust_boundary.resolve_trusted_document(edge["source_document"])
        if source.is_symlink() or not source.is_file():
            raise ValueError("Knowledge graph provenance is not a trusted document")
    return node_map, edges


def retrieve_graph_facts(query: str, *, limit: int = 3) -> list[Evidence]:
    """Return graph facts whose governed entity/relationship text matches the query."""
    query_terms = _tokens(query)
    if not query_terms:
        return []
    nodes, edges = _load_graph()
    candidates: list[tuple[int, str, str, str]] = []
    for edge in edges:
        subject = nodes[edge["subject"]]
        obj = nodes[edge["object"]]
        searchable = " ".join([
            subject["label"], *subject["aliases"], edge["predicate"],
            obj["label"], *obj["aliases"], edge["fact"],
        ])
        score = len(query_terms & _tokens(searchable))
        if score:
            relationship = (
                f'{subject["label"]} --{edge["predicate"]}--> {obj["label"]}. '
                f'{edge["fact"]}'
            )
            candidates.append((score, edge["source_document"], edge["subject"], relationship))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2], item[3]))
    return [Evidence(f"G{i}", document_id, fact)
            for i, (_, document_id, _, fact) in enumerate(candidates[:limit], start=1)]
