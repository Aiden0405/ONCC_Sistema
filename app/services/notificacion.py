from app import db
from app.models.notificacion import Notificacion
from app.models.usuario import Usuario

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
        """Notifica a todos los usuarios que tengan el permiso dado, excluyendo al emisor."""
        try:
            usuarios = Usuario.query.all()
            for u in usuarios:
                # Usa tu sistema existente de permisos en el modelo Usuario
                tiene_permiso = getattr(u, 'has_permission', lambda p: False)(permiso_requerido)
                es_super = getattr(u, 'id_rol', None) in (1, 2)
                
                if (tiene_permiso or es_super) and u.id_usuario != emisor_id:
                    notif = Notificacion(
                        id_usuario=u.id_usuario,
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