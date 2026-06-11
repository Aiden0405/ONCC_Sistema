import os
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.blueprints.mapas import mapas_bp
from app.constants import ESTADOS_TRANSACCION
from app.models.bitacora import BitacoraTransaccion
from app.models.geomatica import MapaRegistro

# Extensiones permitidas por seguridad
EXTENSIONES_PERMITIDAS = {'xlsx', 'xls', 'ssbc', 'csv'}

def archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS

@mapas_bp.route('/geomatica/')
@login_required
def mapas_riesgo_index():
    mapas = MapaRegistro.query.order_by(MapaRegistro.creado_en.desc()).all()
    return render_template('geomatica/carga_ssbc.html', cargas=mapas, estados_flujo=ESTADOS_TRANSACCION)

# --- CREATE ---
@mapas_bp.route('/geomatica/procesar', methods=['POST'])
@login_required
def procesar_archivo():
    # 1. Validaciones del lado del servidor
    nombre = request.form.get('nombre', '').strip()
    version = request.form.get('version', '').strip()
    cobertura = request.form.get('cobertura', '').strip()
    tipo_mapa = request.form.get('tipo_mapa', 'riesgo').strip()

    if not nombre or not version or not cobertura:
        flash('Todos los campos de texto son obligatorios.', 'error')
        return redirect(url_for('mapas.mapas_riesgo_index'))

    if 'archivo_ssbc' not in request.files:
        flash('Debe adjuntar un archivo de data.', 'error')
        return redirect(url_for('mapas.mapas_riesgo_index'))

    archivo = request.files['archivo_ssbc']

    if archivo.filename == '' or not archivo_permitido(archivo.filename):
        flash('Archivo inválido o formato no permitido (.ssbc, .xlsx, .csv).', 'error')
        return redirect(url_for('mapas.mapas_riesgo_index'))

    # 2. Sanitizar el nombre del archivo
    nombre_archivo = secure_filename(archivo.filename)

    try:
        # Aquí guardarías el archivo físicamente: archivo.save(os.path.join(ruta, nombre_archivo))

        # 3. Preparar la Inserción Multi-tabla
        nuevo_mapa = MapaRegistro(
            nombre=nombre,
            tipo_mapa=tipo_mapa,
            version=version,
            archivo=nombre_archivo,
            cobertura=cobertura,
            responsable=current_user.nombre
        )
        db.session.add(nuevo_mapa)
        db.session.flush() # Flush nos da el ID del nuevo_mapa sin hacer el commit final

        nueva_bitacora = BitacoraTransaccion(
            modulo='mapas_registro',
            registro_id=nuevo_mapa.id,
            accion='Crear',
            estado_nuevo=nuevo_mapa.estado,
            usuario=current_user.correo, # Tu BD usa correo en la bitácora según el volcado
            detalle=f'Carga de capa de {tipo_mapa}: {nombre_archivo}'
        )
        db.session.add(nueva_bitacora)

        # 4. Confirmar todo junto
        db.session.commit()
        flash(f'Mapa "{nombre}" registrado exitosamente.', 'success')

    except Exception as e:
        db.session.rollback() # Si algo falla, revertimos para no dejar datos a medias
        flash(f'Error al guardar en la base de datos: {str(e)}', 'error')

    return redirect(url_for('mapas.mapas_riesgo_index'))

# --- UPDATE (Estado) ---
@mapas_bp.route('/geomatica/<int:mapa_id>/estado', methods=['POST'])
@login_required
def cambiar_estado(mapa_id):
    mapa = MapaRegistro.query.get_or_404(mapa_id)
    nuevo_estado = request.form.get('estado', '').strip()
    
    if nuevo_estado not in ESTADOS_TRANSACCION:
        flash('Estado de flujo inválido.', 'error')
        return redirect(url_for('mapas.mapas_riesgo_index'))

    try:
        mapa.estado = nuevo_estado
        
        db.session.add(BitacoraTransaccion(
            modulo='mapas_registro',
            registro_id=mapa.id,
            accion='Modificar',
            estado_nuevo=nuevo_estado,
            usuario=current_user.correo,
            detalle=f'Actualización de estado a {nuevo_estado}'
        ))
        db.session.commit()
        flash('Estado actualizado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al actualizar el estado.', 'error')

    return redirect(url_for('mapas.mapas_riesgo_index'))

# --- DELETE ---
@mapas_bp.route('/geomatica/<int:mapa_id>/eliminar', methods=['POST'])
@login_required
def eliminar_mapa(mapa_id):
    mapa = MapaRegistro.query.get_or_404(mapa_id)
    
    try:
        db.session.add(BitacoraTransaccion(
            modulo='mapas_registro',
            registro_id=mapa.id,
            accion='Eliminar',
            estado_nuevo=None,
            usuario=current_user.correo,
            detalle=f'Se eliminó el mapa: {mapa.nombre}'
        ))
        db.session.delete(mapa)
        db.session.commit()
        flash('Mapa eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se pudo eliminar el mapa por restricciones en la base de datos.', 'error')

    return redirect(url_for('mapas.mapas_riesgo_index'))