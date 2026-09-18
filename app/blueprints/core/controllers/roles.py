import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from flask import current_app, flash, redirect, render_template, request, url_for, abort, Response
from flask_login import current_user, login_required

from app import db
from app.blueprints.core import core_bp
from app.models.role import Permission, Role, Permiso, UserPermissionOverride
from app.models.usuario import Usuario
from app.services.auditoria import registrar_accion
from app.services.notificacion import ServicioNotificacion
from app.constants import KNOWN_PERMISSION_SLUGS, RBAC_MODULES
from app.utils.authorization import current_role_id, is_superuser_role, verificar_permiso_dinamico


# =============================================================================
#  RUTAS DE ROLES
# =============================================================================

@core_bp.route('/admin/roles/')
@login_required
def rol_index():
    verificar_permiso_dinamico('ver_roles')
    roles = Role.query.order_by(Role.id_rol).all()
    
    # 🌟 Agrupación inteligente idéntica a la vista de Usuarios
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
            
    # Manejo seguro por si no has importado LEGACY_PERMISSION_NAMES en este archivo
    try:
        from app.constants import LEGACY_PERMISSION_NAMES
        legacy_names = LEGACY_PERMISSION_NAMES
    except ImportError:
        legacy_names = []

    permisos_sin_modulo = [
        permiso for permiso in permisos
        if permiso.nombre_modulo not in permisos_asignados
        and permiso.nombre_modulo not in legacy_names
    ]
            
    return render_template(
        'roles/index.html', 
        roles=roles, 
        permisos_por_modulo=permisos_por_modulo,
        permisos_sin_modulo=permisos_sin_modulo
    )

@core_bp.route('/admin/roles/reporte')
@login_required
def rol_reporte():
    verificar_permiso_dinamico('reportes_roles')
    roles = Role.query.order_by(Role.id_rol).all()
    
    ids_param = request.args.get('ids')
    if ids_param:
        id_list = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]
        if id_list:
            roles = [r for r in roles if r.id_rol in id_list]

    nivel_filtro = request.args.get('nivel', '')
    permiso_filtro = request.args.get('permiso_filtro', type=int)

    def coincide(rol):
        cantidad = len(rol.permissions)
        is_root = rol.nombre_rol.lower() in ('superusuario', 'super usuario')

        if nivel_filtro == 'raiz' and not is_root:
            return False
        if nivel_filtro == 'privilegiado' and (is_root or cantidad <= 15):
            return False
        if nivel_filtro == 'estandar' and (is_root or cantidad > 15):
            return False

        if permiso_filtro:
            tiene_permiso = any(p.id_modulo == permiso_filtro for p in rol.permissions)
            if not tiene_permiso:
                return False

        return True

    roles_finales = [r for r in roles if coincide(r)]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#16a34a'), spaceAfter=4)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#6b7280'), spaceAfter=12)
    
    header_cell_style = ParagraphStyle('HeaderCell', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.whitesmoke)
    body_cell_style = ParagraphStyle('BodyCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#374151'))
    
    elements.append(Paragraph("Reporte de Auditoría: Matriz de Seguridad y Accesos", title_style))
    elements.append(Paragraph(f"Generado por: {current_user.correo} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    
    headers = [
        Paragraph("ID", header_cell_style),
        Paragraph("Denominación del Rol", header_cell_style),
        Paragraph("Capacidad (Permisos)", header_cell_style),
        Paragraph("Nivel de Acceso", header_cell_style)
    ]
    
    table_data = [headers]
    
    for rol in roles_finales:
        cantidad_permisos = len(rol.permissions)
        
        nivel_acceso = "Estándar"
        if rol.nombre_rol.lower() in ('superusuario', 'super usuario'):
            nivel_acceso = "Raíz (Acceso Total)"
        elif cantidad_permisos > 15:
            nivel_acceso = "Privilegiado"

        table_data.append([
            Paragraph(f"#{rol.id_rol}", body_cell_style),
            Paragraph(rol.nombre_rol, body_cell_style),
            Paragraph(f"{cantidad_permisos} permisos asignados", body_cell_style),
            Paragraph(nivel_acceso, body_cell_style)
        ])
        
    t = Table(table_data, colWidths=[50, 200, 150, 140])
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
    
    return Response(buffer, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename=auditoria_roles_seguridad.pdf'})


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
            flash('Rol registrado. Ahora defina sus accesos.', 'success')
            
            return redirect(url_for('core.rol_gestionar_permisos', rol_id=rol.id_rol))
            
        except Exception as e:
            db.session.rollback()
            flash('Error de consistencia en la base de datos.', 'error')
            return render_template('roles/formulario.html')

    return render_template('roles/formulario.html')


@core_bp.route('/admin/roles/<int:rol_id>/editar', methods=['GET', 'POST'])
@login_required
def rol_editar(rol_id):
    verificar_permiso_dinamico('editar_roles')
    
    rol = Role.query.get_or_404(rol_id)
    if is_superuser_role(rol.nombre_rol):
        flash('El rol superusuario es estructural y no puede renombrarse.', 'error')
        abort(403)
        
    if request.method == 'POST':
        nombre_anterior = rol.nombre_rol
        rol.nombre_rol = (request.form.get('nombre') or rol.nombre_rol).strip()
        
        try:
            db.session.commit()
            mensaje = f"El rol '{nombre_anterior}' fue renombrado a '{rol.nombre_rol}'."
            ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

            registrar_accion('Roles', rol.id_rol, 'Modificar', current_user.nombre_usuario, detalle=f'Actualizado rol {rol.nombre_rol}')
            flash('Nombre del rol actualizado con éxito.', 'success')
            return redirect(url_for('core.rol_index'))
        except Exception:
            db.session.rollback()
            flash('Error al actualizar el rol.', 'error')
            return render_template('roles/formulario.html', rol=rol)

    return render_template('roles/formulario.html', rol=rol)


@core_bp.route('/admin/roles/<int:rol_id>/eliminar', methods=['POST'])
@login_required
def rol_eliminar(rol_id):
    verificar_permiso_dinamico('eliminar_roles')
    
    rol = Role.query.get_or_404(rol_id)
    if is_superuser_role(rol.nombre_rol):
        flash('El rol superusuario es estructural y no puede eliminarse.', 'error')
        abort(403)
        
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
        return redirect(url_for('core.rol_index'))
    except Exception:
        db.session.rollback()
        flash('No se puede eliminar el rol debido a restricciones de integridad en la base de datos.', 'error')
        return redirect(url_for('core.rol_index'))


@core_bp.route('/admin/roles/<int:rol_id>/permisos', methods=['GET', 'POST'])
@login_required
def rol_gestionar_permisos(rol_id):
    verificar_permiso_dinamico('asignar_permisos_roles')
    
    rol = Role.query.get_or_404(rol_id)
    rol_raiz = is_superuser_role(rol.nombre_rol)
    if rol_raiz and request.method == 'POST':
        flash('El rol superusuario tiene acceso total permanente y no se modifica desde esta matriz.', 'error')
        abort(403)
        
    permisos = Permission.query.order_by(Permission.nombre_modulo).all()
    permisos_por_nombre = {permiso.nombre_modulo: permiso for permiso in permisos}
    matriz = [
        (clave, modulo, [
            (accion, permisos_por_nombre.get(slug))
            for accion, slug in modulo['permissions'].items()
            if permisos_por_nombre.get(slug)
        ])
        for clave, modulo in RBAC_MODULES.items()
    ]
    
    if request.method == 'POST':
        seleccion = {
            int(pid) for pid in request.form.getlist('permisos')
            if pid.isdigit()
        }

        for modulo in RBAC_MODULES.values():
            acciones = modulo['permissions']
            permiso_leer = permisos_por_nombre.get(acciones['leer'])
            acciones_internas = [
                permisos_por_nombre[nombre].id_modulo
                for accion, nombre in acciones.items()
                if accion != 'leer' and nombre in permisos_por_nombre
            ]
            if any(permiso_id in seleccion for permiso_id in acciones_internas):
                if not permiso_leer or permiso_leer.id_modulo not in seleccion:
                    flash(
                        f"En el módulo '{modulo['label']}' debe seleccionar primero 'Leer' para asignar acciones internas.",
                        'error',
                    )
                    return render_template('roles/permisos.html', rol=rol, permisos=permisos, matriz=matriz)
        try:
            Permiso.query.filter_by(id_rol=rol.id_rol).delete()
            
            for pid in seleccion:
                db.session.add(Permiso(id_rol=rol.id_rol, id_modulo=pid))
            
            db.session.commit()
            mensaje = f"Se actualizaron los permisos del rol '{rol.nombre_rol}'."
            ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Seguridad')

            registrar_accion('Roles', rol.id_rol, 'ActualizarPermisos', current_user.nombre_usuario, detalle=f'Permisos actualizados para {rol.nombre_rol}: {sorted(seleccion)}')
            flash('Matriz de accesos actualizada con éxito.', 'success')
            return redirect(url_for('core.rol_index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error crítico al guardar la matriz de accesos.', 'error')
            return redirect(url_for('core.rol_index'))

    return render_template('roles/permisos.html', rol=rol, permisos=permisos, matriz=matriz, rol_raiz=rol_raiz)


@core_bp.route('/admin/usuarios/<int:usuario_id>/permisos-excepciones', methods=['POST'])
@login_required
def usuario_permiso_excepcion(usuario_id):
    verificar_permiso_dinamico('asignar_permisos_roles')

    usuario = Usuario.query.get_or_404(usuario_id)
    if is_superuser_role(usuario.rol):
        flash('El superusuario tiene acceso total permanente y no admite permisos individuales.', 'error')
        return redirect(url_for('usuario.index'))

    permiso_id = request.form.get('permiso_id', type=int)
    efecto = request.form.get('efecto')
    if not permiso_id or efecto not in {'conceder', 'revocar', 'quitar'}:
        flash('La excepción de permiso no es válida.', 'error')
        return redirect(url_for('usuario.index'))

    permiso = Permission.query.get_or_404(permiso_id)
    modulo_padre = next(
        (
            module for module in RBAC_MODULES.values()
            if permiso.nombre_modulo in module['permissions'].values()
        ),
        None,
    )
    if modulo_padre:
        permiso_lectura = modulo_padre['permissions']['leer']
        permisos_modulo = set(modulo_padre['permissions'].values())
        if efecto == 'conceder' and permiso.nombre_modulo != permiso_lectura and not usuario.has_permission(permiso_lectura):
            flash('Primero debe conceder el permiso "Leer" del módulo antes de asignar acciones internas.', 'error')
            return redirect(url_for('usuario.index'))
        if efecto == 'revocar' and permiso.nombre_modulo == permiso_lectura:
            conserva_accion = any(
                usuario.has_permission(nombre)
                for nombre in permisos_modulo
                if nombre != permiso_lectura
            )
            if conserva_accion:
                flash('No puede revocar el acceso al módulo mientras conserve acciones internas.', 'error')
                return redirect(url_for('usuario.index'))
    override = UserPermissionOverride.query.get((usuario.id_usuario, permiso.id_modulo))
    try:
        if efecto == 'quitar':
            if override:
                db.session.delete(override)
        elif override:
            override.concedido = efecto == 'conceder'
        else:
            db.session.add(UserPermissionOverride(
                id_usuario=usuario.id_usuario,
                id_modulo=permiso.id_modulo,
                concedido=efecto == 'conceder',
            ))
        db.session.commit()
        flash('Excepción individual actualizada correctamente.', 'success')
    except Exception:
        db.session.rollback()
        flash('No se pudo actualizar la excepción individual.', 'error')

    return redirect(url_for('usuario.index'))


# =============================================================================
#  RUTAS DEL CATÁLOGO DE PERMISOS ATÓMICOS 
# =============================================================================

@core_bp.route('/admin/permisos/')
@login_required
def permiso_index():
    verificar_permiso_dinamico('ver_permisos')
    page = request.args.get('page', 1, type=int)
    pagination = Permission.query.order_by(Permission.id_modulo).paginate(page=page, per_page=10)
    return render_template('roles/permisos_index.html', pagination=pagination, permisos=pagination.items)


@core_bp.route('/admin/permisos/reporte')
@login_required
def permiso_reporte():
    verificar_permiso_dinamico('reportes_permisos')
    permisos = Permission.query.order_by(Permission.nombre_modulo).all()
    
    # 1. Filtros parametrizados
    modulo_filtro = request.args.get('modulo', '').strip().lower()
    asignacion_filtro = request.args.get('asignacion', '').strip()
    
    def coincide_permiso(p):
        # Filtrar por módulo (buscando palabras clave en el nombre del permiso)
        if modulo_filtro:
            if modulo_filtro not in p.nombre_modulo:
                return False
        
        # Filtrar por exposición/asignación
        cantidad_roles = len(p.roles)
        if asignacion_filtro == 'huerfanos' and cantidad_roles > 0:
            return False
        if asignacion_filtro == 'asignados' and cantidad_roles == 0:
            return False
            
        return True
        
    permisos_finales = [p for p in permisos if coincide_permiso(p)]

    # 🌟 GENERACIÓN DE PDF PROFESIONAL PARA PERMISOS
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#16a34a'), spaceAfter=4)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#6b7280'), spaceAfter=12)
    
    header_cell_style = ParagraphStyle('HeaderCell', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.whitesmoke)
    body_cell_style = ParagraphStyle('BodyCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#374151'))
    
    elements.append(Paragraph("Catálogo Global de Privilegios y Permisos (RBAC)", title_style))
    elements.append(Paragraph(f"Generado por: {current_user.correo} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    
    headers = [
        Paragraph("ID", header_cell_style),
        Paragraph("Slug / Nombre Técnico", header_cell_style),
        Paragraph("Descripción del Acceso", header_cell_style),
        Paragraph("Roles Asignados", header_cell_style)
    ]
    
    table_data = [headers]
    
    for permiso in permisos_finales:
        descripcion_txt = permiso.descripcion or getattr(permiso, 'descripcion_modulo', 'Sin descripción')
        cantidad = len(permiso.roles)
        roles_txt = f"{cantidad} rol(es)" if cantidad > 0 else "Sin asignar (Inactivo)"
        
        table_data.append([
            Paragraph(f"#{permiso.id_modulo}", body_cell_style),
            Paragraph(permiso.nombre_modulo, body_cell_style),
            Paragraph(descripcion_txt, body_cell_style),
            Paragraph(roles_txt, body_cell_style)
        ])
        
    t = Table(table_data, colWidths=[50, 180, 400, 100])
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
    
    return Response(buffer, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename=reporte_permisos_catalogo.pdf'})

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
            flash(f'No se puede crear el permiso técnico "{nombre}": no existe en el catálogo.', 'error')
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
            flash(f'No se puede guardar el permiso técnico "{nombre_form}": no existe en el catálogo.', 'error')
            return render_template('roles/permiso_formulario.html', permiso=permiso)
            
        if nombre_form != permiso.nombre_modulo:
            if Permission.query.filter_by(nombre_modulo=nombre_form).first():
                flash(f'El privilegio técnico "{nombre_form}" ya existe.', 'error')
                return render_template('roles/permiso_formulario.html', permiso=permiso)
        
        permiso.nombre = nombre_form
        permiso.descripcion = descripcion_form
        
        try:
            db.session.commit()
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
    
    try:
        db.session.delete(permiso)
        db.session.commit()
        flash('Permiso removido correctamente del catálogo global.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar porque está asignado a roles institucionales activos.', 'error')
        
    return redirect(url_for('core.permiso_index'))