"""Add entity tables

Revision ID: 003_add_entity_tables
Revises: 002_add_topic_fields
Create Date: 2025-12-08 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_entity_tables'
down_revision: Union[str, None] = '002_add_topic_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create entity_types table
    op.create_table(
        'entity_types',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_entity_types_id'), 'entity_types', ['id'], unique=False)
    op.create_index(op.f('ix_entity_types_name'), 'entity_types', ['name'], unique=True)
    
    # Create diseases table
    op.create_table(
        'diseases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('entity_type_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['entity_type_id'], ['entity_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diseases_id'), 'diseases', ['id'], unique=False)
    op.create_index(op.f('ix_diseases_name'), 'diseases', ['name'], unique=True)
    op.create_index(op.f('ix_diseases_entity_type_id'), 'diseases', ['entity_type_id'], unique=False)
    
    # Create targets table
    op.create_table(
        'targets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('entity_type_id', sa.Integer(), nullable=True),
        sa.Column('disease_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['disease_id'], ['diseases.id'], ),
        sa.ForeignKeyConstraint(['entity_type_id'], ['entity_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_targets_id'), 'targets', ['id'], unique=False)
    op.create_index(op.f('ix_targets_name'), 'targets', ['name'], unique=True)
    op.create_index(op.f('ix_targets_entity_type_id'), 'targets', ['entity_type_id'], unique=False)
    op.create_index(op.f('ix_targets_disease_id'), 'targets', ['disease_id'], unique=False)
    
    # Create drugs table
    op.create_table(
        'drugs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('entity_type_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['entity_type_id'], ['entity_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_drugs_id'), 'drugs', ['id'], unique=False)
    op.create_index(op.f('ix_drugs_name'), 'drugs', ['name'], unique=True)
    op.create_index(op.f('ix_drugs_entity_type_id'), 'drugs', ['entity_type_id'], unique=False)
    
    # Create effects table
    op.create_table(
        'effects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('entity_type_id', sa.Integer(), nullable=True),
        sa.Column('drug_id', sa.Integer(), nullable=True),
        sa.Column('effect_type', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['drug_id'], ['drugs.id'], ),
        sa.ForeignKeyConstraint(['entity_type_id'], ['entity_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_effects_id'), 'effects', ['id'], unique=False)
    op.create_index(op.f('ix_effects_entity_type_id'), 'effects', ['entity_type_id'], unique=False)
    op.create_index(op.f('ix_effects_drug_id'), 'effects', ['drug_id'], unique=False)
    
    # Create researches table
    op.create_table(
        'researches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('primary_item', sa.String(), nullable=False),
        sa.Column('secondary_item', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_researches_id'), 'researches', ['id'], unique=False)
    
    # Insert initial data into entity_types
    op.execute("""
        INSERT INTO entity_types (name) VALUES
        ('Disease'),
        ('Target'),
        ('Drug'),
        ('Effect')
    """)
    
    # Get entity type IDs for foreign keys
    # Note: We'll use a subquery approach since we can't easily get IDs in raw SQL migration
    # Insert diseases
    op.execute("""
        INSERT INTO diseases (name, entity_type_id) VALUES
        ('Obesity', (SELECT id FROM entity_types WHERE name = 'Disease')),
        ('Diabetes Type 2', (SELECT id FROM entity_types WHERE name = 'Disease')),
        ('Alzheimer', (SELECT id FROM entity_types WHERE name = 'Disease'))
    """)
    
    # Insert targets
    op.execute("""
        INSERT INTO targets (name, entity_type_id) VALUES
        ('GLP-1 receptor', (SELECT id FROM entity_types WHERE name = 'Target'))
    """)
    
    # Insert drugs
    op.execute("""
        INSERT INTO drugs (name, entity_type_id) VALUES
        ('Ozempic', (SELECT id FROM entity_types WHERE name = 'Drug'))
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_researches_id'), table_name='researches')
    op.drop_table('researches')
    op.drop_index(op.f('ix_effects_drug_id'), table_name='effects')
    op.drop_index(op.f('ix_effects_entity_type_id'), table_name='effects')
    op.drop_index(op.f('ix_effects_id'), table_name='effects')
    op.drop_table('effects')
    op.drop_index(op.f('ix_drugs_entity_type_id'), table_name='drugs')
    op.drop_index(op.f('ix_drugs_name'), table_name='drugs')
    op.drop_index(op.f('ix_drugs_id'), table_name='drugs')
    op.drop_table('drugs')
    op.drop_index(op.f('ix_targets_disease_id'), table_name='targets')
    op.drop_index(op.f('ix_targets_entity_type_id'), table_name='targets')
    op.drop_index(op.f('ix_targets_name'), table_name='targets')
    op.drop_index(op.f('ix_targets_id'), table_name='targets')
    op.drop_table('targets')
    op.drop_index(op.f('ix_diseases_entity_type_id'), table_name='diseases')
    op.drop_index(op.f('ix_diseases_name'), table_name='diseases')
    op.drop_index(op.f('ix_diseases_id'), table_name='diseases')
    op.drop_table('diseases')
    op.drop_index(op.f('ix_entity_types_name'), table_name='entity_types')
    op.drop_index(op.f('ix_entity_types_id'), table_name='entity_types')
    op.drop_table('entity_types')
