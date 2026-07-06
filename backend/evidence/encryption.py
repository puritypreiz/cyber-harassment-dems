"""AES-256-GCM encryption for evidence files and other sensitive blobs at rest.

GCM gives us confidentiality plus an authentication tag, so any tampering with the
ciphertext (bit flips, truncation) is detected on decrypt rather than silently
producing corrupted plaintext - important for evidence that may end up in court.
"""
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE_BYTES = 12  # 96-bit nonce, standard for GCM


class DecryptionError(Exception):
    pass


def encrypt_bytes(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    """Returns (nonce, ciphertext_with_tag)."""
    nonce = os.urandom(NONCE_SIZE_BYTES)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, associated_data=None)
    return nonce, ciphertext


def decrypt_bytes(nonce: bytes, ciphertext: bytes, key: bytes) -> bytes:
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, associated_data=None)
    except InvalidTag as exc:
        raise DecryptionError("Decryption failed integrity check - data may be corrupted or tampered with.") from exc


def encrypt_file(plaintext_path: str, encrypted_path: str, key: bytes) -> bytes:
    """Encrypts a file on disk. Returns the nonce (must be persisted for decryption)."""
    with open(plaintext_path, "rb") as f:
        plaintext = f.read()
    nonce, ciphertext = encrypt_bytes(plaintext, key)
    with open(encrypted_path, "wb") as f:
        f.write(ciphertext)
    return nonce


def decrypt_file(encrypted_path: str, output_path: str, nonce: bytes, key: bytes) -> None:
    with open(encrypted_path, "rb") as f:
        ciphertext = f.read()
    plaintext = decrypt_bytes(nonce, ciphertext, key)
    with open(output_path, "wb") as f:
        f.write(plaintext)
