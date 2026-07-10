from flask import flash, jsonify, redirect, render_template, request, url_for, Response
from flask_login import current_user, login_required

from app.blueprints.logistica import logistica_bp
from app.services.inventario_service import InventarioService


@logistica_bp.route('/inventario/')
@login_required
def inventario_index():
    equipos = InventarioService.listar_equipos()
    return render_template('inventario/index.html', inventario=equipos, inventario_json=InventarioService.serializar(equipos))


@logistica_bp.route('/inventario/nuevo', methods=['POST'])
@login_required
def nuevo():
    resultado = InventarioService.crear_equipo(request.form, current_user)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('inventario.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('inventario.index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/<int:equipo_id>/editar', methods=['POST'])
@login_required
def editar(equipo_id):
    resultado = InventarioService.actualizar_equipo(equipo_id, request.form, current_user)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('inventario.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('inventario.index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/<int:equipo_id>/eliminar', methods=['POST'])
@login_required
def eliminar(equipo_id):
    InventarioService.eliminar_equipo(equipo_id, current_user)
    flash('Equipo eliminado del inventario.', 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/reporte', methods=['GET'])
@login_required
def reporte_inventario():
    ids = request.args.get('ids')
    equipos = InventarioService.listar_equipos()
    if ids:
        id_list = [int(x) for x in ids.split(',') if x.strip().isdigit()]
        if id_list:
            equipos = [e for e in equipos if e.id in id_list]
    buf = InventarioService.generar_reporte_pdf(equipos)
    return Response(buf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=reporte_inventario.pdf'})


@logistica_bp.route('/inventario/reporte-movimientos', methods=['GET'])
@login_required
def reporte_movimientos():
    ids = request.args.get('ids')
    buf = InventarioService.generar_reporte_movimientos_pdf(ids)
    return Response(buf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=reporte_movimientos.pdf'})


@logistica_bp.route('/inventario/<int:equipo_id>/acta', methods=['GET'])
@login_required
def acta_responsabilidad(equipo_id):
    buf = InventarioService.generar_acta_pdf(equipo_id)
    return Response(buf, mimetype='application/pdf',
                    headers={'Content-Disposition': f'inline; filename=acta_{equipo_id}.pdf'})


