from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import text
from app import db
from app.services.notificacion import ServicioNotificacion

from app.models.esquema_activo import ComunidadActiva as Comunidad
from app.models.esquema_activo import NivelActivo as Nivel
from app.models.esquema_activo import InstitucionActiva as Institucion
from app.blueprints.core.controllers.roles import verificar_permiso_dinamico


@login_required
def catalogos_index():
    verificar_permiso_dinamico('ver_catalogos')
    
    comunidades = Comunidad.query.order_by(Comunidad.id_comunidad.asc()).all()
    instituciones = Institucion.query.order_by(Institucion.id_institucion.asc()).all()
    niveles = Nivel.query.order_by(Nivel.id_nivel.asc()).all()
    
    # Cargar las parroquias existentes en BD para el selector
    parroquias = db.session.execute(
        text("SELECT id_parroquia, nombre_parroquia FROM parroquia ORDER BY nombre_parroquia ASC;")
    ).fetchall()
    
    return render_template(
        'parametrizacion/catalogo.html', 
        comunidades=comunidades, 
        instituciones=instituciones, 
        niveles=niveles,
        parroquias=parroquias
    )


# ==============================================================================
# CRUD INSTITUCIONES
# ==============================================================================
@login_required
def nueva_institucion():
    verificar_permiso_dinamico('registrar_instituciones')
    nombre = request.form.get('nombre_institucion', '').strip()
    id_comunidad = request.form.get('id_comunidad', type=int)
    
    if not nombre:
        flash('El nombre de la institución no puede estar vacío.', 'error')
        return redirect(url_for('core.catalogos_index'))

    if not id_comunidad:
        flash('Debe seleccionar una comunidad válida para asociar la institución.', 'error')
        return redirect(url_for('core.catalogos_index'))
        
    try:
        nueva_inst = Institucion(
            nombre_institucion=nombre,
            id_comunidad=id_comunidad,
            tipo_institucion=request.form.get('tipo', 'Educativa'),
            direccion_exacta='Sede Comunitaria',
            numero_contacto='S/N',
            correo_electronico='contacto@oncc.gob.ve'
        )
        db.session.add(nueva_inst)
        db.session.commit()
        mensaje = f'Se registró la institución "{nombre}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash(f'Institución "{nombre}" registrada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la institución: {str(e)}', 'error')
        
    return redirect(url_for('core.catalogos_index'))


@login_required
def editar_institucion(id_inst):
    verificar_permiso_dinamico('editar_instituciones')
    inst = Institucion.query.get_or_404(id_inst)
    nombre = request.form.get('nombre_institucion', '').strip()
    
    if not nombre:
        flash('El nombre no puede estar vacío.', 'error')
        return redirect(url_for('core.catalogos_index'))

    try:
        inst.nombre_institucion = nombre
        db.session.commit()
        mensaje = f'Se actualizó la institución "{nombre}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash('Institución actualizada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('core.catalogos_index'))


@login_required
def eliminar_institucion(id_inst):
    verificar_permiso_dinamico('eliminar_instituciones')
    inst = Institucion.query.get_or_404(id_inst)
    nombre_eliminado = inst.nombre_institucion
    try:
        db.session.delete(inst)
        db.session.commit()
        mensaje = f'Se eliminó la institución "{nombre_eliminado}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash('Institución eliminada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar porque está vinculada a otros registros.', 'error')
    return redirect(url_for('core.catalogos_index'))


# ==============================================================================
# CRUD COMUNIDADES
# ==============================================================================
@login_required
def nueva_comunidad():
    verificar_permiso_dinamico('registrar_comunidades')
    nombre = request.form.get('nombre_comunidad', '').strip()
    id_parroquia = request.form.get('id_parroquia', type=int)
    
    if not nombre:
        flash('El nombre de la comunidad es obligatorio.', 'error')
        return redirect(url_for('core.catalogos_index'))

    if not id_parroquia:
        flash('Debe seleccionar una parroquia válida.', 'error')
        return redirect(url_for('core.catalogos_index'))
        
    try:
        com = Comunidad(
            nombre_comunidad=nombre,
            id_parroquia=id_parroquia
        )
        db.session.add(com)
        db.session.commit()
        mensaje = f'Se registró la comunidad "{nombre}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash(f'Comunidad "{nombre}" agregada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la comunidad: {str(e)}', 'error')
        
    return redirect(url_for('core.catalogos_index'))


@login_required
def editar_comunidad(id_com):
    verificar_permiso_dinamico('editar_comunidades')
    com = Comunidad.query.get_or_404(id_com)
    nombre = request.form.get('nombre_comunidad', '').strip()

    if not nombre:
        flash('El nombre es obligatorio.', 'error')
        return redirect(url_for('core.catalogos_index'))

    try:
        com.nombre_comunidad = nombre
        db.session.commit()
        mensaje = f'Se actualizó la comunidad "{nombre}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash('Comunidad modificada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('core.catalogos_index'))


@login_required
def eliminar_comunidad(id_com):
    verificar_permiso_dinamico('eliminar_comunidades')
    com = Comunidad.query.get_or_404(id_com)
    nombre_eliminado = com.nombre_comunidad
    try:
        db.session.delete(com)
        db.session.commit()
        mensaje = f'Se eliminó la comunidad "{nombre_eliminado}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash('Comunidad removida correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar la comunidad porque tiene actividades o instituciones asociadas.', 'error')
    return redirect(url_for('core.catalogos_index'))


# ==============================================================================
# CRUD NIVELES DE INSTRUCCIÓN
# ==============================================================================
@login_required
def nuevo_nivel():
    verificar_permiso_dinamico('registrar_niveles')
    nombre = request.form.get('nombre_nivel', '').strip()
    descripcion = request.form.get('descripcion', '').strip() or f"Nivel formativo e institucional: {nombre}"
    
    if not nombre:
        flash('El nombre del nivel no puede estar vacío.', 'error')
        return redirect(url_for('core.catalogos_index'))
        
    try:
        niv = Nivel(
            nombre_nivel=nombre,
            descripcion=descripcion
        )
        db.session.add(niv)
        db.session.commit()
        mensaje = f'Se registró el nivel "{nombre}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash(f'Nivel "{nombre}" registrado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar el nivel: {str(e)}', 'error')
        
    return redirect(url_for('core.catalogos_index'))


@login_required
def editar_nivel(id_niv):
    verificar_permiso_dinamico('editar_niveles')
    niv = Nivel.query.get_or_404(id_niv)
    nombre = request.form.get('nombre_nivel', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not nombre:
        flash('El nombre del nivel no puede estar vacío.', 'error')
        return redirect(url_for('core.catalogos_index'))

    try:
        niv.nombre_nivel = nombre
        if descripcion:
            niv.descripcion = descripcion
        db.session.commit()
        mensaje = f'Se actualizó el nivel "{nombre}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash('Nivel actualizado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('core.catalogos_index'))


@login_required
def eliminar_nivel(id_niv):
    verificar_permiso_dinamico('eliminar_niveles')
    niv = Nivel.query.get_or_404(id_niv)
    nombre_eliminado = niv.nombre_nivel
    try:
        db.session.delete(niv)
        db.session.commit()
        mensaje = f'Se eliminó el nivel "{nombre_eliminado}".'
        ServicioNotificacion.notificar_por_permiso('gestionar_usuarios', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Parametrización')
        flash('Nivel eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar el nivel porque está en uso.', 'error')
    return redirect(url_for('core.catalogos_index'))