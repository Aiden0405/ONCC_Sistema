"""Unifica formaciones y sensibilizaciones en formacion.

Revision ID: f4a5b6c7d8e9
Revises: c3d4e5f6a7b8
"""
from alembic import op
import sqlalchemy as sa


revision = 'f4a5b6c7d8e9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def _has_table(bind, name):
    return sa.inspect(bind).has_table(name)


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    formacion_columns = {column['name'] for column in inspector.get_columns('formacion')}

    op.execute('ALTER TABLE formacion DROP CONSTRAINT IF EXISTS chk_solo_formacion')

    if 'tipo_actividad' not in formacion_columns:
        op.add_column('formacion', sa.Column('tipo_actividad', sa.String(length=50), nullable=True))
    if 'tipo_destino' not in formacion_columns:
        op.add_column('formacion', sa.Column('tipo_destino', sa.String(length=30), nullable=True))
    if 'id_tecnico' not in formacion_columns:
        op.add_column('formacion', sa.Column('id_tecnico', sa.Integer(), nullable=True))

    op.execute("UPDATE formacion SET tipo_actividad = 'FORMACION' WHERE tipo_actividad IS NULL")
    op.execute("UPDATE formacion SET tipo_destino = CASE WHEN id_institucion IS NULL THEN 'COMUNIDAD' ELSE 'INSTITUCION' END WHERE tipo_destino IS NULL")
    op.alter_column('formacion', 'id_institucion', nullable=True)
    op.alter_column('formacion', 'tipo_actividad', nullable=False, server_default='FORMACION')
    op.alter_column('formacion', 'tipo_destino', nullable=False, server_default='COMUNIDAD')
    op.execute("ALTER TABLE formacion ADD CONSTRAINT chk_formacion_tipo CHECK (tipo_actividad IN ('FORMACION', 'SENSIBILIZACION'))")

    if _has_table(bind, 'sensibilizacion'):
        op.execute("""
            INSERT INTO formacion
                (nombre_formacion, id_actividad, id_institucion, tipo_actividad, tipo_destino, id_tecnico, id_nivel)
            SELECT nombre_sensibilizacion, id_actividad, NULL, 'SENSIBILIZACION', 'COMUNIDAD', NULL, id_nivel
            FROM sensibilizacion
            WHERE NOT EXISTS (
                SELECT 1 FROM formacion f WHERE f.id_actividad = sensibilizacion.id_actividad
            )
        """)
        op.drop_table('sensibilizacion')


def downgrade():
    bind = op.get_bind()
    if not _has_table(bind, 'sensibilizacion'):
        op.create_table(
            'sensibilizacion',
            sa.Column('id_sensibilizacion', sa.Integer(), primary_key=True),
            sa.Column('nombre_sensibilizacion', sa.Text(), nullable=False),
            sa.Column('id_actividad', sa.Integer(), nullable=False),
            sa.Column('tipo_actividad', sa.String(length=50), nullable=False, server_default='SENSIBILIZACION'),
            sa.Column('id_nivel', sa.Integer(), nullable=False),
        )
    op.execute("""
        INSERT INTO sensibilizacion (nombre_sensibilizacion, id_actividad, tipo_actividad, id_nivel)
        SELECT nombre_formacion, id_actividad, tipo_actividad, id_nivel
        FROM formacion
        WHERE tipo_actividad = 'SENSIBILIZACION'
    """)
    op.drop_column('formacion', 'id_tecnico')
    op.drop_column('formacion', 'tipo_destino')
    op.drop_column('formacion', 'tipo_actividad')
