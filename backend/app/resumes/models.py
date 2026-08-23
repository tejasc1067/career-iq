"""Resume ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

ORIGINAL_FILENAME_MAX_LENGTH = 255
STORED_PATH_MAX_LENGTH = 255
CONTENT_TYPE_MAX_LENGTH = 100


class Resume(Base):
    """A resume file a user has uploaded.

    The row holds metadata only; the bytes live on the filesystem under the
    configured storage root. `stored_path` is relative to that root and is
    built entirely from server-generated identifiers, so `original_filename`
    is never part of a filesystem path.
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
