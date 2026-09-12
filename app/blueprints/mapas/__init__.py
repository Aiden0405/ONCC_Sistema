from flask import Blueprint

mapas_bp = Blueprint('mapas', __name__)

from app.blueprints.mapas.controllers import climaticos  # noqa: F401
from app.blueprints.mapas.controllers import riesgo  # noqa: F401