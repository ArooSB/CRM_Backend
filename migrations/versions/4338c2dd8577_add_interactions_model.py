"""Add interactions model

Revision ID: 4338c2dd8577
Revises: d610b6c25bd8
Create Date: 2024-11-17 16:18:01.045312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4338c2dd8577'
down_revision = 'd610b6c25bd8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('worker_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('interaction_type', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('interaction_date', sa.Date(), nullable=False))
        batch_op.add_column(sa.Column('interaction_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('communication_summary', sa.Text(), nullable=True))
        batch_op.create_foreign_key(None, 'workers', ['worker_id'], ['id'])
        batch_op.drop_column('notes')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('communication_summary')
        batch_op.drop_column('interaction_notes')
        batch_op.drop_column('interaction_date')
        batch_op.drop_column('interaction_type')
        batch_op.drop_column('worker_id')

    # ### end Alembic commands ###
