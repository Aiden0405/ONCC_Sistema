from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.constants import ESTADOS_TRANSACCION
from app.models.bitacora import BitacoraTransaccion
from app.models.formacion import Formacion

formacion_bp = Blueprint('formacion', __name__, url_prefix='/formaciones')


@formacion_bp.route('/')
@login_required
def index():
    formaciones = Formacion.query.order_by(Formacion.fecha.desc()).all()
    return render_template('formaciones/index.html', formaciones=formaciones, estados_flujo=ESTADOS_TRANSACCION)


@formacion_bp.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    tema = request.form.get('tema', '').strip()
    comunidad = request.form.get('comunidad', '').strip()
    facilitador = request.form.get('facilitador', '').strip() or current_user.nombre
    fecha = request.form.get('fecha')

    if not tema or not comunidad or not fecha:
        flash('Tema, comunidad y fecha son obligatorios.', 'error')
        return redirect(url_for('formacion.index'))

    formacion = Formacion(
        tema=tema,
        comunidad=comunidad,
        facilitador=facilitador,
        fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
        asistentes=int(request.form.get('asistentes', 0) or 0),
    )
    db.session.add(formacion)
    db.session.flush()
    db.session.add(BitacoraTransaccion(
        modulo='formaciones',
        registro_id=formacion.id,
        accion='creacion',
        estado_nuevo=formacion.estado,
        usuario=current_user.nombre,
        detalle=f'Formacion {formacion.tema} creada',
    ))
    db.session.commit()

    flash('Jornada de formacion registrada.', 'success')
    return redirect(url_for('formacion.index'))


@formacion_bp.route('/<int:formacion_id>/estado', methods=['POST'])
@login_required
def cambiar_estado(formacion_id):
    formacion = Formacion.query.get_or_404(formacion_id)
    nuevo_estado = request.form.get('estado', '').strip()

    if nuevo_estado not in ESTADOS_TRANSACCION:
        flash('Estado invalido para el flujo.', 'error')
        return redirect(url_for('formacion.index'))

    formacion.estado = nuevo_estado
    db.session.add(BitacoraTransaccion(
        modulo='formaciones',
        registro_id=formacion.id,
        accion='cambio_estado',
        estado_nuevo=nuevo_estado,
        usuario=current_user.nombre,
        detalle=f'Formacion {formacion.tema} paso a {nuevo_estado}',
    ))
    db.session.commit()

    flash('Estado de la formacion actualizado.', 'success')
    return redirect(url_for('formacion.index'))
