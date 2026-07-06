import bcrypt

_BCRYPT_ROUNDS = 12


def hash_password(plain_password: str) -> str:
    if not plain_password:
        raise ValueError("Password must not be empty.")
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    if not plain_password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Malformed hash - fail closed.
        return False
