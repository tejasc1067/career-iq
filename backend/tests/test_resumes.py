"""Tests for the resume upload and management endpoints."""

import io
import os
import uuid
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password
from app.auth.tokens import ACCESS_TOKEN_TYPE, create_access_token
from app.common.config import get_settings
from app.resumes import router as resume_router
from app.resumes.models import ORIGINAL_FILENAME_MAX_LENGTH, Resume
from app.resumes.storage import DOCX_EXTENSION, PDF_EXTENSION
from app.users.models import User

RESUMES_URL = "/api/resumes"
PASSWORD = "correct horse battery staple"
PDF_CONTENT_TYPE = "application/pdf"
DOCX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
PDF_BYTES = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n%%EOF\n"


def _docx_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as package:
        package.writestr("[Content_Types].xml", "<Types/>")
        package.writestr("word/document.xml", "<document/>")
    return buffer.getvalue()


def _plain_zip_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as package:
        package.writestr("notes.txt", "not a resume")
    return buffer.getvalue()


async def _user(session: AsyncSession, email: str = "member@example.com") -> User:
    user = User(email=email, password_hash=hash_password(PASSWORD))
    session.add(user)
    await session.commit()
    return user


def _auth(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _signed(claims: dict, secret: str | None = None) -> str:
    settings = get_settings()
    return jwt.encode(
        claims,
        secret or settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def _base_claims(user_id: uuid.UUID, issued_at: datetime) -> dict:
    return {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=15),
        "type": ACCESS_TOKEN_TYPE,
        "jti": uuid.uuid4().hex,
    }


def _pdf_upload(filename: str = "resume.pdf") -> dict:
    return {"file": (filename, PDF_BYTES, PDF_CONTENT_TYPE)}


def _stored_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


async def _upload_pdf(
    client: AsyncClient, user: User, filename: str = "resume.pdf"
) -> dict:
    response = await client.post(
        RESUMES_URL, files=_pdf_upload(filename), headers=_auth(user)
    )
    assert response.status_code == 201
    return response.json()


async def _row(session: AsyncSession, resume_id: str) -> Resume | None:
    return await session.scalar(select(Resume).where(Resume.id == uuid.UUID(resume_id)))


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("post", RESUMES_URL),
        ("get", RESUMES_URL),
        ("get", f"{RESUMES_URL}/{uuid.uuid4()}"),
        ("delete", f"{RESUMES_URL}/{uuid.uuid4()}"),
    ],
)
async def test_every_endpoint_requires_a_token(
    api_client: AsyncClient, method: str, path: str, storage_root: Path
) -> None:
    """No token means no resource lookup and no file written."""
    response = await api_client.request(method, path)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert _stored_files(storage_root) == []


@pytest.mark.parametrize(
    "header",
    [
        {"Authorization": "Bearer not-a-token"},
        {"Authorization": "Bearer "},
        {"Authorization": "Basic bWVtYmVyOnBhc3N3b3Jk"},
        {"Authorization": "not-even-a-scheme"},
    ],
)
async def test_a_malformed_credential_is_rejected(
    api_client: AsyncClient, header: dict[str, str]
) -> None:
    """Garbage in the Authorization header never reaches the database."""
    response = await api_client.get(RESUMES_URL, headers=header)

    assert response.status_code == 401


async def test_an_expired_token_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A token past its expiry cannot upload."""
    user = await _user(db_session)
    past = datetime.now(UTC) - timedelta(hours=2)
    token = _signed(_base_claims(user.id, past))

    response = await api_client.post(
        RESUMES_URL, files=_pdf_upload(), headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_a_token_signed_with_another_secret_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """A forged signature is rejected even when every claim looks correct."""
    user = await _user(db_session)
    token = _signed(_base_claims(user.id, datetime.now(UTC)), secret="a" * 48)

    response = await api_client.post(
        RESUMES_URL, files=_pdf_upload(), headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert _stored_files(storage_root) == []


async def test_a_token_for_an_unknown_user_is_rejected(api_client: AsyncClient) -> None:
    """A validly signed token whose subject no longer exists grants nothing."""
    token = _signed(_base_claims(uuid.uuid4(), datetime.now(UTC)))

    response = await api_client.get(
        RESUMES_URL, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_uploading_a_pdf_stores_the_file_and_its_metadata(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """A valid PDF is written under the caller's own directory."""
    user = await _user(db_session)

    response = await api_client.post(
        RESUMES_URL, files=_pdf_upload(), headers=_auth(user)
    )

    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "resume.pdf"
    assert body["content_type"] == PDF_CONTENT_TYPE
    assert body["byte_size"] == len(PDF_BYTES)

    stored = await _row(db_session, body["id"])
    assert stored is not None
    assert stored.user_id == user.id
    assert stored.stored_path == f"{user.id}/{body['id']}{PDF_EXTENSION}"

    on_disk = storage_root / str(user.id) / f"{body['id']}{PDF_EXTENSION}"
    assert on_disk.read_bytes() == PDF_BYTES
    assert _stored_files(storage_root) == [on_disk]


async def test_uploading_a_docx_is_accepted(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """A real WordprocessingML package is accepted."""
    user = await _user(db_session)
    content = _docx_bytes()

    response = await api_client.post(
        RESUMES_URL,
        files={"file": ("resume.docx", content, DOCX_CONTENT_TYPE)},
        headers=_auth(user),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["content_type"] == DOCX_CONTENT_TYPE
    assert body["byte_size"] == len(content)
    assert (
        storage_root / str(user.id) / f"{body['id']}{DOCX_EXTENSION}"
    ).read_bytes() == content


async def test_the_stored_filename_is_server_generated(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """The name on disk comes from UUIDs, never from the client's filename."""
    user = await _user(db_session)

    body = await _upload_pdf(api_client, user, "My Résumé (final) v2.pdf")

    stored = await _row(db_session, body["id"])
    assert stored is not None
    assert stored.original_filename == "My Résumé (final) v2.pdf"
    assert "Résumé" not in stored.stored_path
    assert _stored_files(storage_root) == [
        storage_root / str(user.id) / f"{body['id']}{PDF_EXTENSION}"
    ]


async def test_the_stored_file_is_not_world_readable(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """The file is created 0600 where the platform supports it."""
    user = await _user(db_session)

    body = await _upload_pdf(api_client, user)

    on_disk = storage_root / str(user.id) / f"{body['id']}{PDF_EXTENSION}"
    assert oct(on_disk.stat().st_mode & 0o777) == oct(0o600)


async def test_the_response_never_exposes_the_storage_path(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """Clients learn nothing about the filesystem or the file's contents."""
    user = await _user(db_session)

    response = await api_client.post(
        RESUMES_URL, files=_pdf_upload(), headers=_auth(user)
    )

    assert set(response.json()) == {
        "id",
        "original_filename",
        "content_type",
        "byte_size",
        "parse_status",
        "parse_error",
        "created_at",
        "updated_at",
    }
    assert str(storage_root) not in response.text
    assert "stored_path" not in response.text
    assert "extracted_text" not in response.text
    assert "%PDF" not in response.text


@pytest.mark.parametrize(
    "upload",
    [
        pytest.param({"file": ("resume.txt", PDF_BYTES, "text/plain")}, id="extension"),
        pytest.param(
            {"file": ("resume.pdf", PDF_BYTES, "text/plain")}, id="content-type"
        ),
        pytest.param({"file": ("resume", PDF_BYTES, PDF_CONTENT_TYPE)}, id="no-suffix"),
        pytest.param(
            {"file": ("resume.pdf", b"this is not a pdf at all", PDF_CONTENT_TYPE)},
            id="pdf-magic-bytes",
        ),
        pytest.param(
            {"file": ("resume.docx", PDF_BYTES, DOCX_CONTENT_TYPE)},
            id="docx-magic-bytes",
        ),
        pytest.param(
            {"file": ("resume.pdf", b"", PDF_CONTENT_TYPE)},
            id="empty",
        ),
    ],
)
async def test_an_unusable_upload_is_rejected_and_leaves_nothing_behind(
    api_client: AsyncClient,
    db_session: AsyncSession,
    storage_root: Path,
    upload: dict,
) -> None:
    """A rejected upload writes no row and no file."""
    user = await _user(db_session)

    response = await api_client.post(RESUMES_URL, files=upload, headers=_auth(user))

    assert response.status_code == 400
    assert (await db_session.scalars(select(Resume))).all() == []
    assert _stored_files(storage_root) == []


async def test_a_zip_that_is_not_a_word_document_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """A .docx extension on an arbitrary ZIP is not enough to be accepted."""
    user = await _user(db_session)

    response = await api_client.post(
        RESUMES_URL,
        files={"file": ("resume.docx", _plain_zip_bytes(), DOCX_CONTENT_TYPE)},
        headers=_auth(user),
    )

    assert response.status_code == 400
    assert _stored_files(storage_root) == []


async def test_an_oversized_upload_is_rejected(
    api_client: AsyncClient,
    db_session: AsyncSession,
    storage_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The limit is enforced against the bytes read, not against a header."""
    monkeypatch.setenv("MAX_RESUME_UPLOAD_BYTES", str(1024 * 1024))
    get_settings.cache_clear()
    user = await _user(db_session)
    oversized = PDF_BYTES + b"0" * (1024 * 1024)

    response = await api_client.post(
        RESUMES_URL,
        files={"file": ("resume.pdf", oversized, PDF_CONTENT_TYPE)},
        headers=_auth(user),
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Resumes must be 1 MB or smaller."
    assert (await db_session.scalars(select(Resume))).all() == []
    assert _stored_files(storage_root) == []


async def test_an_upload_with_no_file_field_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A request without the file field fails validation."""
    user = await _user(db_session)

    response = await api_client.post(
        RESUMES_URL, data={"note": "no file here"}, headers=_auth(user)
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "filename",
    ["../../etc/passwd.pdf", "..\\..\\windows\\evil.pdf", "/etc/passwd.pdf"],
)
async def test_a_traversal_filename_cannot_escape_the_storage_root(
    api_client: AsyncClient,
    db_session: AsyncSession,
    storage_root: Path,
    filename: str,
) -> None:
    """A path in the filename is reduced to metadata and never used as a path."""
    user = await _user(db_session)

    body = await _upload_pdf(api_client, user, filename)

    stored = await _row(db_session, body["id"])
    assert stored is not None
    assert "/" not in stored.original_filename
    assert "\\" not in stored.original_filename
    assert _stored_files(storage_root) == [
        storage_root / str(user.id) / f"{body['id']}{PDF_EXTENSION}"
    ]


async def test_a_traversal_filename_without_an_allowed_suffix_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """`../../etc/passwd` carries no allowed extension, so it never lands."""
    user = await _user(db_session)

    response = await api_client.post(
        RESUMES_URL,
        files={"file": ("../../etc/passwd", PDF_BYTES, PDF_CONTENT_TYPE)},
        headers=_auth(user),
    )

    assert response.status_code == 400
    assert _stored_files(storage_root) == []


async def test_a_very_long_filename_is_truncated_rather_than_rejected(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A filename longer than the column is stored short, not refused."""
    user = await _user(db_session)

    body = await _upload_pdf(api_client, user, f"{'x' * 400}.pdf")

    stored = await _row(db_session, body["id"])
    assert stored is not None
    assert len(stored.original_filename) == ORIGINAL_FILENAME_MAX_LENGTH


async def test_a_client_supplied_user_id_cannot_change_ownership(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A form field naming another owner is ignored; the token decides."""
    user = await _user(db_session)
    victim = await _user(db_session, email="victim@example.com")

    response = await api_client.post(
        RESUMES_URL,
        files=_pdf_upload(),
        data={"user_id": str(victim.id)},
        headers=_auth(user),
    )

    assert response.status_code == 201
    stored = await _row(db_session, response.json()["id"])
    assert stored is not None
    assert stored.user_id == user.id


async def test_the_orphan_file_is_removed_when_persistence_fails(
    api_client: AsyncClient,
    db_session: AsyncSession,
    storage_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A database failure after the write leaves no file and no row behind."""
    user = await _user(db_session)

    async def failing_commit(self: AsyncSession) -> None:
        raise SQLAlchemyError("commit refused")

    monkeypatch.setattr(AsyncSession, "commit", failing_commit)

    response = await api_client.post(
        RESUMES_URL, files=_pdf_upload(), headers=_auth(user)
    )

    assert response.status_code == 500
    assert response.json()["detail"] == resume_router.SAVE_FAILED_DETAIL
    assert _stored_files(storage_root) == []
    monkeypatch.undo()
    assert (await db_session.scalars(select(Resume))).all() == []


async def test_the_list_returns_only_the_callers_resumes(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Each token sees only the resumes of its own subject."""
    first = await _user(db_session, email="first@example.com")
    second = await _user(db_session, email="second@example.com")
    mine = await _upload_pdf(api_client, first, "mine.pdf")
    theirs = await _upload_pdf(api_client, second, "theirs.pdf")

    seen_by_first = await api_client.get(RESUMES_URL, headers=_auth(first))
    seen_by_second = await api_client.get(RESUMES_URL, headers=_auth(second))

    assert [item["id"] for item in seen_by_first.json()] == [mine["id"]]
    assert [item["id"] for item in seen_by_second.json()] == [theirs["id"]]


async def test_the_list_returns_the_newest_resume_first(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Resumes are ordered by upload time, newest first."""
    user = await _user(db_session)
    older = await _upload_pdf(api_client, user, "older.pdf")
    newer = await _upload_pdf(api_client, user, "newer.pdf")

    now = datetime.now(UTC)
    for offset, body in ((2, older), (1, newer)):
        stored = await _row(db_session, body["id"])
        assert stored is not None
        stored.created_at = now - timedelta(hours=offset)
    await db_session.commit()

    response = await api_client.get(RESUMES_URL, headers=_auth(user))

    assert [item["original_filename"] for item in response.json()] == [
        "newer.pdf",
        "older.pdf",
    ]


async def test_the_list_returns_metadata_only(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """No filesystem path and no file contents reach the client."""
    user = await _user(db_session)
    await _upload_pdf(api_client, user)

    response = await api_client.get(RESUMES_URL, headers=_auth(user))

    assert set(response.json()[0]) == {
        "id",
        "original_filename",
        "content_type",
        "byte_size",
        "parse_status",
        "parse_error",
        "created_at",
        "updated_at",
    }
    assert str(storage_root) not in response.text
    assert "extracted_text" not in response.text
    assert "%PDF" not in response.text


async def test_reading_an_owned_resume_returns_its_metadata(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A user can read back a resume they uploaded."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    response = await api_client.get(f"{RESUMES_URL}/{body['id']}", headers=_auth(user))

    assert response.status_code == 200
    assert response.json() == body


async def test_reading_a_missing_resume_returns_404(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """An identifier that does not exist is a plain not-found."""
    user = await _user(db_session)

    response = await api_client.get(
        f"{RESUMES_URL}/{uuid.uuid4()}", headers=_auth(user)
    )

    assert response.status_code == 404


async def test_another_users_resume_is_indistinguishable_from_a_missing_one(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Reading someone else's resume returns 404, never 403."""
    owner = await _user(db_session, email="owner@example.com")
    intruder = await _user(db_session, email="intruder@example.com")
    body = await _upload_pdf(api_client, owner)

    response = await api_client.get(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(intruder)
    )

    assert response.status_code == 404
    missing = await api_client.get(
        f"{RESUMES_URL}/{uuid.uuid4()}", headers=_auth(intruder)
    )
    assert response.json() == missing.json()


async def test_deleting_a_resume_removes_the_record_and_the_file(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """Deletion is permanent and takes both halves with it."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    response = await api_client.delete(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(user)
    )

    assert response.status_code == 204
    assert await _row(db_session, body["id"]) is None
    assert _stored_files(storage_root) == []


async def test_deleting_one_resume_leaves_the_others_alone(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """Only the named resume is removed, on disk and in the database."""
    user = await _user(db_session)
    doomed = await _upload_pdf(api_client, user, "doomed.pdf")
    kept = await _upload_pdf(api_client, user, "kept.pdf")

    await api_client.delete(f"{RESUMES_URL}/{doomed['id']}", headers=_auth(user))

    assert await _row(db_session, kept["id"]) is not None
    assert _stored_files(storage_root) == [
        storage_root / str(user.id) / f"{kept['id']}{PDF_EXTENSION}"
    ]


async def test_deleting_a_missing_resume_returns_404(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """There is nothing to delete, and nothing is reported about it."""
    user = await _user(db_session)

    response = await api_client.delete(
        f"{RESUMES_URL}/{uuid.uuid4()}", headers=_auth(user)
    )

    assert response.status_code == 404


async def test_a_user_cannot_delete_another_users_resume(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """Another user's resume is untouchable and reported as not found."""
    owner = await _user(db_session, email="owner@example.com")
    intruder = await _user(db_session, email="intruder@example.com")
    body = await _upload_pdf(api_client, owner)

    response = await api_client.delete(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(intruder)
    )

    assert response.status_code == 404
    assert await _row(db_session, body["id"]) is not None
    assert _stored_files(storage_root) == [
        storage_root / str(owner.id) / f"{body['id']}{PDF_EXTENSION}"
    ]


async def test_deleting_a_resume_whose_file_is_already_gone_succeeds(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """A file removed out of band does not block deleting the record."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)
    (storage_root / str(user.id) / f"{body['id']}{PDF_EXTENSION}").unlink()

    response = await api_client.delete(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(user)
    )

    assert response.status_code == 204
    assert await _row(db_session, body["id"]) is None


async def test_a_failed_file_removal_keeps_the_record(
    api_client: AsyncClient,
    db_session: AsyncSession,
    storage_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If the file cannot be removed the deletion is rolled back, not faked."""
    user = await _user(db_session)
    owner_id = user.id
    body = await _upload_pdf(api_client, user)

    def failing_removal(stored_path: str) -> None:
        raise OSError("permission denied")

    monkeypatch.setattr(resume_router, "remove_stored_file", failing_removal)

    response = await api_client.delete(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(user)
    )

    assert response.status_code == 500
    assert response.json()["detail"] == resume_router.DELETE_FAILED_DETAIL
    monkeypatch.undo()
    assert await _row(db_session, body["id"]) is not None
    assert _stored_files(storage_root) == [
        storage_root / str(owner_id) / f"{body['id']}{PDF_EXTENSION}"
    ]


async def test_a_failed_database_delete_keeps_the_file(
    api_client: AsyncClient,
    db_session: AsyncSession,
    storage_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A database failure is reported safely and the file is left in place."""
    user = await _user(db_session)
    owner_id = user.id
    body = await _upload_pdf(api_client, user)

    async def failing_flush(
        self: AsyncSession, *args: object, **kwargs: object
    ) -> None:
        raise SQLAlchemyError("flush refused")

    monkeypatch.setattr(AsyncSession, "flush", failing_flush)

    response = await api_client.delete(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(user)
    )

    assert response.status_code == 500
    assert response.json()["detail"] == resume_router.DELETE_FAILED_DETAIL
    monkeypatch.undo()
    assert _stored_files(storage_root) == [
        storage_root / str(owner_id) / f"{body['id']}{PDF_EXTENSION}"
    ]


async def test_a_failed_commit_leaves_the_record_for_a_second_attempt(
    api_client: AsyncClient,
    db_session: AsyncSession,
    storage_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A commit that fails once the file is gone is safe to retry.

    The rollback restores the record, so the failure is reported rather than
    hidden, the resume stays listed, and deleting it again completes.
    """
    user = await _user(db_session)
    headers = _auth(user)
    body = await _upload_pdf(api_client, user)

    async def failing_commit(self: AsyncSession) -> None:
        raise SQLAlchemyError("commit refused")

    monkeypatch.setattr(AsyncSession, "commit", failing_commit)
    failed = await api_client.delete(f"{RESUMES_URL}/{body['id']}", headers=headers)
    monkeypatch.undo()

    assert failed.status_code == 500
    assert failed.json()["detail"] == resume_router.DELETE_FAILED_DETAIL
    assert await _row(db_session, body["id"]) is not None
    assert _stored_files(storage_root) == []

    retried = await api_client.delete(f"{RESUMES_URL}/{body['id']}", headers=headers)

    assert retried.status_code == 204
    assert await _row(db_session, body["id"]) is None


async def test_a_tampered_storage_path_cannot_delete_outside_the_root(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """A stored path pointing outside the root deletes nothing."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)
    outsider = storage_root.parent / "outsider.pdf"
    outsider.write_bytes(b"not a resume")

    stored = await _row(db_session, body["id"])
    assert stored is not None
    stored.stored_path = f"../{outsider.name}"
    await db_session.commit()

    response = await api_client.delete(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(user)
    )

    assert response.status_code == 500
    assert outsider.exists()
    assert await _row(db_session, body["id"]) is not None


async def test_deleting_a_user_removes_their_resume_records(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The owning foreign key cascades, so no orphan record survives."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    await db_session.delete(user)
    await db_session.commit()

    assert await _row(db_session, body["id"]) is None


async def test_the_storage_root_is_created_with_restrictive_permissions(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """The per-user directory is not readable by other accounts."""
    user = await _user(db_session)
    await _upload_pdf(api_client, user)

    directory = storage_root / str(user.id)
    assert oct(directory.stat().st_mode & 0o077) == oct(0)
    assert os.access(directory, os.R_OK)
