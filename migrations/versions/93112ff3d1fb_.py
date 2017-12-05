"""empty message

Revision ID: 93112ff3d1fb
Revises: 38b7a1032bdd
Create Date: 2017-12-04 09:00:34.910752

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '93112ff3d1fb'
down_revision = '38b7a1032bdd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(length=128), nullable=False),
    sa.Column('result', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_results_domain'), 'results', ['domain'], unique=False)
    op.add_column('links', sa.Column('broken_links', sa.JSON(), nullable=True))
    op.add_column('links', sa.Column('last_check_result_id', sa.Integer(), nullable=True))
    op.alter_column('links', 'domain',
               existing_type=mysql.VARCHAR(length=128),
               nullable=False)
    op.create_index(op.f('ix_links_domain'), 'links', ['domain'], unique=True)
    op.create_foreign_key(None, 'links', 'results', ['last_check_result_id'], ['id'])
    op.drop_column('links', 'brokenLinkList')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('links', sa.Column('brokenLinkList', mysql.JSON(), nullable=True))
    op.drop_constraint(None, 'links', type_='foreignkey')
    op.drop_index(op.f('ix_links_domain'), table_name='links')
    op.alter_column('links', 'domain',
               existing_type=mysql.VARCHAR(length=128),
               nullable=True)
    op.drop_column('links', 'last_check_result_id')
    op.drop_column('links', 'broken_links')
    op.drop_index(op.f('ix_results_domain'), table_name='results')
    op.drop_table('results')
    # ### end Alembic commands ###
