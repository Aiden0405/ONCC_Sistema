from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.role import Role, Permission
from app.utils.authorization import role_required
from app.services.auditoria import registrar_accion
from app.utils.authorization import permission_required

rol_bp = Blueprint('rol', __name__, url_prefix='/admin/roles')


@rol_bp.route('/')
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def index():
    roles = Role.query.order_by(Role.nombre).all()
    return render_template('roles/index.html', roles=roles)


@rol_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def nuevo():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        if not nombre:
            flash('Nombre obligatorio.', 'error')
            return render_template('roles/formulario.html')

        if Role.query.filter_by(nombre=nombre).first():
            flash('Rol ya existe.', 'error')
            return render_template('roles/formulario.html')

        r = Role(nombre=nombre, descripcion=descripcion)
        db.session.add(r)
        db.session.commit()
        registrar_accion('Roles', r.id, 'Crear', current_user.nombre, detalle=f'Creado rol {r.nombre}')
        flash('Rol creado.', 'success')
        return redirect(url_for('rol.index'))

    return render_template('roles/formulario.html')


@rol_bp.route('/<int:rol_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def editar(rol_id):
    rol = Role.query.get_or_404(rol_id)
    if request.method == 'POST':
        rol.nombre = (request.form.get('nombre') or rol.nombre).strip()
        rol.descripcion = (request.form.get('descripcion') or rol.descripcion).strip()
        db.session.commit()
        registrar_accion('Roles', rol.id, 'Modificar', current_user.nombre, detalle=f'Actualizado rol {rol.nombre}')
        flash('Rol actualizado.', 'success')
        return redirect(url_for('rol.index'))

    return render_template('roles/formulario.html', rol=rol)


@rol_bp.route('/<int:rol_id>/eliminar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def eliminar(rol_id):
    rol = Role.query.get_or_404(rol_id)
    db.session.delete(rol)
    db.session.commit()
    registrar_accion('Roles', rol_id, 'Eliminar', current_user.nombre, detalle=f'Eliminado rol {rol.nombre}')
    flash('Rol eliminado.', 'success')
    return redirect(url_for('rol.index'))


@rol_bp.route('/permisos')
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def permisos_index():
    permisos = Permission.query.order_by(Permission.nombre).all()
    return render_template('roles/permissions_index.html', permisos=permisos)


@rol_bp.route('/permisos/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def permiso_nuevo():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        if not nombre:
            flash('Nombre obligatorio.', 'error')
            return render_template('roles/permission_form.html')

        if Permission.query.filter_by(nombre=nombre).first():
            flash('Permiso ya existe.', 'error')
            return render_template('roles/permission_form.html')

        p = Permission(nombre=nombre, descripcion=descripcion)
        db.session.add(p)
        db.session.commit()
        registrar_accion('Permisos', p.id, 'Crear', current_user.nombre, detalle=f'Creado permiso {p.nombre}')
        flash('Permiso creado.', 'success')
        return redirect(url_for('rol.permisos_index'))

    return render_template('roles/permission_form.html')


@rol_bp.route('/<int:rol_id>/permisos', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director')
def gestionar_permisos(rol_id):
    rol = Role.query.get_or_404(rol_id)
    permisos = Permission.query.order_by(Permission.nombre).all()
    if request.method == 'POST':
        seleccion = request.form.getlist('permisos')
        # Asignar los permisos seleccionados
        rol.permissions = [Permission.query.get(int(pid)) for pid in seleccion if pid.isdigit()]
        db.session.commit()
        registrar_accion('Roles', rol.id, 'ActualizarPermisos', current_user.nombre, detalle=f'Permisos actualizados: {seleccion}')
        flash('Permisos actualizados.', 'success')
        return redirect(url_for('rol.index'))

    return render_template('roles/permisos.html', rol=rol, permisos=permisos)
