"""merge repositories head with main

Revision ID: 20260419_merge_repos
Revises: 25c9c391cb35, 20260419_repositories
Create Date: 2026-04-19 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260419_merge_repos'
down_revision = ('25c9c391cb35', '20260419_repositories')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge migration - no schema changes needed
    pass


def downgrade():
    pass
