"""Agregar propietario opcional a las actividades.

Revision ID: f1a2b3c4d5e6
Revises: e7f8a9b0c1d2
"""
from alembic import op
import sqlalchemy as sa

revision = 'f1a2b3c4d5e6'
down_revision = 'e7f8a9b0c1d2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('actividad', sa.Column('id_usuario', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('actividad', 'id_usuario')