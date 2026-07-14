from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Role
from app.models.usuario import Usuario
from app.services.auditoria import registrar_accion
from app.utils.authorization import current_role_id, has_permission, is_superuser


def verificar_permiso_dinamico(nombre_permiso):
    """
    Comprueba dinámicamente si el rol del usuario logueado tiene asignado el permiso 
    solicitado, aplicando un bypass inmediato para los roles jerárquicos del Core (1 y 2).
    """
    if not current_user.is_authenticated:
        abort(403)

    if is_superuser():
        return True

    if not has_permission(nombre_permiso):
        flash('No tiene privilegios institucionales para acceder a este módulo.', 'error')
        abort(403)


@core_bp.route('/admin/usuarios/')
@login_required
def usuario_index():
    verificar_permiso_dinamico('gestionar_usuarios')
    usuarios = Usuario.query.order_by(Usuario.nombre_usuario).all()
    return render_template('usuarios/index.html', whitespaces=True, usuarios=usuarios)


@core_bp.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
def usuario_nuevo():
    verificar_permiso_dinamico('gestionar_usuarios')
    
    if request.method == 'POST':
        nombre = (request.form.get('nombre_usuario') or '').strip()
        correo = (request.form.get('correo') or '').strip().lower()
        id_rol_form = request.form.get('id_rol')
        password = (request.form.get('password') or '').strip()
        estatus_form = request.form.get('estatus')

        if not nombre or not correo or not password or not id_rol_form:
            flash('Nombre, correo, rol y contraseña son obligatorios.', 'error')
            roles = Role.query.order_by(Role.id_rol).all()
            return render_template('usuarios/formulario.html', roles=roles)
            
        # 🛡️ CONTROL DE JERARQUÍA ABSOLUTO EN CREACIÓN
        rol_creador = current_role_id()
        rol_destino = int(id_rol_form)
        
        if rol_creador != 1 and rol_destino <= rol_creador:
            flash('Acceso denegado: No posee el rango jerárquico para asignar este nivel de privilegio.', 'error')
            return redirect(url_for('usuario.index'))

        existe = Usuario.query.filter_by(correo=correo).first()
        if existe:
            flash('Ya existe un usuario con ese correo.', 'error')
            roles = Role.query.order_by(Role.id_rol).all()
            return render_template('usuarios/formulario.html', roles=roles)

        bool_estatus = (estatus_form == '1') if estatus_form is not None else True

        nuevo_usuario = Usuario(
            nombre_usuario=nombre,
            correo=correo,
            id_rol=rol_destino,
            estatus=bool_estatus
        )
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        # 🔔 ALERTA DE ALTA DE USUARIO (CON CORRECCIÓN DE LEIDO)
        try:
            from app.models.notificacion import Notificacion
            alerta = Notificacion(
                categoria='Usuarios',
                mensaje=f"El operador {current_user.nombre_usuario} registró al nuevo usuario {nuevo_usuario.nombre_usuario} en la plataforma.",
                leido=False # 🌟 Forzado para evitar fallos de NULL en la base de datos
            )
            db.session.add(alerta)
            db.session.commit()
        except Exception:
            db.session.rollback()

        registrar_accion('Usuarios', nuevo_usuario.id_usuario, 'Crear', current_user.nombre_usuario, detalle=f'Creado usuario {correo}', estado_nuevo=nuevo_usuario.rol)

        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('usuarios/formulario.html', roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def usuario_editar(usuario_id):
    verificar_permiso_dinamico('gestionar_usuarios')
    
    usuario = Usuario.query.get_or_404(usuario_id)

    # 🛡️ REGLA DE NO AUTO-EDICIÓN EN LA TABLA GENERAL
    if current_role_id() != 1 and usuario.id_usuario == current_user.id_usuario:
        flash('Para modificar sus datos personales, utilice el módulo dedicado "Mi Perfil".', 'error')
        return redirect(url_for('usuario.index'))

    # 🛡️ BARRERA JERÁRQUICA DE EDICIÓN ESTÁNDAR
    rol_operador = current_role_id()
    rol_objetivo = int(usuario.id_rol)

    if rol_operador != 1:
        if rol_operador == 2 and rol_objetivo == 1:
            flash('No tiene jerarquía para modificar los datos de un Superusuario.', 'error')
            abort(403)
        elif rol_operador == 3 and rol_objetivo < 3:
            flash('No tiene jerarquía para modificar los datos de este usuario.', 'error')
            abort(403)

    if request.method == 'POST':
        nombre = (request.form.get('nombre_usuario') or '').strip()
        id_rol_form = request.form.get('id_rol')
        estatus_form = request.form.get('estatus')

        # 🛡️ CONTROL DE ESCALADA Y ANTI AUTO-DEGRADACIÓN
        if id_rol_form and usuario.id_usuario != current_user.id_usuario:
            rol_destino = int(id_rol_form)
            if rol_operador != 1 and rol_destino < rol_operador:
                flash('No puede asignar un nivel de privilegio superior al suyo.', 'error')
                return redirect(url_for('usuario.index'))
            usuario.id_rol = rol_destino

        if estatus_form is not None and usuario.id_usuario != current_user.id_usuario:
            usuario.estatus = (estatus_form == '1')

        usuario.nombre_usuario = nombre or usuario.nombre_usuario

        nueva_pass = (request.form.get('password') or '').strip()
        if nueva_pass:
            usuario.set_password(nueva_pass)

        db.session.commit()

        # 🔔 ALERTA DE MODIFICACIÓN DE DATOS (CON CORRECCIÓN DE LEIDO)
        try:
            from app.models.notificacion import Notificacion
            alerta = Notificacion(
                categoria='Seguridad',
                mensaje=f"Perfil del usuario {usuario.nombre_usuario} fue actualizado por el operador {current_user.nombre_usuario}.",
                leido=False # 🌟 Forzado para evitar fallos de NULL en la base de datos
            )
            db.session.add(alerta)
            db.session.commit()
        except Exception:
            db.session.rollback()
        
        user_correo = getattr(usuario, 'correo', usuario.nombre_usuario)
        registrar_accion('Usuarios', usuario.id_usuario, 'Modificar', current_user.nombre_usuario, detalle=f'Editado usuario {user_correo}', estado_nuevo=usuario.rol)

        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('usuarios/formulario.html', usuario=usuario, roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def usuario_eliminar(usuario_id):
    verificar_permiso_dinamico('gestionar_usuarios')
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puede eliminar su propio usuario mientras esté autenticado en el sistema.', 'error')
        return redirect(url_for('usuario.index'))

    rol_operador = current_role_id()
    rol_objetivo = int(usuario.id_rol)

    if rol_operador != 1:
        if rol_operador == 2 and rol_objetivo == 1:
            flash('Acceso denegado: No posee la jerarquía para eliminar a un Superusuario.', 'error')
            return redirect(url_for('usuario.index'))
        elif rol_operador == 3 and rol_objetivo < 3:
            flash('Acceso denegado: No posee la jerarquía para eliminar a este usuario.', 'error')
            return redirect(url_for('usuario.index'))

    user_correo = getattr(usuario, 'correo', usuario.nombre_usuario)
    nombre_eliminado = usuario.nombre_usuario

    db.session.delete(usuario)
    db.session.commit()

    # 🔔 ALERTA DE ELIMINACIÓN CRÍTICA (CON CORRECCIÓN DE LEIDO)
    try:
        from app.models.notificacion import Notificacion
        alerta = Notificacion(
            categoria='Seguridad',
            mensaje=f"¡CRÍTICO!: La cuenta de {nombre_eliminado} fue removida del sistema por el operador {current_user.nombre_usuario}.",
            leido=False # 🌟 Forzado para evitar fallos de NULL en la base de datos
        )
        db.session.add(alerta)
        db.session.commit()
    except Exception:
        db.session.rollback()
    
    registrar_accion('Usuarios', usuario_id, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado usuario {user_correo}')

    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('usuario.index'))


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

        db.session.add(usuario)
        db.session.commit()
        registrar_accion('Usuarios', usuario.id_usuario, 'ModificarPerfil', usuario.nombre_usuario, detalle='Actualizó perfil propio')
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('usuarios/formulario.html', usuario=usuario, es_perfil=True, roles=roles)


# =============================================================================
#  🔔 ENDPOINT DE ACTUALIZACIÓN ASÍNCRONA PARA LA CAMPANITA
# =============================================================================
@core_bp.route('/admin/notificaciones/leer', methods=['POST'])
@login_required
def marcar_notificaciones_leidas():
    """
    Actualiza masivamente el estado 'leido' a True en la base de datos
    para todas las alertas sin leer del usuario logueado en esta sesión.
    """
    from app.models.notificacion import Notificacion

    try:
        # 🌟 CORRECCIÓN: Usamos .is_(None) para que PostgreSQL reconozca las alertas globales
        notificaciones_pendientes = Notificacion.query.filter(
            (Notificacion.usuario_id == current_user.id_usuario) | (Notificacion.usuario_id.is_(None)),
            Notificacion.leido == False
        ).all()

        for notif in notificaciones_pendientes:
            notif.leido = True
        
        db.session.commit()
        return {'status': 'success', 'message': 'Estatus de lectura sincronizado con éxito.'}, 200

    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}, 500


@core_bp.route('/admin/notificaciones/historial')
@login_required
def notificaciones_historial():
    """
    Vista formal para listar la bandeja de entrada o historial 
    completo de notificaciones del ecosistema.
    """
    from app.models.notificacion import Notificacion

    # 🌟 CORRECCIÓN: Al entrar al historial, limpiamos usando la sintaxis correcta .is_(None)
    try:
        notificaciones_pendientes = Notificacion.query.filter(
            (Notificacion.usuario_id == current_user.id_usuario) | (Notificacion.usuario_id.is_(None)),
            Notificacion.leido == False
        ).all()

        for notif in notificaciones_pendientes:
            notif.leido = True
        
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Consultamos todo el historial usando .is_(None)
    historial = Notificacion.query.filter(
        (Notificacion.usuario_id == current_user.id_usuario) | (Notificacion.usuario_id.is_(None))
    ).order_by(Notificacion.fecha_creacion.desc()).all()

    return render_template('usuarios/notificaciones_historial.html', historial=historial)
