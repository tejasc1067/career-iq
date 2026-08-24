"""Resume ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

ORIGINAL_FILENAME_MAX_LENGTH = 255
STORED_PATH_MAX_LENGTH = 255
CONTENT_TYPE_MAX_LENGTH = 100
PARSE_STATUS_MAX_LENGTH = 20
PARSE_ERROR_MAX_LENGTH = 200

PARSE_STATUS_PENDING = "pending"
PARSE_STATUS_PARSED = "parsed"
PARSE_STATUS_FAILED = "failed"


class Resume(Base):
    """A resume file a user has uploaded.

    The file itself lives on the filesystem under the configured storage root.
    `stored_path` is relative to that root and is built entirely from
    server-generated identifiers, so `original_filename` is never part of a
    filesystem path.

    `extracted_text` holds the text pulled out of the file and
    `structured_resume` what the model understood from it. Both are sensitive
    career information: the text is never returned by the API, and neither is
    ever logged.
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
    structured_resume: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def is_understood(self) -> bool:
        """Whether the model has read this resume."""
        return self.structured_resume is not None
