from flask import Blueprint

core_bp = Blueprint('core', __name__)

# Importaciones directas de los módulos controladores
from app.blueprints.core.controllers import auth  # noqa: F401
from app.blueprints.core.controllers import bitacora  # noqa: F401
from app.blueprints.core.controllers import divulgacion  # noqa: F401
from app.blueprints.core.controllers import roles  # noqa: F401
from app.blueprints.core.controllers import usuarios  # noqa: F401
from app.blueprints.core.controllers import ayuda  # 🌟 ¡Listo! Importación directa del archivo independiente