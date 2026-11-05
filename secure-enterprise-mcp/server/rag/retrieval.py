"""Small lexical retriever for a synthetic trusted corpus; no document ACLs."""
from dataclasses import dataclass
import re

from server.security import trust_boundary

STOP_WORDS = frozenset('a an and are as at be by do does for from how in is it of on or should that the this to what when where which who why with'.split())

@dataclass(frozen=True)
class Evidence:
    source_id: str
    document_id: str
    text: str


def retrieve(query: str) -> list[Evidence]:
    terms = set(re.findall(r'[a-z0-9]+', query.lower())) - STOP_WORDS
    if not terms:
        return []
    candidates = []
    paths = sorted(trust_boundary.TRUSTED_DOCUMENTS_DIR.glob('*.txt'))
    if len(paths) > 100:
        raise ValueError('Demo corpus exceeds 100 documents')
    for path in paths:
        # Do not follow symlinks, including links into quarantine.
        if path.is_symlink() or not path.is_file():
            continue
        safe_path = trust_boundary.resolve_trusted_document(path.name)
        with safe_path.open('rb') as stream:
            raw = stream.read(32769)
        if len(raw) > 32768:
            raise ValueError('Demo document exceeds 32 KiB')
        content = raw.decode('utf-8')
        for start in range(0, len(content), 1200):
            passage = content[start:start + 1200]
            score = len(terms & set(re.findall(r'[a-z0-9]+', passage.lower())))
            if score:
                candidates.append((score, path.name, start, passage))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [Evidence(f'S{i}', name, text)
            for i, (_, name, _, text) in enumerate(candidates[:3], start=1)]
