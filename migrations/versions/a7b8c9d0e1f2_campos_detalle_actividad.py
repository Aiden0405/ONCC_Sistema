"""Add detail fields used by the activity registration form."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = 'a7b8c9d0e1f2'
down_revision = 'f5a6b7c8d9e0'
branch_labels = None
depends_on = None


def upgrade():
    inspector = inspect(op.get_bind())
    columns = {column['name'] for column in inspector.get_columns('actividad')}
    additions = {
        'descripcion': sa.Column('descripcion', sa.Text(), nullable=True),
        'poblacion': sa.Column('poblacion', sa.Integer(), nullable=False, server_default='0'),
        'acuerdos': sa.Column('acuerdos', sa.Text(), nullable=True),
        'minuta_archivo': sa.Column('minuta_archivo', sa.String(length=255), nullable=True),
        'fotos_archivos': sa.Column('fotos_archivos', sa.Text(), nullable=True),
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column('actividad', column)


def downgrade():
    inspector = inspect(op.get_bind())
    columns = {column['name'] for column in inspector.get_columns('actividad')}
    for name in ('fotos_archivos', 'minuta_archivo', 'acuerdos', 'poblacion', 'descripcion'):
        if name in columns:
            op.drop_column('actividad', name)