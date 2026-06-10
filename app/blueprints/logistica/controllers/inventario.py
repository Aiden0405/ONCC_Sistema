from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.blueprints.logistica import logistica_bp
from app.models.bitacora import BitacoraTransaccion
from app.models.inventario import InventarioEquipo


def _serializar(equipos):
    return [{
        'id': e.id,
        'tipo_equipo': e.tipo_equipo,
        'codigo': e.codigo,
        'ubicacion': e.ubicacion,
        'responsable': e.responsable,
        'estado_operativo': e.estado_operativo,
        'estado_flujo': e.estado_flujo,
        'ultimo_mantenimiento': e.ultimo_mantenimiento.strftime('%Y-%m-%d') if e.ultimo_mantenimiento else None,
    } for e in equipos]


@logistica_bp.route('/inventario/')
@login_required
def inventario_index():
    equipos = InventarioEquipo.query.order_by(InventarioEquipo.creado_en.desc()).all()
    return render_template('inventario/index.html', inventario=equipos, inventario_json=_serializar(equipos))


@logistica_bp.route('/inventario/nuevo', methods=['POST'])
@login_required
def nuevo():
    codigo = request.form.get('codigo', '').strip()
    if not codigo:
        flash('Debe indicar el codigo del equipo.', 'error')
        return redirect(url_for('inventario.index'))

    existe = InventarioEquipo.query.filter_by(codigo=codigo).first()
    if existe:
        flash('Ya existe un equipo con ese codigo.', 'error')
        return redirect(url_for('inventario.index'))

    fecha_mantenimiento = request.form.get('ultimo_mantenimiento')
    fecha = None
    if fecha_mantenimiento:
        fecha = datetime.strptime(fecha_mantenimiento, '%Y-%m-%d').date()

    equipo = InventarioEquipo(
        tipo_equipo=request.form.get('tipo_equipo', 'Equipo Tecnico').strip(),
        codigo=codigo,
        ubicacion=request.form.get('ubicacion', 'Sin ubicacion').strip(),
        estado_operativo=request.form.get('estado_operativo', 'Operativo').strip(),
        estado_flujo=request.form.get('estado', 'Disponible').strip(),
        ultimo_mantenimiento=fecha,
        responsable=current_user.nombre,
    )
    db.session.add(equipo)
    db.session.flush()

    db.session.add(BitacoraTransaccion(
        modulo='inventario',
        registro_id=equipo.id,
        accion='creacion',
        estado_nuevo=equipo.estado_flujo,
        usuario=current_user.nombre,
        detalle=f'Registro del equipo {equipo.codigo}',
    ))
    db.session.commit()

    flash('Equipo registrado exitosamente en el inventario.', 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/<int:equipo_id>/editar', methods=['POST'])
@login_required
def editar(equipo_id):
    equipo = InventarioEquipo.query.get_or_404(equipo_id)
    codigo = request.form.get('codigo', '').strip()

    if not codigo:
        flash('Debe indicar el codigo del equipo.', 'error')
        return redirect(url_for('inventario.index'))

    existe = InventarioEquipo.query.filter_by(codigo=codigo).first()
    if existe and existe.id != equipo.id:
        flash('Ya existe otro equipo con ese codigo.', 'error')
        return redirect(url_for('inventario.index'))

    fecha_mantenimiento = request.form.get('ultimo_mantenimiento')
    fecha = None
    if fecha_mantenimiento:
        fecha = datetime.strptime(fecha_mantenimiento, '%Y-%m-%d').date()

    equipo.tipo_equipo = request.form.get('tipo_equipo', equipo.tipo_equipo).strip()
    equipo.codigo = codigo
    equipo.ubicacion = request.form.get('ubicacion', equipo.ubicacion).strip()
    equipo.estado_operativo = request.form.get('estado_operativo', equipo.estado_operativo).strip()
    equipo.estado_flujo = request.form.get('estado', equipo.estado_flujo).strip()
    equipo.ultimo_mantenimiento = fecha
    equipo.responsable = request.form.get('responsable', equipo.responsable).strip()

    db.session.add(BitacoraTransaccion(
        modulo='inventario',
        registro_id=equipo.id,
        accion='modificacion',
        estado_nuevo=equipo.estado_flujo,
        usuario=current_user.nombre,
        detalle=f'Datos del equipo {equipo.codigo} actualizados',
    ))
    db.session.commit()
    flash('Equipo actualizado exitosamente.', 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/<int:equipo_id>/eliminar', methods=['POST'])
@login_required
def eliminar(equipo_id):
    equipo = InventarioEquipo.query.get_or_404(equipo_id)

    db.session.add(BitacoraTransaccion(
        modulo='inventario',
        registro_id=equipo.id,
        accion='eliminacion',
        estado_nuevo=equipo.estado_flujo,
        usuario=current_user.nombre,
        detalle=f'Equipo {equipo.codigo} eliminado del inventario',
    ))
    db.session.delete(equipo)
    db.session.commit()
    flash('Equipo eliminado del inventario.', 'success')
    return redirect(url_for('inventario.index'))


