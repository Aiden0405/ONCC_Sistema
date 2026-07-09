from collections import Counter

from flask import Flask, render_template
from flask_login import LoginManager, login_required
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import Config

# Inicializar extensiones que se conectarán en create_app
migrate = Migrate()
csrf = CSRFProtect()

# 1. Herramientas
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'core.login'
login_manager.login_message = "Por favor, inicie sesión para acceder al sistema ONCC."

# 2. Función Factory
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Conectar BD y Login a la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

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
    from app.blueprints.comunitario import comunitario_bp
    from app.blueprints.core import core_bp
    from app.blueprints.logistica import logistica_bp
    from app.blueprints.mapas import mapas_bp
    from app.blueprints.monitoreo import monitoreo_bp

    # Registramos los cinco dominios principales
    app.register_blueprint(core_bp)
    app.register_blueprint(comunitario_bp)
    app.register_blueprint(mapas_bp)
    app.register_blueprint(monitoreo_bp)
    app.register_blueprint(logistica_bp)

    # Importar modelos para que las migraciones/CLI los detecten
    with app.app_context():
        from app.models.actividad import Actividad  # noqa: F401
        from app.models.bitacora import BitacoraTransaccion  # noqa: F401
        from app.models.esquema_activo import ActividadActiva  # noqa: F401
        from app.models.esquema_activo import ComunidadActiva  # noqa: F401
        from app.models.esquema_activo import EstadoActivo  # noqa: F401
        from app.models.esquema_activo import FormacionActiva  # noqa: F401
        from app.models.esquema_activo import InstitucionActiva  # noqa: F401
        from app.models.esquema_activo import NivelActivo  # noqa: F401
        from app.models.esquema_activo import MunicipioActivo  # noqa: F401
        from app.models.esquema_activo import ParroquiaActiva  # noqa: F401
        from app.models.esquema_activo import SensibilizacionActiva  # noqa: F401
        from app.models.divulgacion import Publicacion  # noqa: F401
        from app.models.geomatica import MapaRiesgo  # noqa: F401
        from app.models.inventario import InventarioEquipo  # noqa: F401
        from app.models.visita_portal import VisitaPortal  # noqa: F401
        from app.models.password_reset import PasswordReset  # noqa: F401
        from app.models.usuario import Usuario  # noqa: F401
        from app.models.role import Role, Permission  # noqa: F401

    from app.blueprints.core.controllers.auth import login as core_login
    from app.blueprints.core.controllers.auth import logout as core_logout
    from app.blueprints.core.controllers.auth import recuperar_contrasena as core_recuperar
    from app.blueprints.core.controllers.bitacora import bitacora_index as core_bitacora_index
    from app.blueprints.core.controllers.divulgacion import acerca as core_acerca
    from app.blueprints.core.controllers.divulgacion import contacto as core_contacto
    from app.blueprints.core.controllers.divulgacion import home as core_home
    from app.blueprints.core.controllers.divulgacion import servicios as core_servicios
    from app.blueprints.core.controllers.roles import rol_editar as core_rol_editar
    from app.blueprints.core.controllers.roles import rol_eliminar as core_rol_eliminar
    from app.blueprints.core.controllers.roles import rol_gestionar_permisos as core_rol_gestionar_permisos
    from app.blueprints.core.controllers.roles import rol_index as core_rol_index
    from app.blueprints.core.controllers.roles import rol_nuevo as core_rol_nuevo
    # Comenta la línea 93
# from app.blueprints.core.controllers.roles import rol_permiso_nuevo as core_permiso_nuevo

# Comenta la línea 94
# from app.blueprints.core.controllers.roles import rol_permisos_index as core_permisos_index
    from app.blueprints.core.controllers.usuarios import usuario_editar as core_usuario_editar
    from app.blueprints.core.controllers.usuarios import usuario_eliminar as core_usuario_eliminar
    from app.blueprints.core.controllers.usuarios import usuario_index as core_usuario_index
    from app.blueprints.core.controllers.usuarios import usuario_nuevo as core_usuario_nuevo
    from app.blueprints.core.controllers.usuarios import usuario_perfil as core_usuario_perfil
    from app.blueprints.logistica.controllers.inventario import editar as logistica_inventario_editar
    from app.blueprints.logistica.controllers.inventario import eliminar as logistica_inventario_eliminar
    from app.blueprints.logistica.controllers.inventario import inventario_index as logistica_inventario_index
    from app.blueprints.logistica.controllers.inventario import nuevo as logistica_inventario_nuevo
    from app.blueprints.mapas.controllers.riesgo import cambiar_estado as mapas_cambiar_estado
    from app.blueprints.mapas.controllers.riesgo import mapas_riesgo_index as mapas_index
    from app.blueprints.mapas.controllers.riesgo import procesar_archivo as mapas_procesar_archivo
    from app.blueprints.monitoreo.controllers.actividades import actividades_cambiar_estado as monitoreo_actividad_cambiar_estado
    from app.blueprints.monitoreo.controllers.actividades import actividades_index as monitoreo_actividad_index
    from app.blueprints.monitoreo.controllers.actividades import nueva as monitoreo_actividad_nueva
    from app.blueprints.comunitario.controllers.formaciones import formacion_cambiar_estado
    from app.blueprints.comunitario.controllers.formaciones import formacion_nuevo
    from app.blueprints.comunitario.controllers.formaciones import formaciones_index as comunitario_formaciones_index
    from app.blueprints.comunitario.controllers.sensibilizaciones import sensibilizacion_cambiar_estado
    from app.blueprints.comunitario.controllers.sensibilizaciones import sensibilizacion_nuevo
    from app.blueprints.comunitario.controllers.sensibilizaciones import sensibilizaciones_index as comunitario_sensibilizaciones_index

    app.add_url_rule('/', endpoint='public.home', view_func=core_home)
    app.add_url_rule('/acerca', endpoint='public.acerca', view_func=core_acerca)
    app.add_url_rule('/servicios', endpoint='public.servicios', view_func=core_servicios)
    app.add_url_rule('/contacto', endpoint='public.contacto', view_func=core_contacto)
    app.add_url_rule('/auth/login', endpoint='auth.login', view_func=core_login, methods=['GET', 'POST'])
    app.add_url_rule('/auth/logout', endpoint='auth.logout', view_func=core_logout)
    app.add_url_rule('/auth/recuperar', endpoint='auth.recuperar_contrasena', view_func=core_recuperar, methods=['GET', 'POST'])

    app.add_url_rule('/formaciones', endpoint='formacion.index', view_func=comunitario_formaciones_index)
    app.add_url_rule('/formaciones/nuevo', endpoint='formacion.nuevo', view_func=formacion_nuevo, methods=['POST'])
    app.add_url_rule('/formaciones/<int:formacion_id>/estado', endpoint='formacion.cambiar_estado', view_func=formacion_cambiar_estado, methods=['POST'])
    app.add_url_rule('/sensibilizaciones', endpoint='sensibilizacion.index', view_func=comunitario_sensibilizaciones_index)
    app.add_url_rule('/sensibilizaciones/nuevo', endpoint='sensibilizacion.nuevo', view_func=sensibilizacion_nuevo, methods=['POST'])
    app.add_url_rule('/sensibilizaciones/<int:sensibilizacion_id>/estado', endpoint='sensibilizacion.cambiar_estado', view_func=sensibilizacion_cambiar_estado, methods=['POST'])

    app.add_url_rule('/admin/usuarios/', endpoint='usuario.index', view_func=core_usuario_index)
    app.add_url_rule('/admin/usuarios/nuevo', endpoint='usuario.nuevo', view_func=core_usuario_nuevo, methods=['GET', 'POST'])
    app.add_url_rule('/admin/usuarios/<int:usuario_id>/editar', endpoint='usuario.editar', view_func=core_usuario_editar, methods=['GET', 'POST'])
    app.add_url_rule('/admin/usuarios/<int:usuario_id>/eliminar', endpoint='usuario.eliminar', view_func=core_usuario_eliminar, methods=['POST'])
    app.add_url_rule('/admin/usuarios/perfil', endpoint='usuario.perfil', view_func=core_usuario_perfil, methods=['GET', 'POST'])

    app.add_url_rule('/admin/roles/', endpoint='rol.index', view_func=core_rol_index)
    app.add_url_rule('/admin/roles/nuevo', endpoint='rol.nuevo', view_func=core_rol_nuevo, methods=['GET', 'POST'])
    app.add_url_rule('/admin/roles/<int:rol_id>/editar', endpoint='rol.editar', view_func=core_rol_editar, methods=['GET', 'POST'])
    app.add_url_rule('/admin/roles/<int:rol_id>/eliminar', endpoint='rol.eliminar', view_func=core_rol_eliminar, methods=['POST'])
    # Comenta la línea 148 que causó el error
# app.add_url_rule('/admin/roles/permisos', endpoint='rol.permisos_index', view_func=core_permisos_index)

# Si hay más líneas similares de 'add_url_rule' para los permisos viejos abajo, coméntalas también:
# app.add_url_rule('/admin/roles/permisos/nuevo', endpoint='rol.permiso_nuevo', view_func=core_permiso_nuevo)
    app.add_url_rule('/admin/roles/<int:rol_id>/permisos', endpoint='rol.gestionar_permisos', view_func=core_rol_gestionar_permisos, methods=['GET', 'POST'])

    app.add_url_rule('/actividades/', endpoint='actividad.index', view_func=monitoreo_actividad_index)
    app.add_url_rule('/actividades/nueva', endpoint='actividad.nueva', view_func=monitoreo_actividad_nueva, methods=['GET', 'POST'])
    app.add_url_rule('/actividades/<int:actividad_id>/estado', endpoint='actividad.cambiar_estado', view_func=monitoreo_actividad_cambiar_estado, methods=['POST'])

    app.add_url_rule('/inventario/', endpoint='inventario.index', view_func=logistica_inventario_index)
    app.add_url_rule('/inventario/nuevo', endpoint='inventario.nuevo', view_func=logistica_inventario_nuevo, methods=['POST'])
    app.add_url_rule('/inventario/<int:equipo_id>/editar', endpoint='inventario.editar', view_func=logistica_inventario_editar, methods=['POST'])
    app.add_url_rule('/inventario/<int:equipo_id>/eliminar', endpoint='inventario.eliminar', view_func=logistica_inventario_eliminar, methods=['POST'])

    app.add_url_rule('/geomatica/', endpoint='geomatica.index', view_func=mapas_index)
    app.add_url_rule('/geomatica/procesar', endpoint='geomatica.procesar_archivo', view_func=mapas_procesar_archivo, methods=['POST'])
    app.add_url_rule('/geomatica/<int:mapa_id>/estado', endpoint='geomatica.cambiar_estado', view_func=mapas_cambiar_estado, methods=['POST'])

    # Registrar comandos CLI (seed, etc.)
    try:
        from app import cli as app_cli
        app_cli.register_cli_commands(app)
    except Exception:
        pass

    # ==============================================================
    # RUTAS PROTEGIDAS
    # ==============================================================
    @app.route('/sistema')
    @app.route('/dashboard')
    @app.route('/monitoreo')
    @login_required
    def dashboard():
        from app.models.actividad import Actividad
        from app.models.divulgacion import Publicacion
        from app.models.geomatica import MapaRiesgo
        from app.models.inventario import InventarioEquipo

        actividades = Actividad.query.order_by(Actividad.creado_en.desc()).limit(5).all()
        total_actividades = Actividad.query.count()

        mapa_estados = [
            {'nombre': 'Lara', 'lat': 10.073, 'lng': -69.322, 'color': '#16a34a', 'conteo': 0},
            {'nombre': 'Yaracuy', 'lat': 10.339, 'lng': -68.745, 'color': '#3b82f6', 'conteo': 0},
            {'nombre': 'Falcón', 'lat': 11.062, 'lng': -69.681, 'color': '#f59e0b', 'conteo': 0},
        ]

        modulos_operativos = {
            'inventario': InventarioEquipo.query.count(),
            'mapas': MapaRiesgo.query.count(),
            'actividades': total_actividades,
            'divulgacion': Publicacion.query.count(),
            'divulgacion_publicadas': Publicacion.query.filter_by(estado_publicacion='publicado').count(),
            'divulgacion_borradores': Publicacion.query.filter_by(estado_publicacion='borrador').count(),
            'comunidades': 0,
            'formaciones': 0,
            'sensibilizaciones': 0,
        }

        resumen = {
            'inventario': modulos_operativos['inventario'],
            'mapas': modulos_operativos['mapas'],
            'formaciones': modulos_operativos['formaciones'],
            'sensibilizaciones': modulos_operativos['sensibilizaciones'],
            'divulgacion': modulos_operativos['divulgacion'],
        }

        return render_template(
            'dashboard.html',
            resumen=resumen,
            comunidades=[],
            actividades_recientes=actividades,
            mapa_estados=mapa_estados,
            modulos_operativos=modulos_operativos,
        )

    return app