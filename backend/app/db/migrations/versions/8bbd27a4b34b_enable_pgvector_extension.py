"""Enable pgvector extension

Revision ID: 8bbd27a4b34b
Revises:
Create Date: 2025-04-29 18:13:56.065908

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8bbd27a4b34b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("Executed: CREATE EXTENSION IF NOT EXISTS vector;")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS vector;")
    print("Executed: DROP EXTENSION IF EXISTS vector;")
    pass
