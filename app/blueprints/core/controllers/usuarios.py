from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
# Importación correcta al archivo físico role.py
from app.models.role import Role
from app.models.usuario import Usuario
from app.services.auditoria import registrar_accion
from app.utils.authorization import role_required


@core_bp.route('/admin/usuarios/')
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_index():
    usuarios = Usuario.query.order_by(Usuario.nombre_usuario).all()
    return render_template('usuarios/index.html', usuarios=usuarios)


@core_bp.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_nuevo():
    if request.method == 'POST':
        # Adaptado a los name del HTML de Tailwind (nombre_usuario, correo, id_rol, password)
        nombre = (request.form.get('nombre_usuario') or '').strip()
        correo = (request.form.get('correo') or '').strip().lower()
        id_rol_form = request.form.get('id_rol')
        password = (request.form.get('password') or '').strip()

        if not nombre or not correo or not password or not id_rol_form:
            flash('Nombre, correo, rol y contraseña son obligatorios.', 'error')
            roles = Role.query.order_by(Role.nombre_rol).all()
            return render_template('usuarios/formulario.html', roles=roles)
            
        existe = Usuario.query.filter_by(correo=correo).first()
        if existe:
            flash('Ya existe un usuario con ese correo.', 'error')
            roles = Role.query.order_by(Role.nombre_rol).all()
            return render_template('usuarios/formulario.html', roles=roles)

        # Guardamos usando el ID de rol numérico que envía el select del HTML
        nuevo_usuario = Usuario(
            nombre_usuario=nombre,
            correo=correo,
            id_rol=int(id_rol_form)
        )
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        registrar_accion('Usuarios', nuevo_usuario.id_usuario, 'Crear', current_user.nombre_usuario, detalle=f'Creado usuario {correo}', estado_nuevo=nuevo_usuario.rol)

        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('core.usuario_index'))

    roles = Role.query.order_by(Role.nombre_rol).all()
    return render_template('usuarios/formulario.html', roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == 'POST':
        nombre = (request.form.get('nombre_usuario') or '').strip()
        id_rol_form = request.form.get('id_rol')

        usuario.nombre_usuario = nombre or usuario.nombre_usuario

        if id_rol_form:
            usuario.id_rol = int(id_rol_form)

        nueva_pass = (request.form.get('password') or '').strip()
        if nueva_pass:
            usuario.set_password(nueva_pass)

        db.session.commit()
        
        user_correo = getattr(usuario, 'correo', usuario.nombre_usuario)
        registrar_accion('Usuarios', usuario.id_usuario, 'Modificar', current_user.nombre_usuario, detalle=f'Editado usuario {user_correo}', estado_nuevo=usuario.rol)

        flash('Usuario actualizado.', 'success')
        return redirect(url_for('core.usuario_index'))

    roles = Role.query.order_by(Role.nombre_rol).all()
    return render_template('usuarios/formulario.html', usuario=usuario, roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_eliminar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puede eliminar su propio usuario mientras esté autenticado.', 'error')
        return redirect(url_for('core.usuario_index'))

    db.session.delete(usuario)
    db.session.commit()
    
    user_correo = getattr(usuario, 'correo', usuario.nombre_usuario)
    registrar_accion('Usuarios', usuario_id, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado usuario {user_correo}')

    flash('Usuario eliminado.', 'success')
    return redirect(url_for('core.usuario_index'))


@core_bp.route('/admin/usuarios/perfil', methods=['GET', 'POST'])
@login_required
def usuario_perfil():
    usuario = Usuario.query.get_or_404(current_user.id_usuario)
    if request.method == 'POST':
        nombre = (request.form.get('nombre_usuario') or usuario.nombre_usuario).strip()
        usuario.nombre_usuario = nombre

        nueva_pass = (request.form.get('password') or '').strip()
        if nueva_pass:
            usuario.set_password(nueva_pass)

        db.session.commit()
        registrar_accion('Usuarios', usuario.id_usuario, 'ModificarPerfil', usuario.nombre_usuario, detalle='Actualizó perfil propio')
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('core.usuario_index'))

    roles = Role.query.order_by(Role.nombre_rol).all()
    return render_template('usuarios/formulario.html', usuario=usuario, es_perfil=True, roles=roles)