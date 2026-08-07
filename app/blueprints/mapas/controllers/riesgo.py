import os
import json
import psycopg2
from datetime import datetime
import xml.etree.ElementTree as ET
from flask import flash, redirect, jsonify, render_template, request, url_for, current_app, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from geoalchemy2.functions import ST_AsGeoJSON, ST_GeomFromGeoJSON
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
import kml2geojson
from app import db
from contextlib import contextmanager
# NOTA: Asegúrate de que el modelo ElementosMapaRiesgo esté bien importado (en tu código original decías ElementoMapaRiesgo en algunas partes, lo he unificado)
from app.models.geomatica import MapaRiesgo, ElementosMapaRiesgo, Simbologia
from app.models.actividad import Actividad
from app.models.esquema_activo import ComunidadActiva, ParroquiaActiva, MunicipioActivo, EstadoActivo

# VALIDACIÓN SEPARADA POR TIPO DE MÓDULO
EXTENSIONES_MAPAS = {'png', 'jpg', 'jpeg', 'svg', 'webp', 'kml', 'geojson'}
EXTENSIONES_SIMBOLOS = {'png', 'jpg', 'jpeg', 'svg', 'webp'}

def archivo_permitido(filename, extensiones_validas):
    """ Verifica la extensión contra la lista específica que se le pase """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensiones_validas


def obtener_poligono_kml(filepath):
    """
    Parsea un KML estandarizado (Google Earth, QGIS, etc.) buscando EXCLUSIVAMENTE el primer <Polygon>.
    Soporta anidamientos profundos, saltos de línea/tabs en coordenadas y remueve altitudes (3D).
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Eliminar namespaces de XML dinámicamente para iteración limpia
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Buscar la primera etiqueta <Polygon> en cualquier nivel del documento
        for polygon in root.iter('Polygon'):
            coords_node = polygon.find('.//coordinates')
            
            if coords_node is not None and coords_node.text:
                coord_tuples = []
                # split() separa automáticamente por espacios, saltos de línea y tabs
                puntos_raw = coords_node.text.strip().split()
                
                for pt in puntos_raw:
                    parts = pt.split(',')
                    if len(parts) >= 2:
                        try:
                            # Se toma partes[0] (Lon) y partes[1] (Lat), descartando la altitud (3D)
                            coord_tuples.append([float(parts[0]), float(parts[1])])
                        except ValueError:
                            continue
                
                if len(coord_tuples) >= 3:
                    # Garantizar cierre del polígono si la primera coordenada no coincide con la última
                    if coord_tuples[0] != coord_tuples[-1]:
                        coord_tuples.append(coord_tuples[0])
                        
                    return {
                        "type": "Polygon",
                        "coordinates": [coord_tuples]
                    }
    except Exception as e:
        print(f"Error parseando el polígono estandarizado del KML: {e}")
        
    return None


@login_required
def extraer_y_procesar_vectores(filepath, nuevo_mapa):
    """
    Busca únicamente el polígono delimitador de la comunidad en el archivo subido
    y lo asigna a 'poligonal_comunidad' usando las funciones de PostGIS (WGS84 2D MultiPolygon).
    Omite puntos y líneas para no saturar ni generar inconsistencias con la simbología.
    """
    geom_json = None

    if filepath.endswith('.kml'):
        geom_json = obtener_poligono_kml(filepath)
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if data.get('type') in ['Polygon', 'MultiPolygon']:
                geom_json = data
            else:
                features = data.get('features', []) if data.get('type') == 'FeatureCollection' else [data]
                for feat in features:
                    g = feat.get('geometry', {})
                    if g.get('type') in ['Polygon', 'MultiPolygon']:
                        geom_json = g
                        break

    if geom_json:
        geom_str = json.dumps(geom_json)
        
        # Inyección espacial mediante PostGIS (2D, WGS84, MultiPolygon)
        nuevo_mapa.poligonal_comunidad = db.func.ST_Multi(
            db.func.ST_SetSRID(
                db.func.ST_Force2D(db.func.ST_GeomFromGeoJSON(geom_str)), 
                4326
            )
        )
    else:
        print("Aviso: El archivo no contenía un polígono delimitador válido. Lienzo en blanco.")


@login_required
def catalogo_index():
    return render_template('geomatica/gestionar_simbologia.html')


@login_required
def mapas_riesgo_index():
    return render_template('geomatica/mapa_riesgo.html')


@login_required
def vista_carga_ssbc():
    """ Vista del formulario de carga con selector de actividades """
    cargas = MapaRiesgo.query.order_by(MapaRiesgo.fecha_creacion.desc()).all()
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
    """ Renderiza la herramienta de dibujo Leaflet """
    mapa = MapaRiesgo.query.get_or_404(mapa_id)
    return render_template('geomatica/dibujar_mapa.html', mapa=mapa)


@login_required
def crear_mapa(): 
    """ Guarda un dibujo individual recibido desde Leaflet """
    datos = request.get_json()
    if not datos or 'id_simbologia' not in datos or 'id_mapa_riesgo' not in datos:
        return jsonify({'status': 'error', 'message': 'Faltan datos requeridos (simbología o mapa).'}), 400

    id_mapa = datos.get('id_mapa_riesgo') 
    geojson_geom = json.dumps(datos.get('geometria')) 

    try:
        nuevo_elemento = ElementosMapaRiesgo(
            id_mapa_riesgo=int(id_mapa),
            id_simbologia=int(datos.get('id_simbologia')),
            nombre_propio=datos.get('nombre_propio', '')[:100],
            descripcion_especifica=datos.get('descripcion', '')[:1000],
            estilo_personalizado=datos.get('estilo_personalizado') or datos.get('estiloCustom'),
            geom=db.func.ST_SetSRID(db.func.ST_Force2D(db.func.ST_GeomFromGeoJSON(geojson_geom)), 4326)
        )
        db.session.add(nuevo_elemento)
        db.session.flush()
        
        id_recien_creado = nuevo_elemento.id_elemento
        
        mapa_padre = MapaRiesgo.query.get(id_mapa)
        if mapa_padre:
            mapa_padre.fecha_creacion = datetime.now()

        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Elemento geográfico registrado con éxito',
            'id_elemento': id_recien_creado
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error al guardar elemento: {str(e)}'}), 500


@login_required
def procesar_archivo():
    """ Procesa la carga inicial del mapa base y responde dinámicamente según el método o cliente """
    if request.method == 'GET':
        return redirect(url_for('geomatica.carga_ssbc'))

    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    id_act_dinamico = request.form.get('id_actividad') 
    archivo = request.files.get('archivo_mapa') 

    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    if not id_act_dinamico or not str(id_act_dinamico).isdigit():
        msg = 'Debe seleccionar una actividad válida de la lista.'
        if es_ajax:
            return jsonify({'status': 'error', 'message': msg}), 400
        flash(msg, 'error')
        return redirect(url_for('geomatica.carga_ssbc'))

    try:
        nuevo_mapa = MapaRiesgo(
            nombre=nombre,
            descripcion=descripcion,
            id_actividad=int(id_act_dinamico),
            tipo_actividad='MAPA_RIESGO',
            fecha_creacion=datetime.now(),
            ruta_kml=None,
            ruta_imagen_mapa=None 
        )
        
        db.session.add(nuevo_mapa)
        db.session.flush()

        if archivo and archivo.filename != '':
            if not archivo_permitido(archivo.filename, EXTENSIONES_MAPAS):
                db.session.rollback()
                msg = 'Formato no soportado. Suba .kml, .geojson o una imagen válida.'
                if es_ajax:
                    return jsonify({'status': 'error', 'message': msg}), 400
                flash(msg, 'error')
                return redirect(url_for('geomatica.carga_ssbc'))

            filename = secure_filename(archivo.filename)
            extension = filename.rsplit('.', 1)[1].lower()

            if extension in ['kml', 'geojson']:
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'mapas', 'vectores') 
                os.makedirs(upload_folder, exist_ok=True)
                ruta_guardado = os.path.join(upload_folder, filename)
                archivo.save(ruta_guardado)
                
                nuevo_mapa.ruta_kml = f'uploads/mapas/vectores/{filename}' 
                
                # Procesa y extrae la poligonal de la comunidad
                extraer_y_procesar_vectores(ruta_guardado, nuevo_mapa)
                
                db.session.commit()
                
                url_destino = url_for('geomatica.dibujar_mapa', mapa_id=nuevo_mapa.id_mapa_riesgo)
                msg = 'Vector cartográfico procesado con éxito.'

                if es_ajax:
                    return jsonify({
                        'status': 'success',
                        'message': msg,
                        'mapa_id': nuevo_mapa.id_mapa_riesgo,
                        'redirect_url': url_destino
                    }), 200

                flash(msg, 'success')
                return redirect(url_destino)

            elif extension in ['png', 'jpg', 'jpeg', 'svg', 'webp']:
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'mapas', 'imagenes')
                os.makedirs(upload_folder, exist_ok=True)
                ruta_guardado = os.path.join(upload_folder, filename)
                archivo.save(ruta_guardado)
                
                nuevo_mapa.ruta_imagen_mapa = f'uploads/mapas/imagenes/{filename}'
                db.session.commit()
                
                url_destino = url_for('geomatica.carga_ssbc')
                msg = 'Imagen del mapa de riesgo guardada exitosamente.'

                if es_ajax:
                    return jsonify({
                        'status': 'success',
                        'message': msg,
                        'mapa_id': nuevo_mapa.id_mapa_riesgo,
                        'redirect_url': url_destino
                    }), 200

                flash(msg, 'success')
                return redirect(url_destino) 
        else:
            db.session.commit()
            url_destino = url_for('geomatica.dibujar_mapa', mapa_id=nuevo_mapa.id_mapa_riesgo)
            msg = 'Información base registrada en lienzo en blanco.'

            if es_ajax:
                return jsonify({
                    'status': 'success',
                    'message': msg,
                    'mapa_id': nuevo_mapa.id_mapa_riesgo,
                    'redirect_url': url_destino
                }), 200

            flash(msg, 'success')
            return redirect(url_destino)

    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        if es_ajax:
            return jsonify({'status': 'error', 'message': f'Error en la transacción: {error_msg}'}), 500
        flash(f'Error en la transacción: {error_msg}', 'error')
        return redirect(url_for('geomatica.carga_ssbc'))
@login_required
def obtener_mapa(mapa_id):
    """ Envía la data espacial (comunidad, encuadre y elementos dibujados) al frontend """
    mapa = MapaRiesgo.query.get(mapa_id)
    if not mapa:
        return jsonify({'message': 'Mapa no encontrado'}), 404

    # 1. Poligonal base de la comunidad (PostGIS)
    poligonal_base = None
    if getattr(mapa, 'poligonal_comunidad', None) is not None:
        geom_base_str = db.session.scalar(db.func.ST_AsGeoJSON(mapa.poligonal_comunidad))
        poligonal_base = json.loads(geom_base_str) if geom_base_str else None

    # 2. Consultamos los elementos dibujados en la tabla ElementosMapaRiesgo
    consulta = db.session.query(
        ElementosMapaRiesgo, 
        Simbologia
    ).join(
        Simbologia, ElementosMapaRiesgo.id_simbologia == Simbologia.id_simbologia
    ).filter(
        ElementosMapaRiesgo.id_mapa_riesgo == mapa_id
    ).all()

    features = []
    for el, simb in consulta:
        geom_json = db.session.scalar(db.func.ST_AsGeoJSON(el.geom))
        features.append({
            "type": "Feature",
            "properties": {
                "id": el.id_elemento, 
                "id_elemento": el.id_elemento, 
                "id_simbologia": el.id_simbologia,
                "categoria": simb.categoria,
                "nombre_elemento": simb.nombre_elemento,
                "nombre_propio": el.nombre_propio or "",
                "descripcion": el.descripcion_especifica or "",
                "estilo_defecto": simb.estilo_defecto,
                "estilo_personalizado": el.estilo_personalizado
            },
            "geometry": json.loads(geom_json) if geom_json else None
        })

    # 3. Retornamos la respuesta separando encuadre de elementos dibujados
    return jsonify({
        'id': mapa.id_mapa_riesgo,
        'nombre': mapa.nombre,
        'descripcion': mapa.descripcion,
        'ruta_kml': mapa.ruta_kml,
        'poligonal_comunidad': poligonal_base,
        'limites_layout': mapa.limites_layout,  # <-- Solo las coordenadas del Bounding Box
        'elementos_riesgo': features           # <-- La lista de elementos dibujados
    }), 200

@login_required
def actualizar_mapa(mapa_id):
    mapa = MapaRiesgo.query.get(mapa_id)
    if not mapa:
        return jsonify({'status': 'error', 'message': 'El mapa no existe.'}), 404

    datos = request.get_json() or {}

    if 'nombre' in datos and datos['nombre']: 
        mapa.nombre = datos['nombre'].strip()[:100]
    
    if 'descripcion' in datos and datos['descripcion']:
        mapa.descripcion = datos['descripcion'].strip()[:1000]

    mapa.fecha_creacion = datetime.now()

    # Poligonal comunidad
    clave_geom = 'geometria_comunidad' if 'geometria_comunidad' in datos else ('poligonal_comunidad' if 'poligonal_comunidad' in datos else None)
    if clave_geom is not None:
        geom_val = datos.get(clave_geom)
        mapa.poligonal_comunidad = ST_GeomFromGeoJSON(json.dumps(geom_val)) if geom_val else None

    # Guarda únicamente las coordenadas del encuadre
    if 'limites_layout' in datos:
        mapa.limites_layout = datos['limites_layout']

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Límites del mapa actualizados correctamente.'}), 200
@login_required
def eliminar_mapa(mapa_id):
    """ Elimina el mapa base, sus polígonos asociados y limpia los archivos físicos """
    mapa = MapaRiesgo.query.get(mapa_id)
    if not mapa:
        return jsonify({'status': 'error', 'message': 'Operación rechazada: El mapa no existe.'}), 404
    
    try:
        ruta_kml_rollback = mapa.ruta_kml
        ruta_img_rollback = mapa.ruta_imagen_mapa

        db.session.delete(mapa)
        db.session.commit()

        # VALIDACIÓN: Se agregó manejo de errores al intentar borrar archivos del SO
        if ruta_kml_rollback:
            path_kml = os.path.join(current_app.root_path, 'static', ruta_kml_rollback)
            if os.path.exists(path_kml):
                try: os.remove(path_kml)
                except OSError: pass
                
        if ruta_img_rollback:
            path_img = os.path.join(current_app.root_path, 'static', ruta_img_rollback)
            if os.path.exists(path_img):
                try: os.remove(path_img)
                except OSError: pass

        return jsonify({'status': 'success', 'message': 'Transacción de mapa cancelada/eliminada con éxito.'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Dependencias en la base de datos impiden la cancelación.'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Ocurrió un error inesperado al eliminar.'}), 500

@login_required
def obtener_todos_mapas():
    """ Obtiene la lista de mapas aplicando los filtros de ubicación """
    estado_id = request.args.get('estado', type=int)
    municipio_id = request.args.get('municipio', type=int)
    parroquia_id = request.args.get('parroquia', type=int)
    comunidad_id = request.args.get('comunidad', type=int)

    # El JOIN compuesto aquí está excelente y maneja perfecto la validación espacial-relacional
    query = db.session.query(MapaRiesgo, Actividad, ComunidadActiva).join(
        Actividad, (MapaRiesgo.id_actividad == Actividad.id_actividad) & 
                   (MapaRiesgo.tipo_actividad == Actividad.tipo_actividad)
    ).join(
        ComunidadActiva, Actividad.id_comunidad == ComunidadActiva.id_comunidad
    ).join(
        ParroquiaActiva, ComunidadActiva.id_parroquia == ParroquiaActiva.id_parroquia
    ).join(
        MunicipioActivo, ParroquiaActiva.id_municipio == MunicipioActivo.id_municipio
    )

    if comunidad_id:
        query = query.filter(ComunidadActiva.id_comunidad == comunidad_id)
    elif parroquia_id:
        query = query.filter(ParroquiaActiva.id_parroquia == parroquia_id)
    elif municipio_id:
        query = query.filter(MunicipioActivo.id_municipio == municipio_id)
    elif estado_id:
        query = query.filter(MunicipioActivo.id_estado == estado_id)

    resultados = query.order_by(MapaRiesgo.fecha_creacion.desc()).all()
    
    mapas_json = []
    for mapa, actividad, comunidad in resultados:
        mapas_json.append({
            'id': mapa.id_mapa_riesgo,
            'nombre': mapa.nombre,
            'descripcion': mapa.descripcion,
            'comunidad': comunidad.nombre_comunidad,
            'fecha_creacion': mapa.fecha_creacion.isoformat() if mapa.fecha_creacion else None,
            'tipo_archivo': 'KML' if mapa.ruta_kml else ('Imagen' if mapa.ruta_imagen_mapa else 'Digitalizado')
        })

    return jsonify(mapas_json), 200

@login_required
def crear_simbologia():
    try:
        datos_str = request.form.get('datos')
        if not datos_str:
            return jsonify({'status': 'error', 'message': 'Petición inválida o formulario vacío.'}), 400

        datos = json.loads(datos_str)
        categoria = str(datos.get('categoria', '')).strip()
        nombre_elemento = str(datos.get('nombre_elemento', '')).strip()
        tipo_geometria = str(datos.get('tipo_geometria', 'Point')).strip()

        if not categoria or not nombre_elemento:
            return jsonify({'status': 'error', 'message': 'La categoría y el nombre son obligatorios.'}), 400
        
        estilo_defecto = datos.get('estilo_defecto', {})
        archivo = request.files.get('icono')

        if archivo and archivo.filename != '':
            # Usamos la lista de extensiones exclusiva para iconos de simbología
            if not archivo_permitido(archivo.filename, EXTENSIONES_SIMBOLOS):
                return jsonify({'status': 'error', 'message': 'Formato no permitido. Usa PNG, JPG, SVG o WEBP.'}), 400
            archivo.seek(0, os.SEEK_END)
            if archivo.tell() > 2 * 1024 * 1024:
                return jsonify({'status': 'error', 'message': 'El archivo supera el límite de 2MB.'}), 400
            archivo.seek(0) 

            filename = secure_filename(archivo.filename)
            filename_unico = f"{int(datetime.now().timestamp())}_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'simbologia')
            os.makedirs(upload_folder, exist_ok=True)
            
            archivo.save(os.path.join(upload_folder, filename_unico))
            estilo_defecto['iconUrl'] = f'/static/uploads/simbologia/{filename_unico}'

        nuevo_simbolo = Simbologia(
            categoria=categoria,
            nombre_elemento=nombre_elemento,
            tipo_geometria=tipo_geometria,
            estilo_defecto=estilo_defecto
        )
        db.session.add(nuevo_simbolo)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Símbolo creado con éxito'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error al crear: {str(e)}'}), 500

@login_required
def actualizar_simbologia(id_simbologia):
    try:
        simbolo = Simbologia.query.get(id_simbologia)
        if not simbolo:
            return jsonify({'status': 'error', 'message': 'El símbolo no existe.'}), 404

        datos_str = request.form.get('datos')
        if not datos_str:
            return jsonify({'status': 'error', 'message': 'Datos inválidos.'}), 400

        datos = json.loads(datos_str)
        
        nueva_cat = datos.get('categoria')
        if nueva_cat: simbolo.categoria = str(nueva_cat).strip()
        
        nuevo_nom = datos.get('nombre_elemento')
        if nuevo_nom: simbolo.nombre_elemento = str(nuevo_nom).strip()[:100]
        
        nueva_geom = datos.get('tipo_geometria')
        if nueva_geom: simbolo.tipo_geometria = str(nueva_geom).strip()
        
        estilo_defecto = datos.get('estilo_defecto', {})
        archivo = request.files.get('icono')

        if archivo and archivo.filename != '':
            # Usamos la lista de extensiones exclusiva para iconos de simbología
            if not archivo_permitido(archivo.filename, EXTENSIONES_SIMBOLOS):
                return jsonify({'status': 'error', 'message': 'Formato de icono no permitido.'}), 400
                
            archivo.seek(0, os.SEEK_END)
            if archivo.tell() > 2 * 1024 * 1024:
                return jsonify({'status': 'error', 'message': 'El archivo supera 2MB.'}), 400
            archivo.seek(0)

            filename = secure_filename(archivo.filename)
            filename_unico = f"{int(datetime.now().timestamp())}_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'simbologia')
            os.makedirs(upload_folder, exist_ok=True)
            
            estilo_viejo = simbolo.estilo_defecto
            if isinstance(estilo_viejo, dict) and estilo_viejo.get('iconUrl'):
                ruta_vieja = os.path.join(current_app.root_path, estilo_viejo['iconUrl'].lstrip('/'))
                if os.path.exists(ruta_vieja):
                    try:
                        os.remove(ruta_vieja)
                    except OSError:
                        pass

            archivo.save(os.path.join(upload_folder, filename_unico))
            estilo_defecto['iconUrl'] = f'/static/uploads/simbologia/{filename_unico}'

        simbolo.estilo_defecto = estilo_defecto
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Símbolo actualizado correctamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error en Base de Datos: {str(e)}'}), 500

@login_required
def eliminar_simbologia(id_simbologia):
    """Elimina el símbolo y destruye el archivo físico asociado"""
    simbolo = Simbologia.query.get(id_simbologia)
    if not simbolo:
        return jsonify({'status': 'error', 'message': 'Símbolo no encontrado'}), 404

    try:
        ruta_icono = simbolo.estilo_defecto.get('iconUrl') if isinstance(simbolo.estilo_defecto, dict) else None

        db.session.delete(simbolo)
        db.session.commit()

        if ruta_icono:
            path_fisico = os.path.join(current_app.root_path, ruta_icono.lstrip('/'))
            if os.path.exists(path_fisico):
                try: os.remove(path_fisico)
                except OSError: pass

        return jsonify({'status': 'success', 'message': 'Símbolo eliminado por completo'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'No se puede eliminar porque está en uso en algún mapa.'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error inesperado: {str(e)}'}), 500

@login_required
def listar_simbologia():
    """Obtiene el catálogo permitiendo filtros"""
    try:
        categoria_filtro = request.args.get('categoria', '').strip()
        query = Simbologia.query
        
        if categoria_filtro:
            query = query.filter(Simbologia.categoria == categoria_filtro)
            
        simbolos = query.order_by(Simbologia.categoria, Simbologia.nombre_elemento).all()
        
        resultados = [{
            'id_simbologia': s.id_simbologia,
            'categoria': s.categoria,
            'nombre_elemento': s.nombre_elemento,
            'tipo_geometria': s.tipo_geometria,
            'estilo_defecto': s.estilo_defecto
        } for s in simbolos]
        
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Error al consultar el catálogo.'}), 500

@login_required
def obtener_simbologia(id_simbologia):
    simbolo = Simbologia.query.get(id_simbologia)
    if not simbolo:
        return jsonify({'status': 'error', 'message': 'Símbolo no encontrado'}), 404

    return jsonify({
        'id_simbologia': simbolo.id_simbologia,
        'categoria': simbolo.categoria,
        'nombre_elemento': simbolo.nombre_elemento,
        'tipo_geometria': simbolo.tipo_geometria,
        'estilo_defecto': simbolo.estilo_defecto
    }), 200
@login_required
def actualizar_elemento(id_elemento):
    try:
        elemento = ElementosMapaRiesgo.query.get_or_404(id_elemento)
        datos = request.get_json()
        
        cambios_realizados = False
        
        if 'geometria' in datos:
            geojson_geom = json.dumps(datos.get('geometria'))
            elemento.geom = db.func.ST_SetSRID(db.func.ST_GeomFromGeoJSON(geojson_geom), 4326)
            cambios_realizados = True
            
        if 'estilo_personalizado' in datos or 'estiloCustom' in datos:
            elemento.estilo_personalizado = datos.get('estilo_personalizado') or datos.get('estiloCustom')
            cambios_realizados = True
            
        if 'descripcion' in datos:
            elemento.descripcion_especifica = datos.get('descripcion')
            cambios_realizados = True

        if 'nombre_propio' in datos:
            elemento.nombre_propio = datos.get('nombre_propio')
            cambios_realizados = True
            
        if cambios_realizados:
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Elemento actualizado correctamente'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No se proporcionaron datos para actualizar'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
@login_required
def eliminar_elemento(id_elemento):
    try:
        elemento = ElementosMapaRiesgo.query.get_or_404(id_elemento)
        db.session.delete(elemento)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Elemento eliminado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500