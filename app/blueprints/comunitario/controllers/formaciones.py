from datetime import datetime

from flask import flash, redirect, render_template, request, url_for

from app import db
from app.blueprints.comunitario import comunitario_bp
from app.models.esquema_activo import (
    ActividadActiva,
    ComunidadActiva,
    EstadoActivo,
    FormacionActiva,
    InstitucionActiva,
    MunicipioActivo,
    NivelActivo,
    ParroquiaActiva,
)


def _asegurar_territorio_base():
    estado = EstadoActivo.query.filter_by(nombre_estado='Lara').first()
    if not estado:
        estado = EstadoActivo(nombre_estado='Lara')
        db.session.add(estado)
        db.session.flush()

    municipio = MunicipioActivo.query.filter_by(nombre_municipio='Iribarren', id_estado=estado.id_estado).first()
    if not municipio:
        municipio = MunicipioActivo(id_estado=estado.id_estado, nombre_municipio='Iribarren')
        db.session.add(municipio)
        db.session.flush()

    parroquia = ParroquiaActiva.query.filter_by(nombre_parroquia='Catedral', id_municipio=municipio.id_municipio).first()
    if not parroquia:
        parroquia = ParroquiaActiva(id_municipio=municipio.id_municipio, nombre_parroquia='Catedral')
        db.session.add(parroquia)
        db.session.flush()

    comunidad = ComunidadActiva.query.filter_by(nombre_comunidad='Comunidad General', id_parroquia=parroquia.id_parroquia).first()
    if not comunidad:
        comunidad = ComunidadActiva(id_parroquia=parroquia.id_parroquia, nombre_comunidad='Comunidad General')
        db.session.add(comunidad)
        db.session.flush()

    nivel = NivelActivo.query.filter_by(nombre_nivel='Base').first()
    if not nivel:
        nivel = NivelActivo(nombre_nivel='Base', descripcion='Nivel base para registros iniciales')
        db.session.add(nivel)
        db.session.flush()

    institucion = InstitucionActiva.query.filter_by(nombre_institucion='Institución General', id_comunidad=comunidad.id_comunidad).first()
    if not institucion:
        institucion = InstitucionActiva(
            id_comunidad=comunidad.id_comunidad,
            nombre_institucion='Institución General',
            tipo_intitucion='Comunitaria',
            direccion_exacta='Sin dirección registrada',
            numero_contacto='Sin contacto',
            correo_electronico='sin-correo@oncc.local',
        )
        db.session.add(institucion)
        db.session.flush()

    return comunidad, nivel, institucion


@comunitario_bp.route('/formaciones')
def formaciones_index():
    _asegurar_territorio_base()
    formaciones = FormacionActiva.query.order_by(FormacionActiva.id_formacion.desc()).all()
    return render_template('formaciones/index.html', formaciones=formaciones, estados_flujo=['registrada'])


@comunitario_bp.route('/formaciones/nuevo', methods=['POST'])
def formacion_nuevo():
    tema = (request.form.get('tema') or '').strip()
    comunidad_nombre = (request.form.get('comunidad') or 'Comunidad General').strip()
    fecha = request.form.get('fecha')

    if not tema or not fecha:
        flash('Tema y fecha son obligatorios.', 'error')
        return redirect(url_for('formacion.index'))

    comunidad, nivel, institucion = _asegurar_territorio_base()
    if comunidad_nombre and comunidad_nombre != comunidad.nombre_comunidad:
        comunidad = ComunidadActiva.query.filter_by(nombre_comunidad=comunidad_nombre, id_parroquia=comunidad.id_parroquia).first()
        if not comunidad:
            comunidad = ComunidadActiva(id_parroquia=comunidad.id_parroquia, nombre_comunidad=comunidad_nombre)
            db.session.add(comunidad)
            db.session.flush()

    actividad = ActividadActiva(
        fecha_actividad=datetime.strptime(fecha, '%Y-%m-%d').date(),
        tipo_actividad=['formacion'],
        id_comunidad=comunidad.id_comunidad,
        id_nivel=nivel.id_nivel,
    )
    db.session.add(actividad)
    db.session.flush()

    formacion = FormacionActiva(
        nombre_formacion=tema,
        id_actividad=actividad.id_actividad,
        id_institucion=institucion.id_institucion,
    )
    db.session.add(formacion)
    db.session.commit()

    flash('Formación registrada correctamente.', 'success')
    return redirect(url_for('formacion.index'))


@comunitario_bp.route('/formaciones/<int:formacion_id>/estado', methods=['POST'])
def formacion_cambiar_estado(formacion_id):
    flash('El esquema entregado no guarda un estado persistente para formaciones.', 'info')
    return redirect(url_for('formacion.index'))