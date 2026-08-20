"""Password hashing.

Argon2id via argon2-cffi. The salt and cost parameters are encoded in the
returned PHC string, so storing the hash alone is sufficient.

Plaintext passwords must never be logged, persisted, or returned to a client.
"""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Return a salted Argon2id hash of `password`."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Return True when `password` matches `password_hash`.

    Returns False for a wrong password and for a malformed, truncated, or
    unsupported hash. Never raises, and never surfaces the password or the hash
    in an exception or log line.
    """
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHash):
        return False
