"""Columnas de inventario para formulario de equipos

Revision ID: a1f2c3d4e5b6
Revises: 7653e1663a01
Create Date: 2026-08-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1f2c3d4e5b6'
down_revision = '7653e1663a01'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('equipo', sa.Column('condicion', sa.String(length=30), nullable=False, server_default='Operativo'))
    op.add_column('equipo', sa.Column('responsable', sa.String(length=120), nullable=True))
    op.add_column('equipo', sa.Column('ultimo_mantenimiento', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('equipo', 'ultimo_mantenimiento')
    op.drop_column('equipo', 'responsable')
    op.drop_column('equipo', 'condicion')
