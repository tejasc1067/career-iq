"""Add parsing fields to the resumes table.

Revision ID: 0006
Revises: 0005
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "resumes",
        sa.Column(
            "parse_status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
    )
    op.add_column("resumes", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column(
        "resumes", sa.Column("parse_error", sa.String(length=200), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("resumes", "parse_error")
    op.drop_column("resumes", "extracted_text")
    op.drop_column("resumes", "parse_status")
