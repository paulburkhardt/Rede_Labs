"""add_wholesale_cost_at_purchase_to_purchases

Revision ID: 88bb53bc0a70
Revises: 4e8f9a2b3c1d
Create Date: 2025-10-29 22:27:42.551606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88bb53bc0a70'
down_revision = '4e8f9a2b3c1d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add wholesale_cost_at_purchase column to purchases table
    op.add_column('purchases', sa.Column('wholesale_cost_at_purchase', sa.Integer(), nullable=False, server_default='0'))
    # Remove server_default after adding the column
    op.alter_column('purchases', 'wholesale_cost_at_purchase', server_default=None)


def downgrade() -> None:
    # Remove wholesale_cost_at_purchase column from purchases table
    op.drop_column('purchases', 'wholesale_cost_at_purchase')
