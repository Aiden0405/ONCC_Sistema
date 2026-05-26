from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from urllib.parse import urljoin, urlparse

from app.blueprints.core import core_bp
from app.blueprints.core.forms import LoginForm, ResetRequestForm, ResetPasswordForm
from app.models.usuario import Usuario
from app.services.gestor_sesion import GestorSesion

gestor = GestorSesion()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@core_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        correo = (form.correo.data or '').strip().lower()
        password = (form.password.data or '').strip()

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
            # Use gestor to create session via Flask-Login
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
        token = gestor.solicitar_recuperacion(correo)
        if token:
            # En entorno real se enviaría por correo; aquí mostramos mensaje informativo
            flash(f'Se ha generado un token de recuperación (temporal): {token}', 'info')
        else:
            flash('Si el correo existe, se ha enviado un enlace de recuperación.', 'info')
        return redirect(url_for('core.login'))

    return render_template('auth/recuperar.html', form=form)


@core_bp.route('/auth/restablecer/<token>', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        pwd = form.password.data or ''
        if gestor.confirmar_restauracion(token, pwd):
            flash('Contraseña restablecida. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('core.login'))
        flash('Token inválido o expirado.', 'error')
    return render_template('auth/reset_password.html', form=form)