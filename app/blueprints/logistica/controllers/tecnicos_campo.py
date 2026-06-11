import secrets
from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app import db
from app.blueprints.logistica import logistica_bp
from app.models.role import Role
from app.models.usuario import Usuario


@logistica_bp.route('/tecnicos-campo')
@login_required
def tecnicos_campo_index():
    role_tecnico = Role.query.filter_by(nombre_rol='Técnico').first()
    tecnicos = Usuario.query.filter_by(id_rol=role_tecnico.id_rol).order_by(Usuario.nombre_usuario).all() if role_tecnico else []
    tecnicos_json = [{
        'id_usuario': u.id_usuario,
        'nombre_usuario': u.nombre_usuario,
        'correo': u.correo,
        'cedula': u.cedula,
        'especialidad': u.especialidad,
        'estatus': u.estatus,
    } for u in tecnicos]
    return render_template('logistica/tecnicos_campo.html', tecnicos=tecnicos, tecnicos_json=tecnicos_json)


@logistica_bp.route('/tecnicos-campo/nuevo', methods=['POST'])
@login_required
def tecnicos_nuevo():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip().lower()
    cedula = request.form.get('cedula', '').strip()
    especialidad = request.form.get('especialidad', '').strip()
    estatus_val = request.form.get('estatus', '1')
    estatus = estatus_val == '1'

    if not nombre or not correo or not cedula or not especialidad:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'Todos los campos son obligatorios.'})
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    existe_correo = Usuario.query.filter_by(correo=correo).first()
    if existe_correo:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'Ya existe un usuario con ese correo.'})
        flash('Ya existe un usuario con ese correo.', 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    if cedula:
        existe_cedula = Usuario.query.filter_by(cedula=cedula).first()
        if existe_cedula:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'ok': False, 'error': 'Ya existe un usuario con esa cédula.'})
            flash('Ya existe un usuario con esa cédula.', 'error')
            return redirect(url_for('logistica.tecnicos_campo_index'))

    role_tecnico = Role.query.filter_by(nombre_rol='Técnico').first()
    if not role_tecnico:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'El rol Técnico no existe. Ejecute flask seed primero.'})
        flash('El rol Técnico no existe. Ejecute flask seed primero.', 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    usuario = Usuario(
        nombre_usuario=nombre,
        correo=correo,
        cedula=cedula,
        especialidad=especialidad,
        id_rol=role_tecnico.id_rol,
        estatus=estatus,
    )
    usuario.set_password(secrets.token_urlsafe(10))
    db.session.add(usuario)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'Esa cédula ya está registrada en el sistema.'})
        flash('Esa cédula ya está registrada en el sistema.', 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('logistica.tecnicos_campo_index'), 'mensaje': 'Técnico registrado exitosamente.'})
    flash('Técnico registrado exitosamente.', 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))


@logistica_bp.route('/tecnicos-campo/<int:tecnico_id>/editar', methods=['POST'])
@login_required
def tecnicos_editar(tecnico_id):
    usuario = Usuario.query.get_or_404(tecnico_id)
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip().lower()
    cedula = request.form.get('cedula', '').strip()
    especialidad = request.form.get('especialidad', '').strip()
    estatus_val = request.form.get('estatus', '1')
    estatus = estatus_val == '1'

    if not nombre or not correo or not cedula or not especialidad:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'Todos los campos son obligatorios.'})
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    existe_correo = Usuario.query.filter_by(correo=correo).first()
    if existe_correo and existe_correo.id_usuario != usuario.id_usuario:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'Ya existe otro usuario con ese correo.'})
        flash('Ya existe otro usuario con ese correo.', 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    if cedula:
        existe_cedula = Usuario.query.filter_by(cedula=cedula).first()
        if existe_cedula and existe_cedula.id_usuario != usuario.id_usuario:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'ok': False, 'error': 'Ya existe otro usuario con esa cédula.'})
            flash('Ya existe otro usuario con esa cédula.', 'error')
            return redirect(url_for('logistica.tecnicos_campo_index'))

    usuario.nombre_usuario = nombre
    usuario.correo = correo
    usuario.cedula = cedula
    usuario.especialidad = especialidad
    usuario.estatus = estatus

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'Esa cédula ya está registrada en el sistema.'})
        flash('Esa cédula ya está registrada en el sistema.', 'error')
        return redirect(url_for('logistica.tecnicos_campo_index'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'redirect': url_for('logistica.tecnicos_campo_index'), 'mensaje': 'Técnico actualizado exitosamente.'})
    flash('Técnico actualizado exitosamente.', 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))


@logistica_bp.route('/tecnicos-campo/<int:tecnico_id>/eliminar', methods=['POST'])
@login_required
def tecnicos_eliminar(tecnico_id):
    usuario = Usuario.query.get_or_404(tecnico_id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Técnico eliminado del sistema.', 'success')
    return redirect(url_for('logistica.tecnicos_campo_index'))
