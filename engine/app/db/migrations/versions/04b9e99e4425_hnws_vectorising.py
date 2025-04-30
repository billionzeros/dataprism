"""hnws_vectorising

Revision ID: 04b9e99e4425
Revises: 5f0e266eee9d
Create Date: 2025-04-30 23:09:15.753940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from alembic.ddl.postgresql import PostgresqlImpl
PostgresqlImpl.transactional_ddl = False

# revision identifiers, used by Alembic.
revision: str = '04b9e99e4425'
down_revision: Union[str, None] = '5f0e266eee9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.get_context().autocommit_block():
        op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vector_embeddings_embedding ON vector_embeddings USING hnsw (embedding vector_cosine_ops);")


def downgrade() -> None:
    """Downgrade schema."""
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_vector_embeddings_embedding;")