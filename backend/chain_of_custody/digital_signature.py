"""RSA digital signatures for chain-of-custody audit entries.

Using asymmetric signatures (rather than a shared HMAC secret) means the server's
public key can be handed to opposing counsel/courts to independently verify that
audit records were produced by this system and have not been altered, without
exposing anything that would let them forge new entries.
"""
import base64
import os
import threading

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

_lock = threading.Lock()
_private_key = None
_public_key = None


def _keys_dir(base_storage_dir: str) -> str:
    path = os.path.join(base_storage_dir, "keys")
    os.makedirs(path, exist_ok=True)
    return path


def _load_or_create_keypair(base_storage_dir: str):
    global _private_key, _public_key
    with _lock:
        if _private_key is not None:
            return _private_key, _public_key

        keys_dir = _keys_dir(base_storage_dir)
        private_path = os.path.join(keys_dir, "custody_signing_private.pem")
        public_path = os.path.join(keys_dir, "custody_signing_public.pem")

        if os.path.exists(private_path):
            with open(private_path, "rb") as f:
                _private_key = serialization.load_pem_private_key(f.read(), password=None)
        else:
            _private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            with open(private_path, "wb") as f:
                f.write(
                    _private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )
            os.chmod(private_path, 0o600)

        _public_key = _private_key.public_key()
        if not os.path.exists(public_path):
            with open(public_path, "wb") as f:
                f.write(_public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))

        return _private_key, _public_key


def sign_data(data: bytes, base_storage_dir: str) -> str:
    private_key, _ = _load_or_create_keypair(base_storage_dir)
    signature = private_key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_signature(data: bytes, signature_b64: str, base_storage_dir: str) -> bool:
    _, public_key = _load_or_create_keypair(base_storage_dir)
    try:
        public_key.verify(
            base64.b64decode(signature_b64),
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def get_public_key_pem(base_storage_dir: str) -> str:
    _, public_key = _load_or_create_keypair(base_storage_dir)
    return public_key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
