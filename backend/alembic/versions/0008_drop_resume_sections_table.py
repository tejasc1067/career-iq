"""Drop the resume_sections table.

Deterministic section detection is replaced by AI resume understanding, so the
table it wrote to is no longer part of the model. Revision 0007 stays in the
history; this revision removes the schema going forward.

Revision ID: 0008
Revises: 0007
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_resume_sections_resume_id"), table_name="resume_sections")
    op.drop_table("resume_sections")


def downgrade() -> None:
    op.create_table(
        "resume_sections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resume_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("heading", sa.String(length=60), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resume_id", "position"),
    )
    op.create_index(
        op.f("ix_resume_sections_resume_id"),
        "resume_sections",
        ["resume_id"],
        unique=False,
    )
