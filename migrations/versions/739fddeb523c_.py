"""empty message

Revision ID: 739fddeb523c
Revises: 
Create Date: 2019-05-01 12:37:09.960928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '739fddeb523c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hosts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('domain', sa.String(length=64), nullable=True),
    sa.Column('ip', sa.String(length=128), nullable=True),
    sa.Column('note', sa.String(length=64), nullable=True),
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hosts_domain'), 'hosts', ['domain'], unique=False)
    op.create_index(op.f('ix_hosts_status'), 'hosts', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_hosts_status'), table_name='hosts')
    op.drop_index(op.f('ix_hosts_domain'), table_name='hosts')
    op.drop_table('hosts')
    # ### end Alembic commands ###