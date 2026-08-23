"""Text extraction for stored resume files.

Covers the Text Extraction stage of the pipeline in ARCHITECTURE.md section
13. Structure detection and section extraction belong to the structured
resume milestone that follows.

Extraction runs synchronously, which section 60 permits, and parser failures
are reported as the messages PRODUCT.md section 33 asks for rather than as
exception text.
"""

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from pypdf import PdfReader

from app.common.config import get_settings
from app.resumes.storage import PDF_EXTENSION

WORDPROCESSING_NAMESPACE = (
    "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
)
DOCUMENT_PART = "word/document.xml"
PROLOG_SCAN_BYTES = 4096

UNREADABLE_PDF_MESSAGE = (
    "We couldn't read this PDF. Try uploading another PDF, or a DOCX version "
    "of your resume."
)
UNREADABLE_DOCX_MESSAGE = (
    "We couldn't read this DOCX file. Try uploading another DOCX, or a PDF "
    "version of your resume."
)
NO_TEXT_PDF_MESSAGE = (
    "We couldn't find any text in this PDF. If it is a scan or an image, "
    "upload a text-based PDF or a DOCX version instead."
)
NO_TEXT_DOCX_MESSAGE = (
    "We couldn't find any text in this DOCX file. Upload a version that "
    "contains your resume text."
)

_LINE_ENDINGS = re.compile(r"\r\n?")
_EXTRA_BLANK_LINES = re.compile(r"\n{3,}")


class ResumeParseError(Exception):
    """Raised when a stored resume yields no usable text.

    Carries the message shown to the user; parser exception text never
    reaches it.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def unreadable_message(extension: str) -> str:
    """Return the message for a file that could not be read at all."""
    if extension == PDF_EXTENSION:
        return UNREADABLE_PDF_MESSAGE
    return UNREADABLE_DOCX_MESSAGE


def _no_text_message(extension: str) -> str:
    if extension == PDF_EXTENSION:
        return NO_TEXT_PDF_MESSAGE
    return NO_TEXT_DOCX_MESSAGE


def normalize_text(raw: str) -> str:
    """Normalize line endings and blank runs without rewriting content.

    Paragraph boundaries survive as single blank lines; nothing else about the
    text is altered, so what is stored stays faithful to the document.
    """
    unified = _LINE_ENDINGS.sub("\n", raw)
    trimmed = "\n".join(line.rstrip() for line in unified.split("\n"))
    return _EXTRA_BLANK_LINES.sub("\n\n", trimmed).strip()


def extract_text(path: Path, extension: str) -> str:
    """Return the normalized text of a stored resume.

    Raises `ResumeParseError` when the file cannot be read or holds no text —
    an image-only scan, for example, since CareerIQ does not perform OCR.
    """
    try:
        raw = _pdf_text(path) if extension == PDF_EXTENSION else _docx_text(path)
    except Exception:
        raise ResumeParseError(unreadable_message(extension)) from None

    text = normalize_text(raw)
    if not text:
        raise ResumeParseError(_no_text_message(extension))
    return text


def _pdf_text(path: Path) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as package, package.open(DOCUMENT_PART) as part:
        limit = get_settings().max_resume_upload_bytes
        document = part.read(limit + 1)

    if len(document) > limit:
        raise ValueError("document part exceeds the configured upload limit")
    if b"<!DOCTYPE" in document[:PROLOG_SCAN_BYTES]:
        raise ValueError("document part declares a document type")

    root = ElementTree.fromstring(document)
    return "\n".join(_paragraph_text(paragraph) for paragraph in root.iter(_tag("p")))


def _paragraph_text(paragraph: ElementTree.Element) -> str:
    parts: list[str] = []
    for node in paragraph.iter():
        if node.tag == _tag("t"):
            parts.append(node.text or "")
        elif node.tag == _tag("tab"):
            parts.append("\t")
        elif node.tag in (_tag("br"), _tag("cr")):
            parts.append("\n")
    return "".join(parts)


def _tag(name: str) -> str:
    return f"{{{WORDPROCESSING_NAMESPACE}}}{name}"
