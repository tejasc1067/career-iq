"""Resume ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

ORIGINAL_FILENAME_MAX_LENGTH = 255
STORED_PATH_MAX_LENGTH = 255
CONTENT_TYPE_MAX_LENGTH = 100
PARSE_STATUS_MAX_LENGTH = 20
PARSE_ERROR_MAX_LENGTH = 200

SECTION_KIND_MAX_LENGTH = 30
SECTION_HEADING_MAX_LENGTH = 60

PARSE_STATUS_PENDING = "pending"
PARSE_STATUS_PARSED = "parsed"
PARSE_STATUS_FAILED = "failed"


class Resume(Base):
    """A resume file a user has uploaded.

    The file itself lives on the filesystem under the configured storage root.
    `stored_path` is relative to that root and is built entirely from
    server-generated identifiers, so `original_filename` is never part of a
    filesystem path.

    `extracted_text` holds the text pulled out of the file. It is sensitive
    career information, so it is never returned by the API and never logged.
    """

    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(ORIGINAL_FILENAME_MAX_LENGTH))
    stored_path: Mapped[str] = mapped_column(String(STORED_PATH_MAX_LENGTH))
    content_type: Mapped[str] = mapped_column(String(CONTENT_TYPE_MAX_LENGTH))
    byte_size: Mapped[int] = mapped_column(BigInteger)
    parse_status: Mapped[str] = mapped_column(
        String(PARSE_STATUS_MAX_LENGTH), server_default=PARSE_STATUS_PENDING
    )
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parse_error: Mapped[str | None] = mapped_column(
        String(PARSE_ERROR_MAX_LENGTH), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ResumeSection(Base):
    """One section detected in a resume's extracted text.

    Rows are derived data: they are replaced whenever the resume's text is
    extracted again, and they belong to the resume, so deleting the resume or
    the account removes them with it.
    """

    __tablename__ = "resume_sections"
    __table_args__ = (UniqueConstraint("resume_id", "position"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(SECTION_KIND_MAX_LENGTH))
    heading: Mapped[str | None] = mapped_column(
        String(SECTION_HEADING_MAX_LENGTH), nullable=True
    )
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
