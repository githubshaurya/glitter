"""Track a revision for each account independently of the order authorization epoch."""

import sqlalchemy as sa
from alembic import op

revision = "b170"
down_revision = "b160"
branch_labels = None
depends_on = None


def upgrade():
    if "generation" not in {col["name"] for col in sa.inspect(op.get_bind()).get_columns("risk_accounts")}:
        op.add_column("risk_accounts", sa.Column("generation", sa.Integer(), nullable=False, server_default="0"))


def downgrade():
    op.drop_column("risk_accounts", "generation")
