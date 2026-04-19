from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.constants import ESTADOS_TRANSACCION
from app.models.bitacora import BitacoraTransaccion
from app.models.sensibilizacion import Sensibilizacion

sensibilizacion_bp = Blueprint('sensibilizacion', __name__, url_prefix='/sensibilizaciones')


@sensibilizacion_bp.route('/')
@login_required
def index():
    sensibilizaciones = Sensibilizacion.query.order_by(Sensibilizacion.fecha.desc()).all()
    return render_template('sensibilizaciones/index.html', sensibilizaciones=sensibilizaciones, estados_flujo=ESTADOS_TRANSACCION)


@sensibilizacion_bp.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    campana = request.form.get('campana', '').strip()
    territorio = request.form.get('territorio', '').strip()
    vocero = request.form.get('vocero', '').strip() or current_user.nombre
    fecha = request.form.get('fecha')

    if not campana or not territorio or not fecha:
        flash('Campana, territorio y fecha son obligatorios.', 'error')
        return redirect(url_for('sensibilizacion.index'))

    sensibilizacion = Sensibilizacion(
        campana=campana,
        territorio=territorio,
        vocero=vocero,
        fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
        alcance=int(request.form.get('alcance', 0) or 0),
    )
    db.session.add(sensibilizacion)
    db.session.flush()
    db.session.add(BitacoraTransaccion(
        modulo='sensibilizaciones',
        registro_id=sensibilizacion.id,
        accion='creacion',
        estado_nuevo=sensibilizacion.estado,
        usuario=current_user.nombre,
        detalle=f'Sensibilizacion {sensibilizacion.campana} creada',
    ))
    db.session.commit()

    flash('Jornada de sensibilizacion registrada.', 'success')
    return redirect(url_for('sensibilizacion.index'))


@sensibilizacion_bp.route('/<int:sensibilizacion_id>/estado', methods=['POST'])
@login_required
def cambiar_estado(sensibilizacion_id):
    sensibilizacion = Sensibilizacion.query.get_or_404(sensibilizacion_id)
    nuevo_estado = request.form.get('estado', '').strip()

    if nuevo_estado not in ESTADOS_TRANSACCION:
        flash('Estado invalido para el flujo.', 'error')
        return redirect(url_for('sensibilizacion.index'))

    sensibilizacion.estado = nuevo_estado
    db.session.add(BitacoraTransaccion(
        modulo='sensibilizaciones',
        registro_id=sensibilizacion.id,
        accion='cambio_estado',
        estado_nuevo=nuevo_estado,
        usuario=current_user.nombre,
        detalle=f'Sensibilizacion {sensibilizacion.campana} paso a {nuevo_estado}',
    ))
    db.session.commit()

    flash('Estado de sensibilizacion actualizado.', 'success')
    return redirect(url_for('sensibilizacion.index'))
