"""Remove unique constraint on articles.url

Revision ID: 005_remove_unique_url_constraint
Revises: 004_add_research_to_articles
Create Date: 2025-12-08 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_remove_unique_url_constraint'
down_revision: Union[str, None] = '004_add_research_to_articles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove unique constraint on articles.url
    # Articles can now have the same URL but different research_id
    op.drop_index('ix_articles_url', table_name='articles')
    op.create_index('ix_articles_url', 'articles', ['url'], unique=False)


def downgrade() -> None:
    # Restore unique constraint on articles.url
    op.drop_index('ix_articles_url', table_name='articles')
    op.create_index('ix_articles_url', 'articles', ['url'], unique=True)
