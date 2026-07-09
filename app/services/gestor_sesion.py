import secrets
from datetime import datetime

from flask_login import login_user, logout_user

from app import db
from app.models.usuario import Usuario
from app.models.password_reset import PasswordReset


class GestorSesion:
    """Encapsula la lógica de autenticación del sistema usando Flask-Login.

    También maneja recuperación de contraseña mediante tokens guardados en BD.
    """

    def iniciar_sesion(self, usuario: Usuario):
        login_user(usuario)

    def cerrar_sesion(self):
        logout_user()

    def solicitar_recuperacion(self, correo: str):
        u = Usuario.query.filter_by(correo=correo).first()
        if not u:
            return None
        token = secrets.token_urlsafe(24)
        pr = PasswordReset(user_id=u.id, token=token, creado_en=datetime.utcnow())
        db.session.add(pr)
        db.session.commit()
        # En producción: enviar por correo. Aquí devolvemos token para pruebas.
        return token

    def confirmar_restauracion(self, token: str, nueva_password: str):
        pr = PasswordReset.query.filter_by(token=token).first()
        if not pr or not pr.is_valid():
            return False
        
        # CORRECCIÓN: Si pr.usuario actúa como una lista, agarramos el primer elemento [0]
        # Si no es una lista sino un objeto directo, intentamos usarlo normal
        try:
            user = pr.usuario[0] if isinstance(pr.usuario, list) else pr.usuario
        except TypeError:
            user = pr.usuario

        if user:
            user.set_password(nueva_password)
            pr.usado = True
            db.session.commit()
            return True
        return False