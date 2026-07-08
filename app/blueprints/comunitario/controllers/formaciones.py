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
    # 1. Estado
    estado = EstadoActivo.query.filter_by(nombre_estado='Lara').first()
    if not estado:
        estado = EstadoActivo(nombre_estado='Lara')
        db.session.add(estado)
        db.session.flush()

    # 2. Municipio
    municipio = MunicipioActivo.query.filter_by(nombre_municipio='Iribarren', id_estado=estado.id_estado).first()
    if not municipio:
        municipio = MunicipioActivo(id_estado=estado.id_estado, nombre_municipio='Iribarren')
        db.session.add(municipio)
        db.session.flush()

    # 3. Parroquia
    parroquia = ParroquiaActiva.query.filter_by(nombre_parroquia='Catedral', id_municipio=municipio.id_municipio).first()
    if not parroquia:
        parroquia = ParroquiaActiva(id_municipio=municipio.id_municipio, nombre_parroquia='Catedral')
        db.session.add(parroquia)
        db.session.flush()

    # 4. Comunidad (¡Aquí definimos la variable que te estaba faltando!)
    comunidad = ComunidadActiva.query.filter_by(nombre_comunidad='Comunidad General', id_parroquia=parroquia.id_parroquia).first()
    if not comunidad:
        comunidad = ComunidadActiva(id_parroquia=parroquia.id_parroquia, nombre_comunidad='Comunidad General')
        db.session.add(comunidad)
        db.session.flush()

    # 5. Nivel
    nivel = NivelActivo.query.filter_by(nombre_nivel='Base').first()
    if not nivel:
        nivel = NivelActivo(nombre_nivel='Base', descripcion='Nivel base para registros iniciales')
        db.session.add(nivel)
        db.session.flush()

    # 6. Institución (Ahora sí conoce a 'comunidad')
    institucion = InstitucionActiva.query.filter(
        InstitucionActiva.nombre_institucion.ilike('%Institucion%'), 
        InstitucionActiva.id_comunidad == comunidad.id_comunidad
    ).first()

    if not institucion:
        institucion = InstitucionActiva(
            id_comunidad=comunidad.id_comunidad,
            nombre_institucion='Institución General',
            tipo_institucion='Comunitaria',
            direccion_exacta='Sin dirección registrada',
            numero_contacto='Sin contacto',
            correo_electronico='sin-correo@oncc.local',
        )
        db.session.add(institucion)
        db.session.flush()
        
    db.session.commit() # Guardamos todo al final
    return comunidad, nivel, institucion


@comunitario_bp.route('/formaciones')
def formaciones_index():
    _asegurar_territorio_base()
    
    # 🌟 QUERY CON JOIN: Une las tablas físicamente para alimentar las columnas exactas del HTML
    formaciones_con_cruces = db.session.query(
        FormacionActiva.id_formacion.label('id_formacion'),
        FormacionActiva.nombre_formacion.label('nombre_formacion'),
        FormacionActiva.id_actividad.label('id_actividad'),
        InstitucionActiva.nombre_institucion.label('nombre_institucion'),
        ActividadActiva.fecha_actividad.label('fecha_actividad'),
        ComunidadActiva.nombre_comunidad.label('nombre_comunidad')
    ).join(ActividadActiva, FormacionActiva.id_actividad == ActividadActiva.id_actividad)\
     .join(InstitucionActiva, FormacionActiva.id_institucion == InstitucionActiva.id_institucion)\
     .join(ComunidadActiva, ActividadActiva.id_comunidad == ComunidadActiva.id_comunidad)\
     .order_by(FormacionActiva.id_formacion.desc()).all()

    # 🌟 Cargamos los datos para los selectores del formulario superior
    actividades = ActividadActiva.query.all()
    instituciones = InstitucionActiva.query.all()

    return render_template(
        'formaciones/index.html', 
        formaciones=formaciones_con_cruces, 
        actividades_disponibles=actividades,
        instituciones_disponibles=instituciones,
        estados_flujo=['registrada']
    )


@comunitario_bp.route('/formaciones/nuevo', methods=['POST'])
def formacion_nuevo():
    # 🌟 Captura los campos exactos enviados por el formulario HTML nuevo
    tema = (request.form.get('nombre_formacion') or '').strip()
    actividad_id = request.form.get('id_actividad')
    institucion_id = request.form.get('id_institucion')

    if not tema or not actividad_id or not institucion_id:
        flash('Todos los campos del formulario son estrictamente obligatorios.', 'error')
        return redirect(url_for('comunitario.formaciones_index'))

    try:
        # Registra la formación amarrándola de manera segura a las llaves foráneas de la base de datos
        nueva_formacion = FormacionActiva(
            nombre_formacion=tema,
            id_actividad=int(actividad_id),
            id_institucion=int(institucion_id)
        )
        db.session.add(nueva_formacion)
        db.session.commit()
        flash('Jornada de formación registrada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar en la base de datos: {str(e)}', 'error')

    return redirect(url_for('comunitario.formaciones_index'))


@comunitario_bp.route('/formaciones/<int:formacion_id>/estado', methods=['POST'])
def formacion_cambiar_estado(formacion_id):
    flash('El esquema entregado no guarda un estado persistente para formaciones.', 'info')
    return redirect(url_for('comunitario.formaciones_index'))