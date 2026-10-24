import hashlib
import json
import time
from typing import Dict, Any, List, Optional

class AuditEntry:
    def __init__(self, index: int, timestamp: float, event_type: str, tenant: str, payload_summary: str, details: Dict[str, Any], prev_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.event_type = event_type
        self.tenant = tenant
        self.payload_summary = payload_summary
        self.details = details
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        record = {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "tenant": self.tenant,
            "payload_summary": self.payload_summary,
            "details": self.details,
            "prev_hash": self.prev_hash
        }
        serialized = json.dumps(record, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "tenant": self.tenant,
            "payload_summary": self.payload_summary,
            "details": self.details,
            "prev_hash": self.prev_hash,
            "hash": self.hash
        }

class CryptographicAuditLedger:
    def __init__(self):
        self.chain: List[AuditEntry] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = AuditEntry(
            index=0,
            timestamp=time.time(),
            event_type="GENESIS",
            tenant="SYSTEM_SECURE_KERNEL",
            payload_summary="SealedBid Immutable Audit Ledger Initialized",
            details={"security_profile": "HARDENED_ISOLATION_V1", "hash_alg": "SHA-256"},
            prev_hash="0" * 64
        )
        self.chain.append(genesis)

    def record_event(self, event_type: str, tenant: str, payload_summary: str, details: Optional[Dict[str, Any]] = None) -> AuditEntry:
        prev_entry = self.chain[-1]
        new_entry = AuditEntry(
            index=len(self.chain),
            timestamp=time.time(),
            event_type=event_type,
            tenant=tenant,
            payload_summary=payload_summary,
            details=details or {},
            prev_hash=prev_entry.hash
        )
        self.chain.append(new_entry)
        return new_entry

    def verify_integrity(self) -> Dict[str, Any]:
        """Validates that all blocks in the ledger are untampered and hash-consistent."""
        if not self.chain:
            return {"valid": False, "reason": "Empty ledger"}

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            # Verify current block's hash re-calculation
            if current.hash != current.compute_hash():
                return {
                    "valid": False,
                    "tampered_index": current.index,
                    "reason": f"Hash mismatch at block {current.index}"
                }

            # Verify link to previous hash
            if current.prev_hash != prev.hash:
                return {
                    "valid": False,
                    "tampered_index": current.index,
                    "reason": f"Broken chain link between block {prev.index} and {current.index}"
                }

        return {
            "valid": True,
            "total_blocks": len(self.chain),
            "latest_hash": self.chain[-1].hash
        }

    def get_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [entry.to_dict() for entry in self.chain[-limit:]]

# Singleton instance
ledger = CryptographicAuditLedger()
