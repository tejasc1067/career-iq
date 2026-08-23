"""Resume API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    """An uploaded resume as returned by the API.

    Deliberately excludes `stored_path` and `extracted_text`: where a file
    sits on disk is not information a client needs, the API never serves the
    bytes, and the extracted text is sensitive career information no screen in
    this milestone displays.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    content_type: str
    byte_size: int
    parse_status: str
    parse_error: str | None
    created_at: datetime
    updated_at: datetime
