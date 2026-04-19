"""merge all heads final

Revision ID: 20260419_merge_final
Revises: 20260419_add_repositories_table, 25c9c391cb35
Create Date: 2026-04-19 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260419_merge_final'
down_revision = ('20260419_add_repositories_table', '25c9c391cb35')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
