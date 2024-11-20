"""Change metric_value to string

Revision ID: c84e118615e0
Revises: df34000fdf80
Create Date: 2024-11-17 20:48:57.867865

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c84e118615e0'
down_revision = 'df34000fdf80'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.alter_column('metric_value',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.String(length=50),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.alter_column('metric_value',
               existing_type=sa.String(length=50),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)

    # ### end Alembic commands ###