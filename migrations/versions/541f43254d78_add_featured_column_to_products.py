"""Add featured column to products

Revision ID: 541f43254d78
Revises: ae1a76cd5b7e
Create Date: 2025-09-16 14:12:41.534172
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '541f43254d78'
down_revision = 'ae1a76cd5b7e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('featured', sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('featured')
