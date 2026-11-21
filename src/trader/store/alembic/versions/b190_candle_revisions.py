"""Scope coverage to the feed and retain candle revision provenance."""

import sqlalchemy as sa
from alembic import op

from trader.features.models import Coverage, MarketBar

revision = "b190"
down_revision = "b180"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    coverage = {column["name"] for column in inspector.get_columns("bar_coverage_history")}
    if "feed" not in coverage:
        op.add_column(
            "bar_coverage_history", sa.Column("feed", sa.String(16), nullable=False, server_default="legacy"),
        )
        # Old omissions lack source provenance. Reconstruct only positive coverage from the actual tape.
        op.execute(sa.text("""
            INSERT INTO bar_coverage_history(record_id, symbol, event_time, known_at, status, feed)
            SELECT record_id, symbol, event_time, known_at, 'VERIFIED_BAR', feed
            FROM market_bar_history WHERE timeframe = '1m'
            ON CONFLICT (record_id) DO NOTHING
        """))
    bars = {column["name"] for column in inspector.get_columns("market_bar_history")}
    if "revision_rank" not in bars:
        op.add_column("market_bar_history", sa.Column("revision_rank", sa.Integer, nullable=False, server_default="1"))
    if "source_event_id" not in bars:
        op.add_column("market_bar_history", sa.Column("source_event_id", sa.String(64), nullable=True))
    for model, name in ((Coverage, "ix_coverage_feed_asof"), (MarketBar, "ix_bars_feed_asof")):
        next(index for index in model.__table__.indexes if index.name == name).create(connection, checkfirst=True)


def downgrade():
    op.drop_index("ix_coverage_feed_asof", table_name="bar_coverage_history")
    op.drop_index("ix_bars_feed_asof", table_name="market_bar_history")
    op.drop_column("market_bar_history", "source_event_id")
    op.drop_column("market_bar_history", "revision_rank")
    op.drop_column("bar_coverage_history", "feed")
