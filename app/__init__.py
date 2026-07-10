from collections import Counter

from flask import Flask, render_template
from flask_login import LoginManager, login_required
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import Config

migrate = Migrate()
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'core.login'
login_manager.login_message = "Por favor, inicie sesión para acceder al sistema ONCC."

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from app.blueprints.comunitario import comunitario_bp
    from app.blueprints.core import core_bp
    from app.blueprints.logistica import logistica_bp
    from app.blueprints.mapas import mapas_bp
    from app.blueprints.monitoreo import monitoreo_bp
    from app.blueprints.geografia import geografia_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(comunitario_bp)
    app.register_blueprint(mapas_bp)
    app.register_blueprint(monitoreo_bp)
    app.register_blueprint(logistica_bp)
    app.register_blueprint(geografia_bp)

    with app.app_context():
        from app.models.actividad import Actividad
        from app.models.bitacora import BitacoraTransaccion
        from app.models.esquema_activo import ComunidadActiva, EstadoActivo, FormacionActiva, InstitucionActiva, NivelActivo, MunicipioActivo, ParroquiaActiva, SensibilizacionActiva
        from app.models.divulgacion import Publicacion
        from app.models.geomatica import MapaRiesgo, ElementoMapaRiesgo
        from app.models.inventario import InventarioEquipo
        from app.models.reporte import ReporteTransaccional
        from app.models.visita_portal import VisitaPortal
        from app.models.password_reset import PasswordReset
        from app.models.usuario import Usuario
        from app.models.role import Role, Permission

    # Core Auth & Public
    from app.blueprints.core.controllers.auth import login as core_login, logout as core_logout, recuperar_contrasena as core_recuperar
    from app.blueprints.core.controllers.bitacora import bitacora_index as core_bitacora_index
    from app.blueprints.core.controllers.divulgacion import acerca as core_acerca, contacto as core_contacto, home as core_home, servicios as core_servicios
    from app.blueprints.core.controllers.roles import rol_editar as core_rol_editar, rol_eliminar as core_rol_eliminar, rol_gestionar_permisos as core_rol_gestionar_permisos, rol_index as core_rol_index, rol_nuevo as core_rol_nuevo
    from app.blueprints.core.controllers.usuarios import usuario_editar as core_usuario_editar, usuario_eliminar as core_usuario_eliminar, usuario_index as core_usuario_index, usuario_nuevo as core_usuario_nuevo, usuario_perfil as core_usuario_perfil
    
    # Logística
    from app.blueprints.logistica.controllers.inventario import editar as logistica_inventario_editar, eliminar as logistica_inventario_eliminar, inventario_index as logistica_inventario_index, nuevo as logistica_inventario_nuevo
    
    # Geomática (Mapas)
    from app.blueprints.mapas.controllers.riesgo import mapas_riesgo_index as mapas_index
    from app.blueprints.mapas.controllers.riesgo import vista_carga_ssbc, vista_dibujar_mapa
    from app.blueprints.mapas.controllers.riesgo import obtener_todos_mapas, crear_mapa as mapas_crear_mapa, obtener_mapa as mapas_obtener_mapa, actualizar_mapa as mapas_actualizar_mapa, eliminar_mapa as mapas_eliminar_mapa, procesar_archivo as mapas_procesar_archivo
    
    # Monitoreo y Comunitario
    from app.blueprints.monitoreo.controllers.actividades import actividades_cambiar_estado as monitoreo_actividad_cambiar_estado, actividades_index as monitoreo_actividad_index, nueva as monitoreo_actividad_nueva
    from app.blueprints.monitoreo.controllers.comparacion_mapas_climaticos import reporte_cambiar_estado as monitoreo_reporte_cambiar_estado, comparacion_index as monitoreo_reporte_index, nuevo as monitoreo_reporte_nuevo
    from app.blueprints.comunitario.controllers.formaciones import formacion_cambiar_estado, formacion_nuevo, formaciones_index as comunitario_formaciones_index
    from app.blueprints.comunitario.controllers.sensibilizaciones import sensibilizacion_cambiar_estado, sensibilizacion_nuevo, sensibilizaciones_index as comunitario_sensibilizaciones_index
    from app.blueprints.geografia.controllers.ubicaciones import obtener_estados, obtener_municipios, obtener_parroquias, obtener_comunidades

    # Rutas estáticas
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
    app.add_url_rule('/admin/roles/<int:rol_id>/permisos', endpoint='rol.gestionar_permisos', view_func=core_rol_gestionar_permisos, methods=['GET', 'POST'])

    app.add_url_rule('/actividades/', endpoint='actividad.index', view_func=monitoreo_actividad_index)
    app.add_url_rule('/actividades/nueva', endpoint='actividad.nueva', view_func=monitoreo_actividad_nueva, methods=['GET', 'POST'])
    app.add_url_rule('/actividades/<int:actividad_id>/estado', endpoint='actividad.cambiar_estado', view_func=monitoreo_actividad_cambiar_estado, methods=['POST'])

    app.add_url_rule('/inventario/', endpoint='inventario.index', view_func=logistica_inventario_index)
    app.add_url_rule('/inventario/nuevo', endpoint='inventario.nuevo', view_func=logistica_inventario_nuevo, methods=['POST'])
    app.add_url_rule('/inventario/<int:equipo_id>/editar', endpoint='inventario.editar', view_func=logistica_inventario_editar, methods=['POST'])
    app.add_url_rule('/inventario/<int:equipo_id>/eliminar', endpoint='inventario.eliminar', view_func=logistica_inventario_eliminar, methods=['POST'])

    # ==============================================================
    # Geomática
    # ==============================================================
    app.add_url_rule('/geomatica/', endpoint='geomatica.index', view_func=mapas_index, methods=['GET'])
    app.add_url_rule('/geomatica/carga-ssbc', endpoint='geomatica.carga_ssbc', view_func=vista_carga_ssbc, methods=['GET'])
    app.add_url_rule('/geomatica/dibujar/<int:mapa_id>', endpoint='geomatica.dibujar_mapa', view_func=vista_dibujar_mapa, methods=['GET'])
    app.add_url_rule('/geomatica/procesar', endpoint='geomatica.procesar_archivo', view_func=mapas_procesar_archivo, methods=['POST'])
    
    # API JSON CRUD
    app.add_url_rule('/geomatica/mapas', endpoint='geomatica.obtener_todos_mapas', view_func=obtener_todos_mapas, methods=['GET'])
    app.add_url_rule('/geomatica/crear_mapa', endpoint='geomatica.crear_mapa', view_func=mapas_crear_mapa, methods=['POST'])
    app.add_url_rule('/geomatica/mapas/<int:mapa_id>', endpoint='geomatica.obtener_mapa', view_func=mapas_obtener_mapa, methods=['GET'])
    app.add_url_rule('/geomatica/mapas/<int:mapa_id>', endpoint='geomatica.actualizar_mapa', view_func=mapas_actualizar_mapa, methods=['PUT'])
    app.add_url_rule('/geomatica/mapas/<int:mapa_id>', endpoint='geomatica.eliminar_mapa', view_func=mapas_eliminar_mapa, methods=['DELETE'])    

    app.add_url_rule('/reportes/', endpoint='reporte.index', view_func=monitoreo_reporte_index)
    app.add_url_rule('/reportes/nuevo', endpoint='reporte.nuevo', view_func=monitoreo_reporte_nuevo, methods=['POST'])
    app.add_url_rule('/reportes/<int:reporte_id>/estado', endpoint='reporte.cambiar_estado', view_func=monitoreo_reporte_cambiar_estado, methods=['POST'])

    app.add_url_rule('/api/geografia/estados', endpoint='geografia.obtener_estados', view_func=obtener_estados, methods=['GET'])
    app.add_url_rule('/api/geografia/municipios/<int:id_estado>', endpoint='geografia.obtener_municipios', view_func=obtener_municipios, methods=['GET'])    
    app.add_url_rule('/api/geografia/parroquias/<int:id_municipio>', endpoint='geografia.obtener_parroquias', view_func=obtener_parroquias, methods=['GET'])
    app.add_url_rule('/api/geografia/comunidades/<int:id_parroquia>', endpoint='geografia.obtener_comunidades', view_func=obtener_comunidades, methods=['GET'])
    
    try:
        from app import cli as app_cli
        app_cli.register_cli_commands(app)
    except Exception:
        pass

    @app.route('/sistema')
    @app.route('/dashboard')
    @app.route('/monitoreo')
    @login_required
    def dashboard():
        from app.models.actividad import Actividad
        from app.models.divulgacion import Publicacion
        from app.models.geomatica import MapaRiesgo
        from app.models.inventario import InventarioEquipo
        from app.models.reporte import ReporteTransaccional

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
            'reportes': ReporteTransaccional.query.count(),
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
            'reportes': modulos_operativos['reportes'],
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