"""add reminder advance_minutes

Revision ID: 7b4f8c2d1a3e
Revises: 47f4735b8cf9
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b4f8c2d1a3e"
down_revision: Union[str, Sequence[str], None] = "47f4735b8cf9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("reminders") as batch_op:
        batch_op.add_column(sa.Column("advance_minutes", sa.Integer(), nullable=False, server_default="15"))


def downgrade() -> None:
    with op.batch_alter_table("reminders") as batch_op:
        batch_op.drop_column("advance_minutes")