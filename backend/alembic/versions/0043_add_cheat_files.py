"""Add cheat_files table

Revision ID: 0043_add_cheat_files
Revises: 0042_add_cheat_codes
Create Date: 2025-06-11 01:00:00

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0043_add_cheat_files"
down_revision = "0042_add_cheat_codes"
branch_labels = None
depends_on = None


def upgrade():
    # Create the cheat_files table
    op.create_table(
        "cheat_files",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "rom_id",
            sa.Integer,
            sa.ForeignKey("roms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=1000), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=False, default=0),
        sa.Column(
            "uploaded_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


def downgrade():
    # Drop the cheat_files table
    op.drop_table("cheat_files")
