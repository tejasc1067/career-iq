"""Resume API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    """An uploaded resume as returned by the API.

    Deliberately excludes `stored_path`: where a file sits on disk is not
    information a client needs, and the API never serves the bytes.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    content_type: str
    byte_size: int
    created_at: datetime
    updated_at: datetime
