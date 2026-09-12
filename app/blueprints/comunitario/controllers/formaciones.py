# app/blueprints/comunitario/controllers/formaciones.py
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app import db
from app.blueprints.comunitario import comunitario_bp
from app.blueprints.comunitario.forms import FormacionForm, SensibilizacionForm
# 🌟 Importamos tu validador de seguridad dinámico del Core
from app.blueprints.core.controllers.roles import verificar_permiso_dinamico
from app.models.esquema_activo import (
    NivelActivo as Nivel,
    InstitucionActiva as Institucion,
    ComunidadActiva as Comunidad
)
from app.models.actividad import Actividad
from app.models.esquema_activo import FormacionActiva as Formacion
from app.models.esquema_activo import SensibilizacionActiva as Sensibilizacion
from app.models.tecnico import Tecnico
from app.services.notificacion import ServicioNotificacion


def _cargar_formacion_choices(form):
    comunidades = Comunidad.query.order_by(Comunidad.nombre_comunidad.asc()).all()
    form.id_comunidad.choices = [(com.id_comunidad, com.nombre_comunidad) for com in comunidades]

    niveles = Nivel.query.order_by(Nivel.nombre_nivel.asc()).all()
    form.id_nivel.choices = [(niv.id_nivel, niv.nombre_nivel) for niv in niveles]

    instituciones = Institucion.query.order_by(Institucion.nombre_institucion.asc()).all()
    form.id_institucion.choices = [(inst.id_institucion, inst.nombre_institucion) for inst in instituciones]

    tecnicos = (
        Tecnico.query
        .filter(Tecnico.id_usuario.isnot(None))
        .order_by(Tecnico.apellidos.asc(), Tecnico.nombres.asc())
        .all()
    )
    form.tecnico.choices = [(t.id_tecnico, f"{t.nombres} {t.apellidos}") for t in tecnicos]


def _cargar_sensibilizacion_choices(form):
    comunidades = Comunidad.query.order_by(Comunidad.nombre_comunidad.asc()).all()
    form.id_comunidad.choices = [(com.id_comunidad, com.nombre_comunidad) for com in comunidades]

    niveles = Nivel.query.order_by(Nivel.nombre_nivel.asc()).all()
    form.id_nivel.choices = [(niv.id_nivel, niv.nombre_nivel) for niv in niveles]

    tecnicos = (
        Tecnico.query
        .filter(Tecnico.id_usuario.isnot(None))
        .order_by(Tecnico.apellidos.asc(), Tecnico.nombres.asc())
        .all()
    )
    form.facilitador.choices = [(t.id_tecnico, f"{t.nombres} {t.apellidos}") for t in tecnicos]


def _registrar_formacion(form):
    institucion_seleccionada = Institucion.query.get(form.id_institucion.data)
    if institucion_seleccionada is None:
        raise ValueError('La institución seleccionada no existe.')

    tecnico = Tecnico.query.get(form.tecnico.data)
    if tecnico is None:
        raise ValueError('El técnico seleccionado no existe o no está activo.')

    nueva_actividad = Actividad(
        fecha_actividad=form.fecha_actividad.data,
        tipo_actividad='FORMACION',
        id_comunidad=form.id_comunidad.data,
        id_nivel=form.id_nivel.data,
        id_usuario=current_user.id_usuario,
    )
    db.session.add(nueva_actividad)
    db.session.flush()

    nombre_tecnico = f"{tecnico.nombres} {tecnico.apellidos}".strip()
    nueva_formacion = Formacion(
        nombre_formacion=f"{form.nombre_formacion.data}||{nombre_tecnico}",
        id_institucion=form.id_institucion.data,
        id_actividad=nueva_actividad.id_actividad,
        id_nivel=form.id_nivel.data,
    )
    db.session.add(nueva_formacion)

# ==========================================
# 1. LISTAR Y REGISTRAR (GET y POST)
# ==========================================
@comunitario_bp.route('/formaciones', methods=['GET', 'POST'])
@login_required  
def formaciones_index():
    # 🛡️ Blindaje Dinámico Ajustado al Slug de la Base de Datos
    verificar_permiso_dinamico('ver_formaciones')

    # 1. Instanciamos los formularios de Flask-WTF
    form = FormacionForm()
    sensibilizacion_form = SensibilizacionForm()

    _cargar_formacion_choices(form)
    _cargar_sensibilizacion_choices(sensibilizacion_form)

    # 4. LISTAR HISTORIAL (Aquí se cumple el MVC: la consulta compleja la hace el Modelo)
    formaciones_procesadas = Formacion.obtener_historial_completo()
    sensibilizaciones_procesadas = Sensibilizacion.obtener_historial_completo()

    # 5. RENDERIZAR LA VISTA
    return render_template(
        'formaciones/index.html', 
        form=form,
        sensibilizacion_form=sensibilizacion_form,
        formaciones=formaciones_procesadas,
        sensibilizaciones=sensibilizaciones_procesadas,
    )


@comunitario_bp.route('/formaciones/nuevo', methods=['GET', 'POST'])
@login_required
def formacion_nuevo():
    verificar_permiso_dinamico('registrar_formaciones')

    form = FormacionForm()
    sensibilizacion_form = SensibilizacionForm()
    _cargar_formacion_choices(form)
    _cargar_sensibilizacion_choices(sensibilizacion_form)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            _registrar_formacion(form)
            db.session.commit()
            mensaje = 'Se registró una nueva formación comunitaria.'
            ServicioNotificacion.notificar_por_permiso('gestionar_formaciones', mensaje, emisor_id=current_user.id_usuario)
            ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Formaciones')
            flash('Formación registrada con éxito.', 'success')
            return redirect(url_for('comunitario.formaciones_index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la formación: {str(e)}', 'error')

    formaciones_procesadas = Formacion.obtener_historial_completo()
    sensibilizaciones_procesadas = Sensibilizacion.obtener_historial_completo()
    return render_template(
        'formaciones/index.html',
        form=form,
        sensibilizacion_form=sensibilizacion_form,
        formaciones=formaciones_procesadas,
        sensibilizaciones=sensibilizaciones_procesadas,
    )


# ==========================================
# 2. MODIFICAR / ACTUALIZAR (POST)
# ==========================================
@comunitario_bp.route('/formaciones/editar/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_editar(id_formacion):
    # 🛡️ Blindaje Dinámico Ajustado al Slug de la Base de Datos
    verificar_permiso_dinamico('editar_formaciones')

    formacion = Formacion.query.get_or_404(id_formacion)
    actividad = Actividad.query.get(formacion.id_actividad)

    tema_nuevo = request.form.get('edit_nombre_formacion')
    id_tecnico_nuevo = request.form.get('edit_tecnico')
    fecha_nueva = request.form.get('edit_fecha')
    id_comunidad_nueva = request.form.get('edit_id_comunidad')
    id_inst_nueva = request.form.get('edit_id_institucion')
    id_nivel_nuevo = request.form.get('edit_id_nivel')

    try:
        tecnico_nuevo = None
        if id_tecnico_nuevo:
            tecnico_selected = Tecnico.query.get(int(id_tecnico_nuevo))
            if tecnico_selected is None:
                raise ValueError('El técnico seleccionado no existe.')
            tecnico_nuevo = f"{tecnico_selected.nombres} {tecnico_selected.apellidos}".strip()

        if fecha_nueva:
            actividad.fecha_actividad = datetime.strptime(fecha_nueva, '%Y-%m-%d').date()
        if id_comunidad_nueva:
            actividad.id_comunidad = int(id_comunidad_nueva)
        if id_nivel_nuevo:
            actividad.id_nivel = int(id_nivel_nuevo)

        formacion.nombre_formacion = f"{tema_nuevo}||{tecnico_nuevo or formacion.tecnico_real}"
        formacion.id_nivel = actividad.id_nivel
        if id_inst_nueva:
            formacion.id_institucion = int(id_inst_nueva)

        db.session.commit()
        mensaje = f'Se actualizó la formación #{id_formacion}.'
        ServicioNotificacion.notificar_por_permiso('gestionar_formaciones', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Formaciones')
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
    verificar_permiso_dinamico('eliminar_formaciones')
 
    formacion = Formacion.query.get_or_404(id_formacion)
    actividad = Actividad.query.get(formacion.id_actividad)

    try:
        db.session.delete(formacion)
        if actividad:
            db.session.delete(actividad)
            
        db.session.commit()
        mensaje = f'Se eliminó la formación #{id_formacion}.'
        ServicioNotificacion.notificar_por_permiso('gestionar_formaciones', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Formaciones')
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
    verificar_permiso_dinamico('cambiar_estado_formaciones')
        
    try:
        flash('Estado de la formación actualizado (Simulado).', 'success')
    except Exception as e:
        flash(f'Error al cambiar estado: {str(e)}', 'error')
        
    return redirect(url_for('comunitario.formaciones_index'))


# ==========================================
# 5. RUTA NUEVO (Compatibilidad)
# ==========================================