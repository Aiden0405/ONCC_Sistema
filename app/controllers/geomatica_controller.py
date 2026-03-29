from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
import os

# Creamos el Blueprint para agrupar las rutas de Geomática
geomatica_bp = Blueprint('geomatica', __name__, url_prefix='/geomatica')

@geomatica_bp.route('/')
@login_required
def index():
    # Mock data de cargas históricas de los archivos SSBC
    cargas_mock = [
        {'id': 1, 'archivo': 'Pluviometro_Falc_Oct.ssbc', 'registros': 4320, 'fecha': '2023-10-28 08:30', 'usuario': 'Ing. Geomática', 'estatus': 'Exitoso'},
        {'id': 2, 'archivo': 'EMA_Lara_Centro_Sem4.xlsx', 'registros': 8640, 'fecha': '2023-10-25 14:15', 'usuario': 'Ing. Geomática', 'estatus': 'Exitoso'},
        {'id': 3, 'archivo': 'TRN005_Yaracuy_Error.ssbc', 'registros': 120, 'fecha': '2023-10-20 09:00', 'usuario': 'Téc. Carlos Luis', 'estatus': 'Error de Formato'}
    ]
    return render_template('geomatica/carga_ssbc.html', cargas=cargas_mock)

@geomatica_bp.route('/procesar', methods=['POST'])
@login_required
def procesar_archivo():
    # 1. Verificamos si la petición web trajo consigo un archivo adjunto
    if 'archivo_ssbc' not in request.files:
        flash('No se encontró ningún archivo en la petición.', 'error')
        return redirect(url_for('geomatica.index'))
        
    archivo = request.files['archivo_ssbc']
    
    # 2. Si el usuario le dio al botón sin seleccionar nada
    if archivo.filename == '':
        flash('No seleccionó ningún archivo válido para subir.', 'error')
        return redirect(url_for('geomatica.index'))
        
    # 3. Si el archivo es válido, lo procesamos
    if archivo:
        nombre_archivo = archivo.filename
        
        # =================================================================
        # MAGIA DEL ESTUDIANTE 3 (A FUTURO AQUÍ ENTRARÁ PANDAS)
        # =================================================================
        # A futuro el código se verá algo así:
        # ruta_temporal = os.path.join('app/static/uploads/temporales_ssbc', nombre_archivo)
        # archivo.save(ruta_temporal)
        # import pandas as pd
        # df = pd.read_excel(ruta_temporal) o pd.read_csv(ruta_temporal)
        # Y un ciclo for para guardar df['temperatura'] en PostgreSQL
        # =================================================================
        
        # Simulamos que todo salió perfecto
        flash(f'Archivo "{nombre_archivo}" recibido y procesado correctamente en el sistema. Los datos climáticos están guardados.', 'success')
        
    return redirect(url_for('geomatica.index'))