"""Keep provider news revisions point in time across REST and stream ingestion."""

import sqlalchemy as sa
from alembic import op

revision = "b250"
down_revision = "b240"
branch_labels = None
depends_on = None


def upgrade():
    if "revision_at" not in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("news_articles")}:
        op.add_column("news_articles", sa.Column("revision_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("news_articles", "revision_at")
