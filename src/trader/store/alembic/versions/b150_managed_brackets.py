"""Persist managed paper positions and exit intents before broker I/O."""

from alembic import op

from trader.store.extended import ManagedBracket

revision = "b150"
down_revision = "b140"
branch_labels = None
depends_on = None


def upgrade():
    ManagedBracket.__table__.create(op.get_bind(), checkfirst=True)


def downgrade():
    ManagedBracket.__table__.drop(op.get_bind(), checkfirst=True)
