"""Initial migration for Sheep model

Revision ID: 59c14d866340
Revises: 
Create Date: 2025-05-31 18:05:20.225878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59c14d866340'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sheep',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.String(length=50), nullable=False),
    sa.Column('gender', sa.String(length=10), nullable=False),
    sa.Column('pregnant', sa.Boolean(), nullable=True),
    sa.Column('medical_records', sa.Text(), nullable=True),
    sa.Column('image', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tag_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sheep')
    # ### end Alembic commands ###
