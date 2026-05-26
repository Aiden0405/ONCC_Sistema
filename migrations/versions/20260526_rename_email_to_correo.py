"""Rename usuarios.email to usuarios.correo

Revision ID: 20260526_rename_email_to_correo
Revises: 935e8e94b01b
Create Date: 2026-05-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260526_rename_email_to_correo'
down_revision = '935e8e94b01b'
branch_labels = None
depends_on = None


def upgrade():
    # Renombrar columna email -> correo en tabla usuarios
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.alter_column('email', new_column_name='correo')


def downgrade():
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.alter_column('correo', new_column_name='email')
