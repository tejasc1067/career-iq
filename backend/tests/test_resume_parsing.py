"""Tests for resume text extraction."""

import io
import logging
import uuid
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password
from app.auth.tokens import ACCESS_TOKEN_TYPE, create_access_token
from app.common.config import get_settings
from app.resumes import parsing
from app.resumes.models import (
    PARSE_STATUS_FAILED,
    PARSE_STATUS_PARSED,
    PARSE_STATUS_PENDING,
    Resume,
)
from app.resumes.parsing import (
    NO_TEXT_DOCX_MESSAGE,
    NO_TEXT_PDF_MESSAGE,
    UNREADABLE_DOCX_MESSAGE,
    UNREADABLE_PDF_MESSAGE,
    normalize_text,
)
from app.users.models import User

RESUMES_URL = "/api/resumes"
PASSWORD = "correct horse battery staple"
PDF_CONTENT_TYPE = "application/pdf"
DOCX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
RESUME_LINES = ["Jane Doe", "Senior Data Engineer", "Python, SQL, Airflow"]
RESUME_TEXT = "\n".join(RESUME_LINES)
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _pdf_bytes(lines: list[str]) -> bytes:
    content = ""
    y = 720
    for line in lines:
        escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        content += f"BT /F1 12 Tf 72 {y} Td ({escaped}) Tj ET\n"
        y -= 18
    stream = content.encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length "
        + str(len(stream)).encode()
        + b" >>\nstream\n"
        + stream
        + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{number} 0 obj\n".encode() + body + b"\nendobj\n")

    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for offset in offsets:
        out.write(f"{offset:010d} 00000 n \n".encode())
    out.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode()
    )
    return out.getvalue()


def _document_xml(body: str) -> str:
    return f'<w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>'


def _paragraph(*runs: str) -> str:
    return "<w:p>" + "".join(f"<w:r>{run}</w:r>" for run in runs) + "</w:p>"


def _text(value: str) -> str:
    return f"<w:t>{value}</w:t>"


def _docx_bytes(document: str | None = None) -> bytes:
    if document is None:
        document = _document_xml(
            "".join(_paragraph(_text(line)) for line in RESUME_LINES)
        )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", "<Types/>")
        package.writestr("word/document.xml", document)
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


async def _upload(
    client: AsyncClient,
    user: User,
    filename: str,
    content: bytes,
    content_type: str,
) -> dict:
    response = await client.post(
        RESUMES_URL,
        files={"file": (filename, content, content_type)},
        headers=_auth(user),
    )
    assert response.status_code == 201
    return response.json()


async def _upload_pdf(
    client: AsyncClient, user: User, lines: list[str] | None = None
) -> dict:
    content = _pdf_bytes(RESUME_LINES if lines is None else lines)
    return await _upload(client, user, "resume.pdf", content, PDF_CONTENT_TYPE)


async def _upload_docx(
    client: AsyncClient, user: User, document: str | None = None
) -> dict:
    return await _upload(
        client, user, "resume.docx", _docx_bytes(document), DOCX_CONTENT_TYPE
    )


async def _row(session: AsyncSession, resume_id: str) -> Resume | None:
    return await session.scalar(select(Resume).where(Resume.id == uuid.UUID(resume_id)))


async def _stored_text(session: AsyncSession, resume_id: str) -> str | None:
    resume = await _row(session, resume_id)
    return resume.extracted_text if resume else None


def _parse_url(resume_id: str) -> str:
    return f"{RESUMES_URL}/{resume_id}/parse"


async def test_uploading_a_text_pdf_extracts_its_text(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A readable PDF is parsed during upload and its text is stored verbatim."""
    user = await _user(db_session)

    body = await _upload_pdf(api_client, user)

    assert body["parse_status"] == PARSE_STATUS_PARSED
    assert body["parse_error"] is None
    assert await _stored_text(db_session, body["id"]) == RESUME_TEXT


async def test_uploading_a_docx_extracts_paragraphs_tables_and_tabs(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Paragraph text, tab separators and table cell text all survive."""
    user = await _user(db_session)
    document = _document_xml(
        _paragraph(_text("Jane Doe"))
        + _paragraph(_text("Senior Data Engineer"), "<w:tab/>", _text("2020-2024"))
        + "<w:tbl><w:tr>"
        + f"<w:tc>{_paragraph(_text('Python'))}</w:tc>"
        + f"<w:tc>{_paragraph(_text('5 years'))}</w:tc>"
        + "</w:tr></w:tbl>"
    )

    body = await _upload_docx(api_client, user, document)

    assert body["parse_status"] == PARSE_STATUS_PARSED
    assert await _stored_text(db_session, body["id"]) == (
        "Jane Doe\nSenior Data Engineer\t2020-2024\nPython\n5 years"
    )


async def test_a_docx_line_break_becomes_a_new_line(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """An explicit break inside a paragraph is kept as a line boundary."""
    user = await _user(db_session)
    document = _document_xml(
        _paragraph(_text("Line one"), "<w:br/>", _text("Line two"))
    )

    body = await _upload_docx(api_client, user, document)

    assert await _stored_text(db_session, body["id"]) == "Line one\nLine two"


async def test_a_pdf_without_text_fails_with_a_scan_message(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """An image-only PDF is a failure with guidance, since there is no OCR."""
    user = await _user(db_session)

    body = await _upload_pdf(api_client, user, lines=[])

    assert body["parse_status"] == PARSE_STATUS_FAILED
    assert body["parse_error"] == NO_TEXT_PDF_MESSAGE
    assert await _stored_text(db_session, body["id"]) is None


async def test_a_docx_without_text_fails_with_a_no_text_message(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """An empty Word document holds nothing to extract."""
    user = await _user(db_session)

    body = await _upload_docx(api_client, user, _document_xml(""))

    assert body["parse_status"] == PARSE_STATUS_FAILED
    assert body["parse_error"] == NO_TEXT_DOCX_MESSAGE


async def test_a_malformed_pdf_is_stored_with_a_failed_status(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """A file that passes the signature check but is broken fails safely."""
    user = await _user(db_session)

    body = await _upload(
        api_client, user, "resume.pdf", b"%PDF-1.4\nnot really a pdf", PDF_CONTENT_TYPE
    )

    assert body["parse_status"] == PARSE_STATUS_FAILED
    assert body["parse_error"] == UNREADABLE_PDF_MESSAGE
    assert _stored_files(storage_root) != []


async def test_a_docx_with_broken_xml_is_stored_with_a_failed_status(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A Word container whose document part is not valid XML fails safely."""
    user = await _user(db_session)

    body = await _upload_docx(api_client, user, "<w:document><w:body>")

    assert body["parse_status"] == PARSE_STATUS_FAILED
    assert body["parse_error"] == UNREADABLE_DOCX_MESSAGE


async def test_a_docx_declaring_a_document_type_is_refused(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A DOCTYPE is where entity-expansion attacks live, so it is not parsed."""
    user = await _user(db_session)
    document = (
        '<?xml version="1.0"?><!DOCTYPE lol [<!ENTITY a "aaaaaaaaaa">]>'
        + _document_xml(_paragraph(_text("&a;")))
    )

    body = await _upload_docx(api_client, user, document)

    assert body["parse_status"] == PARSE_STATUS_FAILED
    assert body["parse_error"] == UNREADABLE_DOCX_MESSAGE


async def test_a_compressed_document_part_larger_than_the_limit_is_refused(
    api_client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A small upload that expands past the limit is not read into memory."""
    monkeypatch.setenv("MAX_RESUME_UPLOAD_BYTES", str(64 * 1024))
    get_settings.cache_clear()
    user = await _user(db_session)
    document = _document_xml(_paragraph(_text("x" * 200_000)))
    content = _docx_bytes(document)
    assert len(content) < 64 * 1024

    body = await _upload_docx(api_client, user, document)

    assert body["parse_status"] == PARSE_STATUS_FAILED
    assert body["parse_error"] == UNREADABLE_DOCX_MESSAGE


async def test_an_unexpected_pdf_parser_error_is_reported_safely(
    api_client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A parser blowing up never reaches the client as parser text."""
    user = await _user(db_session)

    def exploding_reader(*args: object, **kwargs: object) -> object:
        raise RuntimeError("pypdf internal boom")

    monkeypatch.setattr(parsing, "PdfReader", exploding_reader)

    body = await _upload_pdf(api_client, user)

    assert body["parse_status"] == PARSE_STATUS_FAILED
    assert body["parse_error"] == UNREADABLE_PDF_MESSAGE
    assert "boom" not in str(body)
    assert "RuntimeError" not in str(body)


async def test_an_unexpected_docx_parser_error_is_reported_safely(
    api_client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The XML reader failing is handled like any other unreadable file."""
    user = await _user(db_session)

    def exploding_parser(*args: object, **kwargs: object) -> object:
        raise RuntimeError("expat internal boom")

    monkeypatch.setattr(ElementTree, "fromstring", exploding_parser)

    body = await _upload_docx(api_client, user)

    assert body["parse_status"] == PARSE_STATUS_FAILED
    assert body["parse_error"] == UNREADABLE_DOCX_MESSAGE
    assert "boom" not in str(body)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a\r\nb\rc", "a\nb\nc"),
        ("a\n\n\n\n\nb", "a\n\nb"),
        ("  \n\nJane Doe  \n\n  ", "Jane Doe"),
        ("Role\tDates\nNext", "Role\tDates\nNext"),
        ("a\n\nb", "a\n\nb"),
        ("C++ / C#  &  Go", "C++ / C#  &  Go"),
    ],
)
def test_normalization_is_faithful_to_the_document(raw: str, expected: str) -> None:
    """Line endings and blank runs are tidied; content is left alone."""
    assert normalize_text(raw) == expected


async def test_reparsing_a_repaired_file_completes(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """Retry reads the stored file again rather than repeating a stale result."""
    user = await _user(db_session)
    headers = _auth(user)
    body = await _upload(
        api_client, user, "resume.pdf", b"%PDF-1.4\nbroken", PDF_CONTENT_TYPE
    )
    assert body["parse_status"] == PARSE_STATUS_FAILED

    resume = await _row(db_session, body["id"])
    assert resume is not None
    (storage_root / resume.stored_path).write_bytes(_pdf_bytes(RESUME_LINES))

    response = await api_client.post(_parse_url(body["id"]), headers=headers)

    assert response.status_code == 200
    assert response.json()["parse_status"] == PARSE_STATUS_PARSED
    assert response.json()["parse_error"] is None
    assert await _stored_text(db_session, body["id"]) == RESUME_TEXT


async def test_reparsing_a_still_broken_file_stays_failed(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A retry that cannot succeed reports the same failure, not an error."""
    user = await _user(db_session)
    body = await _upload(
        api_client, user, "resume.pdf", b"%PDF-1.4\nbroken", PDF_CONTENT_TYPE
    )

    response = await api_client.post(_parse_url(body["id"]), headers=_auth(user))

    assert response.status_code == 200
    assert response.json()["parse_status"] == PARSE_STATUS_FAILED
    assert response.json()["parse_error"] == UNREADABLE_PDF_MESSAGE


async def test_reparsing_does_not_create_a_second_resume(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Retry replaces the parse result on the existing row."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    await api_client.post(_parse_url(body["id"]), headers=_auth(user))
    await api_client.post(_parse_url(body["id"]), headers=_auth(user))

    rows = (
        await db_session.scalars(select(Resume).where(Resume.user_id == user.id))
    ).all()
    assert len(rows) == 1
    assert str(rows[0].id) == body["id"]


async def test_reparsing_preserves_the_existing_metadata(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Filename, size, type and upload time are untouched by a retry."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    response = await api_client.post(_parse_url(body["id"]), headers=_auth(user))

    reparsed = response.json()
    for field in ("id", "original_filename", "content_type", "byte_size", "created_at"):
        assert reparsed[field] == body[field]


async def test_reparsing_a_resume_whose_file_is_missing_fails_safely(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """A file removed out of band is a failed parse, not a server error."""
    user = await _user(db_session)
    headers = _auth(user)
    body = await _upload_pdf(api_client, user)
    resume = await _row(db_session, body["id"])
    assert resume is not None
    (storage_root / resume.stored_path).unlink()

    response = await api_client.post(_parse_url(body["id"]), headers=headers)

    assert response.status_code == 200
    assert response.json()["parse_status"] == PARSE_STATUS_FAILED
    assert response.json()["parse_error"] == UNREADABLE_PDF_MESSAGE


async def test_the_parse_response_exposes_no_text_or_path(
    api_client: AsyncClient, db_session: AsyncSession, storage_root: Path
) -> None:
    """Retrying returns metadata only, exactly like the other resume reads."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    response = await api_client.post(_parse_url(body["id"]), headers=_auth(user))

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
    assert "Jane Doe" not in response.text
    assert str(storage_root) not in response.text
    assert "stored_path" not in response.text


async def test_extracted_text_is_never_returned_by_the_read_endpoints(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The list and single-resume reads never carry resume contents."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    listed = await api_client.get(RESUMES_URL, headers=_auth(user))
    read = await api_client.get(f"{RESUMES_URL}/{body['id']}", headers=_auth(user))

    for response in (listed, read):
        assert "Jane Doe" not in response.text
        assert "extracted_text" not in response.text


async def test_extracted_text_is_never_logged(
    api_client: AsyncClient, db_session: AsyncSession, caplog: pytest.LogCaptureFixture
) -> None:
    """Parsing a resume writes none of its contents to the log."""
    user = await _user(db_session)

    with caplog.at_level(logging.DEBUG):
        await _upload_pdf(api_client, user)

    assert "Jane Doe" not in caplog.text
    assert "Airflow" not in caplog.text
    assert "%PDF" not in caplog.text


@pytest.mark.parametrize(
    "header",
    [
        None,
        {"Authorization": "Bearer not-a-token"},
        {"Authorization": "Bearer "},
        {"Authorization": "Basic bWVtYmVyOnBhc3N3b3Jk"},
    ],
)
async def test_parsing_rejects_a_missing_or_malformed_credential(
    api_client: AsyncClient, db_session: AsyncSession, header: dict[str, str] | None
) -> None:
    """No usable token means no parse, and no resource lookup."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    response = await api_client.post(_parse_url(body["id"]), headers=header)

    assert response.status_code == 401


async def test_parsing_rejects_an_expired_token(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A token past its expiry cannot trigger parsing."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)
    token = _signed(_base_claims(user.id, datetime.now(UTC) - timedelta(hours=2)))

    response = await api_client.post(
        _parse_url(body["id"]), headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_parsing_rejects_a_token_signed_with_another_secret(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A forged signature is rejected even with correct-looking claims."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)
    token = _signed(_base_claims(user.id, datetime.now(UTC)), secret="a" * 48)

    response = await api_client.post(
        _parse_url(body["id"]), headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_parsing_rejects_a_token_for_an_unknown_user(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A validly signed token whose subject is gone parses nothing."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)
    token = _signed(_base_claims(uuid.uuid4(), datetime.now(UTC)))

    response = await api_client.post(
        _parse_url(body["id"]), headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_a_user_cannot_parse_another_users_resume(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Another user's resume is not found, and its parse state is untouched."""
    owner = await _user(db_session, email="owner@example.com")
    intruder = await _user(db_session, email="intruder@example.com")
    body = await _upload(
        api_client, owner, "resume.pdf", b"%PDF-1.4\nbroken", PDF_CONTENT_TYPE
    )

    response = await api_client.post(_parse_url(body["id"]), headers=_auth(intruder))

    assert response.status_code == 404
    resume = await _row(db_session, body["id"])
    assert resume is not None
    assert resume.parse_status == PARSE_STATUS_FAILED
    assert resume.extracted_text is None


async def test_a_query_user_id_cannot_redirect_a_parse(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Ownership comes from the token, so a query parameter changes nothing."""
    owner = await _user(db_session, email="owner@example.com")
    intruder = await _user(db_session, email="intruder@example.com")
    body = await _upload_pdf(api_client, owner)

    response = await api_client.post(
        f"{_parse_url(body['id'])}?user_id={owner.id}", headers=_auth(intruder)
    )

    assert response.status_code == 404


async def test_parsing_a_missing_resume_returns_404(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """An identifier that does not exist is a plain not-found."""
    user = await _user(db_session)

    response = await api_client.post(_parse_url(str(uuid.uuid4())), headers=_auth(user))

    assert response.status_code == 404


async def test_extracted_text_survives_a_reload_from_the_database(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The text is persisted, not held in the request that produced it."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    db_session.expunge_all()

    assert await _stored_text(db_session, body["id"]) == RESUME_TEXT


async def test_deleting_a_resume_removes_its_extracted_text(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Deletion takes the stored text with the row."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    response = await api_client.delete(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(user)
    )

    assert response.status_code == 204
    assert await _row(db_session, body["id"]) is None
    remaining = (
        await db_session.scalars(
            select(Resume).where(Resume.extracted_text.is_not(None))
        )
    ).all()
    assert remaining == []


async def test_deleting_a_user_removes_their_extracted_text(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The owning foreign key cascades, so no parsed text outlives the account."""
    user = await _user(db_session)
    body = await _upload_pdf(api_client, user)

    await db_session.delete(user)
    await db_session.commit()

    assert await _row(db_session, body["id"]) is None
    assert (await db_session.scalars(select(Resume))).all() == []


def test_pending_is_the_status_for_a_resume_that_was_never_parsed() -> None:
    """The column default matches the state a pre-parsing row is left in."""
    assert Resume.__table__.c.parse_status.server_default.arg == PARSE_STATUS_PENDING


def _stored_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())
