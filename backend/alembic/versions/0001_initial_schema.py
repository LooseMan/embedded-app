"""create initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-18
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("api_name", sa.String(length=255), nullable=False),
        sa.Column("phase", sa.String(length=50), nullable=False),
        sa.Column("result", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "machine_status",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("status", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "file_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "file_set",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "file",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["file_category.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "file_set_rel",
        sa.Column("file_set_id", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["file.id"]),
        sa.ForeignKeyConstraint(["file_set_id"], ["file_set.id"]),
        sa.PrimaryKeyConstraint("file_set_id", "file_id"),
    )


def downgrade() -> None:
    op.drop_table("file_set_rel")
    op.drop_table("file")
    op.drop_table("file_set")
    op.drop_table("file_category")
    op.drop_table("machine_status")
    op.drop_table("api_log")
