import requests
from flask import current_app, flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_required, login_user, logout_user
from urllib.parse import urljoin, urlparse

from flask_mail import Message
from app import mail

from app.blueprints.core import core_bp
from app.blueprints.core.forms import LoginForm, ResetRequestForm, ResetPasswordForm
from app.models.usuario import Usuario
from app.services.gestor_sesion import GestorSesion

gestor = GestorSesion()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def _recaptcha_valido():
    secret = current_app.config.get('RECAPTCHA_SECRET_KEY')
    respuesta = request.form.get('g-recaptcha-response', '').strip()
    if current_app.testing and not respuesta:
        return True
    if not secret or not respuesta:
        return False
    try:
        response = requests.post(
            current_app.config['RECAPTCHA_VERIFY_URL'],
            data={
                'secret': secret,
                'response': respuesta,
                'remoteip': request.remote_addr,
            },
            timeout=5,
        )
        return response.ok and response.json().get('success') is True
    except (requests.RequestException, ValueError):
        return False


@core_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        correo = (form.correo.data or '').strip().lower()
        password = form.password.data or ''
        if not _recaptcha_valido():
            flash('Complete correctamente la verificación de seguridad.', 'error')
            return render_template('auth/login.html', form=form)

        if not correo or not password:
            flash('Debe ingresar correo y contraseña.', 'error')
            return render_template('auth/login.html', form=form)

        usuario = Usuario.query.filter_by(correo=correo).first()

        if not usuario:
            flash('El correo no está registrado en el sistema.', 'error')
            return render_template('auth/login.html', form=form)

        if not usuario.estatus:
            flash('El usuario está inactivo. Contacte al administrador.', 'error')
            return render_template('auth/login.html', form=form)

        if usuario.check_password(password):
            gestor.iniciar_sesion(usuario)
            next_page = request.args.get('next') or form.next.data
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('dashboard'))

        flash('La contraseña es incorrecta. Intente nuevamente.', 'error')
    elif request.method == 'POST':
        flash('Revise los datos del formulario e intente nuevamente.', 'error')

    return render_template('auth/login.html', form=form)


@core_bp.route('/auth/logout')
@login_required
def logout():
    gestor.cerrar_sesion()
    return redirect(url_for('core.login'))


@core_bp.route('/auth/recuperar', methods=['GET', 'POST'])
def recuperar_contrasena():
    form = ResetRequestForm()

    if form.validate_on_submit():
        correo = (form.correo.data or '').strip().lower()

        if not _recaptcha_valido():
            flash('Complete correctamente la verificación de seguridad.', 'error')
            return render_template('auth/recuperar.html', form=form)

        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if usuario:
            token = gestor.solicitar_recuperacion(correo)
            if token:
                enlace_recuperacion = url_for('core.restablecer_contrasena', token=token, _external=True)
                
                try:
                    msg = Message(
                        subject="Restablecimiento de Contraseña - ONCC",
                        recipients=[usuario.correo]
                    )
                    msg.body = f"Hola, {usuario.nombre_usuario}.\n\nPara restablecer tu contraseña del sistema ONCC, haz clic en el siguiente enlace:\n{enlace_recuperacion}\n\nEste enlace expirará en 10 minutos."
                    msg.html = render_template('auth/correo_recuperacion.html', usuario=usuario, enlace=enlace_recuperacion)
                    mail.send(msg)
                except Exception as e:
                    print(f"❌ Error al enviar el correo SMTP: {str(e)}")
                    flash('Ocurrió un inconveniente al procesar el envío del correo de recuperación.', 'error')
                    return render_template('auth/recuperar.html', form=form)

        flash('Si el correo institucional se encuentra registrado, recibirá un enlace de recuperación en breve.', 'info')
        return redirect(url_for('core.login'))

    return render_template('auth/recuperar.html', form=form)


@core_bp.route('/auth/restablecer/<token>', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        pwd = form.password.data or ''
        if gestor.confirmar_restauracion(token, pwd):
            flash('Contraseña restablecida correctamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('core.login'))
        flash('El enlace es inválido o ha expirado.', 'error')
    return render_template('auth/reset_password.html', form=form)