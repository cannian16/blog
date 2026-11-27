"""Initialize the database.

Revision ID: 13a55da86116
Revises:
Create Date: 2026-03-31 17:55:42.808277

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "13a55da86116"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("icon", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("website_url", sa.String(length=200), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("published", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("description", sa.String(length=200), server_default="", nullable=False),
        sa.Column("image", sa.String(length=500), server_default="", nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("category", sa.String(length=100), server_default="", nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("logo", sa.String(length=200), nullable=False),
        sa.Column("url", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "songs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=50), nullable=False),
        sa.Column("artist", sa.String(length=50), nullable=False),
        sa.Column("url", sa.String(length=200), nullable=False),
        sa.Column("cover", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=50), nullable=False),
        sa.Column("subtitle", sa.String(length=50), nullable=False),
        sa.Column("url", sa.String(length=200), nullable=False),
        sa.Column("imgUrl", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tools")
    op.drop_table("songs")
    op.drop_table("skills")
    op.drop_table("posts")
    op.drop_table("messages")
    op.drop_table("links")
