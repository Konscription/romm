"""Add cheat_codes table

Revision ID: 0042_add_cheat_codes
Revises: 0041_assets_t_thumb_cleanup
Create Date: 2025-06-11 00:50:00

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0042_add_cheat_codes"
down_revision = "0041_assets_t_thumb_cleanup"
branch_labels = None
depends_on = None


def upgrade():
    # Create the cheat_codes table
    op.create_table(
        "cheat_codes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "rom_id",
            sa.Integer,
            sa.ForeignKey("roms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "type",
            sa.Enum(
                "raw",
                "game_genie",
                "gameshark",
                "codebreaker",
                "actionreplay",
                name="cheatcodetype",
            ),
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
    # Drop the cheat_codes table
    op.drop_table("cheat_codes")
