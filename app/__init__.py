from collections import Counter

from flask import Flask, render_template, session 
from flask_login import LoginManager, login_required
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_mail import Mail 

from config import Config

migrate = Migrate()
csrf = CSRFProtect()
mail = Mail() 

# 1. Herramientas
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'core.login'
login_manager.login_message = "Por favor, inicie sesión para acceder al sistema ONCC."

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 🌟 CONFIGURACIÓN CON MAILTRAP PARA DESARROLLO (SIN BLOQUEOS)
    app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    
    # 🔑 Credenciales de desarrollo de tu Inbox virtual en Mailtrap
    app.config['MAIL_USERNAME'] = 'e4f11f28a9ae86'
    app.config['MAIL_PASSWORD'] = '7b85444a15b2a5'
    
    app.config['MAIL_DEFAULT_SENDER'] = ('ONCC Sistema', 'soporte@oncc.gob.ve')

    # Conectar BD, Login y el servicio de correos a la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app) 

    from app.models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # ==============================================================
    # REGISTRO DE CONTROLADORES (Blueprints)
    # ==============================================================
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
        from app.models.geomatica import ElementoMapaRiesgo  # noqa: F401
        from app.models.inventario import InventarioEquipo  # noqa: F401
        from app.models.visita_portal import VisitaPortal  # noqa: F401
        from app.models.password_reset import PasswordReset  # noqa: F401
        from app.models.usuario import Usuario  # noqa: F401
        from app.models.role import Role, Permission  # noqa: F401
        from app.models.notificacion import Notificacion  # noqa: F401

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
    from app.blueprints.core.controllers.usuarios import usuario_editar as core_usuario_editar
    from app.blueprints.core.controllers.usuarios import usuario_eliminar as core_usuario_eliminar
    from app.blueprints.core.controllers.usuarios import usuario_index as core_usuario_index
    from app.blueprints.core.controllers.usuarios import usuario_nuevo as core_usuario_nuevo
    from app.blueprints.core.controllers.usuarios import usuario_perfil as core_usuario_perfil
    
    # 📦 CONTROLADORES DE LOGÍSTICA (AILEEN)
    from app.blueprints.logistica.controllers.inventario import editar as logistica_inventario_editar
    from app.blueprints.logistica.controllers.inventario import eliminar as logistica_inventario_eliminar
    from app.blueprints.logistica.controllers.inventario import inventario_index as logistica_inventario_index
    from app.blueprints.logistica.controllers.inventario import nuevo as logistica_inventario_nuevo
    from app.blueprints.logistica.controllers.inventario import nuevo_movimiento as logistica_nuevo_movimiento
    from app.blueprints.logistica.controllers.inventario import editar_movimiento as logistica_editar_movimiento
    from app.blueprints.logistica.controllers.inventario import eliminar_movimiento as logistica_eliminar_movimiento
    from app.blueprints.logistica.controllers.inventario import acta_responsabilidad as logistica_acta_responsabilidad
    from app.blueprints.logistica.controllers.inventario import reporte_inventario as logistica_reporte_inventario
    from app.blueprints.logistica.controllers.inventario import reporte_movimientos as logistica_reporte_movimientos
    
    from app.blueprints.logistica.controllers.tecnicos_campo import tecnicos_campo_index as logistica_tecnicos_index
    from app.blueprints.logistica.controllers.tecnicos_campo import tecnicos_nuevo as logistica_tecnicos_nuevo
    from app.blueprints.logistica.controllers.tecnicos_campo import tecnicos_editar as logistica_tecnicos_editar
    from app.blueprints.logistica.controllers.tecnicos_campo import tecnicos_eliminar as logistica_tecnicos_eliminar
    
    # 🗺️ CONTROLADORES DE MAPAS ACTUALIZADOS DESDE RAMA GABRIEL
    from app.blueprints.mapas.controllers.riesgo import eliminar_mapa as mapas_cambiar_estado
    from app.blueprints.mapas.controllers.riesgo import mapas_riesgo_index as mapas_index
    from app.blueprints.mapas.controllers.riesgo import vista_carga_ssbc, vista_dibujar_mapa
    from app.blueprints.mapas.controllers.riesgo import obtener_todos_mapas, crear_mapa as mapas_crear_mapa, obtener_mapa as mapas_obtener_mapa, actualizar_mapa as mapas_actualizar_mapa, eliminar_mapa as mapas_eliminar_mapa, procesar_archivo as mapas_procesar_archivo
    from app.blueprints.monitoreo.controllers.actividades import actividades_cambiar_estado as monitoreo_actividad_cambiar_estado
    from app.blueprints.monitoreo.controllers.actividades import actividades_index as monitoreo_actividad_index
    from app.blueprints.monitoreo.controllers.actividades import nueva as monitoreo_actividad_nueva
    from app.blueprints.comunitario.controllers.formaciones import formacion_cambiar_estado
    from app.blueprints.comunitario.controllers.formaciones import formacion_nuevo
    from app.blueprints.comunitario.controllers.formaciones import formaciones_index as comunitario_formaciones_index
    from app.blueprints.comunitario.controllers.sensibilizaciones import sensibilizacion_cambiar_estado
    from app.blueprints.comunitario.controllers.sensibilizaciones import sensibilizacion_editar as sensibilizacion_nuevo
    from app.blueprints.comunitario.controllers.sensibilizaciones import sensibilizaciones_index as comunitario_sensibilizaciones_index

    app.add_url_rule('/', endpoint='public.home', view_func=core_home)
    app.add_url_rule('/acerca', endpoint='public.acerca', view_func=core_acerca)
    app.add_url_rule('/servicios', endpoint='public.servicios', view_func=core_servicios)
    app.add_url_rule('/contacto', endpoint='public.contacto', view_func=core_contacto)
    app.add_url_rule('/auth/login', endpoint='auth.login', view_func=core_login, methods=['GET', 'POST'])
    app.add_url_rule('/auth/logout', endpoint='auth.logout', view_func=core_logout)
    app.add_url_rule('/auth/recuperar', endpoint='auth.recuperar_contrasena', view_func=core_recuperar, methods=['GET', 'POST'])

    # Enlazar la nueva ruta dinámica de restablecer que procesará los tokens reales
    from app.blueprints.core.controllers.auth import restablecer_contrasena as core_restablecer
    app.add_url_rule('/auth/restablecer/<token>', endpoint='core.restablecer_contrasena', view_func=core_restablecer, methods=['GET', 'POST'])

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

    # 📦 REGLAS DE ENRUTAMIENTO DE LOGÍSTICA (INVENTARIO)
    app.add_url_rule('/inventario/', endpoint='inventario.index', view_func=logistica_inventario_index)
    app.add_url_rule('/inventario/nuevo', endpoint='inventario.nuevo', view_func=logistica_inventario_nuevo, methods=['POST'])
    app.add_url_rule('/inventario/<int:equipo_id>/editar', endpoint='inventario.editar', view_func=logistica_inventario_editar, methods=['POST'])
    app.add_url_rule('/inventario/<int:equipo_id>/eliminar', endpoint='inventario.eliminar', view_func=logistica_inventario_eliminar, methods=['POST'])
    # 🔄 RUTAS INTERNAS PARA MOVIMIENTOS DE INVENTARIO
    app.add_url_rule('/inventario/nuevo-movimiento', endpoint='inventario.nuevo_movimiento', view_func=logistica_nuevo_movimiento, methods=['POST'])
    app.add_url_rule('/inventario/movimiento/<int:movimiento_id>/editar', endpoint='inventario.editar_movimiento', view_func=logistica_editar_movimiento, methods=['POST'])
    app.add_url_rule('/inventario/movimiento/<int:movimiento_id>/eliminar', endpoint='inventario.eliminar_movimiento', view_func=logistica_eliminar_movimiento, methods=['POST'])
    
    # 📄 RUTAS PARA REPORTES Y ACTAS EN PDF
    app.add_url_rule('/inventario/reporte', endpoint='inventario.reporte_inventario', view_func=logistica_reporte_inventario, methods=['GET'])
    app.add_url_rule('/inventario/reporte-movimientos', endpoint='inventario.reporte_movimientos', view_func=logistica_reporte_movimientos, methods=['GET'])
    app.add_url_rule('/inventario/<int:equipo_id>/acta', endpoint='inventario.acta_responsabilidad', view_func=logistica_acta_responsabilidad, methods=['GET'])
    
    # 👷 REGLAS PARA TÉCNICOS DE CAMPO
    app.add_url_rule('/tecnicos-campo', endpoint='logistica.tecnicos_campo_index', view_func=logistica_tecnicos_index)
    app.add_url_rule('/tecnicos-campo/nuevo', endpoint='logistica.tecnicos_nuevo', view_func=logistica_tecnicos_nuevo, methods=['POST'])
    app.add_url_rule('/tecnicos-campo/<int:tecnico_id>/editar', endpoint='logistica.tecnicos_editar', view_func=logistica_tecnicos_editar, methods=['POST'])
    app.add_url_rule('/tecnicos-campo/<int:tecnico_id>/eliminar', endpoint='logistica.tecnicos_eliminar', view_func=logistica_tecnicos_eliminar, methods=['POST'])

    # 🗺️ REGLAS DE ENRUTAMIENTO CORREGIDAS PARA EVITAR EL BUILDERROR
    app.add_url_rule('/geomatica/', endpoint='geomatica.index', view_func=mapas_index, methods=['GET'])
    app.add_url_rule('/geomatica/carga-ssbc', endpoint='geomatica.carga_ssbc', view_func=vista_carga_ssbc, methods=['GET'])
    app.add_url_rule('/geomatica/dibujar/<int:mapa_id>', endpoint='geomatica.dibujar_mapa', view_func=vista_dibujar_mapa, methods=['GET'])
    app.add_url_rule('/geomatica/procesar', endpoint='geomatica.procesar_archivo', view_func=mapas_procesar_archivo, methods=['POST'])
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


    # ==============================================================
    # ⏱️ FILTRO PERSONALIZADO PARA CALCULAR EL TIEMPO TRANSCURRIDO
    # ==============================================================
    @app.template_filter('tiempo_atras')
    def tiempo_atras_filter(fecha):
        if not fecha:
            return "Ahora"
            
        from datetime import datetime
        ahora = datetime.utcnow()
        diferencia = ahora - fecha

        segundos = int(diferencia.total_seconds())
        
        if segundos < 60:
            return "Hace un momento"
        
        minutos = segundos // 60
        if minutos < 60:
            return f"Hace {minutos} min"
            
        horas = minutos // 60
        if horas < 24:
            return f"Hace {horas} {'hora' if horas == 1 else 'horas'}"
            
        dias = horas // 24
        if dias == 1:
            return "Ayer"
        if dias < 7:
            return f"Hace {dias} días"
            
        return fecha.strftime('%d/%m/%Y')

    @app.context_processor
    def inject_notifications():
        from app.models.notificacion import Notificacion
        from flask_login import current_user

        if current_user.is_authenticated:
            alertas = Notificacion.query.filter(
                (Notificacion.usuario_id == current_user.id_usuario) | (Notificacion.usuario_id.is_(None))
            ).order_by(Notificacion.fecha_creacion.desc()).limit(5).all()
            
            conteo_alertas = Notificacion.query.filter(
                (Notificacion.usuario_id == current_user.id_usuario) | (Notificacion.usuario_id.is_(None)),
                Notificacion.leido == False
            ).count()
            
            return dict(alertas_sistema=alertas, conteo_alertas=conteo_alertas)
        
        return dict(alertas_sistema=[], conteo_alertas=0)
    # Manejador global de errores URL (404)
    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        return render_template('404.html'), 404

    return app