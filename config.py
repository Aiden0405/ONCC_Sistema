import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def build_database_uri():
    engine = os.environ.get('DB_ENGINE', 'postgresql')

    if engine in ['postgres', 'postgresql']:
        user = os.environ.get('DB_USER', 'postgres')
        password = quote_plus(os.environ.get('DB_PASSWORD', ''))
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '5432')
        name = os.environ.get('DB_NAME', 'oncc')
        return f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'

    # ... (Tus bloques de MySQL y SQLite se quedan exactamente igual)
    sqlite_name = os.environ.get('SQLITE_DB_NAME', 'oncc.db')
    return f'sqlite:///{os.path.join(basedir, sqlite_name)}'


# --- NUEVA FUNCIÓN AGREGADA ---
def build_security_database_uri():
    """Genera la URI para conectar específicamente a la base de datos de seguridad."""
    engine = os.environ.get('DB_ENGINE', 'postgresql')
    
    if engine in ['postgres', 'postgresql']:
        user = os.environ.get('DB_USER', 'postgres')
        password = quote_plus(os.environ.get('DB_PASSWORD', ''))
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '5432')
        # Buscamos la variable nueva del .env, si no existe usa 'oncc_seguridad' por defecto
        name = os.environ.get('DB_NAME_SEGURIDAD', 'oncc_seguridad')
        return f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'
        
    return None # Si usas SQLite o MySQL, puedes mapear algo similar aquí si lo requieres


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)

    # Base de datos general (la que maneja todo el negocio)
    SQLALCHEMY_DATABASE_URI = build_database_uri()

    # --- NUEVA CONFIGURACIÓN AGREGADA ---
    # Enlazamos la etiqueta 'seguridad' con la URI de la base de datos de seguridad
    SQLALCHEMY_BINDS = {
        'seguridad': build_security_database_uri()
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
    
    # ... (El resto de tus configuraciones de cookies y roles se quedan exactamente igual)
    SESSION_COOKIE_SECURE = os.environ.get('COOKIE_SECURE', 'true').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    SUPER_ROLE_NAME = os.environ.get('SUPER_ROLE_NAME', 'Director Regional')
    # Claves oficiales de prueba de Google para desarrollo local.
    # Sustituir ambas mediante .env antes de publicar el sistema.
    RECAPTCHA_SITE_KEY = os.environ.get(
        'RECAPTCHA_SITE_KEY',
        '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
    )
    RECAPTCHA_SECRET_KEY = os.environ.get(
        'RECAPTCHA_SECRET_KEY',
        '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
    )
    RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'