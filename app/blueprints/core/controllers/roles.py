from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Permission, Role, Permiso
from app.services.auditoria import registrar_accion
from app.services.notificacion import ServicioNotificacion
from app.constants import KNOWN_PERMISSION_SLUGS
from app.utils.authorization import current_role_id, is_superuser, verificar_permiso_dinamico


# =============================================================================
#  RUTAS DE ROLES
# =============================================================================

@core_bp.route('/admin/roles/')
@login_required
def rol_index():
    verificar_permiso_dinamico('ver_roles')
    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('roles/index.html', roles=roles)


@core_bp.route('/admin/roles/nuevo', methods=['GET', 'POST'])
@login_required
def rol_nuevo():
    verificar_permiso_dinamico('registrar_roles')
    
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
            mensaje = f"Se creó el rol institucional '{rol.nombre_rol}'."
            ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

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
    verificar_permiso_dinamico('editar_roles')
    
    if int(rol_id) == 1 and current_role_id() != 1:
        flash('No tiene jerarquía institucional para modificar el rol de Superusuario.', 'error')
        abort(403)
        
    rol = Role.query.get_or_404(rol_id)
    if request.method == 'POST':
        nombre_anterior = rol.nombre_rol
        rol.nombre_rol = (request.form.get('nombre') or rol.nombre_rol).strip()
        
        try:
            db.session.commit()
            mensaje = f"El rol '{nombre_anterior}' fue renombrado a '{rol.nombre_rol}'."
            ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

            registrar_accion('Roles', rol.id_rol, 'Modificar', current_user.nombre_usuario, detalle=f'Actualizado rol {rol.nombre_rol}')
            flash('Rol actualizado con éxito.', 'success')
            return redirect(url_for('usuario.index'))
        except Exception:
            db.session.rollback()
            flash('Error al actualizar el rol.', 'error')
            return render_template('roles/formulario.html', rol=rol)

    return render_template('roles/formulario.html', rol=rol)


@core_bp.route('/admin/roles/<int:rol_id>/eliminar', methods=['POST'])
@login_required
def rol_eliminar(rol_id):
    verificar_permiso_dinamico('eliminar_roles')
    
    if int(rol_id) == 1 and current_role_id() != 1:
        flash('Acceso denegado: El rol de Superusuario está blindado por el sistema.', 'error')
        abort(403)
        
    rol = Role.query.get_or_404(rol_id)
    rol_id_temp = rol.id_rol
    rol_nombre_temp = rol.nombre_rol
    
    try:
        db.session.delete(rol)
        db.session.commit()
        mensaje = f"El rol '{rol_nombre_temp}' fue eliminado del esquema de seguridad."
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

        registrar_accion('Roles', rol_id_temp, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado rol {rol_nombre_temp}')
        flash('Rol eliminado con éxito.', 'success')
        return redirect(url_for('usuario.index'))
    except Exception:
        db.session.rollback()
        flash('No se puede eliminar el rol debido a restricciones de integridad en la base de datos.', 'error')
        return redirect(url_for('core.rol_index'))


@core_bp.route('/admin/roles/<int:rol_id>/permisos', methods=['GET', 'POST'])
@login_required
def rol_gestionar_permisos(rol_id):
    verificar_permiso_dinamico('asignar_permisos_roles')
    
    if int(rol_id) == 1 and current_role_id() != 1:
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
            mensaje = f"Se actualizaron los permisos del rol '{rol.nombre_rol}'."
            ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

            registrar_accion('Roles', rol.id_rol, 'ActualizarPermisos', current_user.nombre_usuario, detalle=f'Permisos actualizados para {rol.nombre_rol}: {seleccion}')
            flash('Matriz de accesos actualizada con éxito.', 'success')
            
            # 🌟 CORRECCIÓN AQUÍ: Te mantiene en la lista de roles en lugar de mandarte a usuarios
            return redirect(url_for('core.rol_index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error crítico al guardar la matriz de accesos.', 'error')
            
            # 🌟 CORRECCIÓN AQUÍ: En caso de error también te regresa de forma segura a roles
            return redirect(url_for('core.rol_index'))

    return render_template('roles/permisos.html', rol=rol, permisos=permisos)


# =============================================================================
#  RUTAS DEL CATÁLOGO DE PERMISOS ATÓMICOS (CRUD COMPLETO CON VALIDACIÓN REAL)
# =============================================================================

@core_bp.route('/admin/permisos/')
@login_required
def permiso_index():
    verificar_permiso_dinamico('ver_permisos')
    
    # Obtenemos la página actual desde la URL (por defecto la 1)
    page = request.args.get('page', 1, type=int)
    
    # Paginamos de 10 en 10 registros
    pagination = Permission.query.order_by(Permission.id_modulo).paginate(page=page, per_page=10)
    
    return render_template('roles/permisos_index.html', pagination=pagination, permisos=pagination.items)


@core_bp.route('/admin/permisos/nuevo', methods=['GET', 'POST'])
@login_required
def permiso_nuevo():
    verificar_permiso_dinamico('registrar_permisos')
    
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip().lower().replace(' ', '_')
        descripcion = (request.form.get('descripcion') or '').strip()
        
        if not nombre:
            flash('El nombre técnico del permiso es obligatorio.', 'error')
            return redirect(url_for('core.permiso_index'))

        if nombre not in KNOWN_PERMISSION_SLUGS:
            flash(
                f'No se puede crear el permiso técnico "{nombre}": '
                'no existe en el catálogo de capacidades permitidas del sistema.',
                'error'
            )
            return redirect(url_for('core.permiso_index'))

        if Permission.query.filter_by(nombre_modulo=nombre).first():
            flash(f'El privilegio técnico "{nombre}" ya existe en el sistema.', 'error')
            return redirect(url_for('core.permiso_index'))

        ultimo_permiso = Permission.query.order_by(Permission.id_modulo.desc()).first()
        siguiente_id = (ultimo_permiso.id_modulo + 1) if ultimo_permiso else 1

        try:
            nuevo_p = Permission(id_modulo=siguiente_id, nombre=nombre, descripcion=descripcion)
            
            db.session.add(nuevo_p)
            db.session.commit()
            mensaje = f"Se registró el permiso '{nuevo_p.nombre_modulo}'."
            ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

            registrar_accion('Permisos', nuevo_p.id_modulo, 'Crear', current_user.nombre_usuario, detalle=f'Creado el privilegio atómico: {nuevo_p.nombre_modulo}')
            flash(f'Permiso técnico "{nombre}" registrado correctamente.', 'success')
            return redirect(url_for('core.permiso_index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error de consistencia en BD: {str(e)}', 'error')
            return redirect(url_for('core.permiso_index'))
        
    return render_template('roles/permiso_formulario.html', permiso=None)


@core_bp.route('/admin/permisos/<int:permiso_id>/editar', methods=['GET', 'POST'])
@login_required
def permiso_editar(permiso_id):
    verificar_permiso_dinamico('editar_permisos')
    
    permiso = Permission.query.get_or_404(permiso_id)
    
    if request.method == 'POST':
        nombre_form = (request.form.get('nombre') or '').strip().lower().replace(' ', '_')
        descripcion_form = (request.form.get('descripcion') or '').strip()
        
        if not nombre_form:
            flash('El nombre técnico es obligatorio.', 'error')
            return render_template('roles/permiso_formulario.html', permiso=permiso)

        if nombre_form not in KNOWN_PERMISSION_SLUGS:
            flash(
                f'No se puede guardar el permiso técnico "{nombre_form}": '
                'no existe en el catálogo de capacidades permitidas del sistema.',
                'error'
            )
            return render_template('roles/permiso_formulario.html', permiso=permiso)
            
        if nombre_form != permiso.nombre_modulo:
            if Permission.query.filter_by(nombre_modulo=nombre_form).first():
                flash(f'El privilegio técnico "{nombre_form}" ya existe.', 'error')
                return render_template('roles/permiso_formulario.html', permiso=permiso)
        
        permiso.nombre = nombre_form
        permiso.descripcion = descripcion_form
        
        try:
            db.session.commit()
            mensaje = f"Se actualizó el permiso '{permiso.nombre_modulo}'."
            ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

            registrar_accion('Permisos', permiso.id_modulo, 'Modificar', current_user.nombre_usuario, detalle=f'Actualizado el privilegio técnico a: {permiso.nombre_modulo}')
            flash('Privilegio actualizado con éxito en el catálogo.', 'success')
            return redirect(url_for('core.permiso_index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el permiso.', 'error')
            return render_template('roles/permiso_formulario.html', permiso=permiso)
            
    return render_template('roles/permiso_formulario.html', permiso=permiso)


@core_bp.route('/admin/permisos/<int:permiso_id>/eliminar', methods=['POST'])
@login_required
def permiso_eliminar(permiso_id):
    verificar_permiso_dinamico('eliminar_permisos')
    
    permiso = Permission.query.get_or_404(permiso_id)
    id_temp = permiso.id_modulo
    nombre_temp = permiso.nombre_modulo
    
    try:
        db.session.delete(permiso)
        db.session.commit()
        mensaje = f"El permiso '{nombre_temp}' fue eliminado del catálogo."
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

        registrar_accion('Permisos', id_temp, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado el privilegio atómico: {nombre_temp}')
        flash('Permiso removido correctamente del catálogo global.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar porque está asignado a roles institucionales activos.', 'error')
        
    return redirect(url_for('core.permiso_index'))