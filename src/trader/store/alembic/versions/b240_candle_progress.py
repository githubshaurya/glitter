"""Record the earliest unprocessed candle revision per feed and ticker."""

from alembic import op

from trader.features.models import CandleProgress

revision = "b240"
down_revision = "b230"
branch_labels = None
depends_on = None


def upgrade():
    CandleProgress.__table__.create(op.get_bind(), checkfirst=True)


def downgrade():
    op.drop_table(CandleProgress.__tablename__)
