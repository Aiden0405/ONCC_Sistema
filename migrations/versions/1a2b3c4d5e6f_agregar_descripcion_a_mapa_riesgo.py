"""Agregar columnas a tabla mapa_riesgo existente

Revision ID: 1a2b3c4d5e6f
Revises: a6b7f3a058e2
Create Date: 2026-07-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '1a2b3c4d5e6f'
down_revision = '7920ac77e437'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('mapa_riesgo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nombre', sa.String(length=150), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('descripcion', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('archivo', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('estado', sa.String(length=20), nullable=False, server_default='borrador'))
        batch_op.add_column(sa.Column('version', sa.String(length=30), nullable=False, server_default='v1.0'))
        batch_op.add_column(sa.Column('cobertura', sa.String(length=120), nullable=False, server_default='Regional'))
        batch_op.add_column(sa.Column('responsable', sa.String(length=120), nullable=False, server_default='Equipo Geomatica'))
        batch_op.add_column(sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.func.now()))
        batch_op.add_column(sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade():
    with op.batch_alter_table('mapa_riesgo', schema=None) as batch_op:
        batch_op.drop_column('actualizado_en')
        batch_op.drop_column('creado_en')
        batch_op.drop_column('responsable')
        batch_op.drop_column('cobertura')
        batch_op.drop_column('version')
        batch_op.drop_column('estado')
        batch_op.drop_column('archivo')
        batch_op.drop_column('descripcion')
        batch_op.drop_column('nombre')
