# audit_system/audit_logger.py
import json
import hashlib
import datetime
import os
from pathlib import Path

class AuditLogger:
    """
    Audit logger for data access operations:
    
    Each log entry includes a hash of the previous entry,
    creating a chain where any modification to a past entry
    breaks the chain, similar to a blockchain but lightweight.
    
    This directly implements the audit logging requirement
    from Privacy by Design and GDPR Article 30 (records of
    processing activities - https://gdpr-info.eu/art-30-gdpr/).
    """

    def __init__(self, log_path="audit_system/audit_log.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._compute_chain_start()

    def _compute_chain_start(self):
        """Initialize hash chain from existing log or genesis block."""
        if self.log_path.exists() and self.log_path.stat().st_size > 0:
            # Read last entry to continue the chain
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return last_entry.get('entry_hash', 'genesis')
        return 'genesis'

    def _hash_entry(self, entry: dict) -> str:
        """SHA-256 hash of the entry content + previous hash."""
        content = json.dumps(entry, sort_keys=True) + self._last_hash
        return hashlib.sha256(content.encode()).hexdigest()

    def log(self,
            operation: str,
            dataset: str,
            fields_accessed: list,
            purpose: str,
            actor: str = "system",
            row_count: int = None,
            additional_context: dict = None):
        """
        Record a data access or transformation event.

        Args:
            operation: What was done (READ, TRANSFORM, QUERY, SUPPRESS, GENERALIZE)
            dataset: Which dataset was accessed (raw, anonymized, dp_query)
            fields_accessed: List of field names touched
            purpose: Declared purpose for this access
            actor: Who or what performed the operation
            row_count: Number of records affected
            additional_context: Any additional metadata
        """
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "operation": operation,
            "dataset": dataset,
            "fields_accessed": fields_accessed,
            "purpose": purpose,
            "actor": actor,
            "row_count": row_count,
            "context": additional_context or {},
            "previous_hash": self._last_hash
        }

        entry_hash = self._hash_entry(entry)
        entry["entry_hash"] = entry_hash

        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        self._last_hash = entry_hash
        return entry_hash

    def verify_integrity(self):
        """
        Verify the hash chain is unbroken.
        Returns True if log is intact, False if tampering detected.
        """
        if not self.log_path.exists():
            return True

        with open(self.log_path, 'r') as f:
            lines = f.readlines()

        if not lines:
            return True

        previous_hash = 'genesis'
        for i, line in enumerate(lines):
            entry = json.loads(line)
            stored_hash = entry.pop('entry_hash')
            expected_hash = hashlib.sha256(
                (json.dumps(entry, sort_keys=True) + previous_hash).encode()
            ).hexdigest()

            if stored_hash != expected_hash:
                print(f"❌ Integrity violation detected at entry {i+1}")
                print(f"   Timestamp: {entry['timestamp']}")
                print(f"   Expected:  {expected_hash}")
                print(f"   Found:     {stored_hash}")
                return False

            previous_hash = stored_hash

        print(f"✅ Audit log integrity verified — {len(lines)} entries intact")
        return True

    def get_access_report(self):
        """Generate a summary report of all logged operations."""
        if not self.log_path.exists():
            return {}

        operations = {}
        purposes = {}
        fields = {}

        with open(self.log_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                op = entry['operation']
                purpose = entry['purpose']

                operations[op] = operations.get(op, 0) + 1
                purposes[purpose] = purposes.get(purpose, 0) + 1

                for field in entry.get('fields_accessed', []):
                    fields[field] = fields.get(field, 0) + 1

        return {
            "total_entries": sum(operations.values()),
            "operations": operations,
            "purposes": purposes,
            "most_accessed_fields": sorted(
                fields.items(), key=lambda x: x[1], reverse=True
            )[:5]
        }