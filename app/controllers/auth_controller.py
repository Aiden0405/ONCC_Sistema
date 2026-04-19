from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.usuario import Usuario
from app import db

# Creamos un "Blueprint" llamado 'auth'. Esto agrupa todas las rutas que tengan que ver con login.
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya tiene la sesión iniciada, lo mandamos directo al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        # Obtenemos los datos que el usuario escribió en el HTML
        email = (request.form.get('email') or '').strip().lower()
        password = (request.form.get('password') or '').strip()

        if not email or not password:
            flash('Debe ingresar correo y contraseña.', 'error')
            return render_template('auth/login.html')
        
        # Buscamos al usuario en la base de datos por su correo
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario:
            flash('El correo no está registrado en el sistema.', 'error')
            return render_template('auth/login.html')

        if not usuario.estatus:
            flash('El usuario está inactivo. Contacte al administrador.', 'error')
            return render_template('auth/login.html')

        # Validamos la contraseña
        if usuario.check_password(password):
            login_user(usuario)
            return redirect(url_for('dashboard'))

        flash('La contraseña es incorrecta. Intente nuevamente.', 'error')
            
    # Si la petición es GET (solo entró a la página), le mostramos el HTML
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required # Obliga a que estés logueado para poder cerrar sesión
def logout():
    logout_user()
    return redirect(url_for('auth.login'))