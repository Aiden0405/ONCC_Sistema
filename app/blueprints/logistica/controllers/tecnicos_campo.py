from flask import render_template
from flask_login import login_required

from app.blueprints.logistica import logistica_bp


@logistica_bp.route('/tecnicos-campo')
@login_required
def tecnicos_campo_index():
    return render_template('logistica/tecnicos_campo.html')