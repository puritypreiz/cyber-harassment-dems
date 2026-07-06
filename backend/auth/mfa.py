import pyotp
import qrcode
import qrcode.image.svg
from flask import current_app

from backend.evidence.encryption import decrypt_bytes, encrypt_bytes

_NONCE_LEN = 12


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def encrypt_secret(secret: str) -> bytes:
    key = current_app.config["EVIDENCE_ENCRYPTION_KEY"]
    nonce, ciphertext = encrypt_bytes(secret.encode("utf-8"), key)
    return nonce + ciphertext


def decrypt_secret(blob: bytes) -> str:
    key = current_app.config["EVIDENCE_ENCRYPTION_KEY"]
    nonce, ciphertext = blob[:_NONCE_LEN], blob[_NONCE_LEN:]
    return decrypt_bytes(nonce, ciphertext, key).decode("utf-8")


def build_provisioning_uri(secret: str, account_email: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=account_email, issuer_name="Cyber Harassment DEMS")


def provisioning_qr_svg(uri: str) -> str:
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(uri, image_factory=factory)
    buf = img.to_string()
    if isinstance(buf, bytes):
        return buf.decode("utf-8")
    return buf


def verify_totp_code(secret: str, code: str) -> bool:
    if not code or not code.isdigit():
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
