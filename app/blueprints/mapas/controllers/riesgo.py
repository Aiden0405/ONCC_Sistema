import os
import json
from datetime import datetime

from flask import flash, redirect, jsonify, render_template, request, url_for, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from geoalchemy2.functions import ST_AsGeoJSON, ST_GeomFromGeoJSON

from app import db
from app.models.geomatica import MapaRiesgo, ElementoMapaRiesgo
from app.models.actividad import Actividad
from app.models.esquema_activo import ComunidadActiva 

@login_required
def mapas_riesgo_index():
    return render_template('geomatica/mapa_riesgo.html')

@login_required
def vista_carga_ssbc():
    """ Vista del formulario de carga con selector de actividades """
    cargas = MapaRiesgo.query.order_by(MapaRiesgo.fecha_registro.desc()).all()
    actividades_disponibles = Actividad.query.filter_by(tipo_actividad='MAPA_RIESGO').all()
    estados_flujo = ['Pendiente', 'En Revisión', 'Aprobado', 'Rechazado']
    
    return render_template(
        'geomatica/carga_ssbc.html', 
        cargas=cargas, 
        actividades_disponibles=actividades_disponibles,
        estados_flujo=estados_flujo
    )

@login_required
def vista_dibujar_mapa(mapa_id):
    """ Renderiza la herramienta de dibujo Leaflet sobre el KML cargado o lienzo en blanco """
    mapa = MapaRiesgo.query.get_or_404(mapa_id)
    return render_template('geomatica/dibujar_mapa.html', mapa=mapa)

@login_required
def procesar_archivo():
    # 1. Recibir datos del formulario
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    id_act_dinamico = request.form.get('id_actividad') 
    archivo = request.files.get('archivo_mapa') 

    if not id_act_dinamico:
        flash('Debe seleccionar una actividad válida de la lista.', 'error')
        return redirect(url_for('geomatica.carga_ssbc'))

    # 2. Bloque Transaccional Atómico
    try:
        nuevo_mapa = MapaRiesgo(
            nombre=nombre,
            descripcion=descripcion,
            id_actividad=int(id_act_dinamico),
            tipo_actividad='MAPA_RIESGO',
            fecha_registro=datetime.now(),
            ruta_kml=None,
            ruta_imagen_mapa=None 
        )

        # 3. Validar archivo físico
        if archivo and archivo.filename != '':
            filename = secure_filename(archivo.filename)
            extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

            if extension not in ['kml', 'png', 'jpg', 'jpeg']:
                flash('Formato no soportado. Por favor suba un archivo .kml o una imagen (.png, .jpg)', 'error')
                return redirect(url_for('geomatica.carga_ssbc'))

            if extension == 'kml':
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'mapas', 'kml')
                os.makedirs(upload_folder, exist_ok=True)
                ruta_guardado = os.path.join(upload_folder, filename)
                archivo.save(ruta_guardado)
                
                nuevo_mapa.ruta_kml = f'uploads/mapas/kml/{filename}'
                
                db.session.add(nuevo_mapa)
                db.session.commit()
                
                flash('Mapa KML registrado con éxito. Ajuste o dibuje los perímetros en el editor.', 'success')
                return redirect(url_for('geomatica.dibujar_mapa', mapa_id=nuevo_mapa.id_mapa_riesgo))

            elif extension in ['png', 'jpg', 'jpeg']:
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'mapas', 'imagenes')
                os.makedirs(upload_folder, exist_ok=True)
                ruta_guardado = os.path.join(upload_folder, filename)
                archivo.save(ruta_guardado)
                
                nuevo_mapa.ruta_imagen_mapa = f'uploads/mapas/imagenes/{filename}'
                
                db.session.add(nuevo_mapa)
                db.session.commit()
                
                flash('Imagen del mapa de riesgo guardada exitosamente de forma directa.', 'success')
                return redirect(url_for('geomatica.carga_ssbc'))
        else:
            db.session.add(nuevo_mapa)
            db.session.commit()
            flash('Información base registrada. Se ha abierto el lienzo interactivo para digitalizar los riesgos.', 'success')
            return redirect(url_for('geomatica.dibujar_mapa', mapa_id=nuevo_mapa.id_mapa_riesgo))

    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        if 'validar_previa_sensibilizacion' in error_msg or 'Restricción de ONCC' in error_msg:
            flash('La comunidad asociada debe contar con una actividad de sensibilización previa.', 'error')
        elif 'UniqueViolation' in error_msg or 'llave duplicada' in error_msg.lower():
            flash('Error: Ya existe un mapa asignado a esta actividad.', 'error')
        else:
            flash(f'Error en la transacción: {error_msg}', 'error')
        return redirect(url_for('geomatica.carga_ssbc'))

@login_required
def obtener_todos_mapas():
    query = db.session.query(MapaRiesgo, Actividad, ComunidadActiva).join(
        Actividad, (MapaRiesgo.id_actividad == Actividad.id_actividad) & 
                   (MapaRiesgo.tipo_actividad == Actividad.tipo_actividad)
    ).join(
        ComunidadActiva, Actividad.id_comunidad == ComunidadActiva.id_comunidad
    )

    resultados = query.order_by(MapaRiesgo.fecha_registro.desc()).all()
    
    mapas_json = []
    for mapa, actividad, comunidad in resultados:
        mapas_json.append({
            'id': mapa.id_mapa_riesgo,
            'nombre': mapa.nombre,
            'descripcion': mapa.descripcion,
            'comunidad': comunidad.nombre_comunidad,
            'fecha_registro': mapa.fecha_registro.isoformat() if mapa.fecha_registro else None,
            'tipo_archivo': 'KML' if mapa.ruta_kml else ('Imagen' if mapa.ruta_imagen_mapa else 'Digitalizado')
        })

    return jsonify(mapas_json), 200

@login_required
def obtener_mapa(mapa_id):
    mapa = MapaRiesgo.query.get(mapa_id)
    if not mapa:
        return jsonify({'message': 'Mapa no encontrado'}), 404

    elementos = ElementoMapaRiesgo.query.filter_by(id_mapa_riesgo=mapa_id).all()
    features = []
    for el in elementos:
        geom_json = db.session.scalar(ST_AsGeoJSON(el.geometria))
        features.append({
            "type": "Feature",
            "properties": {
                "categoria": el.categoria,
                "subcategoria": el.subcategoria,
                "descripcion": el.descripcion
            },
            "geometry": json.loads(geom_json)
        })

    return jsonify({
        'id': mapa.id_mapa_riesgo,
        'nombre': mapa.nombre,
        'descripcion': mapa.descripcion,
        'ruta_kml': mapa.ruta_kml,
        'ruta_imagen_mapa': mapa.ruta_imagen_mapa,
        'geometria': {"type": "FeatureCollection", "features": features} if features else None
    }), 200

@login_required
def crear_mapa():
    """ Guarda el dibujo individual recibido desde leaflet """
    datos = request.get_json()
    id_mapa = datos.get('id_mapa_riesgo') 
    geojson_geom = json.dumps(datos.get('geometria')) 

    nuevo_elemento = ElementoMapaRiesgo(
        id_mapa_riesgo=id_mapa,
        categoria=datos.get('categoria', 'General'),
        subcategoria=datos.get('subcategoria', 'General'),
        descripcion=datos.get('descripcion', ''),
        geometria=ST_GeomFromGeoJSON(geojson_geom)
    )
    db.session.add(nuevo_elemento)
    
    # NUEVO: Actualizar la fecha del mapa principal al agregar un dibujo
    mapa_padre = MapaRiesgo.query.get(id_mapa)
    if mapa_padre:
        mapa_padre.fecha_registro = datetime.now()

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Elemento geográfico registrado con éxito'}), 201
@login_required
def eliminar_mapa(mapa_id):
    mapa = MapaRiesgo.query.get(mapa_id)
    if not mapa:
        return jsonify({'status': 'error', 'message': 'Mapa no encontrado'}), 404
    try:
        db.session.delete(mapa)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Capa de riesgo eliminada con éxito.'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Dependencias en la base de datos impiden su eliminación.'}), 500

@login_required
def actualizar_mapa(mapa_id):
    """ Modifica el nombre y descripción del mapa desde el panel """
    mapa = MapaRiesgo.query.get(mapa_id)
    if not mapa:
        return jsonify({'status': 'error', 'message': 'Mapa no encontrado'}), 404

    datos = request.get_json()
    
    # NUEVO: Permitir editar el nombre y actualizar la fecha
    mapa.nombre = datos.get('nombre', mapa.nombre)
    mapa.descripcion = datos.get('descripcion', mapa.descripcion)
    mapa.fecha_registro = datetime.now()
    
    # Esta parte se mantiene por si en el futuro envías la geometría completa por aquí
    if 'geometria' in datos:
        geojson_geom = json.dumps(datos.get('geometria'))
        mapa.geometria = ST_GeomFromGeoJSON(geojson_geom)

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Datos actualizados correctamente'}), 200
@mapas_bp.route('/obtener_mapas', methods=['GET'])
@login_required

def obtener_mapas_filtrados():
    # Obtener parámetros de la URL (?estado=1&municipio=2...)
    estado_id = request.args.get('estado')
    municipio_id = request.args.get('municipio')
    parroquia_id = request.args.get('parroquia')
    comunidad_id = request.args.get('comunidad')

    # Consulta base
    query = db.session.query(MapaRiesgo, Actividad, ComunidadActiva).join(...)

    # Filtros condicionales
    if estado_id: query = query.filter(ComunidadActiva.id_estado == estado_id)
    if municipio_id: query = query.filter(ComunidadActiva.id_municipio == municipio_id)
    # ... (repetir para los demás)

    resultados = query.all()
    # ... (convertir a JSON y retornar)
def obtener_todos_mapas():
    # Join con Actividad y Comunidad para poder filtrar
    query = db.session.query(MapaRiesgo, Actividad, ComunidadActiva).join(
        Actividad, (MapaRiesgo.id_actividad == Actividad.id_actividad) & 
                   (MapaRiesgo.tipo_actividad == Actividad.tipo_actividad)
    ).join(
        ComunidadActiva, Actividad.id_comunidad == ComunidadActiva.id_comunidad
    )

    resultados = query.order_by(MapaRiesgo.fecha_registro.desc()).all()
    
    mapas_json = []
    for mapa, actividad, comunidad in resultados:
        mapas_json.append({
            'id': mapa.id_mapa_riesgo,
            'nombre': mapa.nombre,
            'descripcion': mapa.descripcion,
            'comunidad': comunidad.nombre_comunidad,
            'fecha_registro': mapa.fecha_registro.isoformat() if mapa.fecha_registro else None,
            'tipo_archivo': 'KML' if mapa.ruta_kml else ('Imagen' if mapa.ruta_imagen_mapa else 'Digitalizado')
        })

    return jsonify(mapas_json), 200