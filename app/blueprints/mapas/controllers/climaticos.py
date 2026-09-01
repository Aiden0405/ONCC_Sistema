import os
from datetime import datetime
from flask import request, jsonify, current_app, render_template, redirect, url_for, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import db
from app.models.clima import MapaClimatico, RegistroClimatico

# Extensiones exclusivas para mapas climáticos (imágenes)
EXTENSIONES_MAPAS_CLIMATICOS = {'png', 'jpg', 'jpeg', 'svg', 'webp'}

def archivo_permitido(filename, extensiones_validas):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensiones_validas

@login_required
def mapas_climaticos_index():
    return render_template('mapas/climaticos.html')

@login_required
def procesar_mapa_climatico():
    """ Procesa y almacena un nuevo mapa climático enfocado en formato de imagen """
    tipo_mapa = request.form.get('tipo_mapa')
    id_estado = request.form.get('id_estado')
    archivo = request.files.get('archivo_mapa')
    
    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    if not archivo or archivo.filename == '':
        msg = 'Debe adjuntar una imagen cartográfica válida.'
        return jsonify({'status': 'error', 'message': msg}), 400 if es_ajax else redirect(url_for('mapas.mapas_climaticos_index'))

    if not archivo_permitido(archivo.filename, EXTENSIONES_MAPAS_CLIMATICOS):
        msg = 'Formato no soportado. Suba PNG, JPG, JPEG, SVG o WEBP.'
        return jsonify({'status': 'error', 'message': msg}), 400 if es_ajax else redirect(url_for('mapas.mapas_climaticos_index'))

    try:
        filename = secure_filename(archivo.filename)
        filename_unico = f"climatico_{int(datetime.now().timestamp())}_{filename}"
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'mapas', 'climaticos')
        os.makedirs(upload_folder, exist_ok=True)
        ruta_guardado = os.path.join(upload_folder, filename_unico)
        
        archivo.save(ruta_guardado)
        url_relativa = f'uploads/mapas/climaticos/{filename_unico}'

        nuevo_mapa = MapaClimatico(
            id_estado=int(id_estado),
            tipo_de_mapa=tipo_mapa,
            url_mapa=url_relativa,
            fecha_creacion=datetime.now().date()
        )
        
        db.session.add(nuevo_mapa)
        db.session.commit()

        msg = 'Mapa climático registrado exitosamente.'
        if es_ajax:
            return jsonify({'status': 'success', 'message': msg, 'mapa_id': nuevo_mapa.id_mapa_climatico}), 201
            
        flash(msg, 'success')
        return redirect(url_for('mapas.mapas_climaticos_index'))

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@login_required
def listar_mapas_climaticos():
    """ Devuelve el listado de mapas climáticos para la tabla dinámica """
    estado_id = request.args.get('estado', type=int)
    
    query = db.session.query(MapaClimatico)
    if estado_id:
        query = query.filter(MapaClimatico.id_estado == estado_id)
        
    mapas = query.order_by(MapaClimatico.fecha_creacion.desc()).all()
    
    resultados = [{
        'id': m.id_mapa_climatico,
        'tipo_de_mapa': m.tipo_de_mapa,
        'url_mapa': m.url_mapa,
        'fecha_creacion': m.fecha_creacion.isoformat()
    } for m in mapas]
    
    return jsonify(resultados), 200

@login_required
def eliminar_mapa_climatico(mapa_id):
    """ Elimina el registro y el archivo físico del mapa climático """
    mapa = MapaClimatico.query.get_or_404(mapa_id)
    try:
        ruta_fisica = os.path.join(current_app.root_path, 'static', mapa.url_mapa)
        
        db.session.delete(mapa)
        db.session.commit()
        
        if os.path.exists(ruta_fisica):
            try: os.remove(ruta_fisica)
            except OSError: pass
            
        return jsonify({'status': 'success', 'message': 'Mapa climático eliminado.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500