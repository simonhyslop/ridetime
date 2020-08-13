"""Initial setup

Revision ID: 2f204ec873a0
Revises: 
Create Date: 2020-08-10 17:11:08.624243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f204ec873a0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('social_id', sa.String(length=64), nullable=False),
    sa.Column('nickname', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_id')
    )
    op.create_table('route',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('public', sa.Boolean(), nullable=True),
    sa.Column('title', sa.String(length=120), nullable=True),
    sa.Column('distance', sa.Integer(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('bbox', sa.String(length=120), nullable=True),
    sa.Column('polyline', sa.String(length=120), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_route_public'), 'route', ['public'], unique=False)
    op.create_index(op.f('ix_route_timestamp'), 'route', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_route_timestamp'), table_name='route')
    op.drop_index(op.f('ix_route_public'), table_name='route')
    op.drop_table('route')
    op.drop_table('user')
    # ### end Alembic commands ###
