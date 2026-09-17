from flask import current_app

from app import db
from app.models.notificacion import Notificacion
from app.models.usuario import Usuario
from app.utils.authorization import has_full_access_role, is_superuser_role

class ServicioNotificacion:

    @staticmethod
    def crear_aviso(id_usuario, mensaje, categoria="Sistema"):
        """Guarda la notificación para un usuario individual."""
        try:
            notif = Notificacion(
                id_usuario=id_usuario,
                mensaje=mensaje,
                categoria=categoria,
                leido=False
            )
            db.session.add(notif)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def notificar_por_permiso(permiso_requerido, mensaje, categoria="Sistema", emisor_id=None):
        """Notifica al personal autorizado, excluyendo siempre al emisor.

        Los roles con acceso completo reciben todos los eventos. El resto solo
        recibe los eventos del permiso correspondiente a su módulo.
        """
        try:
            destinatarios = []
            usuarios = Usuario.query.filter_by(estatus=True).all()
            for u in usuarios:
                if u.id_usuario == emisor_id:
                    continue

                rol = getattr(u, 'rol', '')
                tiene_permiso = u.has_permission(permiso_requerido)
                if tiene_permiso or has_full_access_role(rol) or is_superuser_role(rol):
                    destinatarios.append(u.id_usuario)

            for id_usuario in destinatarios:
                db.session.add(Notificacion(
                    id_usuario=id_usuario,
                    mensaje=mensaje,
                    categoria=categoria,
                    leido=False,
                ))

            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            current_app.logger.exception('No se pudo distribuir una notificación.')
            return False