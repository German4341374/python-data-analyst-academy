"""Versioned learner state; educational content is versioned in Git."""

import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("email", sa.String(254), unique=True),
        sa.Column("password_hash", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("placement", sa.String(30), nullable=False),
        sa.Column("daily_minutes", sa.Integer, nullable=False),
    )
    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content_id", sa.String(100), nullable=False),
        sa.Column("content_version", sa.Integer, nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("topic", sa.String(50), nullable=False),
        sa.Column("correct", sa.Boolean, nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_attempts_user_id", "attempts", ["user_id"])
    op.create_table(
        "progress",
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("content_id", sa.String(100), primary_key=True),
        sa.Column("kind", sa.String(30), primary_key=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "bookmarks",
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("lesson_id", sa.String(100), primary_key=True),
    )


def downgrade():
    for table in ["bookmarks", "progress", "attempts", "sessions", "users"]:
        op.drop_table(table)
