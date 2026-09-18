"""Completa la integridad de formacion unificada.

Revision ID: f5a6b7c8d9e0
Revises: f4a5b6c7d8e9
"""
from alembic import op
import sqlalchemy as sa


revision = 'f5a6b7c8d9e0'
down_revision = 'f4a5b6c7d8e9'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    foreign_keys = {fk.get('name') for fk in inspector.get_foreign_keys('formacion')}
    if 'fk_formacion_tecnico' not in foreign_keys:
        op.create_foreign_key(
            'fk_formacion_tecnico', 'formacion', 'tecnicos',
            ['id_tecnico'], ['id_tecnico'], ondelete='SET NULL'
        )

    op.execute("""
        UPDATE formacion f
        SET id_tecnico = t.id_tecnico
        FROM tecnicos t
        WHERE f.id_tecnico IS NULL
          AND position('||' in f.nombre_formacion) > 0
          AND trim(split_part(f.nombre_formacion, '||', 2)) =
              trim(t.nombres) || ' ' || trim(t.apellidos)
    """)


def downgrade():
    op.drop_constraint('fk_formacion_tecnico', 'formacion', type_='foreignkey')
