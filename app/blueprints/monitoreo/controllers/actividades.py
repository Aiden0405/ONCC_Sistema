import os
from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.blueprints.monitoreo import monitoreo_bp
from app.constants import ESTADOS_ACTIVIDAD
from app.models.actividad import ActividadLegacy as Actividad
from app.models.bitacora import BitacoraTransaccion


def _guardar_archivo(archivo, carpeta):
    if not archivo or not archivo.filename:
        return None

    nombre_archivo = secure_filename(archivo.filename)
    destino = os.path.join(current_app.root_path, 'static', 'uploads', carpeta)
    os.makedirs(destino, exist_ok=True)
    ruta_completa = os.path.join(destino, nombre_archivo)
    archivo.save(ruta_completa)
    return os.path.join('uploads', carpeta, nombre_archivo).replace('\\', '/')


@monitoreo_bp.route('/actividades/')
@login_required
def actividades_index():
    actividades = Actividad.query.order_by(Actividad.fecha.desc(), Actividad.creado_en.desc()).all()
    return render_template('actividades/index.html', actividades=actividades, estados_actividad=ESTADOS_ACTIVIDAD)


@monitoreo_bp.route('/actividades/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        fecha = request.form.get('fecha', '').strip()
        actividad = request.form.get('actividad', '').strip()
        area = request.form.get('area', '').strip()

        if not fecha or not actividad or not area:
            flash('Debe completar area, actividad y fecha.', 'error')
            return redirect(url_for('actividad.nueva'))

        minuta_archivo = _guardar_archivo(request.files.get('minuta_archivo'), 'minutas')

        fotos_guardadas = []
        for foto in request.files.getlist('fotos_archivos'):
            ruta_foto = _guardar_archivo(foto, 'fotos_actividad')
            if ruta_foto:
                fotos_guardadas.append(ruta_foto)

        nueva_actividad = Actividad(
            area=area,
            actividad=actividad,
            responsable=request.form.get('responsable', '').strip() or current_user.nombre,
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
            estado=request.form.get('estado_actividad', 'Planificada').strip(),
            estado_geo=request.form.get('estado_geo', 'Lara').strip(),
            municipio=request.form.get('municipio', 'Sin municipio').strip(),
            parroquia=request.form.get('parroquia', '').strip() or None,
            descripcion=request.form.get('descripcion', '').strip() or None,
            poblacion=int(request.form.get('poblacion', 0) or 0),
            acuerdos=request.form.get('acuerdos', '').strip() or None,
            minuta_archivo=minuta_archivo,
            fotos_archivos=', '.join(fotos_guardadas) if fotos_guardadas else None,
        )
        db.session.add(nueva_actividad)
        db.session.flush()
        db.session.add(BitacoraTransaccion(
            modulo='actividades',
            registro_id=nueva_actividad.id,
            accion='creacion',
            estado_nuevo=nueva_actividad.estado,
            usuario=current_user.nombre,
            detalle=f'Actividad {nueva_actividad.actividad} registrada',
        ))
        db.session.commit()

        flash('Actividad registrada exitosamente.', 'success')
        return redirect(url_for('actividad.index'))

    return render_template('actividades/formulario.html')


@monitoreo_bp.route('/actividades/<int:actividad_id>/estado', methods=['POST'])
@login_required
def actividades_cambiar_estado(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    nuevo_estado = request.form.get('estado', '').strip()

    if nuevo_estado not in ESTADOS_ACTIVIDAD:
        flash('Estado de actividad invalido.', 'error')
        return redirect(url_for('actividad.index'))

    actividad.estado = nuevo_estado
    db.session.add(BitacoraTransaccion(
        modulo='actividades',
        registro_id=actividad.id,
        accion='cambio_estado',
        estado_nuevo=nuevo_estado,
        usuario=current_user.nombre,
        detalle=f'Actividad {actividad.actividad} paso a {nuevo_estado}',
    ))
    db.session.commit()

    flash('Estado de la actividad actualizado.', 'success')
    return redirect(url_for('actividad.index'))