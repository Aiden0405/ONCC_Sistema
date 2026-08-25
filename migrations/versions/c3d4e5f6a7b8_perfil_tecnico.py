"""Perfil de técnico: especialidad y enlace con usuario

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tecnicos', sa.Column('especialidad', sa.String(length=100), nullable=True))
    op.add_column('tecnicos', sa.Column('id_usuario', sa.Integer(), nullable=True))
    op.create_unique_constraint('uq_tecnicos_id_usuario', 'tecnicos', ['id_usuario'])


def downgrade():
    op.drop_constraint('uq_tecnicos_id_usuario', 'tecnicos', type_='unique')
    op.drop_column('tecnicos', 'id_usuario')
    op.drop_column('tecnicos', 'especialidad')
