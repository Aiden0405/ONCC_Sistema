from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.constants import FASES_COMUNIDAD_MAPA
from app.models.bitacora import BitacoraTransaccion
from app.models.comunidad import Comunidad

# Creamos el Blueprint para agrupar las rutas de Comunidades
comunidad_bp = Blueprint('comunidad', __name__, url_prefix='/comunidades')

@comunidad_bp.route('/')
@login_required
def index():
    comunidades = Comunidad.query.order_by(Comunidad.actualizado_en.desc()).all()
    return render_template('comunidades/kanban.html', comunidades=comunidades)

@comunidad_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        estado = request.form.get('estado_geo', '').strip()
        municipio = request.form.get('municipio', '').strip()

        if not nombre or not estado or not municipio:
            flash('Nombre, estado y municipio son obligatorios.', 'error')
            return redirect(url_for('comunidad.nueva'))

        comunidad = Comunidad(
            nombre=nombre,
            vocero=request.form.get('vocero', '').strip() or None,
            telefono=request.form.get('telefono', '').strip() or None,
            estado=estado,
            municipio=municipio,
            parroquia=request.form.get('parroquia', '').strip() or None,
            familias=int(request.form.get('familias', 0) or 0),
            fase=request.form.get('fase', 'Diagnóstico / Acercamiento').strip(),
            fecha_proximo=datetime.strptime(request.form.get('fecha_proximo'), '%Y-%m-%d').date() if request.form.get('fecha_proximo') else None,
        )
        db.session.add(comunidad)
        db.session.flush()
        db.session.add(BitacoraTransaccion(
            modulo='comunidades',
            registro_id=comunidad.id,
            accion='creacion',
            estado_nuevo=comunidad.fase,
            usuario=current_user.nombre,
            detalle=f'Comunidad {comunidad.nombre} abierta para mapa de riesgo',
        ))
        db.session.commit()

        flash('Comunidad y expediente de mapa de riesgo registrados exitosamente.', 'success')
        return redirect(url_for('comunidad.index'))

    return render_template('comunidades/formulario.html')


@comunidad_bp.route('/<int:comunidad_id>/fase', methods=['POST'])
@login_required
def cambiar_fase(comunidad_id):
    comunidad = Comunidad.query.get_or_404(comunidad_id)
    nueva_fase = request.form.get('fase', '').strip()

    if nueva_fase not in FASES_COMUNIDAD_MAPA:
        flash('Fase invalida para el mapa de riesgo.', 'error')
        return redirect(url_for('comunidad.index'))

    comunidad.fase = nueva_fase
    db.session.add(BitacoraTransaccion(
        modulo='comunidades',
        registro_id=comunidad.id,
        accion='cambio_fase',
        estado_nuevo=nueva_fase,
        usuario=current_user.nombre,
        detalle=f'Comunidad {comunidad.nombre} avanzo a {nueva_fase}',
    ))
    db.session.commit()

    flash('Fase de la comunidad actualizada.', 'success')
    return redirect(url_for('comunidad.index'))