"""Stored feature history, evidence packs, council audit and durable work polling."""

import sqlalchemy as sa
from alembic import op

revision = "b110"
down_revision = "b100"
branch_labels = None
depends_on = None


def tables():
    from trader.features import models as f
    from trader.store.extended import CouncilCall, EvidenceLink, RiskPosition, WorkItem

    return [
        m.__table__
        for m in (
            f.MarketBar,
            f.Coverage,
            f.Gap,
            f.MarketSession,
            f.Article,
            f.FeatureValue,
            f.FeatureLatest,
            f.FeatureState,
            f.Evidence,
            f.ToolMemo,
            f.SourceHealth,
            CouncilCall,
            EvidenceLink,
            RiskPosition,
            WorkItem,
        )
    ]


def upgrade():
    for table in tables():
        table.create(op.get_bind(), checkfirst=True)


def downgrade():
    for table in reversed(tables()):
        sa.Table(table.name, sa.MetaData(), autoload_with=op.get_bind()).drop(op.get_bind())
