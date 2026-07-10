import json
from datetime import datetime
from flask import request, jsonify, render_template, redirect, url_for
from flask_login import current_user, login_required

from app import db
# Ajusta estas importaciones según la ubicación exacta de tus modelos geográficos
from app.models.esquema_activo import EstadoActivo, MunicipioActivo, ParroquiaActiva, ComunidadActiva

# ==========================================
#          VISTAS (RENDER HTML)
# ==========================================

# Nota: Si en algún momento necesitas renderizar una vista propia para el módulo
# de geografía (como un gestor de divisiones), añadirías las funciones aquí.


# ==========================================
#          API REST - AJAX Y FILTROS
# ==========================================

def obtener_estados():
    """
    Devuelve la lista completa de estados ordenados alfabéticamente.
    Diseñado para cargar el primer selector jerárquico.
    """
    try:
        resultados = EstadoActivo.query.order_by(EstadoActivo.nombre_estado).all()
        
        estados_json = []
        for e in resultados:
            estados_json.append({
                'id_estado': e.id_estado,
                'nombre_estado': e.nombre_estado
            })
            
        return jsonify(estados_json), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def obtener_municipios(id_estado):
    """
    Devuelve los municipios correspondientes a un estado específico.
    Escucha el parámetro dinámico 'id_estado' desde la URL.
    """
    try:
        resultados = MunicipioActivo.query.filter_by(id_estado=id_estado).order_by(MunicipioActivo.nombre_municipio).all()
        
        municipios_json = []
        for m in resultados:
            municipios_json.append({
                'id_municipio': m.id_municipio,
                'nombre_municipio': m.nombre_municipio,
                'id_estado': m.id_estado
            })
            
        return jsonify(municipios_json), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def obtener_parroquias(id_municipio):
    """
    Devuelve las parroquias correspondientes a un municipio específico.
    Escucha el parámetro dinámico 'id_municipio' desde la URL.
    """
    try:
        resultados = ParroquiaActiva.query.filter_by(id_municipio=id_municipio).order_by(ParroquiaActiva.nombre_parroquia).all()
        
        parroquias_json = []
        for p in resultados:
            parroquias_json.append({
                'id_parroquia': p.id_parroquia,
                'nombre_parroquia': p.nombre_parroquia,
                'id_municipio': p.id_municipio
            })
            
        return jsonify(parroquias_json), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def obtener_comunidades(id_parroquia):
    """
    Devuelve las comunidades correspondientes a una parroquia específica.
    Escucha el parámetro dinámico 'id_' desde la URL.
    """
    try:
        resultados = ComunidadActiva.query.filter_by(id_parroquia=id_parroquia).order_by(ComunidadActiva.nombre_comunidad).all()
        
        comunidades_json = []
        for c in resultados:
            comunidades_json.append({
                'id_comunidad': c.id_comunidad,
                'nombre_comunidad': c.nombre_comunidad,
                'id_parroquia': c.id_parroquia
            })
            
        return jsonify(comunidades_json), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ==========================================
#        MANTENIMIENTO DE UBICACIONES
# ==========================================

# Aquí puedes añadir funciones tipo CRUD (crear_comunidad, eliminar_comunidad)
# en caso de que el sistema permita a los administradores registrar nuevas zonas.