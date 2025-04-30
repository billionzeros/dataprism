"""Enable pgvector extension

Revision ID: 48e6215726c4
Revises: 
Create Date: 2025-04-30 19:22:21.735866

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '48e6215726c4'
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
