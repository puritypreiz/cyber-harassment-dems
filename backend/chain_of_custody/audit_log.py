import hashlib
import json
from datetime import datetime, timezone

from flask import current_app

from backend.chain_of_custody.digital_signature import sign_data, verify_signature
from backend.database.database import db
from backend.database.models.audit_log import AuditLog


def _normalized_timestamp(dt: datetime) -> str:
    """Strips tzinfo before formatting.

    SQLite has no native timezone-aware datetime type: a value written as UTC-aware
    comes back naive (but still UTC) after a round-trip through the database. Since
    all timestamps in this system are UTC by convention, normalizing to a naive
    isoformat here keeps the canonical representation identical whether the entry
    is hashed immediately after creation or reloaded from the database later.
    """
    return dt.replace(tzinfo=None).isoformat() if dt.tzinfo else dt.isoformat()


def _canonical_bytes(actor_id, action, entity_type, entity_id, details, previous_hash, timestamp: datetime) -> bytes:
    payload = {
        "actor_id": actor_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details or {},
        "previous_entry_hash": previous_hash,
        "timestamp": _normalized_timestamp(timestamp),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def record(action: str, actor_id: str | None, entity_type: str | None = None, entity_id: str | None = None,
           details: dict | None = None, ip_address: str | None = None) -> AuditLog:
    """Appends a tamper-evident entry to the chain-of-custody audit trail.

    Each entry embeds the previous entry's hash (hash-chaining) and is individually
    signed, so any retroactive edit to a historical row breaks verification.
    """
    last_entry = AuditLog.query.order_by(AuditLog.created_at.desc()).first()
    previous_hash = last_entry.entry_hash if last_entry else None

    timestamp = datetime.now(timezone.utc)
    canonical = _canonical_bytes(actor_id, action, entity_type, entity_id, details, previous_hash, timestamp)
    entry_hash = hashlib.sha256(canonical).hexdigest()
    signature = sign_data(entry_hash.encode("utf-8"), current_app.config["STORAGE_DIR"])

    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=ip_address,
        details=details or {},
        previous_entry_hash=previous_hash,
        entry_hash=entry_hash,
        signature=signature,
        created_at=timestamp,
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def verify_entry(entry: AuditLog) -> bool:
    canonical = _canonical_bytes(
        entry.actor_id, entry.action, entry.entity_type, entry.entity_id,
        entry.details, entry.previous_entry_hash, entry.created_at,
    )
    expected_hash = hashlib.sha256(canonical).hexdigest()
    if expected_hash != entry.entry_hash:
        return False
    return verify_signature(entry.entry_hash.encode("utf-8"), entry.signature, current_app.config["STORAGE_DIR"])


def verify_chain(entries: list[AuditLog]) -> list[dict]:
    """Verifies an ordered list of audit entries, including the hash-chain linkage."""
    results = []
    previous_hash = None
    for entry in entries:
        signature_valid = verify_entry(entry)
        chain_valid = entry.previous_entry_hash == previous_hash
        results.append({
            "id": entry.id,
            "action": entry.action,
            "signature_valid": signature_valid,
            "chain_linkage_valid": chain_valid,
        })
        previous_hash = entry.entry_hash
    return results
