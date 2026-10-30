"""update vector dimension to 768 for gemini

Revision ID: 2c7b89e3f4a1
Revises: 1b586c52e5eb
Create Date: 2026-10-30 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import pgvector

# revision identifiers, used by Alembic.
revision: str = '2c7b89e3f4a1'
down_revision: Union[str, Sequence[str], None] = '1b586c52e5eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure vector extension is present
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector;"))
    # Clear any orphaned/mismatched chunks from testing
    op.execute(sa.text("DELETE FROM document_chunks;"))
    # Alter column to exactly 768 dimensions matching Gemini text-embedding-001
    op.execute(sa.text("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768);"))


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM document_chunks;"))
    op.execute(sa.text("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536);"))
