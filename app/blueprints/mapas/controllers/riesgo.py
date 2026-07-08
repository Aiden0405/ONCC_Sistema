from datetime import datetime

from flask import flash, redirect, Blueprint, jsonify, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.blueprints.mapas import mapas_bp
from app.constants import ESTADOS_TRANSACCION
from app.models.bitacora import BitacoraTransaccion
from app.models.geomatica import MapaRiesgo
from geoalchemy2.functions import ST_AsGeoJSON, ST_GeomFromGeoJSON
import json

mapa_bp = Blueprint('mapa_riesgo', __name__)
@mapas_bp.route('/geomatica/')
@login_required
def vista_mapa():
    return render_template('mapa_riesgo.html')

# ==========================================
#          API REST - CRUD OPERACIONES
# ==========================================

# 1. CREATE
@mapa_bp.route('/api/mapas', methods=['POST'])
def crear_mapa():
    datos = request.get_json()
    nombre = datos.get('nombre')
    descripcion = datos.get('descripcion')
    
    # El objeto espacial llega desde el frontend en formato estándar GeoJSON
    geojson_geom = json.dumps(datos.get('geometria')) 

    nuevo_mapa = MapaRiesgo(
        nombre=nombre,
        descripcion=descripcion,
        geometria=ST_GeomFromGeoJSON(geojson_geom)
    )
    
    db.session.add(nuevo_mapa)
    db.session.commit() # El Trigger de PostgreSQL registra de forma automática la acción en Seguridad
    
    return jsonify({
        'status': 'success', 
        'message': 'Capa de mapa de riesgo registrada con éxito', 
        'id': nuevo_mapa.id
    }), 201

# 2. READ
@mapa_bp.route('/api/mapas/<int:id>', methods=['GET'])
def obtener_mapa(id):
    resultado = db.session.query(
        MapaRiesgo.id,
        MapaRiesgo.nombre,
        MapaRiesgo.descripcion,
        ST_AsGeoJSON(MapaRiesgo.geometria).label('geojson'),
        MapaRiesgo.fecha_creacion
    ).filter(MapaRiesgo.id == id).first()

    if not resultado:
        return jsonify({'message': 'El mapa de riesgo solicitado no existe'}), 404

    return jsonify({
        'id': resultado.id,
        'nombre': resultado.nombre,
        'descripcion': resultado.descripcion,
        'geometria': json.loads(resultado.geojson),
        'fecha_creacion': resultado.fecha_creacion.isoformat() if resultado.fecha_creacion else None
    }), 200

# 3. UPDATE
@mapa_bp.route('/api/mapas/<int:id>', methods=['PUT'])
def actualizar_mapa(id):
    mapa = MapaRiesgo.query.get(id)
    if not mapa:
        return jsonify({'message': 'El mapa de riesgo no fue encontrado'}), 404

    datos = request.get_json()
    mapa.nombre = datos.get('nombre', mapa.nombre)
    mapa.descripcion = datos.get('descripcion', mapa.descripcion)
    
    if 'geometria' in datos:
        geojson_geom = json.dumps(datos.get('geometria'))
        mapa.geometria = ST_GeomFromGeoJSON(geojson_geom)

    db.session.commit() # Disparador automático (Trigger) registra la actualización
    return jsonify({'status': 'success', 'message': 'Datos del mapa de riesgo actualizados'}), 200

# 4. DELETE
@mapa_bp.route('/api/mapas/<int:id>', methods=['DELETE'])
def eliminar_mapa(id):
    mapa = MapaRiesgo.query.get(id)
    if not mapa:
        return jsonify({'message': 'El mapa de riesgo no fue encontrado'}), 404

    db.session.delete(mapa)
    db.session.commit() # El Trigger captura los datos y los aloja en la Bitácora
    
    return jsonify({'status': 'success', 'message': 'Capa de riesgo eliminada permanentemente del sistema'}), 200
@mapa_bp.route('/mapa-riesgo', methods=['GET'])
def mapas_riesgo_index():
    # Se consultan todos los mapas registrados para llenar el historial
    cargas = MapaRiesgo.query.all()
    
    # Se definen los estados posibles para el flujo (select del HTML)
    estados_flujo = ['Pendiente', 'En Revisión', 'Aprobado', 'Rechazado']
    
    return render_template(
        'geomatica/carga_ssbc.html', 
        cargas=cargas, 
        estados_flujo=estados_flujo
    )
@mapa_bp.route('/cambiar_estado/<int:mapa_id>', methods=['POST'])
def cambiar_estado(mapa_id):
    # Buscar el registro usando el modelo actualizado MapaRiesgo
    mapa = MapaRiesgo.query.get(mapa_id)
    
    if not mapa:
        # Manejo de error si el registro no existe
        return "Registro no encontrado", 404

    # Capturar el nuevo estado enviado desde el formulario <select name="estado">
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado:
        mapa.estado = nuevo_estado
        db.session.commit() # El disparador (trigger) registrará automáticamente esta acción en la bitácora
        
    # Redirigir nuevamente a la vista principal. 
    # (El nombre 'geomatica.vista_mapa' debe coincidir con el nombre de registro del blueprint)
    return redirect(url_for('geomatica.vista_mapa'))   
@mapa_bp.route('/procesar_archivo', methods=['POST'])
def procesar_archivo():
    # 1. Captura de datos de texto del formulario
    nombre = request.form.get('nombre')
    version = request.form.get('version')
    cobertura = request.form.get('cobertura')
    
    # 2. Captura del archivo físico
    archivo = request.files.get('archivo_ssbc')
    
    if archivo and archivo.filename != '':
        nombre_archivo = secure_filename(archivo.filename)
        # Aquí se integrará la lógica de extracción de coordenadas del Excel/CSV
        # utilizando pandas o geopandas para generar el objeto ST_GeomFromGeoJSON
        
        # Simulación de guardado temporal (Ajustar ruta según configuración del servidor)
        # ruta_guardado = os.path.join('app/static/uploads', nombre_archivo)
        # archivo.save(ruta_guardado)
        
        # Una vez procesada la geometría, se instancia el modelo MapaRiesgo y se ejecuta db.session.commit()
        pass

    # Redirección a la vista principal para recargar la tabla del historial
    # Se asume que el blueprint está registrado bajo el prefijo o nombre 'geomatica' o 'mapas'
    return redirect(url_for('geomatica.mapas_riesgo_index'))