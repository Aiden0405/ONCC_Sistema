from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.blueprints.monitoreo import monitoreo_bp
from app.constants import ESTADOS_TRANSACCION
from app.models.bitacora import BitacoraTransaccion
from app.models.reporte import ReporteTransaccional


@monitoreo_bp.route('/reportes/')
@login_required
def comparacion_index():
    reportes = ReporteTransaccional.query.order_by(ReporteTransaccional.creado_en.desc()).all()
    return render_template('reportes/index.html', reportes=reportes, estados_flujo=ESTADOS_TRANSACCION)


@monitoreo_bp.route('/reportes/nuevo', methods=['POST'])
@login_required
def nuevo():
    titulo = request.form.get('titulo', '').strip()
    if not titulo:
        flash('Debe indicar el titulo del reporte.', 'error')
        return redirect(url_for('reporte.index'))

    rango_desde = request.form.get('rango_desde') or None
    rango_hasta = request.form.get('rango_hasta') or None

    reporte = ReporteTransaccional(
        titulo=titulo,
        modulo_origen=request.form.get('modulo_origen', 'mapas').strip(),
        formato=request.form.get('formato', 'PDF').strip(),
        responsable=current_user.nombre,
        rango_desde=datetime.strptime(rango_desde, '%Y-%m-%d').date() if rango_desde else None,
        rango_hasta=datetime.strptime(rango_hasta, '%Y-%m-%d').date() if rango_hasta else None,
    )
    db.session.add(reporte)
    db.session.flush()
    db.session.add(BitacoraTransaccion(
        modulo='reportes',
        registro_id=reporte.id,
        accion='creacion',
        estado_nuevo=reporte.estado,
        usuario=current_user.nombre,
        detalle=f'Reporte {reporte.titulo} generado',
    ))
    db.session.commit()

    flash('Reporte transaccional registrado.', 'success')
    return redirect(url_for('reporte.index'))


@monitoreo_bp.route('/reportes/<int:reporte_id>/estado', methods=['POST'])
@login_required
def reporte_cambiar_estado(reporte_id):
    reporte = ReporteTransaccional.query.get_or_404(reporte_id)
    nuevo_estado = request.form.get('estado', '').strip()
    if nuevo_estado not in ESTADOS_TRANSACCION:
        flash('Estado invalido para el flujo.', 'error')
        return redirect(url_for('reporte.index'))

    reporte.estado = nuevo_estado
    db.session.add(BitacoraTransaccion(
        modulo='reportes',
        registro_id=reporte.id,
        accion='cambio_estado',
        estado_nuevo=nuevo_estado,
        usuario=current_user.nombre,
        detalle=f'Reporte {reporte.titulo} paso a {nuevo_estado}',
    ))
    db.session.commit()

    flash('Estado del reporte actualizado.', 'success')
    return redirect(url_for('reporte.index'))