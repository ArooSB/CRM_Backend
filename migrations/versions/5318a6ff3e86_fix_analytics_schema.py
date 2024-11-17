"""Fix analytics schema

Revision ID: 5318a6ff3e86
Revises: 4338c2dd8577
Create Date: 2024-11-17 16:29:38.881301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5318a6ff3e86'
down_revision = '4338c2dd8577'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('analytics_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('customer_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('worker_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('period_start_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('period_end_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('metric_value', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.drop_column('id')
        batch_op.drop_column('data')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
        batch_op.drop_column('updated_at')
        batch_op.drop_column('metric_value')
        batch_op.drop_column('period_end_date')
        batch_op.drop_column('period_start_date')
        batch_op.drop_column('worker_id')
        batch_op.drop_column('customer_id')
        batch_op.drop_column('analytics_id')

    # ### end Alembic commands ###
