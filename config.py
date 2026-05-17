import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Buscamos el archivo .env oculto (donde irán las contraseñas reales luego)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def build_database_uri():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url

    engine = os.environ.get('DB_ENGINE', 'sqlite').lower().strip()

    if engine in ['postgres', 'postgresql']:
        user = os.environ.get('DB_USER', 'oncc_user')
        password = quote_plus(os.environ.get('DB_PASSWORD', 'oncc_password'))
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '5432')
        name = os.environ.get('DB_NAME', 'oncc_sistema')
        return f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'

    if engine in ['mysql', 'mariadb']:
        user = os.environ.get('DB_USER', 'oncc_user')
        password = quote_plus(os.environ.get('DB_PASSWORD', 'oncc_password'))
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '3306')
        name = os.environ.get('DB_NAME', 'oncc_sistema')
        return f'mysql+pymysql://{user}:{password}@{host}:{port}/{name}'

    sqlite_name = os.environ.get('SQLITE_DB_NAME', 'oncc_sistema.db')
    return f'sqlite:///{os.path.join(basedir, sqlite_name)}'


class Config:
    # 1. Clave de seguridad (Obligatoria para que funcionen los formularios de Flask-WTF)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'oncc-clave-super-secreta-region-nororiental-2026'

    # 2. Conexión a la base de datos (DATABASE_URL tiene prioridad).
    SQLALCHEMY_DATABASE_URI = build_database_uri()

    # 3. Optimización: Apagamos el rastreador de modificaciones para ahorrar memoria RAM
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
    # Seguridad de sesiones y cookies
    SESSION_COOKIE_SECURE = False  # True si el sitio está detrás de HTTPS (producción)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Flask-Login remember cookie
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # True en producción HTTPS
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # CSRF: no lo activamos globalmente aún (convertir formularios a Flask-WTF primero)
    WTF_CSRF_ENABLED = False
    # Nombre del rol que tiene permisos totales en el sistema
    SUPER_ROLE_NAME = os.environ.get('SUPER_ROLE_NAME', 'Director Regional')