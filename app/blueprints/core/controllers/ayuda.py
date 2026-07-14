from flask import render_template
from flask_login import login_required

from app.blueprints.core import core_bp

@core_bp.route('/admin/ayuda')
@login_required
def modulo_ayuda():
    """
    Controlador independiente y desacoplado para la gestión
    de la biblioteca de soporte técnico y manuales del usuario.
    """
    return render_template('usuarios/ayuda.html')