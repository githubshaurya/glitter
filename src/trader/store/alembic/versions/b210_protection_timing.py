"""Persist the observed partial fill and protection acknowledgement times."""

import sqlalchemy as sa
from alembic import op

revision = "b210"
down_revision = "b200"
branch_labels = None
depends_on = None


def upgrade():
    db = op.get_bind()
    existing = {column["name"] for column in sa.inspect(db).get_columns("managed_brackets")}
    for name in ("partial_observed_at", "protection_acked_at"):
        if name not in existing:
            op.add_column("managed_brackets", sa.Column(name, sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("managed_brackets", "protection_acked_at")
    op.drop_column("managed_brackets", "partial_observed_at")
