"""fusión de migraciones

Revision ID: 54efdb7c6d28
Revises: dc4ff1e3848b, f1a2b3c4d5e6
Create Date: 2026-09-14 00:23:02.190556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54efdb7c6d28'
down_revision = ('dc4ff1e3848b', 'f1a2b3c4d5e6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
