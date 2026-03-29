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
    from app.controllers.actividad_controller import actividad_bp
    from app.controllers.comunidad_controller import comunidad_bp
    from app.controllers.inventario_controller import inventario_bp
    from app.controllers.ente_controller import ente_bp
    from app.controllers.geomatica_controller import geomatica_bp

    # Registramos todos para que el menú pueda encontrar las rutas
    app.register_blueprint(auth_bp)
    app.register_blueprint(actividad_bp)
    app.register_blueprint(comunidad_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(ente_bp)
    app.register_blueprint(geomatica_bp)

    # ==============================================================
    # RUTAS PROTEGIDAS
    # ==============================================================
    @app.route('/')
    @app.route('/dashboard')
    @login_required 
    def dashboard():
        return render_template('dashboard.html')

    return app