"""Tests for resume section detection."""

import io
import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password
from app.auth.tokens import ACCESS_TOKEN_TYPE, create_access_token
from app.common.config import get_settings
from app.resumes.models import (
    SECTION_HEADING_MAX_LENGTH,
    SECTION_KIND_MAX_LENGTH,
    Resume,
    ResumeSection,
)
from app.resumes.sections import (
    HEADING_MAX_LENGTH,
    KIND_CERTIFICATIONS,
    KIND_CONTACT,
    KIND_EDUCATION,
    KIND_EXPERIENCE,
    KIND_OTHER,
    KIND_PROJECTS,
    KIND_SKILLS,
    KIND_SUMMARY,
    detect_sections,
    heading_kind,
)
from app.users.models import User

RESUMES_URL = "/api/resumes"
PASSWORD = "correct horse battery staple"
PDF_CONTENT_TYPE = "application/pdf"

RESUME_LINES = [
    "Jane Doe",
    "jane@example.com",
    "PROFESSIONAL SUMMARY",
    "Senior data engineer with eight years building pipelines.",
    "WORK EXPERIENCE",
    "Acme Corp - Senior Data Engineer",
    "Built streaming ingestion for 40 sources.",
    "EDUCATION",
    "BSc Computer Science, State University",
    "TECHNICAL SKILLS",
    "Python, SQL, Airflow, dbt",
    "CERTIFICATIONS",
    "AWS Certified Data Engineer",
    "PROJECTS",
    "Airflow operator for dbt",
]
RESUME_TEXT = "\n".join(RESUME_LINES)
EXPECTED_KINDS = [
    KIND_OTHER,
    KIND_SUMMARY,
    KIND_EXPERIENCE,
    KIND_EDUCATION,
    KIND_SKILLS,
    KIND_CERTIFICATIONS,
    KIND_PROJECTS,
]


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
    lines: list[str] | None = None,
    content: bytes | None = None,
) -> dict:
    body = content if content is not None else _pdf_bytes(lines or RESUME_LINES)
    response = await client.post(
        RESUMES_URL,
        files={"file": ("resume.pdf", body, PDF_CONTENT_TYPE)},
        headers=_auth(user),
    )
    assert response.status_code == 201
    return response.json()


def _sections_url(resume_id: str) -> str:
    return f"{RESUMES_URL}/{resume_id}/sections"


def _parse_url(resume_id: str) -> str:
    return f"{RESUMES_URL}/{resume_id}/parse"


async def _stored_sections(
    session: AsyncSession, resume_id: str
) -> list[ResumeSection]:
    rows = await session.scalars(
        select(ResumeSection)
        .where(ResumeSection.resume_id == uuid.UUID(resume_id))
        .order_by(ResumeSection.position)
    )
    return list(rows)


def test_a_full_resume_splits_into_its_sections() -> None:
    """Every documented section kind is detected, in document order."""
    sections = detect_sections(RESUME_TEXT)

    assert [section.kind for section in sections] == EXPECTED_KINDS
    assert sections[0].heading is None
    assert sections[0].content == "Jane Doe\njane@example.com"
    assert sections[1].heading == "PROFESSIONAL SUMMARY"
    assert sections[2].content == (
        "Acme Corp - Senior Data Engineer\nBuilt streaming ingestion for 40 sources."
    )
    assert sections[4].content == "Python, SQL, Airflow, dbt"


def test_a_resume_missing_most_sections_yields_only_what_is_present() -> None:
    """A resume is not assumed to declare every section."""
    sections = detect_sections("EXPERIENCE\nAcme Corp\nSKILLS\nPython, Go")

    assert [section.kind for section in sections] == [KIND_EXPERIENCE, KIND_SKILLS]


def test_sections_keep_the_order_the_resume_uses() -> None:
    """Skills ahead of experience stays that way; order is not normalized."""
    sections = detect_sections("SKILLS\nPython\nEDUCATION\nBSc\nEXPERIENCE\nAcme Corp")

    assert [section.kind for section in sections] == [
        KIND_SKILLS,
        KIND_EDUCATION,
        KIND_EXPERIENCE,
    ]


def test_the_same_kind_can_appear_twice() -> None:
    """Two experience blocks are both kept rather than merged or dropped."""
    sections = detect_sections(
        "PROFESSIONAL EXPERIENCE\nAcme\nWORK HISTORY\nEarlier roles"
    )

    assert [section.kind for section in sections] == [
        KIND_EXPERIENCE,
        KIND_EXPERIENCE,
    ]
    assert [section.heading for section in sections] == [
        "PROFESSIONAL EXPERIENCE",
        "WORK HISTORY",
    ]


@pytest.mark.parametrize("text", ["", "   ", "\n\n\t\n"])
def test_text_without_content_yields_no_sections(text: str) -> None:
    """There is nothing to structure in blank text."""
    assert detect_sections(text) == []


def test_a_resume_without_headings_is_kept_as_one_section() -> None:
    """Unrecognized layouts still produce a section rather than nothing."""
    sections = detect_sections("Jane Doe\nSenior Engineer\nPython and Go")

    assert len(sections) == 1
    assert sections[0].kind == KIND_OTHER
    assert sections[0].heading is None
    assert sections[0].content == "Jane Doe\nSenior Engineer\nPython and Go"


def test_a_declared_section_with_no_body_is_still_recorded() -> None:
    """Which sections a resume declares is information in its own right."""
    sections = detect_sections("EXPERIENCE\nAcme Corp\nCERTIFICATIONS")

    assert [section.kind for section in sections] == [
        KIND_EXPERIENCE,
        KIND_CERTIFICATIONS,
    ]
    assert sections[1].content == ""


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("EXPERIENCE", KIND_EXPERIENCE),
        ("Work Experience", KIND_EXPERIENCE),
        ("PROFESSIONAL EXPERIENCE", KIND_EXPERIENCE),
        ("Employment History:", KIND_EXPERIENCE),
        ("  work history  ", KIND_EXPERIENCE),
        ("— EXPERIENCE —", KIND_EXPERIENCE),
        ("Professional Summary", KIND_SUMMARY),
        ("Objective", KIND_SUMMARY),
        ("Technical Skills", KIND_SKILLS),
        ("Core Competencies", KIND_SKILLS),
        ("Education", KIND_EDUCATION),
        ("Licenses & Certifications", KIND_CERTIFICATIONS),
        ("Certificates", KIND_CERTIFICATIONS),
        ("Selected Projects", KIND_PROJECTS),
        ("Contact Information", KIND_CONTACT),
    ],
)
def test_known_headings_map_to_their_kind(line: str, expected: str) -> None:
    """Case, punctuation, decoration and common wording all resolve."""
    assert heading_kind(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "Skills used on this project include Python and Go",
        "Led the experience design team",
        "Education was funded by a scholarship from the university board",
        "My summary of the project is below",
        "",
        "   ",
        "Acme Corp - Senior Data Engineer",
    ],
)
def test_body_text_is_not_mistaken_for_a_heading(line: str) -> None:
    """Only a line that is nothing but a heading starts a new section."""
    assert heading_kind(line) is None


def test_content_keeps_its_line_breaks_and_loses_padding() -> None:
    """Section bodies are normalized the same way the extracted text is."""
    sections = detect_sections("EXPERIENCE\n\n\nAcme Corp\n\n\n\nBuilt things\n\n")

    assert sections[0].content == "Acme Corp\n\nBuilt things"


async def test_uploading_a_resume_stores_its_detected_sections(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Detection runs with extraction, so sections exist after upload."""
    user = await _user(db_session)

    body = await _upload(api_client, user)

    stored = await _stored_sections(db_session, body["id"])
    assert [row.kind for row in stored] == EXPECTED_KINDS
    assert [row.position for row in stored] == list(range(len(EXPECTED_KINDS)))


async def test_the_sections_endpoint_returns_them_in_document_order(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The caller reads back exactly what was detected."""
    user = await _user(db_session)
    body = await _upload(api_client, user)

    response = await api_client.get(_sections_url(body["id"]), headers=_auth(user))

    assert response.status_code == 200
    payload = response.json()
    assert [section["kind"] for section in payload] == EXPECTED_KINDS
    assert [section["position"] for section in payload] == list(range(7))
    assert payload[1]["heading"] == "PROFESSIONAL SUMMARY"


async def test_the_sections_response_carries_no_internals(
    api_client: AsyncClient, db_session: AsyncSession, storage_root
) -> None:
    """No storage path, no ownership column, no authentication material."""
    user = await _user(db_session)
    body = await _upload(api_client, user)

    response = await api_client.get(_sections_url(body["id"]), headers=_auth(user))

    assert set(response.json()[0]) == {"id", "kind", "heading", "content", "position"}
    assert "resume_id" not in response.text
    assert "user_id" not in response.text
    assert "stored_path" not in response.text
    assert str(storage_root) not in response.text
    assert user.password_hash not in response.text


async def test_a_resume_that_was_never_parsed_has_no_sections(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """An unstructured resume is an empty list, not a missing resource."""
    user = await _user(db_session)
    body = await _upload(api_client, user)
    await db_session.execute(
        ResumeSection.__table__.delete().where(
            ResumeSection.resume_id == uuid.UUID(body["id"])
        )
    )
    await db_session.commit()

    response = await api_client.get(_sections_url(body["id"]), headers=_auth(user))

    assert response.status_code == 200
    assert response.json() == []


async def test_an_unreadable_resume_has_no_sections(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Text that could not be extracted cannot be structured."""
    user = await _user(db_session)

    body = await _upload(api_client, user, content=b"%PDF-1.4\nbroken")

    assert body["parse_status"] == "failed"
    assert await _stored_sections(db_session, body["id"]) == []


async def test_reparsing_replaces_the_sections_without_duplicating_them(
    api_client: AsyncClient, db_session: AsyncSession, storage_root
) -> None:
    """A second detection run leaves one set of sections, not two."""
    user = await _user(db_session)
    headers = _auth(user)
    body = await _upload(api_client, user)
    resume = await db_session.scalar(
        select(Resume).where(Resume.id == uuid.UUID(body["id"]))
    )
    assert resume is not None
    (storage_root / resume.stored_path).write_bytes(_pdf_bytes(["SKILLS", "Rust, Go"]))

    response = await api_client.post(_parse_url(body["id"]), headers=headers)

    assert response.status_code == 200
    stored = await _stored_sections(db_session, body["id"])
    assert [row.kind for row in stored] == [KIND_SKILLS]
    assert [row.position for row in stored] == [0]
    assert stored[0].content == "Rust, Go"


async def test_a_failed_reparse_clears_the_previous_sections(
    api_client: AsyncClient, db_session: AsyncSession, storage_root
) -> None:
    """Structure never outlives the text it was derived from."""
    user = await _user(db_session)
    headers = _auth(user)
    body = await _upload(api_client, user)
    resume = await db_session.scalar(
        select(Resume).where(Resume.id == uuid.UUID(body["id"]))
    )
    assert resume is not None
    (storage_root / resume.stored_path).unlink()

    await api_client.post(_parse_url(body["id"]), headers=headers)

    assert await _stored_sections(db_session, body["id"]) == []


async def test_deleting_a_resume_removes_its_sections(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """The owning foreign key cascades from the resume."""
    user = await _user(db_session)
    body = await _upload(api_client, user)

    response = await api_client.delete(
        f"{RESUMES_URL}/{body['id']}", headers=_auth(user)
    )

    assert response.status_code == 204
    assert await _stored_sections(db_session, body["id"]) == []


async def test_deleting_a_user_removes_every_section_they_owned(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Sections do not outlive the account whose resume produced them."""
    user = await _user(db_session)
    await _upload(api_client, user)

    await db_session.delete(user)
    await db_session.commit()

    assert await db_session.scalar(select(func.count()).select_from(ResumeSection)) == 0


@pytest.mark.parametrize(
    "header",
    [
        None,
        {"Authorization": "Bearer not-a-token"},
        {"Authorization": "Bearer "},
        {"Authorization": "Basic bWVtYmVyOnBhc3N3b3Jk"},
        {"Authorization": "not-even-a-scheme"},
    ],
)
async def test_reading_sections_rejects_a_missing_or_malformed_credential(
    api_client: AsyncClient, db_session: AsyncSession, header: dict[str, str] | None
) -> None:
    """No usable token means no section lookup."""
    user = await _user(db_session)
    body = await _upload(api_client, user)

    response = await api_client.get(_sections_url(body["id"]), headers=header)

    assert response.status_code == 401


async def test_reading_sections_rejects_an_expired_token(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A token past its expiry reads nothing."""
    user = await _user(db_session)
    body = await _upload(api_client, user)
    token = _signed(_base_claims(user.id, datetime.now(UTC) - timedelta(hours=2)))

    response = await api_client.get(
        _sections_url(body["id"]), headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_reading_sections_rejects_a_forged_token(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A signature from another secret is refused despite valid claims."""
    user = await _user(db_session)
    body = await _upload(api_client, user)
    token = _signed(_base_claims(user.id, datetime.now(UTC)), secret="a" * 48)

    response = await api_client.get(
        _sections_url(body["id"]), headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_reading_sections_rejects_a_token_for_an_unknown_user(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A validly signed token whose subject is gone reads nothing."""
    user = await _user(db_session)
    body = await _upload(api_client, user)
    token = _signed(_base_claims(uuid.uuid4(), datetime.now(UTC)))

    response = await api_client.get(
        _sections_url(body["id"]), headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


async def test_a_user_cannot_read_another_users_sections(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Another user's resume is indistinguishable from one that is missing."""
    owner = await _user(db_session, email="owner@example.com")
    intruder = await _user(db_session, email="intruder@example.com")
    body = await _upload(api_client, owner)

    response = await api_client.get(_sections_url(body["id"]), headers=_auth(intruder))
    missing = await api_client.get(
        _sections_url(str(uuid.uuid4())), headers=_auth(intruder)
    )

    assert response.status_code == 404
    assert response.json() == missing.json()
    assert "Jane Doe" not in response.text


async def test_a_query_user_id_cannot_reach_another_users_sections(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Ownership comes from the token, so a query parameter changes nothing."""
    owner = await _user(db_session, email="owner@example.com")
    intruder = await _user(db_session, email="intruder@example.com")
    body = await _upload(api_client, owner)

    response = await api_client.get(
        f"{_sections_url(body['id'])}?user_id={owner.id}", headers=_auth(intruder)
    )

    assert response.status_code == 404


async def test_each_user_reads_only_their_own_sections(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Two accounts with resumes see only their own structure."""
    first = await _user(db_session, email="first@example.com")
    second = await _user(db_session, email="second@example.com")
    mine = await _upload(api_client, first)
    theirs = await _upload(api_client, second, lines=["SKILLS", "Rust only"])

    seen_by_first = await api_client.get(
        _sections_url(mine["id"]), headers=_auth(first)
    )
    seen_by_second = await api_client.get(
        _sections_url(theirs["id"]), headers=_auth(second)
    )

    assert [row["kind"] for row in seen_by_first.json()] == EXPECTED_KINDS
    assert [row["kind"] for row in seen_by_second.json()] == [KIND_SKILLS]
    assert "Rust only" not in seen_by_first.text
    assert "Jane Doe" not in seen_by_second.text


async def test_a_malformed_resume_identifier_is_rejected(
    api_client: AsyncClient, db_session: AsyncSession
) -> None:
    """A path that is not an identifier fails validation, not a lookup."""
    user = await _user(db_session)

    response = await api_client.get(
        f"{RESUMES_URL}/not-a-uuid/sections", headers=_auth(user)
    )

    assert response.status_code == 422


def test_every_detectable_heading_and_kind_fits_its_column() -> None:
    """Detection limits stay inside the widths the table declares."""
    assert HEADING_MAX_LENGTH <= SECTION_HEADING_MAX_LENGTH
    kinds = {
        KIND_CONTACT,
        KIND_SUMMARY,
        KIND_EXPERIENCE,
        KIND_EDUCATION,
        KIND_SKILLS,
        KIND_PROJECTS,
        KIND_CERTIFICATIONS,
        KIND_OTHER,
    }
    assert max(len(kind) for kind in kinds) <= SECTION_KIND_MAX_LENGTH
