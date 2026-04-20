"""repair course week columns for legacy local databases

Revision ID: c4c3b8a92f1d
Revises: 9f3e2d4a1b6c
Create Date: 2026-04-20 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4c3b8a92f1d"
down_revision: Union[str, Sequence[str], None] = "9f3e2d4a1b6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("courses")}

    if "week_pattern" not in columns:
        with op.batch_alter_table("courses") as batch_op:
            batch_op.add_column(
                sa.Column("week_pattern", sa.String(length=10), nullable=False, server_default="all")
            )
        columns.add("week_pattern")

    if "week_text" not in columns:
        with op.batch_alter_table("courses") as batch_op:
            batch_op.add_column(sa.Column("week_text", sa.String(length=50), nullable=True))
        columns.add("week_text")

    if "week_type" in columns:
        op.execute("UPDATE courses SET week_pattern = COALESCE(week_type, 'all') WHERE week_pattern IS NULL")

    op.execute("UPDATE courses SET week_pattern = COALESCE(week_pattern, 'all')")
    op.execute(
        """
        UPDATE courses
        SET week_text = CASE
            WHEN COALESCE(week_pattern, 'all') = 'odd'
                THEN 'Week ' || week_start || '-' || week_end || ' (odd)'
            WHEN COALESCE(week_pattern, 'all') = 'even'
                THEN 'Week ' || week_start || '-' || week_end || ' (even)'
            ELSE 'Week ' || week_start || '-' || week_end
        END
        WHERE week_text IS NULL OR week_text = ''
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("courses")}

    with op.batch_alter_table("courses") as batch_op:
        if "week_text" in columns:
            batch_op.drop_column("week_text")
        if "week_pattern" in columns:
            batch_op.drop_column("week_pattern")
