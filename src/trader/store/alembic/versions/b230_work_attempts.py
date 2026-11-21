"""Record bounded retries and terminal work failures."""

import sqlalchemy as sa
from alembic import op

revision = "b230"
down_revision = "b220"
branch_labels = None
depends_on = None


def upgrade():
    table = "durable_work_claims"
    existing = {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}
    if "attempts" not in existing:
        op.add_column(table, sa.Column("attempts", sa.Integer, nullable=False, server_default="1"))
    if "last_error" not in existing:
        op.add_column(table, sa.Column("last_error", sa.String(128), nullable=True))


def downgrade():
    op.drop_column("durable_work_claims", "last_error")
    op.drop_column("durable_work_claims", "attempts")
