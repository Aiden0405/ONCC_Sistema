import os
import json
from datetime import datetime

from flask import flash, redirect, jsonify, render_template, request, url_for, current_app, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from geoalchemy2.functions import ST_AsGeoJSON, ST_GeomFromGeoJSON

from app import db
from app.blueprints.mapas.forms import MapaRiesgoForm
from app.models.geomatica import MapaRiesgo, ElementoMapaRiesgo
from app.models.actividad import Actividad
from app.models.esquema_activo import ComunidadActiva, ParroquiaActiva, MunicipioActivo, EstadoActivo


def _cargar_actividades_mapa(form):
    actividades = Actividad.query.filter_by(tipo_actividad='MAPA_RIESGO').order_by(Actividad.id_actividad.desc()).all()
    if actividades:
        form.id_actividad.choices = [(0, '-- Seleccione la actividad correspondiente --')]
        form.id_actividad.choices.extend(
            (act.id_actividad, f"ID Actividad: {act.id_actividad} | Tipo: {act.tipo_actividad} | Planificada: {act.fecha_actividad}")
            for act in actividades
        )
    else:
        form.id_actividad.choices = [(0, 'No hay actividades registradas')]

@login_required
def mapas_riesgo_index():
    return render_template('geomatica/mapa_riesgo.html')

@login_required
def vista_carga_ssbc():
    """ Vista del formulario de carga con selector de actividades """
    form = MapaRiesgoForm()
    _cargar_actividades_mapa(form)
    cargas = MapaRiesgo.query.order_by(MapaRiesgo.fecha_registro.desc()).all()
    estados_flujo = ['Pendiente', 'En Revisión', 'Aprobado', 'Rechazado']
    
    return render_template(
        'geomatica/carga_ssbc.html', 
        form=form,
        cargas=cargas, 
        estados_flujo=estados_flujo
    )

@login_required
def vista_dibujar_mapa(mapa_id):
    """ Renderiza la herramienta de dibujo Leaflet """
    # SEGURIDAD: get_or_404 bloquea la URL si el ID no existe o fue alterado manualmente
    mapa = MapaRiesgo.query.get_or_404(mapa_id)
    return render_template('geomatica/dibujar_mapa.html', mapa=mapa)

@login_required
def procesar_archivo():
    """ Procesa el formulario de carga inicial del mapa base """
    form = MapaRiesgoForm()
    _cargar_actividades_mapa(form)

    if not form.validate_on_submit():
        flash('Debe completar los campos obligatorios del mapa de riesgo.', 'error')
        return render_template(
            'geomatica/carga_ssbc.html',
            form=form,
            cargas=MapaRiesgo.query.order_by(MapaRiesgo.fecha_registro.desc()).all(),
            estados_flujo=['Pendiente', 'En Revisión', 'Aprobado', 'Rechazado']
        )

    nombre = form.nombre.data
    descripcion = form.descripcion.data
    id_act_dinamico = form.id_actividad.data
    archivo = form.archivo_mapa.data

    if not id_act_dinamico:
        flash('Debe seleccionar una actividad válida de la lista.', 'error')
        return redirect(url_for('geomatica.carga_ssbc'))

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
                
                flash('Imagen del mapa de riesgo guardada exitosamente.', 'success')
                return redirect(url_for('geomatica.index')) 
        else:
            db.session.add(nuevo_mapa)
            db.session.commit()
            flash('Información base registrada. Se ha abierto el lienzo interactivo.', 'success')
            return redirect(url_for('geomatica.dibujar_mapa', mapa_id=nuevo_mapa.id_mapa_riesgo))

    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        if 'validar_previa_sensibilizacion' in error_msg or 'Restricción de ONCC' in error_msg:
            flash('La comunidad asociada debe contar con una actividad previa.', 'error')
        elif 'UniqueViolation' in error_msg or 'llave duplicada' in error_msg.lower():
            flash('Error: Ya existe un mapa asignado a esta actividad.', 'error')
        else:
            flash(f'Error en la transacción: {error_msg}', 'error')
        return redirect(url_for('geomatica.carga_ssbc'))

@login_required
def obtener_mapa(mapa_id):
    """ API para enviar los datos guardados en PostGIS hacia el frontend (Leaflet) """
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
    """ Guarda un dibujo individual recibido desde leaflet en PostGIS """
    datos = request.get_json()
    if not datos:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos.'}), 400

    id_mapa = datos.get('id_mapa_riesgo') 
    geojson_geom = json.dumps(datos.get('geometria')) 

    nuevo_elemento = ElementoMapaRiesgo(
        id_mapa_riesgo=id_mapa,
        categoria=datos.get('categoria', 'General')[:50],
        subcategoria=datos.get('subcategoria', 'General')[:100],
        descripcion=datos.get('descripcion', ''),
        geometria=ST_GeomFromGeoJSON(geojson_geom)
    )
    db.session.add(nuevo_elemento)
    
    mapa_padre = MapaRiesgo.query.get(id_mapa)
    if mapa_padre:
        mapa_padre.fecha_registro = datetime.now()

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Elemento geográfico registrado con éxito'}), 201

@login_required
def actualizar_mapa(mapa_id):
    """ Modifica el nombre y descripción del mapa desde el panel (Seguridad Backend Aplicada) """
    mapa = MapaRiesgo.query.get(mapa_id)
    if not mapa:
        return jsonify({'status': 'error', 'message': 'Operación rechazada: El mapa no existe o el ID fue alterado.'}), 404

    datos = request.get_json()
    if not datos:
        return jsonify({'status': 'error', 'message': 'Datos inválidos.'}), 400
    
    # SEGURIDAD: Limpieza de espacios en blanco inyectados y validación de existencia
    nuevo_nombre = datos.get('nombre', '').strip()
    nueva_desc = datos.get('descripcion', '').strip()

    if not nuevo_nombre or not nueva_desc:
        return jsonify({'status': 'error', 'message': 'El nombre y la descripción no pueden estar vacíos.'}), 400

    # SEGURIDAD: Límite estricto de caracteres en el servidor
    mapa.nombre = nuevo_nombre[:100]
    mapa.descripcion = nueva_desc[:1000]
    mapa.fecha_registro = datetime.now()
    
    if 'geometria' in datos:
        geojson_geom = json.dumps(datos.get('geometria'))
        mapa.geometria = ST_GeomFromGeoJSON(geojson_geom)

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Datos actualizados correctamente'}), 200

@login_required
def eliminar_mapa(mapa_id):
    """ Elimina el mapa base y todos sus polígonos asociados """
    mapa = MapaRiesgo.query.get(mapa_id)
    if not mapa:
        return jsonify({'status': 'error', 'message': 'Operación rechazada: El mapa no existe.'}), 404
    try:
        db.session.delete(mapa)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Capa de riesgo eliminada con éxito.'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Dependencias en la base de datos impiden su eliminación.'}), 500

@login_required
def obtener_todos_mapas():
    """ Obtiene la lista de mapas para la tabla interactiva aplicando los filtros de ubicación """
    estado_id = request.args.get('estado', type=int)
    municipio_id = request.args.get('municipio', type=int)
    parroquia_id = request.args.get('parroquia', type=int)
    comunidad_id = request.args.get('comunidad', type=int)

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