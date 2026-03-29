from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

# Creamos el Blueprint para agrupar las rutas de Entes y Solicitudes
ente_bp = Blueprint('ente', __name__, url_prefix='/entes')

@ente_bp.route('/')
@login_required
def index():
    # Datos simulados (Mocks). Luego esto vendrá de: Ente.query.all() y Solicitud.query.all()
    entes_mock = [
        {'id': 1, 'nombre': 'Alcaldía de Iribarren', 'tipo': 'Alcaldía', 'contacto': 'Lcda. Juana Gómez', 'estatus': 'Activo'},
        {'id': 2, 'nombre': 'Universidad Yacambú', 'tipo': 'Universidad', 'contacto': 'Dr. Luis Pérez', 'estatus': 'Activo'},
        {'id': 3, 'nombre': 'Liceo Bolivariano Cují', 'tipo': 'Educación', 'contacto': 'Prof. Ana Silva', 'estatus': 'Activo'}
    ]
    
    solicitudes_mock = [
        {'id': 1, 'ente': 'Universidad Yacambú', 'tipo': 'Taller de Formación', 'fecha_solicitada': '2023-11-05', 'estatus': 'Aprobada'},
        {'id': 2, 'ente': 'Liceo Bolivariano Cují', 'tipo': 'Taller de Sensibilización', 'fecha_solicitada': '2023-11-12', 'estatus': 'Pendiente'},
        {'id': 3, 'ente': 'Alcaldía de Iribarren', 'tipo': 'Asistencia Técnica', 'fecha_solicitada': '2023-10-30', 'estatus': 'Programada'}
    ]
    
    # Renderizamos la vista de entes y le pasamos los datos
    return render_template('entes/index.html', entes=entes_mock, solicitudes=solicitudes_mock)

@ente_bp.route('/nueva_solicitud', methods=['POST'])
@login_required
def nueva_solicitud():
    # Aquí capturamos los datos que el usuario llenó en el formulario (modal)
    # Por ejemplo:
    # ente_id = request.form.get('ente_id')
    # tipo_solicitud = request.form.get('tipo_solicitud')
    # detalles = request.form.get('detalles')
    # fecha = request.form.get('fecha_propuesta')
    # estatus = request.form.get('estatus')
    
    # A futuro: Aquí guardaríamos el nuevo objeto 'Solicitud' en PostgreSQL con db.session.add()
    
    # Enviamos un mensaje de éxito a la vista (Flash message)
    flash('Solicitud institucional registrada exitosamente.', 'success')
    
    # Redirigimos de vuelta a la página principal de entes
    return redirect(url_for('ente.index'))