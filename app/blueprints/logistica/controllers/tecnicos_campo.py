from flask import flash, jsonify, redirect, render_template, request, url_for, Response
from flask_login import login_required, current_user

from app import db
from app.blueprints.logistica import logistica_bp
from app.services.tecnico_service import TecnicoService
from app.models.bitacora import BitacoraTransaccion
from app.utils.authorization import verificar_permiso_dinamico


@logistica_bp.route('/tecnicos-campo')
@login_required
def tecnicos_campo_index():
    verificar_permiso_dinamico('ver_tecnicos')
    usuarios_tecnicos = TecnicoService.listar_tecnicos()
    tecnicos = TecnicoService.serializar(usuarios_tecnicos)
    return render_template('logistica/tecnicos_campo.html', tecnicos=tecnicos, tecnicos_json=TecnicoService.serializar(usuarios_tecnicos))


@logistica_bp.route('/tecnicos-campo/nuevo', methods=['POST'])
@login_required
def tecnicos_nuevo():
    verificar_permiso_dinamico('registrar_tecnicos')
    resultado = TecnicoService.crear_tecnico(request.form)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    # 🌟 REGISTRO EN BITÁCORA
    try:
        nombre_usr = getattr(current_user, 'nombre_usuario', None) or getattr(current_user, 'usuario', 'Administrador')
        nombres = request.form.get('nombres', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        nombre_completo = f"{nombres} {apellidos}".strip() or "Nuevo Técnico"

        db.session.add(BitacoraTransaccion(
            modulo='tecnicos',
            registro_id=resultado.get('id_tecnico'),
            accion='creacion',
            estado_nuevo='Activo',
            usuario=nombre_usr,
            detalle=f'Registrado técnico de campo: {nombre_completo}'
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('logistica.tecnicos_campo_index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))


@logistica_bp.route('/tecnicos-campo/<int:tecnico_id>/editar', methods=['POST'])
@login_required
def tecnicos_editar(tecnico_id):
    permiso_edicion = 'editar_mi_tecnico' if int(tecnico_id) == int(current_user.id_usuario) else 'editar_tecnicos'
    verificar_permiso_dinamico(permiso_edicion)
    resultado = TecnicoService.actualizar_tecnico(tecnico_id, request.form)
    if not resultado['ok']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': resultado['error']})
        flash(resultado['error'], 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    # 🌟 REGISTRO EN BITÁCORA
    try:
        nombre_usr = getattr(current_user, 'nombre_usuario', None) or getattr(current_user, 'usuario', 'Administrador')
        nombres = request.form.get('nombres', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        nombre_completo = f"{nombres} {apellidos}".strip() or f"ID #{tecnico_id}"

        db.session.add(BitacoraTransaccion(
            modulo='tecnicos',
            registro_id=tecnico_id,
            accion='modificacion',
            estado_nuevo='Activo',
            usuario=nombre_usr,
            detalle=f'Actualizados datos del técnico de campo #{tecnico_id}: {nombre_completo}'
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('logistica.tecnicos_campo_index'), 'mensaje': resultado['mensaje']})
    flash(resultado['mensaje'], 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))


@logistica_bp.route('/tecnicos-campo/<int:tecnico_id>/eliminar', methods=['POST'])
@login_required
def tecnicos_eliminar(tecnico_id):
    verificar_permiso_dinamico('eliminar_tecnicos')
    # 🌟 REGISTRO EN BITÁCORA ANTES DE ELIMINAR
    try:
        nombre_usr = getattr(current_user, 'nombre_usuario', None) or getattr(current_user, 'usuario', 'Administrador')
        db.session.add(BitacoraTransaccion(
            modulo='tecnicos',
            registro_id=tecnico_id,
            accion='eliminacion',
            estado_nuevo=None,
            usuario=nombre_usr,
            detalle=f'Eliminado técnico de campo #{tecnico_id}'
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()

    TecnicoService.eliminar_tecnico(tecnico_id)
    flash('Técnico eliminado del sistema.', 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))


@logistica_bp.route('/tecnicos-campo/<int:tecnico_id>/movimientos')
@login_required
def tecnicos_movimientos(tecnico_id):
    verificar_permiso_dinamico('ver_movimientos_tecnicos')
    movimientos = TecnicoService.serializar_movimientos_tecnico(tecnico_id)
    return jsonify({'movimientos': movimientos})


@logistica_bp.route('/tecnicos-campo/reporte', methods=['GET'])
@login_required
def reporte_tecnicos():
    verificar_permiso_dinamico('ver_reportes_tecnicos')
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