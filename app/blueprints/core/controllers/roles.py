from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Permission, Role, Permiso
from app.services.auditoria import registrar_accion


def verificar_permiso_dinamico(nombre_permiso):
    """
    Comprueba en la base de datos si el rol del usuario posee el permiso solicitado,
    aplicando un bypass inmediato para los roles jerárquicos del Core (1 y 2).
    """
    if not current_user.is_authenticated:
        abort(403)
        
    # Superusuario (1) y Administrador (2) pasan directo sin validar la tabla pívot
    if int(current_user.id_rol) in (1, 2):
        return True
        
    permisos_del_rol = [p.nombre_modulo for p in current_user.role.permissions]
    
    if nombre_permiso not in permisos_del_rol:
        flash('No tiene privilegios institucionales para acceder a este módulo.', 'error')
        abort(403)


@core_bp.route('/admin/roles/')
@login_required
def rol_index():
    verificar_permiso_dinamico('gestionar_usuarios')
    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('roles/index.html', roles=roles)


@core_bp.route('/admin/roles/nuevo', methods=['GET', 'POST'])
@login_required
def rol_nuevo():
    verificar_permiso_dinamico('gestionar_usuarios')
    
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        
        if not nombre:
            flash('Nombre obligatorio.', 'error')
            return render_template('roles/formulario.html')

        if Role.query.filter_by(nombre_rol=nombre).first():
            flash('Rol ya existe.', 'error')
            return render_template('roles/formulario.html')

        rol = Role(nombre=nombre)
        
        try:
            db.session.add(rol)
            db.session.commit()
            
            registrar_accion('Roles', rol.id_rol, 'Crear', current_user.nombre_usuario, detalle=f'Creado rol {rol.nombre_rol}')
            flash('Rol creado con éxito.', 'success')
            return redirect(url_for('usuario.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error de consistencia en la base de datos.', 'error')
            return render_template('roles/formulario.html')

    return render_template('roles/formulario.html')


@core_bp.route('/admin/roles/<int:rol_id>/editar', methods=['GET', 'POST'])
@login_required
def rol_editar(rol_id):
    verificar_permiso_dinamico('gestionar_usuarios')
    
    if int(rol_id) == 1 and int(current_user.id_rol) != 1:
        flash('No tiene jerarquía institucional para modificar el rol de Superusuario.', 'error')
        abort(403)
        
    rol = Role.query.get_or_404(rol_id)
    if request.method == 'POST':
        rol.nombre_rol = (request.form.get('nombre') or rol.nombre_rol).strip()
        db.session.commit()
        
        registrar_accion('Roles', rol.id_rol, 'Modificar', current_user.nombre_usuario, detalle=f'Actualizado rol {rol.nombre_rol}')
        flash('Rol actualizado con éxito.', 'success')
        return redirect(url_for('usuario.index'))

    return render_template('roles/formulario.html', rol=rol)


@core_bp.route('/admin/roles/<int:rol_id>/eliminar', methods=['POST'])
@login_required
def rol_eliminar(rol_id):
    verificar_permiso_dinamico('gestionar_usuarios')
    
    if int(rol_id) == 1 and int(current_user.id_rol) != 1:
        flash('Acceso denegado: El rol de Superusuario está blindado por el sistema.', 'error')
        abort(403)
        
    rol = Role.query.get_or_404(rol_id)
    rol_id_temp = rol.id_rol
    rol_nombre_temp = rol.nombre_rol
    
    db.session.delete(rol)
    db.session.commit()
    
    registrar_accion('Roles', rol_id_temp, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado rol {rol_nombre_temp}')
    flash('Rol eliminado con éxito.', 'success')
    return redirect(url_for('usuario.index'))


@core_bp.route('/admin/roles/<int:rol_id>/permisos', methods=['GET', 'POST'])
@login_required
def rol_gestionar_permisos(rol_id):
    verificar_permiso_dinamico('gestionar_usuarios')
    
    if int(rol_id) == 1 and int(current_user.id_rol) != 1:
        flash('No tiene jerarquía para alterar la matriz de accesos del Superusuario.', 'error')
        abort(403)
        
    rol = Role.query.get_or_404(rol_id)
    permisos = Permission.query.order_by(Permission.nombre_modulo).all()
    
    if request.method == 'POST':
        seleccion = request.form.getlist('permisos')
        
        try:
            Permiso.query.filter_by(id_rol=rol.id_rol).delete()
            
            for pid in seleccion:
                if pid.isdigit():
                    nueva_relacion = Permiso(id_rol=rol.id_rol, id_modulo=int(pid))
                    db.session.add(nueva_relacion)
            
            db.session.commit()
            
            registrar_accion('Roles', rol.id_rol, 'ActualizarPermisos', current_user.nombre_usuario, detalle=f'Permisos actualizados para {rol.nombre_rol}: {seleccion}')
            flash('Matriz de accesos actualizada con éxito.', 'success')
            return redirect(url_for('usuario.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error crítico al guardar la matriz de accesos.', 'error')
            return redirect(url_for('usuario.index'))

    return render_template('roles/permisos.html', rol=rol, permisos=permisos)