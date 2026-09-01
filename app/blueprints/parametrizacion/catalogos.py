from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db

from app.models.esquema_activo import ComunidadActiva as Comunidad
from app.models.esquema_activo import NivelActivo as Nivel
from app.models.esquema_activo import InstitucionActiva as Institucion
from app.blueprints.core.controllers.roles import verificar_permiso_dinamico


@login_required
def catalogos_index():
    verificar_permiso_dinamico('gestionar_usuarios')
    
    comunidades = Comunidad.query.order_by(Comunidad.id_comunidad.asc()).all()
    instituciones = Institucion.query.order_by(Institucion.id_institucion.asc()).all()
    niveles = Nivel.query.order_by(Nivel.id_nivel.asc()).all()
    
    return render_template(
        'parametrizacion/catalogo.html', 
        comunidades=comunidades, 
        instituciones=instituciones, 
        niveles=niveles
    )


# ==============================================================================
# CRUD INSTITUCIONES
# ==============================================================================
@login_required
def nueva_institucion():
    nombre = request.form.get('nombre_institucion', '').strip()
    
    if not nombre:
        flash('El nombre de la institución no puede estar vacío.', 'error')
        return redirect(url_for('core.catalogos_index'))
        
    try:
        nueva_inst = Institucion(
            nombre_institucion=nombre,
            id_comunidad=int(request.form.get('id_comunidad', 1)),
            tipo_institucion=request.form.get('tipo', 'Educativa'),
            direccion_exacta='Sede Comunitaria',
            numero_contacto='S/N',
            correo_electronico='contacto@oncc.gob.ve'
        )
        db.session.add(nueva_inst)
        db.session.commit()
        flash(f'Institución "{nombre}" registrada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la institución: {str(e)}', 'error')
        
    return redirect(url_for('core.catalogos_index'))


@login_required
def editar_institucion(id_inst):
    inst = Institucion.query.get_or_404(id_inst)
    nombre = request.form.get('nombre_institucion', '').strip()
    
    if not nombre:
        flash('El nombre no puede estar vacío.', 'error')
        return redirect(url_for('core.catalogos_index'))

    try:
        inst.nombre_institucion = nombre
        db.session.commit()
        flash('Institución actualizada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('core.catalogos_index'))


@login_required
def eliminar_institucion(id_inst):
    inst = Institucion.query.get_or_404(id_inst)
    try:
        db.session.delete(inst)
        db.session.commit()
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
    nombre = request.form.get('nombre_comunidad', '').strip()
    
    if not nombre:
        flash('El nombre de la comunidad es obligatorio.', 'error')
        return redirect(url_for('core.catalogos_index'))
        
    try:
        com = Comunidad(
            nombre_comunidad=nombre,
            id_parroquia=int(request.form.get('id_parroquia', 1))
        )
        db.session.add(com)
        db.session.commit()
        flash(f'Comunidad "{nombre}" agregada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la comunidad: {str(e)}', 'error')
        
    return redirect(url_for('core.catalogos_index'))


@login_required
def editar_comunidad(id_com):
    com = Comunidad.query.get_or_404(id_com)
    nombre = request.form.get('nombre_comunidad', '').strip()

    if not nombre:
        flash('El nombre es obligatorio.', 'error')
        return redirect(url_for('core.catalogos_index'))

    try:
        com.nombre_comunidad = nombre
        db.session.commit()
        flash('Comunidad modificada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('core.catalogos_index'))


@login_required
def eliminar_comunidad(id_com):
    com = Comunidad.query.get_or_404(id_com)
    try:
        db.session.delete(com)
        db.session.commit()
        flash('Comunidad removida correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar la comunidad porque tiene actividades asociadas.', 'error')
    return redirect(url_for('core.catalogos_index'))


# ==============================================================================
# CRUD NIVELES DE INSTRUCCIÓN (CORREGIDO CON NOT NULL SUPPORT)
# ==============================================================================
@login_required
def nuevo_nivel():
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
        flash(f'Nivel "{nombre}" registrado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar el nivel: {str(e)}', 'error')
        
    return redirect(url_for('core.catalogos_index'))


@login_required
def editar_nivel(id_niv):
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
        flash('Nivel actualizado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('core.catalogos_index'))


@login_required
def eliminar_nivel(id_niv):
    niv = Nivel.query.get_or_404(id_niv)
    try:
        db.session.delete(niv)
        db.session.commit()
        flash('Nivel eliminado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar el nivel porque está en uso.', 'error')
    return redirect(url_for('core.catalogos_index'))