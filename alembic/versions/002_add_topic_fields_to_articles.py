"""Add topic fields to articles

Revision ID: 002_add_topic_fields
Revises: 001_initial
Create Date: 2025-12-08 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_topic_fields'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add topic, main_item, and secondary_item columns to articles table
    op.add_column('articles', sa.Column('topic', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('main_item', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('secondary_item', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('articles', 'secondary_item')
    op.drop_column('articles', 'main_item')
    op.drop_column('articles', 'topic')
