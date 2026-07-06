import os

from flask import current_app

from backend.chain_of_custody.audit_log import record as record_audit
from backend.database.database import db
from backend.database.models.evidence import Evidence
from backend.database.models.qr_code import QRCode
from backend.evidence.encryption import decrypt_bytes, encrypt_bytes
from backend.evidence.file_validator import (
    FileValidationError,
    generate_stored_filename,
    resolve_storage_path,
    validate_upload,
)
from backend.evidence.hash_verify import hashes_match, sha256_of_bytes
from backend.evidence.metadata import extract_metadata
from backend.evidence.qr_generator import build_token, generate_qr_image
from backend.utils.constants import AuditAction
from backend.utils.helpers import utcnow


class EvidenceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def upload_evidence(case, uploaded_by, filename: str, file_bytes: bytes, description: str | None,
                     ip_address: str | None) -> Evidence:
    config = current_app.config
    try:
        safe_name, mime_type = validate_upload(
            filename, file_bytes,
            config["ALLOWED_EVIDENCE_EXTENSIONS"], config["ALLOWED_MIME_TYPES"],
            config["MAX_CONTENT_LENGTH"],
        )
    except FileValidationError as exc:
        raise EvidenceError(str(exc)) from exc

    sha256_hash = sha256_of_bytes(file_bytes)
    metadata = extract_metadata(file_bytes, mime_type)

    stored_filename = generate_stored_filename(safe_name)
    storage_path = resolve_storage_path(config["ENCRYPTED_EVIDENCE_DIR"], stored_filename)

    nonce, ciphertext = encrypt_bytes(file_bytes, config["EVIDENCE_ENCRYPTION_KEY"])
    with open(storage_path, "wb") as f:
        f.write(ciphertext)
    os.chmod(storage_path, 0o600)

    evidence = Evidence(
        case_id=case.id,
        uploaded_by_id=uploaded_by.id,
        original_filename=safe_name,
        stored_filename=stored_filename,
        mime_type=mime_type,
        size_bytes=len(file_bytes),
        sha256_hash=sha256_hash,
        encryption_nonce=nonce.hex(),
        description=description,
        captured_metadata=metadata,
        is_verified=True,
    )
    db.session.add(evidence)
    db.session.commit()

    record_audit(
        action=AuditAction.EVIDENCE_UPLOADED,
        actor_id=uploaded_by.id,
        entity_type="evidence",
        entity_id=evidence.id,
        details={"case_id": case.id, "filename": safe_name, "sha256": sha256_hash},
        ip_address=ip_address,
    )

    _generate_qr_for_evidence(evidence)
    return evidence


def _generate_qr_for_evidence(evidence: Evidence) -> QRCode:
    token = build_token(evidence.id, evidence.case_id, evidence.sha256_hash)
    filename = f"{evidence.id}.png"
    generate_qr_image(token, current_app.config["QR_CODE_DIR"], filename)

    qr = QRCode(evidence_id=evidence.id, token=token, image_filename=filename)
    db.session.add(qr)
    db.session.commit()

    record_audit(
        action=AuditAction.QR_GENERATED,
        actor_id=evidence.uploaded_by_id,
        entity_type="evidence",
        entity_id=evidence.id,
        details={"qr_id": qr.id},
    )
    return qr


def decrypt_evidence_bytes(evidence: Evidence) -> bytes:
    config = current_app.config
    storage_path = resolve_storage_path(config["ENCRYPTED_EVIDENCE_DIR"], evidence.stored_filename)
    with open(storage_path, "rb") as f:
        ciphertext = f.read()
    nonce = bytes.fromhex(evidence.encryption_nonce)
    return decrypt_bytes(nonce, ciphertext, config["EVIDENCE_ENCRYPTION_KEY"])


def verify_integrity(evidence: Evidence, actor_id: str | None = None) -> bool:
    """Decrypts the stored file and confirms its hash still matches what was
    recorded at upload time. Any mismatch is logged as a security-relevant event.
    """
    try:
        plaintext = decrypt_evidence_bytes(evidence)
    except Exception:
        evidence.is_verified = False
        db.session.commit()
        record_audit(
            action=AuditAction.EVIDENCE_INTEGRITY_FAILED,
            actor_id=actor_id,
            entity_type="evidence",
            entity_id=evidence.id,
            details={"reason": "decryption_failed"},
        )
        return False

    current_hash = sha256_of_bytes(plaintext)
    is_valid = hashes_match(current_hash, evidence.sha256_hash)
    evidence.is_verified = is_valid
    evidence.last_verified_at = utcnow()
    db.session.commit()

    record_audit(
        action=AuditAction.EVIDENCE_VERIFIED if is_valid else AuditAction.EVIDENCE_INTEGRITY_FAILED,
        actor_id=actor_id,
        entity_type="evidence",
        entity_id=evidence.id,
        details={"expected_sha256": evidence.sha256_hash, "computed_sha256": current_hash},
    )
    return is_valid
