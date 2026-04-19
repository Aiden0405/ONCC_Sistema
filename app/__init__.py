from collections import Counter

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from config import Config

# 1. Herramientas
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Por favor, inicie sesión para acceder al sistema ONCC."

# 2. Función Factory
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Conectar BD y Login a la app
    db.init_app(app)
    login_manager.init_app(app)

    # ==============================================================
    # Cargador de Usuarios para Flask-Login
    # ==============================================================
    from app.models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # ==============================================================
    # REGISTRO DE CONTROLADORES (Blueprints)
    # ¡Aquí es donde debes agregar los que faltaban!
    # ==============================================================
    from app.controllers.auth_controller import auth_bp
    from app.controllers.public_controller import public_bp
    from app.controllers.actividad_controller import actividad_bp
    from app.controllers.comunidad_controller import comunidad_bp
    from app.controllers.inventario_controller import inventario_bp
    from app.controllers.ente_controller import ente_bp
    from app.controllers.geomatica_controller import geomatica_bp
    from app.controllers.reporte_controller import reporte_bp
    from app.controllers.formacion_controller import formacion_bp
    from app.controllers.sensibilizacion_controller import sensibilizacion_bp

    # Registramos todos para que el menú pueda encontrar las rutas
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(actividad_bp)
    app.register_blueprint(comunidad_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(ente_bp)
    app.register_blueprint(geomatica_bp)
    app.register_blueprint(reporte_bp)
    app.register_blueprint(formacion_bp)
    app.register_blueprint(sensibilizacion_bp)

    # Crea tablas faltantes al iniciar para evitar fallos por esquema incompleto.
    with app.app_context():
        # Importar modelos garantiza que SQLAlchemy conozca todas las tablas.
        from app.models.actividad import Actividad  # noqa: F401
        from app.models.bitacora import BitacoraTransaccion  # noqa: F401
        from app.models.comunidad import Comunidad  # noqa: F401
        from app.models.formacion import Formacion  # noqa: F401
        from app.models.geomatica import MapaRegistro  # noqa: F401
        from app.models.inventario import InventarioEquipo  # noqa: F401
        from app.models.reporte import ReporteTransaccional  # noqa: F401
        from app.models.sensibilizacion import Sensibilizacion  # noqa: F401
        from app.models.visita_portal import VisitaPortal  # noqa: F401
        from app.models.usuario import Usuario  # noqa: F401

        db.create_all()

    # ==============================================================
    # RUTAS PROTEGIDAS
    # ==============================================================
    @app.route('/sistema')
    @app.route('/dashboard')
    @app.route('/monitoreo')
    @login_required 
    def dashboard():
        from app.models.actividad import Actividad
        from app.models.comunidad import Comunidad
        from app.models.formacion import Formacion
        from app.models.geomatica import MapaRegistro
        from app.models.inventario import InventarioEquipo
        from app.models.reporte import ReporteTransaccional
        from app.models.sensibilizacion import Sensibilizacion

        comunidades = Comunidad.query.all()
        actividades = Actividad.query.order_by(Actividad.creado_en.desc()).limit(5).all()
        total_actividades = Actividad.query.count()
        conteo_estados = Counter((comunidad.estado or 'Sin estado') for comunidad in comunidades)

        mapa_estados = [
            {'nombre': 'Lara', 'lat': 10.073, 'lng': -69.322, 'color': '#16a34a', 'conteo': conteo_estados.get('Lara', 0)},
            {'nombre': 'Yaracuy', 'lat': 10.339, 'lng': -68.745, 'color': '#3b82f6', 'conteo': conteo_estados.get('Yaracuy', 0)},
            {'nombre': 'Falcón', 'lat': 11.062, 'lng': -69.681, 'color': '#f59e0b', 'conteo': conteo_estados.get('Falcón', 0)},
        ]

        modulos_operativos = {
            'inventario': InventarioEquipo.query.count(),
            'mapas': MapaRegistro.query.count(),
            'reportes': ReporteTransaccional.query.count(),
            'formaciones': Formacion.query.count(),
            'sensibilizaciones': Sensibilizacion.query.count(),
            'comunidades': len(comunidades),
            'actividades': total_actividades,
        }

        resumen = {
            'inventario': modulos_operativos['inventario'],
            'mapas': modulos_operativos['mapas'],
            'reportes': modulos_operativos['reportes'],
            'formaciones': modulos_operativos['formaciones'],
            'sensibilizaciones': modulos_operativos['sensibilizaciones'],
        }
        return render_template(
            'dashboard.html',
            resumen=resumen,
            comunidades=comunidades,
            actividades_recientes=actividades,
            mapa_estados=mapa_estados,
            modulos_operativos=modulos_operativos,
        )

    return app