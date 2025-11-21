"""add_battle_id_to_all_tables

Revision ID: c92456e9dae2
Revises: 8910042dc77d
Create Date: 2025-11-20 15:57:58.437060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c92456e9dae2'
down_revision = '8910042dc77d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add battle_id to sellers table
    op.add_column('sellers', sa.Column('battle_id', sa.String(), nullable=False, server_default='default'))
    op.alter_column('sellers', 'battle_id', server_default=None)
    op.create_index(op.f('ix_sellers_battle_id'), 'sellers', ['battle_id'], unique=False)
    
    # Add battle_id to buyers table
    op.add_column('buyers', sa.Column('battle_id', sa.String(), nullable=False, server_default='default'))
    op.alter_column('buyers', 'battle_id', server_default=None)
    op.create_index(op.f('ix_buyers_battle_id'), 'buyers', ['battle_id'], unique=False)
    
    # Add battle_id to products table
    op.add_column('products', sa.Column('battle_id', sa.String(), nullable=False, server_default='default'))
    op.alter_column('products', 'battle_id', server_default=None)
    op.create_index(op.f('ix_products_battle_id'), 'products', ['battle_id'], unique=False)
    
    # Add battle_id to purchases table
    op.add_column('purchases', sa.Column('battle_id', sa.String(), nullable=False, server_default='default'))
    op.alter_column('purchases', 'battle_id', server_default=None)
    op.create_index(op.f('ix_purchases_battle_id'), 'purchases', ['battle_id'], unique=False)
    
    # Restructure metadata table to have composite primary key (key, battle_id)
    # Drop existing primary key constraint
    op.drop_constraint('metadata_pkey', 'metadata', type_='primary')
    
    # Add battle_id column
    op.add_column('metadata', sa.Column('battle_id', sa.String(), nullable=False, server_default='default'))
    op.alter_column('metadata', 'battle_id', server_default=None)
    op.create_index(op.f('ix_metadata_battle_id'), 'metadata', ['battle_id'], unique=False)
    
    # Create new composite primary key
    op.create_primary_key('metadata_pkey', 'metadata', ['key', 'battle_id'])


def downgrade() -> None:
    # Revert metadata table changes
    op.drop_constraint('metadata_pkey', 'metadata', type_='primary')
    op.drop_index(op.f('ix_metadata_battle_id'), table_name='metadata')
    op.drop_column('metadata', 'battle_id')
    op.create_primary_key('metadata_pkey', 'metadata', ['key'])
    
    # Remove battle_id from purchases
    op.drop_index(op.f('ix_purchases_battle_id'), table_name='purchases')
    op.drop_column('purchases', 'battle_id')
    
    # Remove battle_id from products
    op.drop_index(op.f('ix_products_battle_id'), table_name='products')
    op.drop_column('products', 'battle_id')
    
    # Remove battle_id from buyers
    op.drop_index(op.f('ix_buyers_battle_id'), table_name='buyers')
    op.drop_column('buyers', 'battle_id')
    
    # Remove battle_id from sellers
    op.drop_index(op.f('ix_sellers_battle_id'), table_name='sellers')
    op.drop_column('sellers', 'battle_id')

