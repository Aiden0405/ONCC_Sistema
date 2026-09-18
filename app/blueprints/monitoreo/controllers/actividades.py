# app/blueprints/monitoreo/controllers/actividades.py
import os
import io
from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for, Response
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app import db
from app.blueprints.monitoreo import monitoreo_bp
from app.constants import ESTADOS_ACTIVIDAD
from app.models.actividad import Actividad, ActividadTecnico, Monitoreo, Imagenes, ImagenesActividad
from app.models.bitacora import BitacoraTransaccion
from app.models.tecnico import Tecnico
from app.models.esquema_activo import ComunidadActiva as Comunidad
from app.models.esquema_activo import NivelActivo as Nivel
from app.blueprints.core.forms import ActividadForm
from app.blueprints.core.controllers.roles import verificar_permiso_dinamico
from app.services.notificacion import ServicioNotificacion
from app.services.reportes import respuesta_csv
from app.utils.validation import normalize_text, parse_positive_int


def _guardar_archivo(archivo, carpeta):
    if not archivo or not archivo.filename:
        return None

    nombre_archivo = secure_filename(archivo.filename)
    extensiones = {
        'minutas': {'pdf'},
        'fotos_actividad': {'jpg', 'jpeg', 'png', 'webp'},
    }.get(carpeta, set())
    if not nombre_archivo or '.' not in nombre_archivo or nombre_archivo.rsplit('.', 1)[1].lower() not in extensiones:
        return None
    destino = os.path.join(current_app.root_path, 'static', 'uploads', carpeta)
    os.makedirs(destino, exist_ok=True)
    ruta_completa = os.path.join(destino, nombre_archivo)
    archivo.save(ruta_completa)
    return os.path.join('uploads', carpeta, nombre_archivo).replace('\\', '/')


def _cargar_tecnicos(form):
    tecnicos = Tecnico.query.order_by(Tecnico.apellidos.asc(), Tecnico.nombres.asc()).all()
    form.tecnico_responsable.choices = [(0, 'Seleccione el analista/técnico...')]

    if tecnicos:
        form.tecnico_responsable.choices.extend(
            (tecnico.id_tecnico, f"{tecnico.nombres} {tecnico.apellidos}")
            for tecnico in tecnicos
        )
    else:
        form.tecnico_responsable.choices = [(0, 'No hay técnicos registrados')]


# ==============================================================================
# 1. READ (HISTORIAL DE ACTIVIDADES Y REPORTES)
# ==============================================================================
@monitoreo_bp.route('/actividades/')
@login_required
def actividades_index():
    verificar_permiso_dinamico('ver_actividades')
    actividades = Actividad.query.order_by(Actividad.fecha_actividad.desc()).all()
    
    for act in actividades:
        ultima_bitacora = BitacoraTransaccion.query.filter_by(modulo='actividades', registro_id=act.id_actividad).order_by(BitacoraTransaccion.id.desc()).first()
        act.estado_operativo_real = ultima_bitacora.estado_nuevo if ultima_bitacora and ultima_bitacora.estado_nuevo else 'Completado'

        if act.comunidad and act.comunidad.parroquia:
            act.parroquia_nombre = act.comunidad.parroquia.nombre_parroquia
            if act.comunidad.parroquia.municipio:
                act.municipio_nombre = act.comunidad.parroquia.municipio.nombre_municipio
                if act.comunidad.parroquia.municipio.estado:
                    act.estado_geo_nombre = act.comunidad.parroquia.municipio.estado.nombre_estado
                else:
                    act.estado_geo_nombre = 'Lara'
            else:
                act.municipio_nombre = 'Iribarren'
                act.estado_geo_nombre = 'Lara'
        else:
            act.parroquia_nombre = 'Catedral'
            act.municipio_nombre = 'Iribarren'
            act.estado_geo_nombre = 'Lara'

    comunidades = Comunidad.query.order_by(Comunidad.nombre_comunidad.asc()).all()
    niveles = Nivel.query.order_by(Nivel.nombre_nivel.asc()).all()

    return render_template(
        'actividades/index.html', 
        actividades=actividades, 
        estados_actividad=ESTADOS_ACTIVIDAD,
        comunidades=comunidades,
        niveles=niveles
    )


@monitoreo_bp.route('/actividades/reporte')
@login_required
def actividades_reporte():
    verificar_permiso_dinamico('reportes_actividades')
    actividades = Actividad.query.order_by(Actividad.fecha_actividad.desc()).all()
    
    ids_param = request.args.get('ids')
    if ids_param:
        id_list = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]
        if id_list:
            actividades = [a for a in actividades if a.id_actividad in id_list]

    tipo_filtro = request.args.get('tipo', '').strip()
    desde = request.args.get('desde', '').strip()
    hasta = request.args.get('hasta', '').strip()
    comunidad_id = request.args.get('comunidad', type=int)
    nivel_id = request.args.get('nivel', type=int)

    def coincide(act):
        fecha_str = str(act.fecha_actividad) if act.fecha_actividad else ''

        return (
            (not tipo_filtro or act.tipo_actividad == tipo_filtro)
            and (not comunidad_id or act.id_comunidad == comunidad_id)
            and (not nivel_id or act.id_nivel == nivel_id)
            and (not desde or (fecha_str and fecha_str >= desde))
            and (not hasta or (fecha_str and fecha_str <= hasta))
        )

    actividades_finales = [a for a in actividades if coincide(a)]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#16a34a'), spaceAfter=4)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#6b7280'), spaceAfter=12)
    
    header_cell_style = ParagraphStyle('HeaderCell', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.whitesmoke)
    body_cell_style = ParagraphStyle('BodyCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, textColor=colors.HexColor('#374151'))
    
    elements.append(Paragraph("Reporte Consolidado de Despliegues y Actividades", title_style))
    elements.append(Paragraph(f"Generado por: {current_user.correo} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    
    headers = [
        Paragraph("ID", header_cell_style),
        Paragraph("Fecha", header_cell_style),
        Paragraph("Área / Tipo", header_cell_style),
        Paragraph("Nombre de la Actividad", header_cell_style),
        Paragraph("Estatus", header_cell_style),
        Paragraph("Técnico Asignado", header_cell_style),
        Paragraph("Comunidad / Ubicación", header_cell_style)
    ]
    
    table_data = [headers]
    
    for act in actividades_finales:
        nombre_act = "Jornada General"
        if act.monitoreo and act.monitoreo.nombre_monitoreo:
            nombre_act = act.monitoreo.nombre_monitoreo
        elif hasattr(act, 'formacion_activa_rel') and act.formacion_activa_rel and hasattr(act.formacion_activa_rel, 'tema_real'):
            nombre_act = act.formacion_activa_rel.tema_real
        elif hasattr(act, 'sensibilizacion_activa_rel') and act.sensibilizacion_activa_rel and hasattr(act.sensibilizacion_activa_rel, 'campana_real'):
            nombre_act = act.sensibilizacion_activa_rel.campana_real
        elif hasattr(act, 'descripcion') and act.descripcion:
            nombre_act = act.descripcion

        ultima_bitacora = BitacoraTransaccion.query.filter_by(modulo='actividades', registro_id=act.id_actividad).order_by(BitacoraTransaccion.id.desc()).first()
        estatus = ultima_bitacora.estado_nuevo if ultima_bitacora and ultima_bitacora.estado_nuevo else 'Completado'

        tecnico_txt = "Sin asignar"
        if act.tecnicos_asociados:
            t = act.tecnicos_asociados[0].tecnico
            tecnico_txt = f"{t.nombres} {t.apellidos}"
        elif hasattr(act, 'formacion_activa_rel') and act.formacion_activa_rel and hasattr(act.formacion_activa_rel, 'tecnico_real'):
            tecnico_txt = act.formacion_activa_rel.tecnico_real
        elif hasattr(act, 'sensibilizacion_activa_rel') and act.sensibilizacion_activa_rel and hasattr(act.sensibilizacion_activa_rel, 'facilitador_real'):
            tecnico_txt = act.sensibilizacion_activa_rel.facilitador_real

        comunidad_txt = act.comunidad.nombre_comunidad if act.comunidad else "Comunidad Central"

        table_data.append([
            Paragraph(f"#{act.id_actividad}", body_cell_style),
            Paragraph(str(act.fecha_actividad) if act.fecha_actividad else 'N/D', body_cell_style),
            Paragraph(str(act.tipo_actividad), body_cell_style),
            Paragraph(nombre_act, body_cell_style),
            Paragraph(estatus, body_cell_style),
            Paragraph(tecnico_txt, body_cell_style),
            Paragraph(comunidad_txt, body_cell_style)
        ])
        
    t = Table(table_data, colWidths=[40, 70, 95, 230, 80, 110, 117])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    
    return Response(buffer, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename=reporte_actividades.pdf'})


# ==============================================================================
# 2. CREATE (NUEVA ACTIVIDAD)
# ==============================================================================
@monitoreo_bp.route('/actividades/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    verificar_permiso_dinamico('registrar_actividades')
    form = ActividadForm()
    _cargar_tecnicos(form)
    
    comunidades = Comunidad.query.order_by(Comunidad.nombre_comunidad.asc()).all()
    niveles = Nivel.query.order_by(Nivel.nombre_nivel.asc()).all()
    
    if request.method == 'POST':
        fecha = request.form.get('fecha', '').strip()
        nombre_actividad = request.form.get('actividad', '').strip()
        area = request.form.get('area', 'MONITOREO').strip()
        
        try:
            id_tecnico = int(form.tecnico_responsable.data or 0)
        except (ValueError, TypeError):
            id_tecnico = 0

        try:
            nombre_actividad = normalize_text(nombre_actividad, max_length=180, field='El nombre de la actividad')
            fecha_actividad = datetime.strptime(fecha, '%Y-%m-%d').date()
            comunidad_id = parse_positive_int(request.form.get('id_comunidad'), field='La comunidad')
            nivel_id = parse_positive_int(request.form.get('id_nivel'), field='El nivel')
            poblacion = int(request.form.get('poblacion', 0) or 0)
            if poblacion < 0 or poblacion > 100000000:
                raise ValueError('La población debe ser un número entre 0 y 100000000.')
        except (ValueError, TypeError):
            flash('Debe completar el nombre de la actividad y la fecha.', 'error')
            return render_template('actividades/formulario.html', form=form, comunidades=comunidades, niveles=niveles)

        try:
            user_id = getattr(current_user, 'id_usuario', None) or getattr(current_user, 'id', 1)

            nueva_actividad = Actividad(
                fecha_actividad=fecha_actividad,
                tipo_actividad=area if area in ['MONITOREO', 'FORMACION', 'SENSIBILIZACION'] else 'MONITOREO',
                id_comunidad=comunidad_id,
                id_nivel=nivel_id,
                id_usuario=user_id,
                descripcion=request.form.get('descripcion', '').strip() or None,
                poblacion=poblacion,
                acuerdos=request.form.get('acuerdos', '').strip() or None,
            )

            minuta_pdf = _guardar_archivo(request.files.get('minuta_archivo'), 'minutas')
            if minuta_pdf:
                nueva_actividad.minuta_archivo = minuta_pdf

            db.session.add(nueva_actividad)
            db.session.flush()

            if id_tecnico > 0:
                db.session.add(ActividadTecnico(id_actividad=nueva_actividad.id_actividad, id_tecnico=id_tecnico))

            if nueva_actividad.tipo_actividad == 'MONITOREO':
                db.session.add(Monitoreo(
                    id_actividad=nueva_actividad.id_actividad, 
                    nombre_monitoreo=nombre_actividad, 
                    tipo_actividad='MONITOREO'
                ))

            for foto in request.files.getlist('fotos_archivos'):
                ruta_foto = _guardar_archivo(foto, 'fotos_actividad')
                if ruta_foto:
                    rutas_fotos = [ruta for ruta in (nueva_actividad.fotos_archivos or '').split(', ') if ruta]
                    rutas_fotos.append(ruta_foto)
                    nueva_actividad.fotos_archivos = ', '.join(rutas_fotos)
                    nueva_img = Imagenes(url_imagen=ruta_foto, nombre_imagen=os.path.basename(ruta_foto), fecha_imagen=datetime.utcnow().date())
                    db.session.add(nueva_img)
                    db.session.flush()
                    db.session.add(ImagenesActividad(id_imagen=nueva_img.id_imagen, id_actividad=nueva_actividad.id_actividad))

            estado_operativo = request.form.get('estado_actividad', 'Planificada')
            db.session.add(BitacoraTransaccion(
                modulo='actividades',
                registro_id=nueva_actividad.id_actividad,
                accion='creacion',
                estado_nuevo=estado_operativo,
                usuario=getattr(current_user, 'nombre_usuario', 'Usuario Activo'),
                detalle=f'Actividad {nueva_actividad.tipo_actividad} registrada en {estado_operativo}'
            ))

            db.session.commit()
            mensaje = f'Se registró la actividad #{nueva_actividad.id_actividad}.'
            ServicioNotificacion.notificar_por_permiso('gestionar_actividades', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Actividades')
            if id_tecnico > 0:
                tecnico = Tecnico.query.get(id_tecnico)
                if tecnico and tecnico.id_usuario:
                    ServicioNotificacion.crear_aviso(id_usuario=tecnico.id_usuario, mensaje=f'Se te asignó la actividad #{nueva_actividad.id_actividad}.', categoria='Actividades')
            flash('Actividad registrada exitosamente.', 'success')
            return redirect(url_for('monitoreo.actividades_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la actividad: {str(e)}', 'error')

    return render_template('actividades/formulario.html', form=form, actividad_obj=None, comunidades=comunidades, niveles=niveles)


# ==============================================================================
# 3. UPDATE (EDITAR ACTIVIDAD - BLINDADO PARA TÍTULOS Y MÓDULOS)
# ==============================================================================
@monitoreo_bp.route('/actividades/<int:actividad_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(actividad_id):
    verificar_permiso_dinamico('editar_actividades')
    actividad_obj = Actividad.query.get_or_404(actividad_id)
    form = ActividadForm()
    _cargar_tecnicos(form)

    comunidades = Comunidad.query.order_by(Comunidad.nombre_comunidad.asc()).all()
    niveles = Nivel.query.order_by(Nivel.nombre_nivel.asc()).all()

    if request.method == 'POST':
        try:
            with db.session.no_autoflush:
                fecha_str = request.form.get('fecha', '').strip()
                if fecha_str:
                    actividad_obj.fecha_actividad = datetime.strptime(fecha_str, '%Y-%m-%d').date()

                area_nueva = request.form.get('area', 'MONITOREO').strip()
                if area_nueva in ['MONITOREO', 'FORMACION', 'SENSIBILIZACION']:
                    actividad_obj.tipo_actividad = area_nueva

                actividad_obj.id_comunidad = int(request.form.get('id_comunidad', 1) or 1)
                actividad_obj.id_nivel = int(request.form.get('id_nivel', 1) or 1)
                actividad_obj.descripcion = request.form.get('descripcion', '').strip() or None
                actividad_obj.poblacion = int(request.form.get('poblacion', 0) or 0)
                if actividad_obj.poblacion < 0 or actividad_obj.poblacion > 100000000:
                    raise ValueError('La población debe ser un número entre 0 y 100000000.')
                actividad_obj.acuerdos = request.form.get('acuerdos', '').strip() or None

                nombre_actividad = request.form.get('actividad', '').strip()
                if nombre_actividad:
                    if actividad_obj.tipo_actividad == 'MONITOREO':
                        if actividad_obj.monitoreo:
                            actividad_obj.monitoreo.nombre_monitoreo = nombre_actividad
                            actividad_obj.monitoreo.tipo_actividad = 'MONITOREO'
                        else:
                            db.session.add(Monitoreo(
                                id_actividad=actividad_obj.id_actividad, 
                                nombre_monitoreo=nombre_actividad, 
                                tipo_actividad='MONITOREO'
                            ))
                    elif actividad_obj.tipo_actividad == 'FORMACION':
                        if hasattr(actividad_obj, 'formacion_activa_rel') and actividad_obj.formacion_activa_rel:
                            tecnico_previo = getattr(actividad_obj.formacion_activa_rel, 'tecnico_real', '')
                            actividad_obj.formacion_activa_rel.nombre_formacion = f"{nombre_actividad}||{tecnico_previo}"
                        else:
                            actividad_obj.descripcion = nombre_actividad
                    elif actividad_obj.tipo_actividad == 'SENSIBILIZACION':
                        if hasattr(actividad_obj, 'sensibilizacion_activa_rel') and actividad_obj.sensibilizacion_activa_rel:
                            facilitador_previo = getattr(actividad_obj.sensibilizacion_activa_rel, 'facilitador_real', '')
                            actividad_obj.sensibilizacion_activa_rel.nombre_sensibilizacion = f"{nombre_actividad}||{facilitador_previo}"
                        else:
                            actividad_obj.descripcion = nombre_actividad

                nueva_minuta = _guardar_archivo(request.files.get('minuta_archivo'), 'minutas')
                if nueva_minuta:
                    actividad_obj.minuta_archivo = nueva_minuta

                try:
                    id_tecnico = int(form.tecnico_responsable.data or 0)
                except (ValueError, TypeError):
                    id_tecnico = 0

                if id_tecnico > 0:
                    ActividadTecnico.query.filter_by(id_actividad=actividad_obj.id_actividad).delete()
                    db.session.add(ActividadTecnico(id_actividad=actividad_obj.id_actividad, id_tecnico=id_tecnico))

                for foto in request.files.getlist('fotos_archivos'):
                    ruta_foto = _guardar_archivo(foto, 'fotos_actividad')
                    if ruta_foto:
                        rutas_fotos = [ruta for ruta in (actividad_obj.fotos_archivos or '').split(', ') if ruta]
                        rutas_fotos.append(ruta_foto)
                        actividad_obj.fotos_archivos = ', '.join(rutas_fotos)
                        nueva_img = Imagenes(url_imagen=ruta_foto, nombre_imagen=os.path.basename(ruta_foto), fecha_imagen=datetime.utcnow().date())
                        db.session.add(nueva_img)
                        db.session.flush()
                        db.session.add(ImagenesActividad(id_imagen=nueva_img.id_imagen, id_actividad=actividad_obj.id_actividad))

                estado_operativo = request.form.get('estado_actividad', 'Planificada')
                db.session.add(BitacoraTransaccion(
                    modulo='actividades',
                    registro_id=actividad_obj.id_actividad,
                    accion='edicion',
                    estado_nuevo=estado_operativo,
                    usuario=getattr(current_user, 'nombre_usuario', 'Usuario Activo'),
                    detalle=f'Actividad {actividad_obj.tipo_actividad} actualizada a {estado_operativo}'
                ))

            db.session.commit()
            mensaje = f'Se actualizó la actividad #{actividad_obj.id_actividad}.'
            ServicioNotificacion.notificar_por_permiso('gestionar_actividades', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Actividades')
            if id_tecnico > 0:
                tecnico = Tecnico.query.get(id_tecnico)
                if tecnico and tecnico.id_usuario:
                    ServicioNotificacion.crear_aviso(id_usuario=tecnico.id_usuario, mensaje=f'Se te asignó la actividad #{actividad_obj.id_actividad}.', categoria='Actividades')
            flash('Actividad actualizada exitosamente.', 'success')
            return redirect(url_for('monitoreo.actividades_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al modificar la actividad: {str(e)}', 'error')

    # PRECARGA EN GET
    if actividad_obj.monitoreo:
        actividad_obj.nombre_formulario = actividad_obj.monitoreo.nombre_monitoreo
    elif hasattr(actividad_obj, 'formacion_activa_rel') and actividad_obj.formacion_activa_rel:
        actividad_obj.nombre_formulario = actividad_obj.formacion_activa_rel.tema_real
    elif hasattr(actividad_obj, 'sensibilizacion_activa_rel') and actividad_obj.sensibilizacion_activa_rel:
        actividad_obj.nombre_formulario = actividad_obj.sensibilizacion_activa_rel.campana_real
    else:
        actividad_obj.nombre_formulario = actividad_obj.descripcion or "Actividad General"

    if actividad_obj.tecnicos_asociados:
        form.tecnico_responsable.data = actividad_obj.tecnicos_asociados[0].id_tecnico

    ultima_bitacora = BitacoraTransaccion.query.filter_by(modulo='actividades', registro_id=actividad_obj.id_actividad).order_by(BitacoraTransaccion.id.desc()).first()
    actividad_obj.estado = ultima_bitacora.estado_nuevo if ultima_bitacora and ultima_bitacora.estado_nuevo else 'Completado'

    if actividad_obj.comunidad and actividad_obj.comunidad.parroquia:
        actividad_obj.parroquia = actividad_obj.comunidad.parroquia.nombre_parroquia
        if actividad_obj.comunidad.parroquia.municipio:
            actividad_obj.municipio = actividad_obj.comunidad.parroquia.municipio.nombre_municipio
            if actividad_obj.comunidad.parroquia.municipio.estado:
                actividad_obj.estado_geo = actividad_obj.comunidad.parroquia.municipio.estado.nombre_estado
            else:
                actividad_obj.estado_geo = 'Lara'
        else:
            actividad_obj.municipio = 'Iribarren'
            actividad_obj.estado_geo = 'Lara'
    else:
        actividad_obj.parroquia = 'Catedral'
        actividad_obj.municipio = 'Iribarren'
        actividad_obj.estado_geo = 'Lara'

    if actividad_obj.imagenes_asociadas:
        actividad_obj.fotos_archivos = ", ".join([img_rel.imagen.url_imagen for img_rel in actividad_obj.imagenes_asociadas])

    return render_template('actividades/formulario.html', form=form, actividad_obj=actividad_obj, comunidades=comunidades, niveles=niveles)


# ==============================================================================
# 4. DELETE (ELIMINAR ACTIVIDAD)
# ==============================================================================
@monitoreo_bp.route('/actividades/<int:actividad_id>/eliminar', methods=['POST'])
@login_required
def eliminar(actividad_id):
    verificar_permiso_dinamico('eliminar_actividades')
    actividad_obj = Actividad.query.get_or_404(actividad_id)

    try:
        db.session.delete(actividad_obj)
        db.session.commit()
        mensaje = f'Se eliminó la actividad #{actividad_id}.'
        ServicioNotificacion.notificar_por_permiso('gestionar_actividades', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Actividades')
        flash('Actividad eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'No se pudo eliminar la actividad: {str(e)}', 'error')

    return redirect(url_for('monitoreo.actividades_index'))


# ==============================================================================
# 5. CAMBIAR ESTADO RÁPIDO
# ==============================================================================
@monitoreo_bp.route('/actividades/<int:actividad_id>/estado', methods=['POST'])
@login_required
def actividades_cambiar_estado(actividad_id):
    verificar_permiso_dinamico('cambiar_estado_actividades')
    flash('Estado actualizado.', 'success')
    return redirect(url_for('monitoreo.actividades_index'))