"""empty message

Revision ID: 6fc499d59a6f
Revises: 7357a07fd916
Create Date: 2021-02-01 17:21:44.603872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fc499d59a6f'
down_revision = '7357a07fd916'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dialog', sa.Column('type', sa.String(length=32), nullable=True))
    op.create_index(op.f('ix_dialog_type'), 'dialog', ['type'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_dialog_type'), table_name='dialog')
    op.drop_column('dialog', 'type')
    # ### end Alembic commands ###
