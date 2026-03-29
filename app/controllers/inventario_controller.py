from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

# Creamos el Blueprint para agrupar las rutas de Inventario Físico
inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@inventario_bp.route('/')
@login_required
def index():
    # Datos simulados (Mocks). Luego esto vendrá de: Equipo.query.all()
    inventario_mock = [
        {'id': 1, 'equipo': 'Pluviómetro de campo', 'codigo': 'PLV-001', 'ubicacion': 'Parque Nacional Yurubí', 'estado': 'Operativo', 'ultimo_mantenimiento': '2023-08-15'},
        {'id': 2, 'equipo': 'Aparato Transmisor Data (SSBC)', 'codigo': 'TRN-005', 'ubicacion': 'Sede ONCC Lara', 'estado': 'Operativo', 'ultimo_mantenimiento': '2023-09-01'},
        {'id': 3, 'equipo': 'Estación Meteorológica (EMA)', 'codigo': 'EMA-002', 'ubicacion': 'Morrocoy (Falcón)', 'estado': 'Requiere Mantenimiento', 'ultimo_mantenimiento': '2023-10-10'},
        {'id': 4, 'equipo': 'GPS Garmin', 'codigo': 'GPS-012', 'ubicacion': 'Sede ONCC Falcón', 'estado': 'Dañado / Inoperativo', 'ultimo_mantenimiento': '2022-11-20'},
    ]
    # Renderizamos la tabla de inventario
    return render_template('inventario/index.html', inventario=inventario_mock)

@inventario_bp.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    # El formulario del inventario lo hicimos como un Modal (ventana emergente)
    # Por lo tanto, esta ruta solo recibe POST para procesar el guardado
    
    # tipo = request.form.get('tipo_equipo')
    # codigo = request.form.get('codigo')
    # ... guardar en BD ...
    
    flash('Equipo registrado exitosamente en el inventario.', 'success')
    return redirect(url_for('inventario.index'))