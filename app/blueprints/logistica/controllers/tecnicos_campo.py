from flask import flash, jsonify, redirect, render_template, request, url_for, Response
from flask_login import login_required

from app.blueprints.logistica import logistica_bp
from app.services.tecnico_service import TecnicoService


@logistica_bp.route('/tecnicos-campo')
@login_required
def tecnicos_campo_index():
    usuarios_tecnicos = TecnicoService.listar_tecnicos()
    tecnicos = TecnicoService.serializar(usuarios_tecnicos)
    return render_template('logistica/tecnicos_campo.html', tecnicos=tecnicos, tecnicos_json=TecnicoService.serializar(usuarios_tecnicos))


@logistica_bp.route('/tecnicos-campo/nuevo', methods=['POST'])
@login_required
def tecnicos_nuevo():
    resultado = TecnicoService.crear_tecnico(request.form)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('logistica.tecnicos_campo_index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))


@logistica_bp.route('/tecnicos-campo/<int:tecnico_id>/editar', methods=['POST'])
@login_required
def tecnicos_editar(tecnico_id):
    resultado = TecnicoService.actualizar_tecnico(tecnico_id, request.form)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('logistica.tecnicos_campo_index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))


@logistica_bp.route('/tecnicos-campo/<int:tecnico_id>/eliminar', methods=['POST'])
@login_required
def tecnicos_eliminar(tecnico_id):
    TecnicoService.eliminar_tecnico(tecnico_id)
    flash('Técnico eliminado del sistema.', 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))


@logistica_bp.route('/tecnicos-campo/reporte', methods=['GET'])
@login_required
def reporte_tecnicos():
    usuarios_tecnicos = TecnicoService.listar_tecnicos()
    tecnicos = TecnicoService.serializar(usuarios_tecnicos)
    ids = request.args.get('ids')
    if ids:
        id_list = [int(x) for x in ids.split(',') if x.strip().isdigit()]
        if id_list:
            tecnicos = [t for t in tecnicos if t['id_usuario'] in id_list]
    buf = TecnicoService.generar_reporte_pdf(tecnicos)
    return Response(buf, mimetype='application/pdf',
                    headers={'Content-Disposition': 'inline; filename=reporte_tecnicos.pdf'})
