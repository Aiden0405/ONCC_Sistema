from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.constants import ESTADOS_TRANSACCION
from app.models.bitacora import BitacoraTransaccion
from app.models.geomatica import MapaRegistro

# Creamos el Blueprint para agrupar las rutas de Geomática
geomatica_bp = Blueprint('geomatica', __name__, url_prefix='/geomatica')

@geomatica_bp.route('/')
@login_required
def index():
    mapas = MapaRegistro.query.order_by(MapaRegistro.creado_en.desc()).all()
    return render_template('geomatica/carga_ssbc.html', cargas=mapas, estados_flujo=ESTADOS_TRANSACCION)

@geomatica_bp.route('/procesar', methods=['POST'])
@login_required
def procesar_archivo():
    if 'archivo_ssbc' not in request.files:
        flash('No se encontró ningún archivo en la petición.', 'error')
        return redirect(url_for('geomatica.index'))
        
    archivo = request.files['archivo_ssbc']
    
    if archivo.filename == '':
        flash('No seleccionó ningún archivo válido para subir.', 'error')
        return redirect(url_for('geomatica.index'))
        
    if archivo:
        nombre_archivo = archivo.filename.strip()
        tipo_mapa = request.form.get('tipo_mapa', 'riesgo').strip()
        cobertura = request.form.get('cobertura', 'Regional').strip()

        mapa = MapaRegistro(
            nombre=f'Mapa {tipo_mapa.capitalize()} {datetime.utcnow().strftime("%Y-%m-%d")}',
            tipo_mapa=tipo_mapa,
            archivo=nombre_archivo,
            cobertura=cobertura,
            responsable=current_user.nombre,
        )
        db.session.add(mapa)
        db.session.flush()

        db.session.add(BitacoraTransaccion(
            modulo='mapas',
            registro_id=mapa.id,
            accion='carga_archivo',
            estado_nuevo=mapa.estado,
            usuario=current_user.nombre,
            detalle=f'Archivo {nombre_archivo} cargado para {tipo_mapa}',
        ))
        db.session.commit()

        flash(f'Archivo "{nombre_archivo}" registrado para procesamiento de mapas.', 'success')

    return redirect(url_for('geomatica.index'))


@geomatica_bp.route('/<int:mapa_id>/estado', methods=['POST'])
@login_required
def cambiar_estado(mapa_id):
    mapa = MapaRegistro.query.get_or_404(mapa_id)
    nuevo_estado = request.form.get('estado', '').strip()
    if nuevo_estado not in ESTADOS_TRANSACCION:
        flash('Estado de flujo invalido.', 'error')
        return redirect(url_for('geomatica.index'))

    mapa.estado = nuevo_estado
    db.session.add(BitacoraTransaccion(
        modulo='mapas',
        registro_id=mapa.id,
        accion='cambio_estado',
        estado_nuevo=nuevo_estado,
        usuario=current_user.nombre,
        detalle=f'Mapa {mapa.nombre} actualizado',
    ))
    db.session.commit()

    flash('Estado del mapa actualizado.', 'success')
    return redirect(url_for('geomatica.index'))