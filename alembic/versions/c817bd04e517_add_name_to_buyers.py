"""Add buyer name column

Revision ID: c817bd04e517
Revises: 8910042dc77d
Create Date: 2025-11-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c817bd04e517'
down_revision = '8910042dc77d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('buyers', sa.Column('name', sa.String(), nullable=True))
    op.execute("UPDATE buyers SET name = 'unknown_buyer' WHERE name IS NULL")
    op.alter_column('buyers', 'name', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    op.drop_column('buyers', 'name')
