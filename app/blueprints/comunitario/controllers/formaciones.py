# app/blueprints/comunitario/controllers/formaciones.py
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app import db
from app.blueprints.comunitario import comunitario_bp
from app.blueprints.comunitario.forms import FormacionForm
# 🌟 Importamos tu validador de seguridad dinámico del Core
from app.blueprints.core.controllers.roles import verificar_permiso_dinamico
from app.models.esquema_activo import (
    NivelActivo as Nivel,
    InstitucionActiva as Institucion,
    ComunidadActiva as Comunidad
)
from app.models.actividad import Actividad
from app.models.esquema_activo import FormacionActiva as Formacion

# ==========================================
# 1. LISTAR Y REGISTRAR (GET y POST)
# ==========================================
@comunitario_bp.route('/formaciones', methods=['GET', 'POST'])
@login_required  
def formaciones_index():
    # 🛡️ Blindaje Dinámico Ajustado al Slug de la Base de Datos
    verificar_permiso_dinamico('gestionar_formaciones')

    # 1. Instanciamos el formulario de Flask-WTF
    form = FormacionForm()

    # 2. MENÚS DESPLEGABLES (Se cargan dinámicamente)
    instituciones = Institucion.query.all()
    form.id_institucion.choices = [(inst.id_institucion, inst.nombre_institucion) for inst in instituciones]
    
    niveles = Nivel.query.all()
    form.id_nivel.choices = [(niv.id_nivel, niv.nombre_nivel) for niv in niveles]

    # 3. CLICK EN "REGISTRAR" (Validación segura con Flask-WTF)
    if form.validate_on_submit():
        try:
            # Buscamos la institución seleccionada para heredar su comunidad
            institucion_seleccionada = Institucion.query.get(form.id_institucion.data)
            id_comunidad_asignada = institucion_seleccionada.id_comunidad if institucion_seleccionada else 1
            
            # Registramos primero la fila en la tabla 'actividad' (Padre).
            nueva_actividad = Actividad(
                fecha_actividad=form.fecha.data,
                tipo_actividad=['formacion'],
                id_comunidad=id_comunidad_asignada,
                id_nivel=form.id_nivel.data
            )
            db.session.add(nueva_actividad)
            db.session.flush()  # Genera el id_actividad automáticamente

            # Formateamos el string compuesto (Lógica de negocio permitida temporalmente)
            tema_consolidado = f"{form.nombre_formacion.data}||{form.tecnico.data}"

            # Registramos la formación usando el ID generado 
            nueva_formacion = Formacion(
                nombre_formacion=tema_consolidado,
                id_institucion=form.id_institucion.data,
                id_actividad=nueva_actividad.id_actividad
            )
            db.session.add(nueva_formacion)
            
            db.session.commit()
            flash('Formación registrada con éxito.', 'success')
            return redirect(url_for('comunitario.formaciones_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la formación: {str(e)}', 'error')

    # 4. LISTAR HISTORIAL (Aquí se cumple el MVC: la consulta compleja la hace el Modelo)
    formaciones_procesadas = Formacion.obtener_historial_completo()

    # 5. RENDERIZAR LA VISTA
    return render_template(
        'formaciones/index.html', 
        form=form, 
        formaciones=formaciones_procesadas
    )


# ==========================================
# 2. MODIFICAR / ACTUALIZAR (POST)
# ==========================================
@comunitario_bp.route('/formaciones/editar/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_editar(id_formacion):
    # 🛡️ Blindaje Dinámico Ajustado al Slug de la Base de Datos
    verificar_permiso_dinamico('gestionar_formaciones')

    formacion = Formacion.query.get_or_404(id_formacion)
    actividad = Actividad.query.get(formacion.id_actividad)

    tema_nuevo = request.form.get('edit_nombre_formacion')
    tecnico_nuevo = request.form.get('edit_tecnico')
    fecha_nueva = request.form.get('edit_fecha')
    id_inst_nueva = request.form.get('edit_id_institucion')
    id_nivel_nuevo = request.form.get('edit_id_nivel')

    try:
        if fecha_nueva:
            actividad.fecha_actividad = datetime.strptime(fecha_nueva, '%Y-%m-%d').date()
        if id_nivel_nuevo:
            actividad.id_nivel = int(id_nivel_nuevo)

        formacion.nombre_formacion = f"{tema_nuevo}||{tecnico_nuevo}"
        if id_inst_nueva:
            formacion.id_institucion = int(id_inst_nueva)

        db.session.commit()
        flash('Formación actualizada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al modificar: {str(e)}', 'error')

    return redirect(url_for('comunitario.formaciones_index'))


# ==========================================
# 3. ELIMINAR (POST)
# ==========================================
@comunitario_bp.route('/formaciones/eliminar/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_eliminar(id_formacion):
    # 🛡️ Blindaje Dinámico Ajustado al Slug de la Base de Datos
    verificar_permiso_dinamico('gestionar_formaciones')
 
    formacion = Formacion.query.get_or_404(id_formacion)
    actividad = Actividad.query.get(formacion.id_actividad)

    try:
        db.session.delete(formacion)
        if actividad:
            db.session.delete(actividad)
            
        db.session.commit()
        flash('Formación eliminada del historial.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'error')

    return redirect(url_for('comunitario.formaciones_index'))


# ==========================================
# 4. CAMBIAR ESTADO (Compatibilidad)
# ==========================================
@comunitario_bp.route('/formaciones/cambiar_estado/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_cambiar_estado(id_formacion):
    # 🛡️ Blindaje Dinámico Ajustado al Slug de la Base de Datos
    verificar_permiso_dinamico('gestionar_formaciones')
        
    try:
        flash('Estado de la formación actualizado (Simulado).', 'success')
    except Exception as e:
        flash(f'Error al cambiar estado: {str(e)}', 'error')
        
    return redirect(url_for('comunitario.formaciones_index'))


# ==========================================
# 5. RUTA NUEVO (Compatibilidad)
# ==========================================
@comunitario_bp.route('/formaciones/nuevo', methods=['POST'])
@login_required
def formacion_nuevo():
    # 🛡️ Blindaje Dinámico Ajustado al Slug de la Base de Datos
    verificar_permiso_dinamico('gestionar_formaciones')
    return redirect(url_for('comunitario.formaciones_index'))