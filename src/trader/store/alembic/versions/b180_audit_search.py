"""Index audit filters and chronological pagination."""

from alembic import op

from trader.reporting.star import AUDIT_INDEXES

revision = "b180"
down_revision = "b170"
branch_labels = None
depends_on = None


def upgrade():
    for index in AUDIT_INDEXES:
        index.create(op.get_bind(), checkfirst=True)


def downgrade():
    for index in reversed(AUDIT_INDEXES):
        index.drop(op.get_bind(), checkfirst=True)
