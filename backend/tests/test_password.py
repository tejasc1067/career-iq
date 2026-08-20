"""Tests for password hashing."""

import pytest

from app.auth.password import hash_password, verify_password

PASSWORD = "correct horse battery staple"


def test_hashing_produces_an_argon2id_hash() -> None:
    """A password hashes to a PHC-format Argon2id string."""
    hashed = hash_password(PASSWORD)

    assert hashed.startswith("$argon2id$")


def test_hash_is_not_the_plaintext() -> None:
    """The plaintext must not appear in or equal the stored hash."""
    hashed = hash_password(PASSWORD)

    assert hashed != PASSWORD
    assert PASSWORD not in hashed


def test_same_password_hashes_differently_because_of_salting() -> None:
    """Each hash uses a fresh random salt, so digests differ."""
    first = hash_password(PASSWORD)
    second = hash_password(PASSWORD)

    assert first != second
    assert verify_password(PASSWORD, first)
    assert verify_password(PASSWORD, second)


def test_correct_password_verifies() -> None:
    """The right password verifies against its own hash."""
    assert verify_password(PASSWORD, hash_password(PASSWORD)) is True


@pytest.mark.parametrize(
    "wrong",
    ["", "wrong password", PASSWORD.upper(), PASSWORD + " ", " " + PASSWORD],
)
def test_incorrect_password_fails(wrong: str) -> None:
    """A wrong password does not verify, including near misses."""
    assert verify_password(wrong, hash_password(PASSWORD)) is False


@pytest.mark.parametrize(
    "malformed",
    [
        "",
        "not-a-hash",
        "$argon2id$",
        "$argon2id$v=19$m=65536,t=3,p=4$YWJjZGVmZ2g$dHJ1bmNhdGVk",
        "$2b$12$abcdefghijklmnopqrstuv",
        "$unknown$v=1$foo",
    ],
)
def test_malformed_hash_is_rejected_without_raising(malformed: str) -> None:
    """A malformed or foreign hash returns False rather than raising."""
    assert verify_password(PASSWORD, malformed) is False


def test_verification_failure_leaks_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    """A failed verification writes neither the password nor the hash anywhere."""
    hashed = hash_password(PASSWORD)

    assert verify_password("wrong", hashed) is False
    assert verify_password(PASSWORD, "not-a-hash") is False

    captured = capsys.readouterr()
    assert PASSWORD not in captured.out + captured.err
    assert hashed not in captured.out + captured.err
