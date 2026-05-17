from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.utils.authorization import role_required
from app import db
from app.models.usuario import Usuario
from app.models.role import Role
from app.services.auditoria import registrar_accion

usuario_bp = Blueprint('usuario', __name__, url_prefix='/admin/usuarios')


# Use registrar_accion from services/auditoria.py


@usuario_bp.route('/')
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def index():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return render_template('usuarios/index.html', usuarios=usuarios)


@usuario_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def nuevo():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        rol = (request.form.get('rol') or 'Técnico').strip()
        password = (request.form.get('password') or '').strip()

        if not nombre or not email or not password:
            flash('Nombre, correo y contraseña son obligatorios.', 'error')
            return render_template('usuarios/formulario.html')

        if Usuario.query.filter_by(email=email).first():
            flash('Ya existe un usuario con ese correo.', 'error')
            return render_template('usuarios/formulario.html')

        nuevo = Usuario(nombre=nombre, email=email, rol=rol, estatus=True)
        nuevo.set_password(password)

        # Asociar rol relacional si existe
        role_obj = Role.query.filter_by(nombre=rol).first()
        if role_obj:
            nuevo.roles = [role_obj]

        db.session.add(nuevo)
        db.session.commit()

        registrar_accion('Usuarios', nuevo.id, 'Crear', current_user.nombre, detalle=f'Creado usuario {email}', estado_nuevo=nuevo.rol)

        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.nombre).all()
    return render_template('usuarios/formulario.html', roles=roles)


@usuario_bp.route('/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        rol = (request.form.get('rol') or usuario.rol).strip()
        estatus = bool(request.form.get('estatus'))

        usuario.nombre = nombre or usuario.nombre
        usuario.rol = rol
        usuario.estatus = estatus

        # Cambiar contraseña opcionalmente
        nueva_pass = (request.form.get('password') or '').strip()
        if nueva_pass:
            usuario.set_password(nueva_pass)

        # Actualizar relación de roles
        role_obj = Role.query.filter_by(nombre=rol).first()
        if role_obj:
            usuario.roles = [role_obj]

        db.session.commit()
        registrar_accion('Usuarios', usuario.id, 'Modificar', current_user.nombre, detalle=f'Editado usuario {usuario.email}', estado_nuevo=usuario.rol)

        flash('Usuario actualizado.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.nombre).all()
    return render_template('usuarios/formulario.html', usuario=usuario, roles=roles)


@usuario_bp.route('/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def eliminar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.id == current_user.id:
        flash('No puede eliminar su propio usuario mientras esté autenticado.', 'error')
        return redirect(url_for('usuario.index'))

    db.session.delete(usuario)
    db.session.commit()
    registrar_accion('Usuarios', usuario_id, 'Eliminar', current_user.nombre, detalle=f'Eliminado usuario {usuario.email}')

    flash('Usuario eliminado.', 'success')
    return redirect(url_for('usuario.index'))


@usuario_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    usuario = Usuario.query.get_or_404(current_user.id)
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or usuario.nombre).strip()
        usuario.nombre = nombre

        nueva_pass = (request.form.get('password') or '').strip()
        if nueva_pass:
            usuario.set_password(nueva_pass)

        db.session.commit()
        registrar_bitacora('Usuarios', usuario.id, 'ModificarPerfil', usuario.nombre, detalle='Actualizó perfil propio')
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('dashboard'))

    roles = Role.query.order_by(Role.nombre).all()
    return render_template('usuarios/formulario.html', usuario=usuario, es_perfil=True, roles=roles)
