"""Filesystem handling for uploaded resumes.

Every path is built from server-generated UUIDs, per ARCHITECTURE.md section
14: a user-supplied filename is metadata and never a path component. The
storage root lives outside anything the application serves, and no endpoint
returns file contents.
"""

import contextlib
import os
import uuid
import zipfile
from pathlib import Path

from fastapi import UploadFile

from app.common.config import get_settings

PDF_EXTENSION = ".pdf"
DOCX_EXTENSION = ".docx"

ALLOWED_CONTENT_TYPES = {
    PDF_EXTENSION: "application/pdf",
    DOCX_EXTENSION: (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ),
}

PDF_SIGNATURE = b"%PDF-"
ZIP_SIGNATURE = b"PK\x03\x04"
OOXML_CONTENT_TYPES_PART = "[Content_Types].xml"
WORDPROCESSING_PART = "word/document.xml"

CHUNK_SIZE = 64 * 1024
DIRECTORY_MODE = 0o700
FILE_MODE = 0o600


class UploadTooLargeError(Exception):
    """Raised when an upload exceeds the configured size limit."""


class StoragePathError(Exception):
    """Raised when a stored path would resolve outside the storage root."""


def storage_root() -> Path:
    """Return the configured storage root."""
    return get_settings().resume_storage_dir


def display_filename(raw: str | None) -> str:
    """Reduce a client-supplied filename to a safe display value.

    Both separators are stripped so a traversal attempt such as
    `../../etc/passwd` or `..\\windows\\evil.docx` is recorded as a plain name.
    The result is metadata only and is never used to build a path.
    """
    if not raw:
        return ""
    return raw.replace("\\", "/").rsplit("/", 1)[-1].strip()


def extension_of(filename: str) -> str:
    """Return the lowercased extension of a sanitized filename."""
    return Path(filename).suffix.lower()


def relative_path(user_id: uuid.UUID, resume_id: uuid.UUID, extension: str) -> str:
    """Build the storage path for a resume, relative to the storage root."""
    return f"{user_id}/{resume_id}{extension}"


def absolute_path(stored_path: str) -> Path:
    """Resolve a stored path, refusing anything outside the storage root."""
    root = storage_root().resolve()
    resolved = (root / stored_path).resolve()
    if not resolved.is_relative_to(root):
        raise StoragePathError(stored_path)
    return resolved


async def write_upload(upload: UploadFile, stored_path: str, max_bytes: int) -> int:
    """Stream an upload to disk, stopping if it exceeds `max_bytes`.

    The limit is applied to the bytes actually read rather than to
    `Content-Length`, which a client controls and may omit.
    """
    destination = absolute_path(stored_path)
    destination.parent.mkdir(mode=DIRECTORY_MODE, parents=True, exist_ok=True)

    written = 0
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE)
    with os.fdopen(descriptor, "wb") as sink:
        while chunk := await upload.read(CHUNK_SIZE):
            written += len(chunk)
            if written > max_bytes:
                raise UploadTooLargeError(stored_path)
            sink.write(chunk)
    return written


def matches_expected_format(stored_path: str, extension: str) -> bool:
    """Check the stored bytes against the format the extension claims."""
    path = absolute_path(stored_path)
    if extension == PDF_EXTENSION:
        return _starts_with(path, PDF_SIGNATURE)
    return _starts_with(path, ZIP_SIGNATURE) and _is_wordprocessing_package(path)


def _starts_with(path: Path, signature: bytes) -> bool:
    with path.open("rb") as handle:
        return handle.read(len(signature)) == signature


def _is_wordprocessing_package(path: Path) -> bool:
    """Confirm the ZIP is a WordprocessingML package, not an arbitrary archive."""
    try:
        with zipfile.ZipFile(path) as package:
            names = set(package.namelist())
    except (zipfile.BadZipFile, OSError):
        return False
    return OOXML_CONTENT_TYPES_PART in names and WORDPROCESSING_PART in names


def remove_stored_file(stored_path: str) -> None:
    """Delete a stored resume file, tolerating one that is already gone."""
    absolute_path(stored_path).unlink(missing_ok=True)


def discard_stored_file(stored_path: str) -> None:
    """Remove a file written for an upload that will not be persisted."""
    with contextlib.suppress(OSError, StoragePathError):
        remove_stored_file(stored_path)
