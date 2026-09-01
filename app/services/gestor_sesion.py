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

        PasswordReset.query.filter_by(user_id=u.id, usado=False).delete()
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

        user = pr.usuario
        if not user:
            return False

        user.set_password(nueva_password)
        pr.usado = True
        db.session.commit()
        return True