from datetime import datetime

from flask import flash, redirect, render_template, request, url_for

from app import db
from app.blueprints.comunitario import comunitario_bp
from app.models.actividad import Actividad as ActividadActiva
from app.models.esquema_activo import (
    ComunidadActiva,
    EstadoActivo,
    InstitucionActiva,
    NivelActivo,
    ParroquiaActiva,
    SensibilizacionActiva,
    MunicipioActivo,
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


@comunitario_bp.route('/sensibilizaciones')
def sensibilizaciones_index():
    _asegurar_territorio_base()
    sensibilizaciones = SensibilizacionActiva.query.order_by(SensibilizacionActiva.id_sensivilizacion.desc()).all()
    return render_template('sensibilizaciones/index.html', sensibilizaciones=sensibilizaciones, estados_flujo=['registrada'])


@comunitario_bp.route('/sensibilizaciones/nuevo', methods=['POST'])
def sensibilizacion_nuevo():
    campana = (request.form.get('campana') or '').strip()
    territorio_nombre = (request.form.get('territorio') or 'Comunidad General').strip()
    fecha = request.form.get('fecha')

    if not campana or not fecha:
        flash('Campaña y fecha son obligatorias.', 'error')
        return redirect(url_for('sensibilizacion.index'))

    comunidad, nivel, _ = _asegurar_territorio_base()
    if territorio_nombre and territorio_nombre != comunidad.nombre_comunidad:
        comunidad = ComunidadActiva.query.filter_by(nombre_comunidad=territorio_nombre, id_parroquia=comunidad.id_parroquia).first()
        if not comunidad:
            comunidad = ComunidadActiva(id_parroquia=comunidad.id_parroquia, nombre_comunidad=territorio_nombre)
            db.session.add(comunidad)
            db.session.flush()

    actividad = ActividadActiva(
        fecha_actividad=datetime.strptime(fecha, '%Y-%m-%d').date(),
        tipo_actividad=['sensibilizacion'],
        id_comunidad=comunidad.id_comunidad,
        id_nivel=nivel.id_nivel,
    )
    db.session.add(actividad)
    db.session.flush()

    sensibilizacion = SensibilizacionActiva(
        nombre_sensibilizacion=campana,
        id_actividad=actividad.id_actividad,
    )
    db.session.add(sensibilizacion)
    db.session.commit()

    flash('Sensibilización registrada correctamente.', 'success')
    return redirect(url_for('sensibilizacion.index'))


@comunitario_bp.route('/sensibilizaciones/<int:sensibilizacion_id>/estado', methods=['POST'])
def sensibilizacion_cambiar_estado(sensibilizacion_id):
    flash('El esquema entregado no guarda un estado persistente para sensibilizaciones.', 'info')
    return redirect(url_for('sensibilizacion.index'))