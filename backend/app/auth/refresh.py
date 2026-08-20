"""Refresh token hashing.

Refresh tokens are high-entropy random values, so a single fast one-way hash is
sufficient and — unlike a salted password hash — is deterministic, which is what
makes lookup by hash possible. Generation and rotation are implemented
separately.
"""

import hashlib

TOKEN_HASH_LENGTH = 64


def hash_refresh_token(token: str) -> str:
    """Return the stored form of an opaque refresh token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
