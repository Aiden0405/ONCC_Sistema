from flask import render_template
from flask_login import login_required

from app.blueprints.mapas import mapas_bp


@mapas_bp.route('/mapas-climaticos')
@login_required
def mapas_climaticos_index():
    return render_template('mapas/climaticos.html')