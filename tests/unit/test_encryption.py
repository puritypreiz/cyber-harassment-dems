import os

import pytest

from backend.evidence.encryption import DecryptionError, decrypt_bytes, encrypt_bytes


def test_round_trip():
    key = os.urandom(32)
    plaintext = b"sensitive evidence content"
    nonce, ciphertext = encrypt_bytes(plaintext, key)
    assert decrypt_bytes(nonce, ciphertext, key) == plaintext


def test_ciphertext_differs_from_plaintext():
    key = os.urandom(32)
    _, ciphertext = encrypt_bytes(b"hello world", key)
    assert ciphertext != b"hello world"


def test_tampered_ciphertext_fails_integrity_check():
    key = os.urandom(32)
    nonce, ciphertext = encrypt_bytes(b"hello world", key)
    tampered = bytearray(ciphertext)
    tampered[0] ^= 0xFF
    with pytest.raises(DecryptionError):
        decrypt_bytes(nonce, bytes(tampered), key)


def test_wrong_key_fails():
    key1, key2 = os.urandom(32), os.urandom(32)
    nonce, ciphertext = encrypt_bytes(b"hello world", key1)
    with pytest.raises(DecryptionError):
        decrypt_bytes(nonce, ciphertext, key2)
