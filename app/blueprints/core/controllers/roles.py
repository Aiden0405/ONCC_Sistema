from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Permission, Role
from app.services.auditoria import registrar_accion
from app.utils.authorization import role_required


@core_bp.route('/admin/roles/')
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def rol_index():
    roles = Role.query.order_by(Role.nombre).all()
    return render_template('roles/index.html', roles=roles)


@core_bp.route('/admin/roles/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def rol_nuevo():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        if not nombre:
            flash('Nombre obligatorio.', 'error')
            return render_template('roles/formulario.html')

        if Role.query.filter_by(nombre=nombre).first():
            flash('Rol ya existe.', 'error')
            return render_template('roles/formulario.html')

        rol = Role(nombre=nombre, descripcion=descripcion)
        db.session.add(rol)
        db.session.commit()
        registrar_accion('Roles', rol.id, 'Crear', current_user.nombre, detalle=f'Creado rol {rol.nombre}')
        flash('Rol creado.', 'success')
        return redirect(url_for('rol.index'))

    return render_template('roles/formulario.html')


@core_bp.route('/admin/roles/<int:rol_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def rol_editar(rol_id):
    rol = Role.query.get_or_404(rol_id)
    if request.method == 'POST':
        rol.nombre = (request.form.get('nombre') or rol.nombre).strip()
        rol.descripcion = (request.form.get('descripcion') or rol.descripcion).strip()
        db.session.commit()
        registrar_accion('Roles', rol.id, 'Modificar', current_user.nombre, detalle=f'Actualizado rol {rol.nombre}')
        flash('Rol actualizado.', 'success')
        return redirect(url_for('rol.index'))

    return render_template('roles/formulario.html', rol=rol)


@core_bp.route('/admin/roles/<int:rol_id>/eliminar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def rol_eliminar(rol_id):
    rol = Role.query.get_or_404(rol_id)
    db.session.delete(rol)
    db.session.commit()
    registrar_accion('Roles', rol_id, 'Eliminar', current_user.nombre, detalle=f'Eliminado rol {rol.nombre}')
    flash('Rol eliminado.', 'success')
    return redirect(url_for('rol.index'))


@core_bp.route('/admin/roles/permisos')
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def rol_permisos_index():
    permisos = Permission.query.order_by(Permission.nombre).all()
    return render_template('roles/permissions_index.html', permisos=permisos)


@core_bp.route('/admin/roles/permisos/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def rol_permiso_nuevo():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        if not nombre:
            flash('Nombre obligatorio.', 'error')
            return render_template('roles/permission_form.html')

        if Permission.query.filter_by(nombre=nombre).first():
            flash('Permiso ya existe.', 'error')
            return render_template('roles/permission_form.html')

        permiso = Permission(nombre=nombre, descripcion=descripcion)
        db.session.add(permiso)
        db.session.commit()
        registrar_accion('Permisos', permiso.id, 'Crear', current_user.nombre, detalle=f'Creado permiso {permiso.nombre}')
        flash('Permiso creado.', 'success')
        return redirect(url_for('rol.permisos_index'))

    return render_template('roles/permission_form.html')


@core_bp.route('/admin/roles/<int:rol_id>/permisos', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def rol_gestionar_permisos(rol_id):
    rol = Role.query.get_or_404(rol_id)
    permisos = Permission.query.order_by(Permission.nombre).all()
    if request.method == 'POST':
        seleccion = request.form.getlist('permisos')
        rol.permissions = [Permission.query.get(int(pid)) for pid in seleccion if pid.isdigit()]
        db.session.commit()
        registrar_accion('Roles', rol.id, 'ActualizarPermisos', current_user.nombre, detalle=f'Permisos actualizados: {seleccion}')
        flash('Permisos actualizados.', 'success')
        return redirect(url_for('rol.index'))

    return render_template('roles/permisos.html', rol=rol, permisos=permisos)