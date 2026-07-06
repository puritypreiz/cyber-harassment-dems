from backend.utils.validators import is_strong_password, is_valid_email, is_valid_username


def test_valid_email():
    assert is_valid_email("student@example.org")
    assert not is_valid_email("not-an-email")
    assert not is_valid_email("")


def test_strong_password():
    assert is_strong_password("Str0ngPass!word")
    assert not is_strong_password("weak")
    assert not is_strong_password("alllowercase1!")
    assert not is_strong_password("ALLUPPERCASE1!")
    assert not is_strong_password("NoDigitsHere!")
    assert not is_strong_password("NoSpecialChars1")


def test_valid_username():
    assert is_valid_username("jane_doe")
    assert not is_valid_username("a")
    assert not is_valid_username("has spaces")
