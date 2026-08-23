"""Resume upload and management endpoints."""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.auth.dependencies import CurrentUserDep
from app.common.config import get_settings
from app.database.session import SessionDep
from app.resumes.models import (
    ORIGINAL_FILENAME_MAX_LENGTH,
    PARSE_STATUS_FAILED,
    PARSE_STATUS_PARSED,
    Resume,
)
from app.resumes.parsing import ResumeParseError, extract_text, unreadable_message
from app.resumes.schemas import ResumeRead
from app.resumes.storage import (
    ALLOWED_CONTENT_TYPES,
    StoragePathError,
    UploadTooLargeError,
    absolute_path,
    discard_stored_file,
    display_filename,
    extension_of,
    matches_expected_format,
    relative_path,
    remove_stored_file,
    write_upload,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/resumes",
    tags=["resumes"],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"}},
)

UNSUPPORTED_FORMAT_DETAIL = "Upload a PDF or DOCX resume."
UNREADABLE_FILE_DETAIL = "We couldn't read this file. Upload a PDF or DOCX resume."
EMPTY_FILE_DETAIL = "This file is empty. Choose your resume file and try again."
SAVE_FAILED_DETAIL = "We could not save your resume. Please try again."
DELETE_FAILED_DETAIL = "We could not delete your resume. Please try again."
PARSE_FAILED_DETAIL = "We could not read your resume just now. Please try again."
NOT_FOUND_DETAIL = "Resume not found."

BYTES_PER_MEGABYTE = 1024 * 1024


def _too_large_detail(max_bytes: int) -> str:
    return f"Resumes must be {max_bytes // BYTES_PER_MEGABYTE} MB or smaller."


def _parse_outcome(
    stored_path: str, extension: str
) -> tuple[str, str | None, str | None]:
    """Extract text from a stored file, reporting failure as a stored status.

    A file that cannot be read leaves the resume in place with a message the
    user can act on, per PRODUCT.md sections 19 and 33.
    """
    try:
        text = extract_text(absolute_path(stored_path), extension)
    except ResumeParseError as error:
        return PARSE_STATUS_FAILED, None, error.message
    except (OSError, StoragePathError):
        logger.warning("stored resume file could not be opened for parsing")
        return PARSE_STATUS_FAILED, None, unreadable_message(extension)
    return PARSE_STATUS_PARSED, text, None


@router.post(
    "",
    response_model=ResumeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a resume",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Unsupported or unreadable file"},
        status.HTTP_413_CONTENT_TOO_LARGE: {"description": "File too large"},
    },
)
async def upload_resume(
    file: Annotated[UploadFile, File()], user: CurrentUserDep, session: SessionDep
) -> Resume:
    """Store an uploaded resume for the token's subject.

    Nothing is written until the claimed format is allowed, and nothing is kept
    unless the bytes on disk match that format. The owning user comes from the
    access token, so no form field can direct the upload at another account.

    Text extraction runs here, synchronously. A file that cannot be read is
    still stored, with a failed parse status the user can retry.
    """
    settings = get_settings()
    filename = display_filename(file.filename)
    extension = extension_of(filename)
    expected_content_type = ALLOWED_CONTENT_TYPES.get(extension)

    if expected_content_type is None or file.content_type != expected_content_type:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, UNSUPPORTED_FORMAT_DETAIL)

    resume_id = uuid.uuid4()
    stored_path = relative_path(user.id, resume_id, extension)

    try:
        byte_size = await write_upload(
            file, stored_path, settings.max_resume_upload_bytes
        )
    except UploadTooLargeError:
        discard_stored_file(stored_path)
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            _too_large_detail(settings.max_resume_upload_bytes),
        ) from None
    except OSError:
        discard_stored_file(stored_path)
        logger.exception("resume upload could not be written")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, SAVE_FAILED_DETAIL
        ) from None

    if byte_size == 0:
        discard_stored_file(stored_path)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, EMPTY_FILE_DETAIL)

    if not matches_expected_format(stored_path, extension):
        discard_stored_file(stored_path)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, UNREADABLE_FILE_DETAIL)

    parse_status, extracted_text, parse_error = _parse_outcome(stored_path, extension)

    resume = Resume(
        id=resume_id,
        user_id=user.id,
        original_filename=filename[:ORIGINAL_FILENAME_MAX_LENGTH],
        stored_path=stored_path,
        content_type=expected_content_type,
        byte_size=byte_size,
        parse_status=parse_status,
        extracted_text=extracted_text,
        parse_error=parse_error,
    )
    session.add(resume)
    try:
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        discard_stored_file(stored_path)
        logger.exception("resume metadata could not be persisted")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, SAVE_FAILED_DETAIL
        ) from None

    return resume


@router.get(
    "",
    response_model=list[ResumeRead],
    summary="List the signed-in user's resumes",
)
async def list_resumes(user: CurrentUserDep, session: SessionDep) -> list[Resume]:
    """Return the caller's resumes, newest first."""
    resumes = await session.scalars(
        select(Resume)
        .where(Resume.user_id == user.id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
    )
    return list(resumes)


@router.get(
    "/{resume_id}",
    response_model=ResumeRead,
    summary="Read one of the signed-in user's resumes",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Resume not found"}},
)
async def read_resume(
    resume_id: uuid.UUID, user: CurrentUserDep, session: SessionDep
) -> Resume:
    """Return one resume owned by the caller.

    A resume belonging to another user is indistinguishable from one that does
    not exist, so an identifier cannot be probed for existence.
    """
    return await _owned_resume(session, resume_id, user.id)


@router.post(
    "/{resume_id}/parse",
    response_model=ResumeRead,
    summary="Extract text from one of the signed-in user's resumes",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Resume not found"}},
)
async def parse_resume(
    resume_id: uuid.UUID, user: CurrentUserDep, session: SessionDep
) -> Resume:
    """Re-run text extraction for a resume the caller owns.

    This is the retry PRODUCT.md section 6 asks for. It replaces the parse
    result on the existing row, so retrying never creates a second resume, and
    a file that still cannot be read simply stays failed. The extension comes
    from the stored path rather than from the client.
    """
    resume = await _owned_resume(session, resume_id, user.id)
    resume.parse_status, resume.extracted_text, resume.parse_error = _parse_outcome(
        resume.stored_path, extension_of(resume.stored_path)
    )

    try:
        await session.commit()
        await session.refresh(resume)
    except SQLAlchemyError:
        await session.rollback()
        logger.exception("resume parse result could not be persisted")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, PARSE_FAILED_DETAIL
        ) from None

    return resume


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete one of the signed-in user's resumes",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Resume not found"}},
)
async def delete_resume(
    resume_id: uuid.UUID, user: CurrentUserDep, session: SessionDep
) -> None:
    """Delete a resume the caller owns, record and file together.

    The row is deleted first but committed last: if the file cannot be removed
    the transaction is rolled back, so the database never reports a deletion
    that did not happen. A file already missing is treated as deleted.
    """
    resume = await _owned_resume(session, resume_id, user.id)
    stored_path = resume.stored_path

    try:
        await session.delete(resume)
        await session.flush()
    except SQLAlchemyError:
        await session.rollback()
        logger.exception("resume record could not be deleted")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, DELETE_FAILED_DETAIL
        ) from None

    try:
        remove_stored_file(stored_path)
    except (OSError, StoragePathError):
        await session.rollback()
        logger.exception("stored resume file could not be removed")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, DELETE_FAILED_DETAIL
        ) from None

    try:
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        logger.exception("resume deletion could not be committed")
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, DELETE_FAILED_DETAIL
        ) from None


async def _owned_resume(
    session: SessionDep, resume_id: uuid.UUID, user_id: uuid.UUID
) -> Resume:
    resume = await session.scalar(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    if resume is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND_DETAIL)
    return resume
