"""add course week pattern fields

Revision ID: 9f3e2d4a1b6c
Revises: 7b4f8c2d1a3e
Create Date: 2026-04-20 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3e2d4a1b6c"
down_revision: Union[str, Sequence[str], None] = "7b4f8c2d1a3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("courses") as batch_op:
        batch_op.add_column(
            sa.Column("week_pattern", sa.String(length=10), nullable=False, server_default="all")
        )
        batch_op.add_column(sa.Column("week_text", sa.String(length=50), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("courses") as batch_op:
        batch_op.drop_column("week_text")
        batch_op.drop_column("week_pattern")
