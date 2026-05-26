from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Role
from app.models.usuario import Usuario
from app.services.auditoria import registrar_accion
from app.utils.authorization import role_required


@core_bp.route('/admin/usuarios/')
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_index():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return render_template('usuarios/index.html', usuarios=usuarios)


@core_bp.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_nuevo():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        correo = (request.form.get('correo') or '').strip().lower()
        rol = (request.form.get('rol') or 'Técnico').strip()
        password = (request.form.get('password') or '').strip()

        if not nombre or not correo or not password:
            flash('Nombre, correo y contraseña son obligatorios.', 'error')
            return render_template('usuarios/formulario.html')
        if Usuario.query.filter_by(correo=correo).first():
            flash('Ya existe un usuario con ese correo.', 'error')
            return render_template('usuarios/formulario.html')
        nuevo_usuario = Usuario(nombre=nombre, correo=correo, rol=rol, estatus=True)
        nuevo_usuario.set_password(password)

        role_obj = Role.query.filter_by(nombre=rol).first()
        if role_obj:
            nuevo_usuario.roles = [role_obj]

        db.session.add(nuevo_usuario)
        db.session.commit()

        registrar_accion('Usuarios', nuevo_usuario.id, 'Crear', current_user.nombre, detalle=f'Creado usuario {correo}', estado_nuevo=nuevo_usuario.rol)

        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.nombre).all()
    return render_template('usuarios/formulario.html', roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        rol = (request.form.get('rol') or usuario.rol).strip()
        estatus = bool(request.form.get('estatus'))

        usuario.nombre = nombre or usuario.nombre
        usuario.rol = rol
        usuario.estatus = estatus

        nueva_pass = (request.form.get('password') or '').strip()
        if nueva_pass:
            usuario.set_password(nueva_pass)

        role_obj = Role.query.filter_by(nombre=rol).first()
        if role_obj:
            usuario.roles = [role_obj]

        db.session.commit()
        registrar_accion('Usuarios', usuario.id, 'Modificar', current_user.nombre, detalle=f'Editado usuario {usuario.correo}', estado_nuevo=usuario.rol)

        flash('Usuario actualizado.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.nombre).all()
    return render_template('usuarios/formulario.html', usuario=usuario, roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_eliminar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.id == current_user.id:
        flash('No puede eliminar su propio usuario mientras esté autenticado.', 'error')
        return redirect(url_for('usuario.index'))

    db.session.delete(usuario)
    db.session.commit()
    registrar_accion('Usuarios', usuario_id, 'Eliminar', current_user.nombre, detalle=f'Eliminado usuario {usuario.correo}')

    flash('Usuario eliminado.', 'success')
    return redirect(url_for('usuario.index'))


@core_bp.route('/admin/usuarios/perfil', methods=['GET', 'POST'])
@login_required
def usuario_perfil():
    usuario = Usuario.query.get_or_404(current_user.id)
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or usuario.nombre).strip()
        usuario.nombre = nombre

        nueva_pass = (request.form.get('password') or '').strip()
        if nueva_pass:
            usuario.set_password(nueva_pass)

        db.session.commit()
        registrar_accion('Usuarios', usuario.id, 'ModificarPerfil', usuario.nombre, detalle='Actualizó perfil propio')
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('dashboard'))

    roles = Role.query.order_by(Role.nombre).all()
    return render_template('usuarios/formulario.html', usuario=usuario, es_perfil=True, roles=roles)