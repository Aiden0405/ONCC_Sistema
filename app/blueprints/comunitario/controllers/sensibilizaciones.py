from datetime import datetime

from flask import flash, redirect, render_template, request, url_for

from flask_login import login_required, current_user

from app import db
from app.blueprints.comunitario import comunitario_bp
from app.blueprints.comunitario.forms import SensibilizacionForm
from app.models.esquema_activo import (
    ActividadActiva as Actividad,
    NivelActivo as Nivel,
    SensibilizacionActiva as Sensibilizacion,
    ComunidadActiva as Comunidad
)

# ==========================================
# 1. LISTAR Y REGISTRAR (GET y POST)
# ==========================================

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
            tipo_institucion='Comunitaria',
            direccion_exacta='Sin dirección registrada',
            numero_contacto='Sin contacto',
            correo_electronico='sin-correo@oncc.local',
        )
        db.session.add(institucion)
        db.session.flush()

    return comunidad, nivel, institucion


@comunitario_bp.route('/sensibilizaciones', methods=['GET', 'POST'])
@login_required
def sensibilizaciones_index():
    form = SensibilizacionForm()

    # Cargar menús desplegables
    comunidades = Comunidad.query.all()
    form.id_comunidad.choices = [(c.id_comunidad, c.nombre_comunidad) for c in comunidades]
    
    niveles = Nivel.query.all()
    form.id_nivel.choices = [(niv.id_nivel, niv.nombre_nivel) for niv in niveles]

    # CLICK EN "REGISTRAR"
    if form.validate_on_submit():
        try:
            # 1. Registrar fila en la tabla 'actividad' (Padre)
            nueva_actividad = Actividad(
                fecha_actividad=form.fecha.data,
                tipo_actividad=['sensibilizacion'],
                id_comunidad=form.id_comunidad.data,
                id_nivel=form.id_nivel.data
            )
            db.session.add(nueva_actividad)
            db.session.flush() # Genera la id_actividad automáticamente

            # Consolidamos el nombre con el vocero usando tu formato original "||"
            campana_consolidada = f"{form.nombre_sensibilizacion.data}||{form.vocero.data}"

            # 2. Registrar en la tabla 'sensibilizacion' (Hijo)
            nueva_sensibilizacion = Sensibilizacion(
                nombre_sensibilizacion=campana_consolidada,
                id_actividad=nueva_actividad.id_actividad
            )
            db.session.add(nueva_sensibilizacion)
            
            db.session.commit()
            flash('Taller de sensibilización registrado con éxito.', 'success')
            return redirect(url_for('comunitario.sensibilizaciones_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la sensibilización: {str(e)}', 'error')

    # 4. CONSULTA CON JOINs - LISTAR HISTORIAL
    historial = db.session.query(
        Sensibilizacion.id_sensibilizacion,
        Sensibilizacion.nombre_sensibilizacion,
        Comunidad.nombre_comunidad,
        Actividad.fecha_actividad,
        Sensibilizacion.id_actividad,
        Actividad.id_nivel,
        Actividad.id_comunidad
    ).join(Actividad, Sensibilizacion.id_actividad == Actividad.id_actividad)\
     .join(Comunidad, Actividad.id_comunidad == Comunidad.id_comunidad)\
     .order_by(Sensibilizacion.id_sensibilizacion.desc()).all()

    # Procesar la lista para separar la campaña del vocero de forma limpia
    sensibilizaciones_procesadas = []
    for item in historial:
        if "||" in item.nombre_sensibilizacion:
            campana, vocero = item.nombre_sensibilizacion.split("||", 1)
        else:
            campana = item.nombre_sensibilizacion
            vocero = "No asignado"
        
        sensibilizaciones_procesadas.append({
            'id_sensibilizacion': item.id_sensibilizacion,
            'campana': campana,
            'vocero': vocero,
            'nombre_comunidad': item.nombre_comunidad,
            'fecha_actividad': item.fecha_actividad,
            'id_actividad': item.id_actividad,
            'id_nivel': item.id_nivel,
            'id_comunidad': item.id_comunidad
        })

    return render_template(
        'sensibilizaciones/index.html', 
        form=form, 
        sensibilizaciones=sensibilizaciones_procesadas
    )

# ==========================================
# 2. MODIFICAR / ACTUALIZAR (POST)
# ==========================================
@comunitario_bp.route('/sensibilizaciones/editar/<int:id_sensibilizacion>', methods=['POST'])
@login_required
def sensibilizacion_editar(id_sensibilizacion):
    if current_user.id_rol not in [1, 2]: 
        flash('No tienes permisos para modificar registros de sensibilización.', 'error')
        return redirect(url_for('comunitario.sensibilizaciones_index'))

    sensibilizacion = Sensibilizacion.query.get_or_404(id_sensibilizacion)
    actividad = Actividad.query.get(sensibilizacion.id_actividad)

    campana_nueva = request.form.get('edit_nombre_sensibilizacion')
    vocero_nuevo = request.form.get('edit_vocero')
    fecha_nueva = request.form.get('edit_fecha')
    id_comunidad_nueva = request.form.get('edit_id_comunidad')
    id_nivel_nuevo = request.form.get('edit_id_nivel')

    try:
        if fecha_nueva:
            actividad.fecha_actividad = datetime.strptime(fecha_nueva, '%Y-%m-%d').date()
        if id_nivel_nuevo:
            actividad.id_nivel = int(id_nivel_nuevo)
        if id_comunidad_nueva:
            actividad.id_comunidad = int(id_comunidad_nueva)

        sensibilizacion.nombre_sensibilizacion = f"{campana_nueva}||{vocero_nuevo}"

        db.session.commit()
        flash('Sensibilización actualizada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al modificar: {str(e)}', 'error')

    return redirect(url_for('comunitario.sensibilizaciones_index'))

# ==========================================
# 3. ELIMINAR (POST)
# ==========================================
@comunitario_bp.route('/sensibilizaciones/eliminar/<int:id_sensibilizacion>', methods=['POST'])
@login_required
def sensibilizacion_eliminar(id_sensibilizacion):
    if current_user.id_rol not in [1, 2]:
        flash('No tienes permisos para eliminar registros de sensibilización.', 'error')
        return redirect(url_for('comunitario.sensibilizaciones_index'))

    sensibilizacion = Sensibilizacion.query.get_or_404(id_sensibilizacion)
    actividad = Actividad.query.get(sensibilizacion.id_actividad)

    try:
        db.session.delete(sensibilizacion)
        if actividad:
            db.session.delete(actividad)
            
        db.session.commit()
        flash('Sensibilización eliminada del historial.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'error')

    return redirect(url_for('comunitario.sensibilizaciones_index'))

# Compatibilidad con rutas adicionales si se requieren
@comunitario_bp.route('/sensibilizaciones/nuevo', methods=['POST'])
@login_required
def sensibilizacion_nuevo():
    return redirect(url_for('comunitario.sensibilizaciones_index'))

# ==========================================
# 4. CAMBIO DE ESTADO (Manejado por app.add_url_rule)
# ==========================================
@login_required
def sensibilizacion_cambiar_estado(sensibilizacion_id):
    """
    Controlador para cambiar el estado de una sensibilización.
    Mapeado manualmente en la línea 137 de app/__init__.py
    """
    flash('Funcionalidad de cambio de estado en desarrollo.', 'info')
    return redirect(url_for('comunitario.sensibilizaciones_index'))