from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

# Creamos el Blueprint para agrupar las rutas de Comunidades
comunidad_bp = Blueprint('comunidad', __name__, url_prefix='/comunidades')

@comunidad_bp.route('/')
@login_required
def index():
    # Datos simulados (Mocks). Luego esto vendrá de: Comunidad.query.all()
    comunidades_mock = [
        {'id': 1, 'nombre': 'Consejo Comunal El Jebe', 'estado': 'Lara', 'municipio': 'Iribarren', 'fase': 'Entrega del Mapa', 'fecha': '2023-10-26', 'vocero': 'Carmen López', 'familias': 120},
        {'id': 2, 'nombre': 'Comuna Simón Bolívar', 'estado': 'Yaracuy', 'municipio': 'Peña', 'fase': 'Elaboración e Impresión', 'fecha': '2023-10-20', 'vocero': 'José Pérez', 'familias': 85},
        {'id': 3, 'nombre': 'Sector Las Margaritas', 'estado': 'Falcón', 'municipio': 'Carirubana', 'fase': 'Recolección de Datos', 'fecha': '2023-10-15', 'vocero': 'María Silva', 'familias': 210},
        {'id': 4, 'nombre': 'C.C. Río Claro', 'estado': 'Lara', 'municipio': 'Iribarren', 'fase': 'Diagnóstico / Acercamiento', 'fecha': '2023-10-28', 'vocero': 'Pedro Alvarado', 'familias': 340},
    ]
    # Renderizamos el tablero Kanban
    return render_template('comunidades/kanban.html', comunidades=comunidades_mock)

@comunidad_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        # Aquí capturamos los datos del formulario a futuro
        # nombre = request.form.get('nombre')
        # familias = request.form.get('familias')
        # ... guardar en BD ...
        flash('Comunidad y expediente de Mapa de Riesgo registrados exitosamente.', 'success')
        return redirect(url_for('comunidad.index'))
        
    # Si es GET, mostramos la página completa del formulario
    return render_template('comunidades/formulario.html')