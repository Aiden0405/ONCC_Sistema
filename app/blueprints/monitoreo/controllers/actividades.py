import os
from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

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


def _guardar_archivo(archivo, carpeta):
    if not archivo or not archivo.filename:
        return None

    nombre_archivo = secure_filename(archivo.filename)
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


# 1. READ (HISTORIAL DE ACTIVIDADES)
@monitoreo_bp.route('/actividades/')
@login_required
def actividades_index():
    verificar_permiso_dinamico('gestionar_actividades')
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

    return render_template('actividades/index.html', actividades=actividades, estados_actividad=ESTADOS_ACTIVIDAD)


# 2. CREATE (NUEVA ACTIVIDAD - RESPETANDO CHECK CONSTRAINT)
@monitoreo_bp.route('/actividades/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    verificar_permiso_dinamico('gestionar_actividades')
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

        if not fecha or not nombre_actividad:
            flash('Debe completar el nombre de la actividad y la fecha.', 'error')
            return render_template('actividades/formulario.html', form=form, comunidades=comunidades, niveles=niveles)

        try:
            user_id = getattr(current_user, 'id_usuario', None) or getattr(current_user, 'id', 1)

            nueva_actividad = Actividad(
                fecha_actividad=datetime.strptime(fecha, '%Y-%m-%d').date(),
                tipo_actividad=area if area in ['MONITOREO', 'FORMACION', 'SENSIBILIZACION'] else 'MONITOREO',
                id_comunidad=int(request.form.get('id_comunidad', 1) or 1),
                id_nivel=int(request.form.get('id_nivel', 1) or 1),
                id_usuario=user_id,
                descripcion=request.form.get('descripcion', '').strip() or None,
                poblacion=int(request.form.get('poblacion', 0) or 0),
                acuerdos=request.form.get('acuerdos', '').strip() or None
            )

            minuta_pdf = _guardar_archivo(request.files.get('minuta_archivo'), 'minutas')
            if minuta_pdf:
                nueva_actividad.minuta_archivo = minuta_pdf

            db.session.add(nueva_actividad)
            db.session.flush()

            if id_tecnico > 0:
                db.session.add(ActividadTecnico(id_actividad=nueva_actividad.id_actividad, id_tecnico=id_tecnico))

            # 🌟 SOLO INSERTAR EN MONITOREO CON TIPO 'MONITOREO' PARA EVITAR CHK_SOLO_MONITOREO
            if nueva_actividad.tipo_actividad == 'MONITOREO':
                db.session.add(Monitoreo(
                    id_actividad=nueva_actividad.id_actividad, 
                    nombre_monitoreo=nombre_actividad, 
                    tipo_actividad='MONITOREO'
                ))

            for foto in request.files.getlist('fotos_archivos'):
                ruta_foto = _guardar_archivo(foto, 'fotos_actividad')
                if ruta_foto:
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
            flash('Actividad registrada exitosamente.', 'success')
            return redirect(url_for('monitoreo.actividades_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la actividad: {str(e)}', 'error')

    return render_template('actividades/formulario.html', form=form, actividad_obj=None, comunidades=comunidades, niveles=niveles)


# 3. UPDATE (EDITAR ACTIVIDAD)
@monitoreo_bp.route('/actividades/<int:actividad_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(actividad_id):
    verificar_permiso_dinamico('gestionar_actividades')
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

                    if hasattr(actividad_obj, 'formacion_activa_rel') and actividad_obj.formacion_activa_rel:
                        tecnico_previo = actividad_obj.formacion_activa_rel.tecnico_real
                        actividad_obj.formacion_activa_rel.nombre_formacion = f"{nombre_actividad}||{tecnico_previo}"

                    if hasattr(actividad_obj, 'sensibilizacion_activa_rel') and actividad_obj.sensibilizacion_activa_rel:
                        facilitador_previo = actividad_obj.sensibilizacion_activa_rel.facilitador_real
                        actividad_obj.sensibilizacion_activa_rel.nombre_sensibilizacion = f"{nombre_actividad}||{facilitador_previo}"

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


# 4. DELETE (ELIMINAR ACTIVIDAD)
@monitoreo_bp.route('/actividades/<int:actividad_id>/eliminar', methods=['POST'])
@login_required
def eliminar(actividad_id):
    verificar_permiso_dinamico('gestionar_actividades')
    actividad_obj = Actividad.query.get_or_404(actividad_id)

    try:
        db.session.delete(actividad_obj)
        db.session.commit()
        flash('Actividad eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'No se pudo eliminar la actividad: {str(e)}', 'error')

    return redirect(url_for('monitoreo.actividades_index'))


# 5. CAMBIAR ESTADO RÁPIDO
@monitoreo_bp.route('/actividades/<int:actividad_id>/estado', methods=['POST'])
@login_required
def actividades_cambiar_estado(actividad_id):
    verificar_permiso_dinamico('gestionar_actividades')
    flash('Estado actualizado.', 'success')
    return redirect(url_for('monitoreo.actividades_index'))