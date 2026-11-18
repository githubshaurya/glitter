"""Cover point-in-time feature lookup, including the tie-break order."""

from alembic import op
from sqlalchemy import text

revision = "b140"
down_revision = "b130"
branch_labels = None
depends_on = None

INDEX_NAME = "ix_features_latest_lookup"
COLUMNS = ["entity_type", "entity_id", "name", "version", text("event_time DESC"), text("known_at DESC"),
           text("rec_hash DESC")]


def upgrade():
    if op.get_bind().dialect.name != "postgresql":
        op.create_index(INDEX_NAME, "feature_values", COLUMNS, if_not_exists=True)
        return
    with op.get_context().autocommit_block():
        connection = op.get_bind()
        valid = connection.scalar(text("SELECT indisvalid FROM pg_index WHERE indexrelid = to_regclass(:name)"),
                                  {"name": INDEX_NAME})
        if valid is False:
            op.drop_index(INDEX_NAME, "feature_values", postgresql_concurrently=True)
        op.create_index(INDEX_NAME, "feature_values", COLUMNS, if_not_exists=True, postgresql_concurrently=True)


def downgrade():
    if op.get_bind().dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.drop_index(INDEX_NAME, "feature_values", if_exists=True, postgresql_concurrently=True)
    else:
        op.drop_index(INDEX_NAME, "feature_values", if_exists=True)
