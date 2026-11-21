"""Persist signed council exit requests alongside managed positions."""

import sqlalchemy as sa
from alembic import op

from trader.store.models import JSONType

revision = "b260"
down_revision = "b250"
branch_labels = None
depends_on = None


def upgrade():
    if "exit_request" not in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("managed_brackets")}:
        op.add_column("managed_brackets", sa.Column("exit_request", JSONType, nullable=True))


def downgrade():
    op.drop_column("managed_brackets", "exit_request")
