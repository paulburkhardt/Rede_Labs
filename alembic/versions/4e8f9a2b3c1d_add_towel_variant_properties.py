"""add towel variant properties

Revision ID: 4e8f9a2b3c1d
Revises: bd3be98698d9
Create Date: 2025-10-29 21:59:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e8f9a2b3c1d'
down_revision = 'bd3be98698d9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for towel variants
    towel_variant_enum = sa.Enum('budget', 'mid_tier', 'premium', name='towelvariant')
    towel_variant_enum.create(op.get_bind(), checkfirst=True)
    
    # Add towel variant columns to products table (all required/NOT NULL)
    op.add_column('products', sa.Column('towel_variant', towel_variant_enum, nullable=False))
    op.add_column('products', sa.Column('gsm', sa.Integer(), nullable=False))
    op.add_column('products', sa.Column('width_inches', sa.Integer(), nullable=False))
    op.add_column('products', sa.Column('length_inches', sa.Integer(), nullable=False))
    op.add_column('products', sa.Column('material', sa.String(), nullable=False))
    op.add_column('products', sa.Column('wholesale_cost_cents', sa.Integer(), nullable=False))


def downgrade() -> None:
    # Drop towel variant columns
    op.drop_column('products', 'wholesale_cost_cents')
    op.drop_column('products', 'material')
    op.drop_column('products', 'length_inches')
    op.drop_column('products', 'width_inches')
    op.drop_column('products', 'gsm')
    op.drop_column('products', 'towel_variant')
    
    # Drop enum type
    towel_variant_enum = sa.Enum('budget', 'mid_tier', 'premium', name='towelvariant')
    towel_variant_enum.drop(op.get_bind(), checkfirst=True)
