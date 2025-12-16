"""Add research FK to articles

Revision ID: 004_add_research_to_articles
Revises: 003_add_entity_tables
Create Date: 2025-12-08 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_research_to_articles'
down_revision: Union[str, None] = '003_add_entity_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add research_id foreign key column to articles table
    op.add_column('articles', sa.Column('research_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_articles_research_id',
        'articles',
        'researches',
        ['research_id'],
        ['id']
    )
    op.create_index(op.f('ix_articles_research_id'), 'articles', ['research_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_articles_research_id'), table_name='articles')
    op.drop_constraint('fk_articles_research_id', 'articles', type_='foreignkey')
    op.drop_column('articles', 'research_id')
