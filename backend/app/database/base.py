"""Declarative base for all ORM models.

Every model must inherit from `Base` so that Alembic autogenerate can see it.
Domain modules define their own models; none exist yet.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for CareerIQ ORM models."""
