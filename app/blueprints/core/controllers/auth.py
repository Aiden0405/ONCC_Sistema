import random  # Generar los números aleatorios del captcha
from flask import flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_required, login_user, logout_user
from urllib.parse import urljoin, urlparse

# 🌟 IMPORTANTE: Importamos la herramienta 'mail' de tu app y la clase 'Message' para estructurar el correo
from flask_mail import Message
from app import mail

from app.blueprints.core import core_bp
from app.blueprints.core.forms import LoginForm, ResetRequestForm, ResetPasswordForm
from app.models.usuario import Usuario
from app.services.gestor_sesion import GestorSesion

gestor = GestorSesion()


def _generar_captcha():
    num1 = random.randint(1, 9)
    num2 = random.randint(1, 9)
    session['captcha_resultado'] = num1 + num2
    session['captcha_texto'] = f"¿Cuánto es {num1} + {num2}?"


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@core_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    # 🌟 Ya no limpiamos variables de simulación porque la bandeja local fue removida por seguridad
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

    if request.method == 'GET' or 'captcha_resultado' not in session:
        _generar_captcha()

    if form.validate_on_submit():
        correo = (form.correo.data or '').strip().lower()
        captcha_usuario = request.form.get('captcha', '').strip()

        try:
            captcha_valido = int(captcha_usuario) == int(session.get('captcha_resultado'))
        except (TypeError, ValueError):
            captcha_valido = False

        # Validación del Captcha Matemático antes de procesar el token
        if not captcha_valido:
            flash('La verificación de seguridad (Captcha) es incorrecta.', 'error')
            _generar_captcha()
            return render_template('auth/recuperar.html', form=form)

        # Buscamos si el usuario existe en la BD
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        # 🌟 Si el usuario existe, generamos el token y mandamos el correo real
        if usuario:
            token = gestor.solicitar_recuperacion(correo)
            if token:
                enlace_recuperacion = url_for('core.restablecer_contrasena', token=token, _external=True)
                
                try:
                    # Estructuramos el mensaje de correo
                    msg = Message(
                        subject="Restablecimiento de Contraseña - ONCC",
                        recipients=[usuario.correo]
                    )
                    # Texto alternativo por si el cliente de correo no lee HTML
                    msg.body = f"Hola, {usuario.nombre_usuario}.\n\nPara restablecer tu contraseña del sistema ONCC, haz clic en el siguiente enlace:\n{enlace_recuperacion}\n\nEste enlace expirará en 10 minutos."
                    
                    # Plantilla de correo HTML estructurada y bonita (la que creas en el paso siguiente)
                    msg.html = render_template('auth/correo_recuperacion.html', usuario=usuario, enlace=enlace_recuperacion)
                    
                    # 🌟 Flask-Mail envía el correo a la bandeja de destino real de manera segura y privada
                    mail.send(msg)
                    
                except Exception as e:
                    print(f"❌ Error al enviar el correo SMTP: {str(e)}")
                    flash('Ocurrió un inconveniente al procesar el envío del correo de recuperación.', 'error')
                    return render_template('auth/recuperar.html', form=form)

        # Mensaje seguro único (se muestra siempre para evitar revelación de cuentas existentes)
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