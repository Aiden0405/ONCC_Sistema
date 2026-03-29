import os
from dotenv import load_dotenv

# Buscamos el archivo .env oculto (donde irán las contraseñas reales luego)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # 1. Clave de seguridad (Obligatoria para que funcionen los formularios de Flask-WTF)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'oncc-clave-super-secreta-region-nororiental-2026'
    
    # 2. Conexión a la Base de Datos (¡Cambiado a SQLite para que corra YA MISMO sin errores!)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///oncc_sistema.db'
    
    # 3. Optimización: Apagamos el rastreador de modificaciones para ahorrar memoria RAM
    SQLALCHEMY_TRACK_MODIFICATIONS = False