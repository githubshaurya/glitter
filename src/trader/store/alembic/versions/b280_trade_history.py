"""Persist the searchable trade history and affected trading dates."""

from alembic import op

from trader.reporting.trade_history import HISTORY

revision = "b280"
down_revision = "b270"
branch_labels = None
depends_on = None


def upgrade():
    HISTORY.create_all(op.get_bind())


def downgrade():
    HISTORY.drop_all(op.get_bind())
