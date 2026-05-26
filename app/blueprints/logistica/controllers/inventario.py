from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.blueprints.logistica import logistica_bp
from app.constants import ESTADOS_TRANSACCION
from app.models.bitacora import BitacoraTransaccion
from app.models.inventario import InventarioEquipo


@logistica_bp.route('/inventario/')
@login_required
def inventario_index():
    equipos = InventarioEquipo.query.order_by(InventarioEquipo.creado_en.desc()).all()
    return render_template('inventario/index.html', inventario=equipos, estados_flujo=ESTADOS_TRANSACCION)


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
        estado_operativo=request.form.get('estado', 'Operativo').strip(),
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


@logistica_bp.route('/inventario/<int:equipo_id>/estado', methods=['POST'])
@login_required
def cambiar_estado(equipo_id):
    equipo = InventarioEquipo.query.get_or_404(equipo_id)
    nuevo_estado = request.form.get('estado_flujo', '').strip()

    if nuevo_estado not in ESTADOS_TRANSACCION:
        flash('Estado de flujo invalido.', 'error')
        return redirect(url_for('inventario.index'))

    equipo.estado_flujo = nuevo_estado
    db.session.add(BitacoraTransaccion(
        modulo='inventario',
        registro_id=equipo.id,
        accion='cambio_estado',
        estado_nuevo=nuevo_estado,
        usuario=current_user.nombre,
        detalle=f'Estado del expediente {equipo.codigo} actualizado',
    ))
    db.session.commit()
    flash('Estado transaccional actualizado.', 'success')
    return redirect(url_for('inventario.index'))