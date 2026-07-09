from flask import Blueprint

comunitario_bp = Blueprint('comunitario', __name__)

from app.blueprints.comunitario.controllers import formaciones  # noqa: F401
from app.blueprints.comunitario.controllers import sensibilizaciones  # noqa: F401