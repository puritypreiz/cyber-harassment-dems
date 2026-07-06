import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

import qrcode
from flask import current_app


def sign_payload(payload_b64: str, signing_key: str) -> str:
    return hmac.new(signing_key.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()


def build_token(evidence_id: str, case_id: str, sha256_hash: str) -> str:
    """Builds a tamper-evident token: base64url(payload).hmac_signature.

    The QR code only ever needs to prove "this evidence record's hash was X at the
    time the QR was generated" - it doesn't need to carry the file itself.
    """
    payload = {
        "evidence_id": evidence_id,
        "case_id": case_id,
        "sha256": sha256_hash,
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("utf-8")
    signature = sign_payload(payload_b64, current_app.config["QR_SIGNING_KEY"])
    return f"{payload_b64}.{signature}"


def generate_qr_image(token: str, output_dir: str, filename: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    img = qrcode.make(token, error_correction=qrcode.constants.ERROR_CORRECT_H)
    path = os.path.join(output_dir, filename)
    img.save(path)
    return path
