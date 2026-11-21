"""Lease committed work independently of Kafka delivery."""

import sqlalchemy as sa
from alembic import op

from trader.store.extended import WorkClaim, WorkItem

revision = "b200"
down_revision = "b190"
branch_labels = None
depends_on = None


def upgrade():
    db = op.get_bind()
    table = WorkItem.__tablename__
    if "expires_at" not in {col["name"] for col in sa.inspect(db).get_columns(table)}:
        op.add_column(table, sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
        if db.dialect.name == "postgresql":
            op.execute(sa.text(
                "UPDATE durable_work_items SET expires_at = CAST(envelope->>'expires_at' AS timestamptz)"
            ))
    if db.dialect.name == "postgresql":
        op.alter_column(table, "identifier", type_=sa.String(128), existing_type=sa.String(64))
    WorkClaim.__table__.create(db, checkfirst=True)
    next(index for index in WorkItem.__table__.indexes if index.name == "ix_work_claim_schedule").create(
        db, checkfirst=True,
    )


def downgrade():
    op.drop_index("ix_work_claim_schedule", table_name=WorkItem.__tablename__)
    op.drop_column(WorkItem.__tablename__, "expires_at")
    op.drop_table(WorkClaim.__tablename__)
