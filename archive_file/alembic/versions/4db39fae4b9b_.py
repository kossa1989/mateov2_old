"""empty message

Revision ID: 4db39fae4b9b
Revises: 0c270ae53cfc
Create Date: 2018-07-05 09:51:55.208892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4db39fae4b9b'
down_revision = '0c270ae53cfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dicts', sa.Column('path_pickle', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dicts', 'path_pickle')
    # ### end Alembic commands ###
