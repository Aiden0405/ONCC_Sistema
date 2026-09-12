from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Permission, Role, UserPermissionOverride
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion
from app.models.password_reset import PasswordReset
from app.services.auditoria import registrar_accion
from app.services.notificacion import ServicioNotificacion
from app.utils.authorization import current_role_id, is_superuser, verificar_permiso_dinamico
from app.services.reportes import respuesta_csv
from app.utils.validation import parse_positive_int, validate_password, validate_person_text


@core_bp.route('/admin/usuarios/')
@login_required
def usuario_index():
    verificar_permiso_dinamico('ver_usuarios')
    usuarios = Usuario.query.order_by(Usuario.nombre_usuario).all()
    permisos = Permission.query.order_by(Permission.nombre_modulo).all()
    excepciones = {
        usuario.id_usuario: {
            override.id_modulo: override
            for override in UserPermissionOverride.query.filter_by(id_usuario=usuario.id_usuario).all()
        }
        for usuario in usuarios
    }
    return render_template(
        'usuarios/index.html',
        whitespaces=True,
        usuarios=usuarios,
        permisos=permisos,
        excepciones=excepciones,
        puede_gestionar_excepciones=is_superuser() or current_role_id() in (1, 2),
    )


@core_bp.route('/admin/usuarios/reporte')
@login_required
def usuario_reporte():
    verificar_permiso_dinamico('reportes_usuarios')
    usuarios = Usuario.query.order_by(Usuario.nombre_usuario).all()
    filas = [
        (u.id_usuario, u.nombre_usuario, u.correo, u.rol, 'Activo' if u.estatus else 'Inactivo')
        for u in usuarios
    ]
    return respuesta_csv(
        'reporte_usuarios.csv',
        ('ID', 'Nombre', 'Correo', 'Rol', 'Estatus'),
        filas,
    )


@core_bp.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
def usuario_nuevo():
    verificar_permiso_dinamico('registrar_usuarios')
    
    if request.method == 'POST':
        nombre = (request.form.get('nombre_usuario') or '').strip()
        correo = (request.form.get('correo') or '').strip().lower()
        id_rol_form = request.form.get('id_rol')
        password = request.form.get('password') or ''
        estatus_form = request.form.get('estatus')

        if not nombre or not correo or not password or not id_rol_form:
            flash('Nombre, correo, rol y contraseña son obligatorios.', 'error')
            roles = Role.query.order_by(Role.id_rol).all()
            return render_template('usuarios/formulario.html', roles=roles)
            
        try:
            nombre = validate_person_text(nombre, field='El nombre')
            if len(correo) > 50 or '@' not in correo:
                raise ValueError('El correo no es válido.')
            validate_password(password)
            rol_destino = parse_positive_int(id_rol_form, field='El rol')
        except ValueError as error:
            flash(str(error), 'error')
            roles = Role.query.order_by(Role.id_rol).all()
            return render_template('usuarios/formulario.html', roles=roles)

        # 🛡️ CONTROL DE JERARQUÍA ABSOLUTO EN CREACIÓN
        rol_creador = current_role_id()
        
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
        mensaje = f"Se registró al nuevo usuario {nuevo_usuario.nombre_usuario}."
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=nuevo_usuario.id_usuario, mensaje=mensaje, categoria='Usuarios')

        registrar_accion('Usuarios', nuevo_usuario.id_usuario, 'Crear', current_user.nombre_usuario, detalle=f'Creado usuario {correo}', estado_nuevo=nuevo_usuario.rol)

        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('usuarios/formulario.html', roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def usuario_editar(usuario_id):
    verificar_permiso_dinamico('editar_usuarios')
    
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
            try:
                rol_destino = parse_positive_int(id_rol_form, field='El rol')
            except ValueError as error:
                flash(str(error), 'error')
                return redirect(url_for('usuario.index'))
            if rol_operador != 1 and rol_destino < rol_operador:
                flash('No puede asignar un nivel de privilegio superior al suyo.', 'error')
                return redirect(url_for('usuario.index'))
            usuario.id_rol = rol_destino

        if estatus_form is not None and usuario.id_usuario != current_user.id_usuario:
            usuario.estatus = (estatus_form == '1')

        if nombre:
            try:
                usuario.nombre_usuario = validate_person_text(nombre, field='El nombre')
            except ValueError as error:
                flash(str(error), 'error')
                return redirect(url_for('usuario.index'))

        nueva_pass = request.form.get('password') or ''
        if nueva_pass:
            try:
                validate_password(nueva_pass)
            except ValueError as error:
                flash(str(error), 'error')
                return redirect(url_for('usuario.index'))
            usuario.set_password(nueva_pass)

        db.session.commit()
        mensaje = f"Tu perfil fue actualizado por {current_user.nombre_usuario}."
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', f'Se actualizó el usuario {usuario.nombre_usuario}.', emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Usuarios')
        
        user_correo = getattr(usuario, 'correo', usuario.nombre_usuario)
        registrar_accion('Usuarios', usuario.id_usuario, 'Modificar', current_user.nombre_usuario, detalle=f'Editado usuario {user_correo}', estado_nuevo=usuario.rol)

        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuario.index'))

    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('usuarios/formulario.html', usuario=usuario, roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def usuario_eliminar(usuario_id):
    verificar_permiso_dinamico('eliminar_usuarios')
    
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

    # Estas filas pertenecen a la cuenta y no pueden quedar con id_usuario NULL.
    Notificacion.query.filter_by(id_usuario=usuario.id_usuario).delete(synchronize_session=False)
    PasswordReset.query.filter_by(user_id=usuario.id_usuario).delete(synchronize_session=False)
    db.session.delete(usuario)
    db.session.commit()
    mensaje = f"Se eliminó la cuenta de {nombre_eliminado}."
    ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
    
    registrar_accion('Usuarios', usuario_id, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado usuario {user_correo}')

    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('usuario.index'))


@core_bp.route('/admin/usuarios/perfil', methods=['GET', 'POST'])
@login_required
def usuario_perfil():
    usuario = Usuario.query.get_or_404(current_user.id_usuario)
    if request.method == 'POST':
        nombre = (request.form.get('nombre_usuario') or usuario.nombre_usuario).strip()
        try:
            usuario.nombre_usuario = validate_person_text(nombre, field='El nombre')
        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for('usuario.index'))

        nueva_pass = request.form.get('password') or ''
        if nueva_pass:
            try:
                validate_password(nueva_pass)
            except ValueError as error:
                flash(str(error), 'error')
                return redirect(url_for('usuario.index'))
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
            (Notificacion.id_usuario == current_user.id_usuario) | (Notificacion.id_usuario.is_(None)),
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
            (Notificacion.id_usuario == current_user.id_usuario) | (Notificacion.id_usuario.is_(None)),
            Notificacion.leido == False
        ).all()

        for notif in notificaciones_pendientes:
            notif.leido = True
        
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Consultamos todo el historial usando .is_(None)
    historial = Notificacion.query.filter(
        (Notificacion.id_usuario == current_user.id_usuario) | (Notificacion.id_usuario.is_(None))
    ).order_by(Notificacion.fecha_creacion.desc()).all()

    return render_template('usuarios/notificaciones_historial.html', historial=historial)
