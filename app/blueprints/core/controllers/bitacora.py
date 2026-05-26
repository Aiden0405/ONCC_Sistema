from flask import render_template

from app.blueprints.core import core_bp


@core_bp.route('/bitacora')
def bitacora_index():
    return render_template('dashboard.html')