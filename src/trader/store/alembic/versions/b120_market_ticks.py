"""Lossless market tick archive; cursors and gaps use existing durable feature tables."""

from typing import cast

from alembic import op
from sqlalchemy import Table

from trader.features.models import MarketTick

revision = "b120"
down_revision = "b110"
branch_labels = None
depends_on = None


def upgrade():
    cast(Table, MarketTick.__table__).create(op.get_bind(), checkfirst=True)


def downgrade():
    cast(Table, MarketTick.__table__).drop(op.get_bind(), checkfirst=True)
