"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-08 12:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create hypotheses table
    op.create_table(
        'hypotheses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hypotheses_id'), 'hypotheses', ['id'], unique=False)
    op.create_index(op.f('ix_hypotheses_title'), 'hypotheses', ['title'], unique=True)
    
    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_articles_id'), 'articles', ['id'], unique=False)
    op.create_index(op.f('ix_articles_url'), 'articles', ['url'], unique=True)
    
    # Create validation_results table
    op.create_table(
        'validation_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hypothesis_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('relevancy', sa.Float(), nullable=False),
        sa.Column('key_take', sa.Text(), nullable=False),
        sa.Column('validity', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.ForeignKeyConstraint(['hypothesis_id'], ['hypotheses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_validation_results_id'), 'validation_results', ['id'], unique=False)
    op.create_index(op.f('ix_validation_results_hypothesis_id'), 'validation_results', ['hypothesis_id'], unique=False)
    op.create_index(op.f('ix_validation_results_article_id'), 'validation_results', ['article_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_validation_results_article_id'), table_name='validation_results')
    op.drop_index(op.f('ix_validation_results_hypothesis_id'), table_name='validation_results')
    op.drop_index(op.f('ix_validation_results_id'), table_name='validation_results')
    op.drop_table('validation_results')
    op.drop_index(op.f('ix_articles_url'), table_name='articles')
    op.drop_index(op.f('ix_articles_id'), table_name='articles')
    op.drop_table('articles')
    op.drop_index(op.f('ix_hypotheses_title'), table_name='hypotheses')
    op.drop_index(op.f('ix_hypotheses_id'), table_name='hypotheses')
    op.drop_table('hypotheses')

