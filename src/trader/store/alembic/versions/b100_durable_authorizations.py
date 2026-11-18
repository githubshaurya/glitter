"""Durable account authorization and notification outbox.

Revision ID: b100
Revises: a5bc8453ef37
"""

import sqlalchemy as sa
from alembic import op

revision = "b100"
down_revision = "a5bc8453ef37"
branch_labels = None
depends_on = None


def upgrade():
    from trader.store.extended import Blob, CouncilRun, Outbox, Reservation, RiskAccount

    for model in (RiskAccount, Reservation, Outbox, Blob, CouncilRun):
        model.metadata.tables[model.__tablename__].create(op.get_bind(), checkfirst=True)


def downgrade():
    for name in ("council_runs", "content_blobs", "event_outbox", "risk_reservations", "risk_accounts"):
        sa.Table(name, sa.MetaData(), autoload_with=op.get_bind()).drop(op.get_bind())
