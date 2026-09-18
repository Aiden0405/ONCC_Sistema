"""merge de migraciones

Revision ID: a910b0ff37f2
Revises: 54efdb7c6d28, c151141fef6e
Create Date: 2026-09-17 10:17:43.813722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a910b0ff37f2'
down_revision = ('54efdb7c6d28', 'c151141fef6e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
