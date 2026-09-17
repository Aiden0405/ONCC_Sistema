"""Fusionar multiples cabezas

Revision ID: c151141fef6e
Revises: a7b8c9d0e1f2, dc4ff1e3848b, f1a2b3c4d5e6
Create Date: 2026-09-17 06:24:43.436930

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c151141fef6e'
down_revision = ('a7b8c9d0e1f2', 'dc4ff1e3848b', 'f1a2b3c4d5e6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
