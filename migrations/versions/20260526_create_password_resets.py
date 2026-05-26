"""Crear tabla password_resets

Revision ID: 20260526_create_password_resets
Revises: 20260526_create_publicaciones
Create Date: 2026-05-26 00:00:02.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260526_create_password_resets'
down_revision = '20260526_create_publicaciones'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'password_resets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('usuarios.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(length=128), nullable=False, unique=True),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expiracion', sa.DateTime(), nullable=False),
        sa.Column('usado', sa.Boolean(), nullable=False, server_default=sa.text('0')),
    )
    op.create_index('idx_password_resets_user_id', 'password_resets', ['user_id'])


def downgrade():
    op.drop_index('idx_password_resets_user_id', table_name='password_resets')
    op.drop_table('password_resets')
