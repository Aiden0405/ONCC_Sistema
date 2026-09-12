"""Agregar excepciones de permisos por usuario.

Revision ID: e7f8a9b0c1d2
Revises: 7653e1663a01
"""
from alembic import op
import sqlalchemy as sa

revision = 'e7f8a9b0c1d2'
down_revision = '7653e1663a01'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'usuario_permiso_excepcion',
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('id_modulo', sa.Integer(), nullable=False),
        sa.Column('concedido', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_modulo'], ['modulos.id_modulo'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_usuario', 'id_modulo'),
    )


def downgrade():
    op.drop_table('usuario_permiso_excepcion')
