"""Section detection for extracted resume text.

Covers Document Structure Detection and Section Extraction from
ARCHITECTURE.md section 13, and the Section Detection step of PRODUCT.md
section 6. Detection is deterministic: section 3.3 reserves AI for work that
cannot be done reliably without it, and section 20 places resume
interpretation — reading a company, role or date out of a line — in the AI
stage that follows this one.

The kinds mirror the top-level nodes of the structured resume model in
section 16.
"""

import re
from typing import NamedTuple

from app.resumes.parsing import normalize_text

KIND_CONTACT = "contact"
KIND_SUMMARY = "summary"
KIND_EXPERIENCE = "experience"
KIND_EDUCATION = "education"
KIND_SKILLS = "skills"
KIND_PROJECTS = "projects"
KIND_CERTIFICATIONS = "certifications"
KIND_OTHER = "other"

HEADING_MAX_LENGTH = 60

_HEADINGS: dict[str, str] = {
    "contact": KIND_CONTACT,
    "contact information": KIND_CONTACT,
    "contact details": KIND_CONTACT,
    "summary": KIND_SUMMARY,
    "professional summary": KIND_SUMMARY,
    "career summary": KIND_SUMMARY,
    "profile": KIND_SUMMARY,
    "professional profile": KIND_SUMMARY,
    "objective": KIND_SUMMARY,
    "career objective": KIND_SUMMARY,
    "about me": KIND_SUMMARY,
    "experience": KIND_EXPERIENCE,
    "work experience": KIND_EXPERIENCE,
    "working experience": KIND_EXPERIENCE,
    "professional experience": KIND_EXPERIENCE,
    "employment": KIND_EXPERIENCE,
    "employment history": KIND_EXPERIENCE,
    "work history": KIND_EXPERIENCE,
    "career history": KIND_EXPERIENCE,
    "professional background": KIND_EXPERIENCE,
    "education": KIND_EDUCATION,
    "education and training": KIND_EDUCATION,
    "academic background": KIND_EDUCATION,
    "academics": KIND_EDUCATION,
    "skills": KIND_SKILLS,
    "technical skills": KIND_SKILLS,
    "core skills": KIND_SKILLS,
    "key skills": KIND_SKILLS,
    "skills and expertise": KIND_SKILLS,
    "technical expertise": KIND_SKILLS,
    "core competencies": KIND_SKILLS,
    "technologies": KIND_SKILLS,
    "projects": KIND_PROJECTS,
    "key projects": KIND_PROJECTS,
    "selected projects": KIND_PROJECTS,
    "personal projects": KIND_PROJECTS,
    "project experience": KIND_PROJECTS,
    "certifications": KIND_CERTIFICATIONS,
    "certification": KIND_CERTIFICATIONS,
    "certificates": KIND_CERTIFICATIONS,
    "licenses and certifications": KIND_CERTIFICATIONS,
    "courses and certifications": KIND_CERTIFICATIONS,
}

_DECORATION = re.compile(r"[^0-9a-z& ]+")
_SPACES = re.compile(r"\s+")


class DetectedSection(NamedTuple):
    """One detected section, in document order."""

    kind: str
    heading: str | None
    content: str


def heading_kind(line: str) -> str | None:
    """Return the section kind a line announces, or None if it is body text.

    Only a line that is nothing but a known heading counts. Requiring the
    whole line to match keeps prose such as "Skills used on this project"
    from being read as the start of a new section.
    """
    stripped = line.strip()
    if not stripped or len(stripped) > HEADING_MAX_LENGTH:
        return None

    normalized = _DECORATION.sub(" ", stripped.lower().replace("&", " and "))
    return _HEADINGS.get(_SPACES.sub(" ", normalized).strip())


def detect_sections(text: str) -> list[DetectedSection]:
    """Split extracted resume text into its sections, in document order.

    Text ahead of the first heading is kept as an `other` section so the name
    and contact block at the top of most resumes is not lost, and a resume
    with no recognizable headings still yields one section rather than
    nothing. A heading with no body is recorded with empty content, because
    which sections a resume declares is itself information.
    """
    if not text.strip():
        return []

    sections: list[DetectedSection] = []
    kind = KIND_OTHER
    heading: str | None = None
    body: list[str] = []

    for line in text.split("\n"):
        found = heading_kind(line)
        if found is None:
            body.append(line)
            continue

        _append(sections, kind, heading, body)
        kind, heading, body = found, line.strip(), []

    _append(sections, kind, heading, body)
    return sections


def _append(
    sections: list[DetectedSection],
    kind: str,
    heading: str | None,
    body: list[str],
) -> None:
    content = normalize_text("\n".join(body))
    if heading is None and not content:
        return
    sections.append(DetectedSection(kind=kind, heading=heading, content=content))
