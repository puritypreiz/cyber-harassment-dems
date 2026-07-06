import pytest

from backend.evidence.qr_generator import build_token
from backend.evidence.qr_verifier import QRVerificationError, parse_and_verify_token


def test_build_and_verify_token(app):
    with app.app_context():
        token = build_token("evidence-1", "case-1", "abc123")
        payload = parse_and_verify_token(token)
        assert payload["evidence_id"] == "evidence-1"
        assert payload["case_id"] == "case-1"
        assert payload["sha256"] == "abc123"


def test_tampered_token_rejected(app):
    with app.app_context():
        token = build_token("evidence-1", "case-1", "abc123")
        tampered = token[:-3] + ("aaa" if not token.endswith("aaa") else "bbb")
        with pytest.raises(QRVerificationError):
            parse_and_verify_token(tampered)


def test_malformed_token_rejected(app):
    with app.app_context():
        with pytest.raises(QRVerificationError):
            parse_and_verify_token("not-a-valid-token")
