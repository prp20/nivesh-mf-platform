"""add metrics_jobs table

Revision ID: b1f685a1ee31
Revises: 5882befa3dbe
Create Date: 2026-01-26 02:02:25.747510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1f685a1ee31'
down_revision: Union[str, Sequence[str], None] = '5882befa3dbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
    "metrics_jobs",
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("fund_id", sa.Integer(), sa.ForeignKey("mutual_funds.id")),
    sa.Column("status", sa.String(length=20), nullable=False),
    sa.Column("error_message", sa.String(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("started_at", sa.DateTime(timezone=True)),
    sa.Column("finished_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
