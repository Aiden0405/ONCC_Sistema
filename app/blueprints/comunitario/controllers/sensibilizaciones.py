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

            # Consolidamos el nombre con el facilitador usando tu formato original "||"
            campana_consolidada = f"{form.nombre_sensibilizacion.data}||{form.facilitador.data}"

            # 2. Registrar en la tabla 'sensibilizacion' (Hijo)
            nueva_sensibilizacion = Sensibilizacion(
                nombre_sensivilizacion=campana_consolidada,
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
        Sensibilizacion.nombre_sensivilizacion,
        Comunidad.nombre_comunidad,
        Actividad.fecha_actividad,
        Sensibilizacion.id_actividad,
        Actividad.id_nivel,
        Actividad.id_comunidad
    ).join(Actividad, Sensibilizacion.id_actividad == Actividad.id_actividad)\
     .join(Comunidad, Actividad.id_comunidad == Comunidad.id_comunidad)\
     .order_by(Sensibilizacion.id_sensibilizacion.desc()).all()

    # Procesar la lista para separar la campaña del facilitador de forma limpia
    sensibilizaciones_procesadas = []
    for item in historial:
        if "||" in item.nombre_sensivilizacion:
            campana, facilitador = item.nombre_sensivilizacion.split("||", 1)
        else:
            campana = item.nombre_sensivilizacion
            facilitador = "No asignado"
        
        sensibilizaciones_procesadas.append({
            'id_sensibilizacion': item.id_sensibilizacion,
            'campana': campana,
            'facilitador': facilitador,
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
    facilitador_nuevo = request.form.get('edit_facilitador') # <-- Cambiado para coincidir con el name del modal HTML
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

        # Usamos la variable correcta corregida
        sensibilizacion.nombre_sensivilizacion = f"{campana_nueva}||{facilitador_nuevo}"

        db.session.commit()
        flash('Sensibilización actualizada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al modificar: {str(e)}', 'error')

    # Como las registraste mediante add_url_rule con el endpoint 'sensibilizacion.index'
    return redirect(url_for('sensibilizacion.index'))

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