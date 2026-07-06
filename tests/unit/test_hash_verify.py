from backend.evidence.hash_verify import hashes_match, sha256_of_bytes


def test_same_content_same_hash():
    assert sha256_of_bytes(b"abc") == sha256_of_bytes(b"abc")


def test_different_content_different_hash():
    assert sha256_of_bytes(b"abc") != sha256_of_bytes(b"abd")


def test_hashes_match_is_case_insensitive():
    h = sha256_of_bytes(b"abc")
    assert hashes_match(h, h.upper())


def test_hashes_match_false_for_mismatch():
    assert not hashes_match(sha256_of_bytes(b"abc"), sha256_of_bytes(b"xyz"))
