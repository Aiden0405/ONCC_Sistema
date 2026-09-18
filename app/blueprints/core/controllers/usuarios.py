# app/blueprints/core/controllers/usuarios.py
import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from flask import flash, redirect, render_template, request, url_for, abort, Response
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Permission, Role, UserPermissionOverride
from app.constants import LEGACY_PERMISSION_NAMES, RBAC_MODULES
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion
from app.models.password_reset import PasswordReset
from app.services.auditoria import registrar_accion
from app.services.notificacion import ServicioNotificacion
from app.utils.authorization import current_role_id, has_full_access_role, is_superuser, verificar_permiso_dinamico
from app.utils.validation import parse_positive_int, validate_password, validate_person_text


@core_bp.route('/admin/usuarios/')
@login_required
def usuario_index():
    verificar_permiso_dinamico('ver_usuarios')
    usuarios = Usuario.query.order_by(Usuario.nombre_usuario).all()
    roles = Role.query.order_by(Role.id_rol).all()
    
    permisos = Permission.query.order_by(Permission.nombre_modulo).all()
    permisos_por_nombre = {permiso.nombre_modulo: permiso for permiso in permisos}
    permisos_por_modulo = []
    permisos_asignados = set()
    for module in RBAC_MODULES.values():
        permisos_modulo = [
            (accion, permisos_por_nombre[nombre])
            for accion, nombre in module['permissions'].items()
            if nombre in permisos_por_nombre
        ]
        if permisos_modulo:
            permisos_por_modulo.append((module['label'], permisos_modulo))
            permisos_asignados.update(permiso.nombre_modulo for _, permiso in permisos_modulo)
    permisos_sin_modulo = [
        permiso for permiso in permisos
        if permiso.nombre_modulo not in permisos_asignados
        and permiso.nombre_modulo not in LEGACY_PERMISSION_NAMES
    ]
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
        roles=roles,
        permisos=permisos,
        permisos_por_modulo=permisos_por_modulo,
        permisos_sin_modulo=permisos_sin_modulo,
        excepciones=excepciones,
        puede_gestionar_excepciones=has_full_access_role(current_user.rol),
    )


@core_bp.route('/admin/usuarios/reporte')
@login_required
def usuario_reporte():
    verificar_permiso_dinamico('reportes_usuarios')
    usuarios = Usuario.query.order_by(Usuario.nombre_usuario).all()
    
    ids_param = request.args.get('ids')
    if ids_param:
        id_list = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]
        if id_list:
            usuarios = [u for u in usuarios if u.id_usuario in id_list]

    rol_filtro = request.args.get('rol', type=int)
    estatus_filtro = request.args.get('estatus')

    def coincide(u):
        if rol_filtro and u.id_rol != rol_filtro:
            return False
        if estatus_filtro == '1' and not u.estatus:
            return False
        if estatus_filtro == '0' and u.estatus:
            return False
        return True

    usuarios_finales = [u for u in usuarios if coincide(u)]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#16a34a'), spaceAfter=4)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#6b7280'), spaceAfter=12)
    
    header_cell_style = ParagraphStyle('HeaderCell', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.whitesmoke)
    body_cell_style = ParagraphStyle('BodyCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#374151'))
    
    elements.append(Paragraph("Reporte de Autenticación y Cuentas de Acceso Institucional", title_style))
    elements.append(Paragraph(f"Generado por: {current_user.correo} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    
    headers = [
        Paragraph("ID", header_cell_style),
        Paragraph("Nombre de Usuario", header_cell_style),
        Paragraph("Correo Electrónico", header_cell_style),
        Paragraph("Rol Asignado", header_cell_style),
        Paragraph("Estatus", header_cell_style)
    ]
    
    table_data = [headers]
    
    for u in usuarios_finales:
        estatus_txt = "Activo" if u.estatus else "Inactivo (Suspendido)"
        rol_txt = u.rol if u.rol else "Sin definir"
        
        table_data.append([
            Paragraph(f"#{u.id_usuario}", body_cell_style),
            Paragraph(u.nombre_usuario, body_cell_style),
            Paragraph(u.correo, body_cell_style),
            Paragraph(rol_txt, body_cell_style),
            Paragraph(estatus_txt, body_cell_style)
        ])
        
    t = Table(table_data, colWidths=[50, 180, 250, 140, 110])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    
    return Response(buffer, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename=reporte_usuarios.pdf'})


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
            
            # 🌟 VALIDACIÓN ROBUSTA DE CORREO
            patron_correo = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not correo or not re.match(patron_correo, correo) or len(correo) > 100:
                raise ValueError('El correo electrónico no es válido. Debe tener un formato real (ejemplo: usuario@gmail.com).')
                
            validate_password(password)
            rol_destino = parse_positive_int(id_rol_form, field='El rol')
        except ValueError as error:
            flash(str(error), 'error')
            roles = Role.query.order_by(Role.id_rol).all()
            return render_template('usuarios/formulario.html', roles=roles)

        rol_creador = current_role_id()
        
        if not has_full_access_role(current_user.rol) and rol_destino <= rol_creador:
            flash('Acceso denegado: No posee el rango jerárquico para asignar este nivel de privilegio.', 'error')
            return redirect(url_for('core.usuario_index'))

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
        return redirect(url_for('core.usuario_index'))

    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('usuarios/formulario.html', roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def usuario_editar(usuario_id):
    verificar_permiso_dinamico('editar_usuarios')
    
    usuario = Usuario.query.get_or_404(usuario_id)

    if current_role_id() != 1 and usuario.id_usuario == current_user.id_usuario:
        flash('Para modificar sus datos personales, utilice el módulo dedicado "Mi Perfil".', 'error')
        return redirect(url_for('core.usuario_index'))

    rol_operador = current_role_id()
    rol_objetivo = int(usuario.id_rol)

    if not has_full_access_role(current_user.rol):
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

        if id_rol_form and usuario.id_usuario != current_user.id_usuario:
            try:
                rol_destino = parse_positive_int(id_rol_form, field='El rol')
            except ValueError as error:
                flash(str(error), 'error')
                return redirect(url_for('core.usuario_index'))
            if rol_operador != 1 and rol_destino < rol_operador:
                flash('No puede asignar un nivel de privilegio superior al suyo.', 'error')
                return redirect(url_for('core.usuario_index'))
            usuario.id_rol = rol_destino

        if estatus_form is not None and usuario.id_usuario != current_user.id_usuario:
            usuario.estatus = (estatus_form == '1')

        if nombre:
            try:
                usuario.nombre_usuario = validate_person_text(nombre, field='El nombre')
            except ValueError as error:
                flash(str(error), 'error')
                return redirect(url_for('core.usuario_index'))

        nueva_pass = request.form.get('password') or ''
        if nueva_pass:
            try:
                validate_password(nueva_pass)
            except ValueError as error:
                flash(str(error), 'error')
                return redirect(url_for('core.usuario_index'))
            usuario.set_password(nueva_pass)

        db.session.commit()
        mensaje = f"Tu perfil fue actualizado por {current_user.nombre_usuario}."
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', f'Se actualizó el usuario {usuario.nombre_usuario}.', emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Usuarios')
        
        user_correo = getattr(usuario, 'correo', usuario.nombre_usuario)
        registrar_accion('Usuarios', usuario.id_usuario, 'Modificar', current_user.nombre_usuario, detalle=f'Editado usuario {user_correo}', estado_nuevo=usuario.rol)

        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('core.usuario_index'))

    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('usuarios/formulario.html', usuario=usuario, roles=roles)


@core_bp.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def usuario_eliminar(usuario_id):
    verificar_permiso_dinamico('eliminar_usuarios')
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puede eliminar su propio usuario mientras esté autenticado en el sistema.', 'error')
        return redirect(url_for('core.usuario_index'))

    rol_operador = current_role_id()
    rol_objetivo = int(usuario.id_rol)

    if not has_full_access_role(current_user.rol):
        if rol_operador == 2 and rol_objetivo == 1:
            flash('Acceso denegado: No posee la jerarquía para eliminar a un Superusuario.', 'error')
            return redirect(url_for('core.usuario_index'))
        elif rol_operador == 3 and rol_objetivo < 3:
            flash('Acceso denegado: No posee la jerarquía para eliminar a este usuario.', 'error')
            return redirect(url_for('core.usuario_index'))

    user_correo = getattr(usuario, 'correo', usuario.nombre_usuario)
    nombre_eliminado = usuario.nombre_usuario

    Notificacion.query.filter_by(id_usuario=usuario.id_usuario).delete(synchronize_session=False)
    PasswordReset.query.filter_by(user_id=usuario.id_usuario).delete(synchronize_session=False)
    db.session.delete(usuario)
    db.session.commit()
    mensaje = f"Se eliminó la cuenta de {nombre_eliminado}."
    ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
    
    registrar_accion('Usuarios', usuario_id, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado usuario {user_correo}')

    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('core.usuario_index'))


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
            return redirect(url_for('core.usuario_index'))

        nueva_pass = request.form.get('password') or ''
        if nueva_pass:
            try:
                validate_password(nueva_pass)
            except ValueError as error:
                flash(str(error), 'error')
                return redirect(url_for('core.usuario_index'))
            usuario.set_password(nueva_pass)

        db.session.add(usuario)
        db.session.commit()
        registrar_accion('Usuarios', usuario.id_usuario, 'ModificarPerfil', usuario.nombre_usuario, detalle='Actualizó perfil propio')
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('core.usuario_index'))

    roles = Role.query.order_by(Role.id_rol).all()
    return render_template('usuarios/formulario.html', usuario=usuario, es_perfil=True, roles=roles)


@core_bp.route('/admin/notificaciones/leer', methods=['POST'])
@login_required
def marcar_notificaciones_leidas():
    from app.models.notificacion import Notificacion

    try:
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
    from app.models.notificacion import Notificacion

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

    historial = Notificacion.query.filter(
        (Notificacion.id_usuario == current_user.id_usuario) | (Notificacion.id_usuario.is_(None))
    ).order_by(Notificacion.fecha_creacion.desc()).all()

    return render_template('usuarios/notificaciones_historial.html', historial=historial)