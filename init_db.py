from app import create_app, db
from app.models.actividad import Actividad
from app.models.bitacora import BitacoraTransaccion
from app.models.comunidad import Comunidad
from app.models.formacion import Formacion
from app.models.geomatica import MapaRegistro
from app.models.inventario import InventarioEquipo
from app.models.reporte import ReporteTransaccional
from app.models.sensibilizacion import Sensibilizacion
from app.models.visita_portal import VisitaPortal
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    print("Creando la base de datos SQLite...")
    print(f"Base de datos activa: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # 1. Crea todas las tablas 
    db.create_all()
    print("Tablas creadas exitosamente.")

    # 2. Verificar si el usuario Director ya existe
    director = Usuario.query.filter_by(email='director@oncc.gob.ve').first()
    
    if not director:
        print("Creando el usuario Director por defecto...")
        nuevo_director = Usuario(
            nombre='Director Regional',
            email='director@oncc.gob.ve',
            rol='Director',
            estatus=True
        )
        nuevo_director.set_password('123456')
        
        db.session.add(nuevo_director)
        db.session.commit()
        
        print("¡Usuario 'director@oncc.gob.ve' creado con la clave '123456'!")
    else:
        print("El usuario Director ya estaba registrado.")