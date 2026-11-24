"""Allow managed paper lots to carry without a forced close time."""

from sqlalchemy import inspect

from alembic import op

revision = "b290"
down_revision = "b280"
branch_labels = None
depends_on = None


def upgrade():
    if any(c["name"] == "close_at" and not c["nullable"]
           for c in inspect(op.get_bind()).get_columns("managed_brackets")):
        with op.batch_alter_table("managed_brackets") as batch:
            batch.alter_column("close_at", nullable=True)


def downgrade():
    with op.batch_alter_table("managed_brackets") as batch:
        batch.alter_column("close_at", nullable=False)
