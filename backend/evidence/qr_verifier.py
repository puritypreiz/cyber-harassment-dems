import base64
import json

from flask import current_app

from backend.evidence.hash_verify import hashes_match
from backend.evidence.qr_generator import sign_payload


class QRVerificationError(Exception):
    pass


def parse_and_verify_token(token: str) -> dict:
    """Verifies the HMAC signature on a QR token and returns its payload.

    Raises QRVerificationError if the token is malformed or the signature does not
    match - i.e. the QR code was forged or edited after issuance.
    """
    try:
        payload_b64, signature = token.rsplit(".", 1)
    except ValueError as exc:
        raise QRVerificationError("Malformed QR token.") from exc

    expected_signature = sign_payload(payload_b64, current_app.config["QR_SIGNING_KEY"])
    if not hashes_match(signature, expected_signature):
        raise QRVerificationError("QR token signature is invalid - this code may have been tampered with.")

    try:
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
    except (ValueError, json.JSONDecodeError) as exc:
        raise QRVerificationError("Malformed QR token payload.") from exc

    for field in ("evidence_id", "case_id", "sha256"):
        if field not in payload:
            raise QRVerificationError("QR token payload is missing required fields.")

    return payload


def verify_against_current_hash(token: str, current_sha256: str) -> dict:
    payload = parse_and_verify_token(token)
    payload["hash_matches_current_file"] = hashes_match(payload["sha256"], current_sha256)
    return payload
