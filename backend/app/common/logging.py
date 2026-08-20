"""Logging configuration.

Logs must never contain passwords, tokens, full resume contents, or other
sensitive personal information. See ARCHITECTURE.md section 48.
"""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once, at application startup."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        force=True,
    )
