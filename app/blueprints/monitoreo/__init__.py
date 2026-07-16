from flask import Blueprint

monitoreo_bp = Blueprint('monitoreo', __name__)

from app.blueprints.monitoreo.controllers import actividades  # noqa: F401
