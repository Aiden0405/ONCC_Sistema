from flask import Blueprint

geografia_bp = Blueprint('geografia', __name__)

from app.blueprints.geografia.controllers import ubicaciones  # noqa: F401
