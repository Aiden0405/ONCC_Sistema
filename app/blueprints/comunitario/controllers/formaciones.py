#CONTROLADOR
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app import db
from app.blueprints.comunitario import comunitario_bp
from app.blueprints.comunitario.forms import FormacionForm
from app.models.esquema_activo import (
    ActividadActiva as Actividad,
    NivelActivo as Nivel,
    FormacionActiva as Formacion,
    InstitucionActiva as Institucion,
    ComunidadActiva as Comunidad
)


# ==========================================
# 1. LISTAR Y REGISTRAR (GET y POST)
# ==========================================

@comunitario_bp.route('/formaciones', methods=['GET', 'POST'])
# lo siguiente exige que el usuario haya iniciado sesión para ver o registrar
@login_required  
def formaciones_index():
    # 1. Instanciamos el formulario creado
    form = FormacionForm()

    # 2. MENÚS DESPLEGABLES
    # Traemos las instituciones de la base de datos
    instituciones = Institucion.query.all()
    # [(id, 'Texto a mostrar')]
    form.id_institucion.choices = [(inst.id_institucion, inst.nombre_institucion) for inst in instituciones]
    # Traemos los niveles de instrucción académicos de la base de datos
    niveles = Nivel.query.all()
    form.id_nivel.choices = [(niv.id_nivel, niv.nombre_nivel) for niv in niveles]

    # 3. CLICK EN "REGISTRAR"
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
            # Guardamos los datos temporalmente y se genera una id_actividad automática
            db.session.flush()

            # Preparar el tema de la formación incluyendo al técnico/facilitador (por ahora)
            tema_consolidado = f"{form.nombre_formacion.data}||{form.tecnico.data}"

            # Registramos la formación usando el ID generado 
            nueva_formacion = Formacion(
                nombre_formacion=tema_consolidado,
                id_institucion=form.id_institucion.data
            )

            # Le asignamos la ID de la nueva actividad a la nueva formación
            nueva_formacion.id_actividad = nueva_actividad.id_actividad

            db.session.add(nueva_formacion)
            
            # Confirmamos definitivamente todos los cambios en PostgreSQL
            db.session.commit()

            flash('Formación registrada con éxito.', 'success')
            return redirect(url_for('comunitario.formaciones_index'))

        except Exception as e:
            # Si algo falla, deshacemos los cambios 
            db.session.rollback()
            flash(f'Error al registrar la formación: {str(e)}', 'error')

    # 4. CONSULTA INNER JOIN - LISTAR HISTORIAL
    # Cruzamos la tabla Formacion con Institucion y Actividad 
    historial_formaciones = db.session.query(
        Formacion.id_formacion,
        Formacion.nombre_formacion,
        Institucion.nombre_institucion,
        Actividad.fecha_actividad,
        Formacion.id_actividad,
        Actividad.id_nivel,
        Formacion.id_institucion
    ).join(Institucion, Formacion.id_institucion == Institucion.id_institucion)\
     .join(Actividad, Formacion.id_actividad == Actividad.id_actividad)\
     .order_by(Formacion.id_formacion.desc()).all()
    # Traer todos los resultados obtenidos y ordenar según la ID de forma descendente

# Procesamos la lista en Python para separar el tema del técnico limpiamente antes de enviarlo al HTML
    formaciones_procesadas = []
    for item in historial_formaciones:
        if "||" in item.nombre_formacion:
            tema, tecnico = item.nombre_formacion.split("||", 1)
        else:
            tema = item.nombre_formacion
            tecnico = "No asignado"
        
        formaciones_procesadas.append({
            'id_formacion': item.id_formacion,
            'tema': tema,
            'tecnico': tecnico,
            'nombre_institucion': item.nombre_institucion,
            'fecha_actividad': item.fecha_actividad,
            'id_actividad': item.id_actividad,
            'id_nivel': item.id_nivel,
            'id_institucion': item.id_institucion
        })

    # 5. RENDERIZAR LA VISTA
    return render_template(
        'formaciones/index.html', 
        #pasamos objeto del formulario
        form=form, 
        #pasamos lista del historial
        formaciones=formaciones_procesadas
    )

# ==========================================
# 2. MODIFICAR / ACTUALIZAR (POST)
# ==========================================
@comunitario_bp.route('/formaciones/editar/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_editar(id_formacion):
    # El técnico no puede editar (Técnico ID = 3)
    if current_user.id_rol not in [1, 2]: 
        flash('No tienes permisos para modificar registros de formación.', 'error')
        return redirect(url_for('comunitario.formaciones_index'))

    formacion = Formacion.query.get_or_404(id_formacion)
    actividad = Actividad.query.get(formacion.id_actividad)

    # Recolectamos lo enviado desde los campos de edición en el HTML
    tema_nuevo = request.form.get('edit_nombre_formacion')
    tecnico_nuevo = request.form.get('edit_tecnico')
    fecha_nueva = request.form.get('edit_fecha')
    id_inst_nueva = request.form.get('edit_id_institucion')
    id_nivel_nuevo = request.form.get('edit_id_nivel')

    try:
        # Actualizamos la actividad asociada
        if fecha_nueva:
            actividad.fecha_actividad = datetime.strptime(fecha_nueva, '%Y-%m-%d').date()
        if id_nivel_nuevo:
            actividad.id_nivel = int(id_nivel_nuevo)

        # Tema y técnico modificados
        formacion.nombre_formacion = f"{tema_nuevo}||{tecnico_nuevo}"
        if id_inst_nueva:
            formacion.id_institucion = int(id_inst_nueva)

        # Subimos cambios
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
    # Regla de negocio: El técnico no puede eliminar
    if current_user.id_rol not in [1, 2]:
        flash('No tienes permisos para eliminar registros de formación.', 'error')
        return redirect(url_for('comunitario.formaciones_index'))

    formacion = Formacion.query.get_or_404(id_formacion)
    actividad = Actividad.query.get(formacion.id_actividad)

    try:
        # Eliminamos primero el hijo (formación) y luego el padre (actividad)
        db.session.delete(formacion)
        if actividad:
            db.session.delete(actividad)
            
        db.session.commit()
        flash('Formación eliminada del historial.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'error')

    return redirect(url_for('comunitario.formaciones_index'))

# A PARTIR DE AQUÍ, COSAS PARA QUE LOGRE EJECUTAR

# ==========================================
# 4. CAMBIAR ESTADO (Agregado para evitar el ImportError)
# ==========================================
@comunitario_bp.route('/formaciones/cambiar_estado/<int:id_formacion>', methods=['POST'])
@login_required
def formacion_cambiar_estado(id_formacion):
    if current_user.id_rol not in [1, 2]:
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('comunitario.formaciones_index'))
        
    try:
        #cambiar el estado si se necesita
        flash('Estado de la formación actualizado (Simulado).', 'success')
    except Exception as e:
        flash(f'Error al cambiar estado: {str(e)}', 'error')
        
    return redirect(url_for('comunitario.formaciones_index'))

# ==========================================
# 5. RUTA COMPATIBLE (Agregada para evitar el ImportError de app/__init__.py)
# ==========================================
@comunitario_bp.route('/formaciones/nuevo', methods=['POST'])
@login_required
def formacion_nuevo():
    # Como tu lógica de registro ya la maneja formaciones_index en el método 'POST',
    # redirigimos directamente allá para que se procese el formulario de forma segura.
    return redirect(url_for('comunitario.formaciones_index'))