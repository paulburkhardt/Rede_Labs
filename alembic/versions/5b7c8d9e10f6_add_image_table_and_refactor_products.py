"""Add image table and refactor products

Revision ID: 5b7c8d9e10f6
Revises: 4ae0691e63d5
Create Date: 2025-10-27 19:16:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b7c8d9e10f6'
down_revision = 'f673f1ed3fc4'  # Changed to point to the latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create images table
    op.create_table('images',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('base64', sa.Text(), nullable=False),
        sa.Column('image_description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add image_id column to products table
    op.add_column('products', sa.Column('image_id', sa.String(), nullable=True))
    op.create_foreign_key('fk_products_image_id', 'products', 'images', ['image_id'], ['id'])
    
    # Remove old image columns from products table
    op.drop_column('products', 'image_url')
    op.drop_column('products', 'image_alternative_text')


def downgrade() -> None:
    # Add back old image columns to products table
    op.add_column('products', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('products', sa.Column('image_alternative_text', sa.String(), nullable=True))
    
    # Remove image_id column and foreign key
    op.drop_constraint('fk_products_image_id', 'products', type_='foreignkey')
    op.drop_column('products', 'image_id')
    
    # Drop images table
    op.drop_table('images')
