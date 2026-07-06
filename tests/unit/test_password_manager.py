import pytest

from backend.auth.password_manager import hash_password, verify_password


def test_hash_is_not_plaintext():
    hashed = hash_password("Str0ngPass!word")
    assert hashed != "Str0ngPass!word"


def test_verify_correct_password():
    hashed = hash_password("Str0ngPass!word")
    assert verify_password("Str0ngPass!word", hashed)


def test_verify_incorrect_password():
    hashed = hash_password("Str0ngPass!word")
    assert not verify_password("WrongPassword!1", hashed)


def test_hash_password_empty_raises():
    with pytest.raises(ValueError):
        hash_password("")


def test_verify_password_malformed_hash_fails_closed():
    assert not verify_password("anything", "not-a-real-bcrypt-hash")
