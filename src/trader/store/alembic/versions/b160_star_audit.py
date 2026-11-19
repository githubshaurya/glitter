"""Add dimensional decision, role log and fill facts for the viewer."""

from alembic import op

from trader.reporting.star import STAR

revision = "b160"
down_revision = "b150"
branch_labels = None
depends_on = None


def upgrade():
    STAR.create_all(op.get_bind())


def downgrade():
    STAR.drop_all(op.get_bind())
