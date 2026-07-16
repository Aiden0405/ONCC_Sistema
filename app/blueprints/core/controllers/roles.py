from flask import flash, redirect, render_template, request, url_for, abort, current_app
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Permission, Role, Permiso
from app.services.auditoria import registrar_accion
from app.utils.authorization import current_role_id, has_permission, is_superuser


def verificar_permiso_dinamico(nombre_permiso):
    """
    Comprueba en la base de datos si el rol del usuario posee el permiso solicitado,
    aplicando un bypass inmediato para los roles jerárquicos del Core (1 y 2).
    """
    if not current_user.is_authenticated:
        abort(403)

    if is_superuser():
        return True

    if not has_permission(nombre_permiso):
        flash('No tiene privilegios institucionales para acceder a este módulo.', 'error')
        abort(403)


# =============================================================================
#  RUTAS DE ROLES
# =============================================================================

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
            
            # 🔔 ALERTA: NUEVO ROL REGISTRADO
            try:
                from app.models.notificacion import Notificacion
                alerta = Notificacion(
                    categoria='Seguridad',
                    mensaje=f"Estructura RBAC: El operador {current_user.nombre_usuario} creó el nuevo rango institucional '{rol.nombre_rol}'.",
                    usuario_id=None,  # 🌟 Forzado para la correcta consulta de PostgreSQL
                    leido=False 
                )
                db.session.add(alerta)
                db.session.commit()
            except Exception:
                db.session.rollback()

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
    
    if int(rol_id) == 1 and current_role_id() != 1:
        flash('No tiene jerarquía institucional para modificar el rol de Superusuario.', 'error')
        abort(403)
        
    rol = Role.query.get_or_404(rol_id)
    if request.method == 'POST':
        nombre_anterior = rol.nombre_rol
        rol.nombre_rol = (request.form.get('nombre') or rol.nombre_rol).strip()
        
        try:
            db.session.commit()
            
            # 🔔 ALERTA: NOMBRE DE ROL MODIFICADO
            try:
                from app.models.notificacion import Notificacion
                alerta = Notificacion(
                    categoria='Seguridad',
                    mensaje=f"Estructura RBAC: Rol institucional '{nombre_anterior}' renombrado a '{rol.nombre_rol}' por {current_user.nombre_usuario}.",
                    usuario_id=None,  # 🌟 Forzado para la correcta consulta de PostgreSQL
                    leido=False 
                )
                db.session.add(alerta)
                db.session.commit()
            except Exception:
                db.session.rollback()

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
    verificar_permiso_dinamico('gestionar_usuarios')
    
    if int(rol_id) == 1 and current_role_id() != 1:
        flash('Acceso denegado: El rol de Superusuario está blindado por el sistema.', 'error')
        abort(403)
        
    rol = Role.query.get_or_404(rol_id)
    rol_id_temp = rol.id_rol
    rol_nombre_temp = rol.nombre_rol
    
    try:
        db.session.delete(rol)
        db.session.commit()
        
        # 🔔 ALERTA: DESTRUCCIÓN DE ROL INSTITUCIONAL
        try:
            from app.models.notificacion import Notificacion
            alerta = Notificacion(
                categoria='Seguridad',
                mensaje=f"⚠️ MODIFICACIÓN CRÍTICA: El rol '{rol_nombre_temp}' fue eliminado del esquema de seguridad por {current_user.nombre_usuario}.",
                usuario_id=None,  # 🌟 Forzado para la correcta consulta de PostgreSQL
                leido=False 
            )
            db.session.add(alerta)
            db.session.commit()
        except Exception:
            db.session.rollback()

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
    verificar_permiso_dinamico('gestionar_usuarios')
    
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
            
            # 🔔 ALERTA: MATRIZ DE ACCESOS O PRIVILEGIOS CAMBIADA
            try:
                from app.models.notificacion import Notificacion
                alerta = Notificacion(
                    categoria='Seguridad',
                    mensaje=f"🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol '{rol.nombre_rol}' fue reconfigurada por {current_user.nombre_usuario}.",
                    usuario_id=None,
                    leido=False 
                )
                db.session.add(alerta)
                db.session.commit()
            except Exception:
                db.session.rollback()

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
    verificar_permiso_dinamico('gestionar_usuarios')
    todos_los_permisos = Permission.query.order_by(Permission.id_modulo).all()
    return render_template('roles/permisos_index.html', permisos=todos_los_permisos)


@core_bp.route('/admin/permisos/nuevo', methods=['GET', 'POST'])
@login_required
def permiso_nuevo():
    verificar_permiso_dinamico('gestionar_usuarios')
    
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip().lower().replace(' ', '_')
        descripcion = (request.form.get('descripcion') or '').strip()
        
        # =====================================================================
        # 🔍 INSPECCIÓN DINÁMICA DE ENDPOINTS (MÁXIMA FLEXIBILIDAD)
        # =====================================================================
        # 1. Recuperamos los nombres de todos los endpoints registrados en Flask en este momento
        endpoints_reales = list(current_app.view_functions.keys())
        
        # 2. Extraemos los nombres de los módulos y blueprints activos (prefijos o nombres clave)
        modulos_activos = set()
        for ep in endpoints_reales:
            if '.' in ep:
                modulos_activos.add(ep.split('.')[0])
            else:
                modulos_activos.add(ep)
        
        # 3. Validamos si el slug ingresado tiene que ver con algún módulo o función real en el código
        es_valido = False
        modulo_detectado = None
        
        # Primero buscamos coincidencia con los nombres de los blueprints/módulos
        for modulo in modulos_activos:
            if modulo in nombre:
                es_valido = True
                modulo_detectado = modulo
                break
                
        # Si no coincidió, buscamos si la palabra clave está dentro de algún endpoint completo (ej: "tecnicos" en "logistica.tecnicos_campo_index")
        if not es_valido:
            for ep in endpoints_reales:
                # Limpiamos el endpoint para buscar palabras clave (ej: "tecnicos_campo_index" -> ["tecnicos", "campo", "index"])
                partes_endpoint = ep.replace('.', '_').split('_')
                for parte in partes_endpoint:
                    if parte in nombre and len(parte) > 3: # Evitamos coincidencias con palabras muy cortas
                        es_valido = True
                        modulo_detectado = ep.split('.')[0] # Asocia el permiso al blueprint padre
                        break
                if es_valido:
                    break
        
        # 🛡️ REDIRECCIÓN DIRECTA AL CATÁLOGO CON EL MENSAJE DE ERROR
        if not es_valido:
            flash(
                f'¡Hey! El permiso técnico "{nombre}" no coincide con ningún módulo real cargado en el servidor. '
                f'Asegúrate de que el módulo exista en el código antes de registrar su permiso en el catálogo.', 
                'error'
            )
            return redirect(url_for('core.permiso_index'))
        # =====================================================================

        if not nombre:
            flash('El nombre técnico del permiso es obligatorio.', 'error')
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
            
            # 🔔 ALERTA: PRIVILEGIO ATÓMICO AGREGADO AL CATÁLOGO
            try:
                from app.models.notificacion import Notificacion
                alerta = Notificacion(
                    categoria='Seguridad',
                    mensaje=f"Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: '{nuevo_p.nombre_modulo}'.",
                    usuario_id=None,
                    leido=False 
                )
                db.session.add(alerta)
                db.session.commit()
            except Exception:
                db.session.rollback()

            registrar_accion('Permisos', nuevo_p.id_modulo, 'Crear', current_user.nombre_usuario, detalle=f'Creado el privilegio atómico: {nuevo_p.nombre_modulo}')
            flash(f'Capacidad atómica registrada con éxito para el módulo "{modulo_detectado}".', 'success')
            return redirect(url_for('core.permiso_index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error de consistencia en BD: {str(e)}', 'error')
            return redirect(url_for('core.permiso_index'))
        
    return render_template('roles/permiso_formulario.html', permiso=None)


@core_bp.route('/admin/permisos/<int:permiso_id>/editar', methods=['GET', 'POST'])
@login_required
def permiso_editar(permiso_id):
    verificar_permiso_dinamico('gestionar_usuarios')
    
    permiso = Permission.query.get_or_404(permiso_id)
    
    if request.method == 'POST':
        nombre_form = (request.form.get('nombre') or '').strip().lower().replace(' ', '_')
        descripcion_form = (request.form.get('descripcion') or '').strip()
        
        if not nombre_form:
            flash('El nombre técnico es obligatorio.', 'error')
            return render_template('roles/permiso_formulario.html', permiso=permiso)
            
        if nombre_form != permiso.nombre_modulo:
            if Permission.query.filter_by(nombre_modulo=nombre_form).first():
                flash(f'El privilegio técnico "{nombre_form}" ya existe.', 'error')
                return render_template('roles/permiso_formulario.html', permiso=permiso)
        
        permiso.nombre = nombre_form
        permiso.descripcion = descripcion_form
        
        try:
            db.session.commit()
            
            # 🔔 ALERTA: PRIVILEGIO EDITADO
            try:
                from app.models.notificacion import Notificacion
                alerta = Notificacion(
                    categoria='Seguridad',
                    mensaje=f"Ecosistema: El privilegio técnico '{permiso.nombre_modulo}' fue actualizado en el catálogo por {current_user.nombre_usuario}.",
                    usuario_id=None,
                    leido=False 
                )
                db.session.add(alerta)
                db.session.commit()
            except Exception:
                db.session.rollback()

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
    verificar_permiso_dinamico('gestionar_usuarios')
    
    permiso = Permission.query.get_or_404(permiso_id)
    id_temp = permiso.id_modulo
    nombre_temp = permiso.nombre_modulo
    
    try:
        db.session.delete(permiso)
        db.session.commit()
        
        # 🔔 ALERTA: PRIVILEGIO ELIMINADO DEL CATÁLOGO
        try:
            from app.models.notificacion import Notificacion
            alerta = Notificacion(
                categoria='Seguridad',
                mensaje=f"⚠️ ATENCIÓN: El privilegio atómico '{nombre_temp}' fue revocado y removido permanentemente del catálogo global.",
                usuario_id=None,
                leido=False 
                )
            db.session.add(alerta)
            db.session.commit()
        except Exception:
            db.session.rollback()

        registrar_accion('Permisos', id_temp, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado el privilegio atómico: {nombre_temp}')
        flash('Permiso removido correctamente del catálogo global.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar porque está asignado a roles institucionales activos.', 'error')
        
    return redirect(url_for('core.permiso_index'))