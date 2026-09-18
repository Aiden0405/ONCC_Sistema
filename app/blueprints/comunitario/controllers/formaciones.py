# app/blueprints/comunitario/controllers/formaciones.py
import io
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for, Response
from flask_login import login_required, current_user

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app import db
from app.blueprints.comunitario import comunitario_bp
from app.blueprints.comunitario.forms import RegistroComunitarioForm
from app.blueprints.core.controllers.roles import verificar_permiso_dinamico
from app.models.esquema_activo import (
    NivelActivo as Nivel,
    InstitucionActiva as Institucion,
    ComunidadActiva as Comunidad
)
from app.models.actividad import Actividad
from app.models.bitacora import BitacoraTransaccion
from app.models.esquema_activo import FormacionActiva as Formacion
from app.models.tecnico import Tecnico
from app.services.notificacion import ServicioNotificacion
from app.utils.authorization import has_permission


def _cargar_registro_choices(form):
    # Mostrar solo Actividades de FORMACION o SENSIBILIZACION sin vinculación previa
    actividades_disponibles = (
        Actividad.query
        .outerjoin(Formacion, Actividad.id_actividad == Formacion.id_actividad)
        .filter(Formacion.id_formacion == None)
        .filter(Actividad.tipo_actividad.in_(['FORMACION', 'SENSIBILIZACION']))
        .order_by(Actividad.id_actividad.desc())
        .all()
    )

    if actividades_disponibles:
        form.id_actividad.choices = [
            (a.id_actividad, f"Actividad #{a.id_actividad} - {a.tipo_actividad} ({a.fecha_actividad})") 
            for a in actividades_disponibles
        ]
    else:
        form.id_actividad.choices = [(0, "No hay actividades disponibles para vincular")]

    instituciones = Institucion.query.order_by(Institucion.nombre_institucion.asc()).all()
    form.id_institucion.choices = [(0, 'No aplica')] + [
        (inst.id_institucion, inst.nombre_institucion) for inst in instituciones
    ]

    tecnicos = Tecnico.query.filter(Tecnico.id_usuario.isnot(None)).order_by(
        Tecnico.apellidos.asc(), Tecnico.nombres.asc()
    ).all()
    form.tecnico.choices = [(t.id_tecnico, f"{t.nombres} {t.apellidos}") for t in tecnicos]
    
    return actividades_disponibles


def _registrar_registro_comunitario(form):
    tecnico = Tecnico.query.get(form.tecnico.data)
    if tecnico is None:
        raise ValueError('El técnico seleccionado no existe o no está activo.')

    actividad_padre = Actividad.query.get(form.id_actividad.data)
    if not actividad_padre:
        raise ValueError('Debe vincular la formación a una actividad de campo existente.')

    nombre_tecnico = f"{tecnico.nombres} {tecnico.apellidos}".strip()
    tipo_heredado = actividad_padre.tipo_actividad
    
    db.session.add(Formacion(
        nombre_formacion=f"{form.nombre.data}||{nombre_tecnico}",
        id_institucion=form.id_institucion.data or None,
        tipo_destino=form.tipo_destino.data,
        id_tecnico=form.tecnico.data,
        id_actividad=actividad_padre.id_actividad,
        id_nivel=actividad_padre.id_nivel,
        tipo_actividad=tipo_heredado 
    ))


@comunitario_bp.route('/formaciones', methods=['GET', 'POST'])
@login_required  
def formaciones_index():
    if not (has_permission('ver_formaciones') or has_permission('ver_sensibilizaciones')):
        verificar_permiso_dinamico('ver_formaciones')

    form = RegistroComunitarioForm()
    act_disponibles = _cargar_registro_choices(form)
    formaciones_procesadas = Formacion.obtener_historial_completo()
    instituciones = Institucion.query.all()

    return render_template(
        'formaciones/index.html', 
        form=form,
        formaciones=formaciones_procesadas,
        actividades_disponibles=act_disponibles,
        instituciones=instituciones
    )


@comunitario_bp.route('/formaciones/reporte')
@login_required
def formaciones_reporte():
    if not (has_permission('reportes_formaciones') or has_permission('reportes_sensibilizaciones')):
        verificar_permiso_dinamico('reportes_formaciones')

    registros = Formacion.obtener_historial_completo()
    
    ids_param = request.args.get('ids')
    if ids_param:
        id_list = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]
        if id_list:
            registros = [r for r in registros if r['id_formacion'] in id_list]

    tecnico = request.args.get('tecnico', type=int)
    comunidad = request.args.get('comunidad', type=int)
    nivel = request.args.get('nivel', type=int)
    tipo = request.args.get('tipo')
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    estado = request.args.get('estado')
    
    estados = {}
    for bitacora in BitacoraTransaccion.query.filter_by(modulo='actividades').order_by(BitacoraTransaccion.id.desc()).all():
        estados.setdefault(bitacora.registro_id, bitacora.estado_nuevo or 'Completado')

    def coincide(registro):
        fecha_str = str(registro.get('fecha_actividad_cruda', '')) 
        
        return (
            (not tecnico or registro.get('id_tecnico') == tecnico)
            and (not comunidad or registro.get('id_comunidad') == comunidad)
            and (not nivel or registro.get('id_nivel') == nivel)
            and (not tipo or registro.get('tipo') == tipo)
            and (not desde or fecha_str >= desde)
            and (not hasta or fecha_str <= hasta)
            and (not mes or (len(fecha_str) >= 7 and int(fecha_str[5:7]) == mes))
            and (not anio or (len(fecha_str) >= 4 and int(fecha_str[0:4]) == anio))
            and (not estado or estados.get(registro.get('id_actividad'), 'Completado') == estado)
        )

    filas_filtradas = [r for r in registros if coincide(r)]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#16a34a'), spaceAfter=4)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#6b7280'), spaceAfter=12)
    
    header_cell_style = ParagraphStyle('HeaderCell', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.whitesmoke)
    body_cell_style = ParagraphStyle('BodyCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, textColor=colors.HexColor('#374151'))
    
    elements.append(Paragraph("Reporte Consolidado de Formaciones y Sensibilizaciones", title_style))
    elements.append(Paragraph(f"Generado por: {current_user.correo} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    
    headers = [
        Paragraph("Tipo", header_cell_style),
        Paragraph("ID", header_cell_style),
        Paragraph("Tema / Campaña", header_cell_style),
        Paragraph("Técnico", header_cell_style),
        Paragraph("Destino", header_cell_style),
        Paragraph("Comunidad / Inst.", header_cell_style),
        Paragraph("Fecha", header_cell_style),
        Paragraph("Nivel", header_cell_style),
        Paragraph("Estado", header_cell_style)
    ]
    
    table_data = [headers]
    
    for reg in filas_filtradas:
        destino_str = f"Inst: {reg.get('nombre_institucion', '')}" if reg.get('tipo_destino') == 'INSTITUCION' else f"Com: {reg.get('nombre_comunidad', '')}"
        table_data.append([
            Paragraph(str(reg.get('tipo', '')), body_cell_style),
            Paragraph(f"#{reg.get('id_formacion', '')}", body_cell_style),
            Paragraph(str(reg.get('tema', '')), body_cell_style),
            Paragraph(str(reg.get('tecnico', '')), body_cell_style),
            Paragraph(str(reg.get('tipo_destino', '')), body_cell_style),
            Paragraph(destino_str, body_cell_style),
            Paragraph(str(reg.get('fecha_actividad_cruda', '')), body_cell_style),
            Paragraph(str(reg.get('nombre_nivel', '')), body_cell_style),
            Paragraph(str(estados.get(reg.get('id_actividad'), 'Completado')), body_cell_style)
        ])
        
    t = Table(table_data, colWidths=[65, 32, 140, 110, 65, 150, 65, 80, 65])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    
    return Response(buffer, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename=reporte_formaciones.pdf'})


@comunitario_bp.route('/formaciones/nuevo', methods=['GET', 'POST'])
@login_required
def formacion_nuevo():
    if not (has_permission('registrar_formaciones') or has_permission('registrar_sensibilizaciones')):
        verificar_permiso_dinamico('registrar_formaciones')

    form = RegistroComunitarioForm()
    act_disponibles = _cargar_registro_choices(form)
    instituciones = Institucion.query.all()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            _registrar_registro_comunitario(form)
            db.session.commit()
            
            actividad_padre = Actividad.query.get(form.id_actividad.data)
            es_formacion = actividad_padre.tipo_actividad == 'FORMACION'
            
            modulo = 'gestionar_formaciones' if es_formacion else 'gestionar_sensibilizaciones'
            categoria = 'Formaciones' if es_formacion else 'Sensibilizaciones'
            etiqueta = 'formación' if es_formacion else 'sensibilización'
            
            mensaje = f'Se registró una nueva {etiqueta} comunitaria.'
            ServicioNotificacion.notificar_por_permiso(modulo, mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria=categoria)
            flash(f'{etiqueta.capitalize()} registrada con éxito.', 'success')
            return redirect(url_for('comunitario.formaciones_index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la formación: {str(e)}', 'error')

    formaciones_procesadas = Formacion.obtener_historial_completo()
    return render_template(
        'formaciones/index.html',
        form=form,
        formaciones=formaciones_procesadas,
        actividades_disponibles=act_disponibles,
        instituciones=instituciones
    )


@comunitario_bp.route('/formaciones/editar/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_editar(id_formacion):
    permiso_edicion = 'editar_sensibilizaciones' if Formacion.query.get_or_404(id_formacion).tipo_actividad == 'SENSIBILIZACION' else 'editar_formaciones'
    verificar_permiso_dinamico(permiso_edicion)

    formacion = Formacion.query.get_or_404(id_formacion)

    tema_nuevo = request.form.get('edit_nombre_formacion')
    id_tecnico_nuevo = request.form.get('edit_tecnico')
    id_inst_nueva = request.form.get('edit_id_institucion')
    tipo_destino_nuevo = request.form.get('edit_tipo_destino') or formacion.tipo_destino

    try:
        tecnico_nuevo = None
        if id_tecnico_nuevo:
            tecnico_selected = Tecnico.query.get(int(id_tecnico_nuevo))
            if tecnico_selected is None:
                raise ValueError('El técnico seleccionado no existe.')
            tecnico_nuevo = f"{tecnico_selected.nombres} {tecnico_selected.apellidos}".strip()

        formacion.nombre_formacion = f"{tema_nuevo}||{tecnico_nuevo or getattr(formacion, 'tecnico_real', '')}"
        formacion.tipo_destino = tipo_destino_nuevo
        formacion.id_tecnico = int(id_tecnico_nuevo) if id_tecnico_nuevo else formacion.id_tecnico
        formacion.id_institucion = int(id_inst_nueva) if id_inst_nueva and int(id_inst_nueva) > 0 else None

        db.session.commit()
        mensaje = f'Se actualizó la formación #{id_formacion}.'
        ServicioNotificacion.notificar_por_permiso('gestionar_formaciones', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Formaciones')
        flash('Formación actualizada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al modificar: {str(e)}', 'error')

    return redirect(url_for('comunitario.formaciones_index'))


@comunitario_bp.route('/formaciones/eliminar/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_eliminar(id_formacion):
    formacion = Formacion.query.get_or_404(id_formacion)
    permiso_eliminacion = 'eliminar_sensibilizaciones' if formacion.tipo_actividad == 'SENSIBILIZACION' else 'eliminar_formaciones'
    verificar_permiso_dinamico(permiso_eliminacion)
    
    try:
        db.session.delete(formacion)
        db.session.commit()
        mensaje = f'Se eliminó la formación #{id_formacion}.'
        ServicioNotificacion.notificar_por_permiso('gestionar_formaciones', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Formaciones')
        flash('Formación eliminada del historial (La actividad base se mantiene).', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'error')

    return redirect(url_for('comunitario.formaciones_index'))


@comunitario_bp.route('/formaciones/cambiar_estado/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_cambiar_estado(id_formacion):
    verificar_permiso_dinamico('cambiar_estado_formaciones')
    try:
        flash('Estado de la formación actualizado (Simulado).', 'success')
    except Exception as e:
        flash(f'Error al cambiar estado: {str(e)}', 'error')
    return redirect(url_for('comunitario.formaciones_index'))