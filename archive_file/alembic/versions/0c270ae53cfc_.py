"""empty message

Revision ID: 0c270ae53cfc
Revises: 37ad2116233b
Create Date: 2018-07-02 16:44:25.751129

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0c270ae53cfc'
down_revision = '37ad2116233b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dicts', 'os_timestamp')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dicts', sa.Column('os_timestamp', mysql.FLOAT(), nullable=True))
    # ### end Alembic commands ###