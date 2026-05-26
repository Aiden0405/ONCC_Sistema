"""Crear tabla publicaciones

Revision ID: 20260526_create_publicaciones
Revises: 20260526_rename_email_to_correo
Create Date: 2026-05-26 00:00:00.000001
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260526_create_publicaciones'
down_revision = '20260526_rename_email_to_correo'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'publicaciones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tipo', sa.String(length=40), nullable=False, server_default='boletin'),
        sa.Column('titulo', sa.String(length=180), nullable=False),
        sa.Column('resumen', sa.Text(), nullable=True),
        sa.Column('contenido', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='borrador'),
        sa.Column('publicado_en', sa.DateTime(), nullable=True),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade():
    op.drop_table('publicaciones')
