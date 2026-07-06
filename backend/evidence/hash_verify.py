import hashlib
import hmac

_CHUNK_SIZE = 1024 * 1024


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_of_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def hashes_match(hash_a: str, hash_b: str) -> bool:
    """Constant-time comparison to avoid timing side-channels."""
    return hmac.compare_digest(hash_a.lower(), hash_b.lower())
