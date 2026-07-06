import pytest

from backend.evidence.file_validator import FileValidationError, validate_upload

ALLOWED_EXT = {"png", "jpg", "txt"}
ALLOWED_MIME = {"image/png", "image/jpeg", "text/plain"}


def test_rejects_disallowed_extension():
    with pytest.raises(FileValidationError):
        validate_upload("malware.exe", b"data", ALLOWED_EXT, ALLOWED_MIME, 1024)


def test_rejects_mismatched_content_type():
    # A binary blob renamed to .txt should not sniff as text/plain.
    with pytest.raises(FileValidationError):
        validate_upload("fake.txt", b"\x4d\x5a\x90\x00" + b"\x00" * 100, ALLOWED_EXT, ALLOWED_MIME, 1024)


def test_rejects_oversized_file():
    with pytest.raises(FileValidationError):
        validate_upload("note.txt", b"x" * 2000, ALLOWED_EXT, ALLOWED_MIME, 1024)


def test_rejects_empty_file():
    with pytest.raises(FileValidationError):
        validate_upload("note.txt", b"", ALLOWED_EXT, ALLOWED_MIME, 1024)


def test_accepts_valid_text_file():
    safe_name, mime = validate_upload("note.txt", b"hello world", ALLOWED_EXT, ALLOWED_MIME, 1024)
    assert safe_name == "note.txt"
    assert mime == "text/plain"


def test_sanitizes_path_traversal_filename():
    safe_name, _ = validate_upload("../../etc/passwd.txt", b"hello", ALLOWED_EXT, ALLOWED_MIME, 1024)
    assert ".." not in safe_name
    assert "/" not in safe_name
