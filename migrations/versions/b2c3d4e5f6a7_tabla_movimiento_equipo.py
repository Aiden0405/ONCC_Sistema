"""Tabla movimiento_equipo para historial real de movimientos

Revision ID: b2c3d4e5f6a7
Revises: a1f2c3d4e5b6
Create Date: 2026-08-20 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1f2c3d4e5b6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('movimiento_equipo',
    sa.Column('id_movimiento', sa.Integer(), nullable=False),
    sa.Column('id_equipo', sa.Integer(), nullable=False),
    sa.Column('fecha_movimiento', sa.Date(), nullable=False),
    sa.Column('ubicacion_origen', sa.String(length=100), nullable=False),
    sa.Column('ubicacion_destino', sa.String(length=100), nullable=False),
    sa.Column('motivo_responsable', sa.String(length=200), nullable=False),
    sa.Column('creado_en', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['id_equipo'], ['equipo.id_equipo']),
    sa.PrimaryKeyConstraint('id_movimiento')
    )


def downgrade():
    op.drop_table('movimiento_equipo')
