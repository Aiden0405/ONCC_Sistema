from flask import Blueprint

logistica_bp = Blueprint('logistica', __name__)

from app.blueprints.logistica.controllers import inventario  # noqa: F401
from app.blueprints.logistica.controllers import tecnicos_campo  # noqa: F401