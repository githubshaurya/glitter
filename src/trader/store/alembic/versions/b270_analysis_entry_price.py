"""Keep the analysis-side entry quote in the durable proposal audit."""

import sqlalchemy as sa
from alembic import op

revision = "b270"
down_revision = "b260"
branch_labels = None
depends_on = None


def upgrade():
    if "analysis_entry_price" not in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("proposals")}:
        op.add_column("proposals", sa.Column("analysis_entry_price", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("proposals", "analysis_entry_price")
