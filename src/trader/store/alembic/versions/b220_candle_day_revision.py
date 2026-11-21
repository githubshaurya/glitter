"""Track feed-day invalidation of the completed candle cache."""

from alembic import op

from trader.features.models import CandleDayRevision

revision = "b220"
down_revision = "b210"
branch_labels = None
depends_on = None


def upgrade():
    db = op.get_bind()
    CandleDayRevision.__table__.create(db, checkfirst=True)
    # Give pre-upgrade rows an as-of boundary, including revisions observed after their exchange date.
    op.execute("""
        INSERT INTO candle_day_revisions(feed, day, generation, newest_known_at)
        SELECT feed, day, 1, MAX(known_at)
        FROM (
            SELECT feed, SUBSTR(CAST(event_time AS TEXT), 1, 10) AS day, known_at
            FROM market_bar_history WHERE timeframe = '1m'
            UNION ALL
            SELECT feed, SUBSTR(CAST(event_time AS TEXT), 1, 10), known_at FROM bar_coverage_history
        ) observations GROUP BY feed, day
        ON CONFLICT (feed, day) DO NOTHING
    """)


def downgrade():
    op.drop_table(CandleDayRevision.__tablename__)
