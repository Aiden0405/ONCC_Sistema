from flask import flash, jsonify, redirect, render_template, request, url_for, Response
from flask_login import current_user, login_required

from app.blueprints.logistica import logistica_bp
from app.services.inventario_service import InventarioService
from app.utils.authorization import verificar_permiso_dinamico


@logistica_bp.route('/inventario/')
@login_required
def inventario_index():
    verificar_permiso_dinamico('ver_inventario')
    equipos = InventarioService.listar_equipos()
    movimientos = InventarioService.listar_movimientos()
    return render_template('inventario/index.html',
                           inventario=equipos,
                           inventario_json=InventarioService.serializar(equipos),
                           movimientos=movimientos,
                           movimientos_json=InventarioService.serializar_movimientos(movimientos))


@logistica_bp.route('/inventario/nuevo', methods=['POST'])
@login_required
def nuevo():
    verificar_permiso_dinamico('registrar_inventario')
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
    verificar_permiso_dinamico('editar_inventario')
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
    verificar_permiso_dinamico('eliminar_inventario')
    InventarioService.eliminar_equipo(equipo_id, current_user)
    flash('Equipo eliminado del inventario.', 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/reporte', methods=['GET'])
@login_required
def reporte_inventario():
    verificar_permiso_dinamico('ver_reportes_inventario')
    ids = request.args.get('ids')
    equipos = InventarioService.listar_equipos()
    if ids:
        id_list = [int(x) for x in ids.split(',') if x.strip().isdigit()]
        if id_list:
            equipos = [e for e in equipos if e.id in id_list]
    buf = InventarioService.generar_reporte_pdf(equipos)
    return Response(buf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=reporte_inventario.pdf'})


@logistica_bp.route('/inventario/nuevo-movimiento', methods=['POST'])
@login_required
def nuevo_movimiento():
    verificar_permiso_dinamico('registrar_movimientos_inventario')
    resultado = InventarioService.crear_movimiento(request.form, current_user)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('inventario.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('inventario.index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/movimiento/<int:movimiento_id>/editar', methods=['POST'])
@login_required
def editar_movimiento(movimiento_id):
    verificar_permiso_dinamico('editar_movimientos_inventario')
    resultado = InventarioService.actualizar_movimiento(movimiento_id, request.form, current_user)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('inventario.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('inventario.index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/movimiento/<int:movimiento_id>/eliminar', methods=['POST'])
@login_required
def eliminar_movimiento(movimiento_id):
    verificar_permiso_dinamico('eliminar_movimientos_inventario')
    resultado = InventarioService.eliminar_movimiento(movimiento_id, current_user)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('inventario.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('inventario.index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('inventario.index'))


@logistica_bp.route('/inventario/reporte-movimientos', methods=['GET'])
@login_required
def reporte_movimientos():
    verificar_permiso_dinamico('ver_reportes_inventario')
    ids = request.args.get('ids')
    buf = InventarioService.generar_reporte_movimientos_pdf(ids)
    return Response(buf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=reporte_movimientos.pdf'})


@logistica_bp.route('/inventario/<int:equipo_id>/acta', methods=['GET'])
@login_required
def acta_responsabilidad(equipo_id):
    verificar_permiso_dinamico('ver_actas_inventario')
    buf = InventarioService.generar_acta_pdf(equipo_id)
    return Response(buf, mimetype='application/pdf',
                    headers={'Content-Disposition': f'inline; filename=acta_{equipo_id}.pdf'})


@logistica_bp.route('/equipos/lista-json', methods=['GET'])
@login_required
def listar_equipos_json():
    verificar_permiso_dinamico('ver_inventario')
    try:
        equipos = InventarioService.listar_equipos()
        # Reutiliza el serializador que ya tienes en InventarioService
        return jsonify({
            'ok': True,
            'equipos': InventarioService.serializar(equipos)
        }), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500