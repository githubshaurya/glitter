"""Retain individual model attempts, including failures and late outputs."""

from typing import cast

from alembic import op
from sqlalchemy import Table

from trader.store.extended import CouncilAttempt

revision = "b130"
down_revision = "b120"
branch_labels = None
depends_on = None


def upgrade():
    cast(Table, CouncilAttempt.__table__).create(op.get_bind(), checkfirst=True)


def downgrade():
    cast(Table, CouncilAttempt.__table__).drop(op.get_bind(), checkfirst=True)
