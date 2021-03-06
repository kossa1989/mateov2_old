"""empty message

Revision ID: 6934b3be5e69
Revises: 1c945540a3cd
Create Date: 2018-04-27 11:34:27.382000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6934b3be5e69'
down_revision = '1c945540a3cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pl_wm',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.Column('nazwa', sa.String(length=500), nullable=True),
    sa.Column('jedn_miary', sa.String(length=40), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pl_wm')
    # ### end Alembic commands ###
