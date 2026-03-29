from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

# Creamos el Blueprint para agrupar las rutas de actividades
actividad_bp = Blueprint('actividad', __name__, url_prefix='/actividades')

@actividad_bp.route('/')
@login_required
def index():
    # Datos simulados (Mocks). Luego esto vendrá de: Actividad.query.all()
    actividades_mock = [
        {'id': 1, 'fecha': '2023-10-25', 'area': 'Formación', 'actividad': 'Taller Cambio Climático', 'responsable': 'Téc. María Pérez', 'estado': 'Completado'},
        {'id': 2, 'fecha': '2023-10-24', 'area': 'Monitoreo', 'actividad': 'Revisión Pluviómetro', 'responsable': 'Téc. Carlos Luis', 'estado': 'En proceso'}
    ]
    # Apunta al index.html dentro de la carpeta actividades
    return render_template('actividades/index.html', actividades=actividades_mock)

@actividad_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        # Aquí capturaremos los datos del formulario a futuro
        # area = request.form.get('area')
        # etc...
        flash('Actividad registrada exitosamente', 'success')
        return redirect(url_for('actividad.index'))
        
    # Si es GET, mostramos el formulario
    return render_template('actividades/formulario.html')