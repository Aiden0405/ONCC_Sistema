from datetime import datetime
from app import db
from sqlalchemy.orm import synonym


class CategoriaEquipo(db.Model):
    __tablename__ = 'categoria'
    __table_args__ = {'extend_existing': True}

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre_categoria = db.Column(db.String(50), nullable=False)
    descripcion_categoria = db.Column(db.Text, nullable=False, default='Categoría automática del sistema',
                                      server_default='Categoría automática del sistema')


class ModeloEquipo(db.Model):
    __tablename__ = 'modelos_equipo'
    __table_args__ = {'extend_existing': True}

    id_modelos_equipo = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'), nullable=False)
    nombre_modelos_equipo = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False, default='N/D')
    marca = db.Column(db.String(50), nullable=False, default='N/D')

    categoria = db.relationship('CategoriaEquipo', backref=db.backref('modelos', lazy='dynamic'))


class UbicacionEquipo(db.Model):
    __tablename__ = 'ubicacion'
    __table_args__ = {'extend_existing': True}

    id_ubicacion = db.Column(db.Integer, primary_key=True)
    id_parroquia = db.Column(db.Integer, nullable=False)
    nombre_ubicacion = db.Column(db.String(100), nullable=False)


class MovimientoEquipo(db.Model):
    __tablename__ = 'movimiento_equipo'

    id_movimiento = db.Column(db.Integer, primary_key=True)
    id_equipo = db.Column(db.Integer, db.ForeignKey('equipo.id_equipo'), nullable=False)
    fecha_movimiento = db.Column(db.Date, nullable=False)
    ubicacion_origen = db.Column(db.String(100), nullable=False)
    ubicacion_destino = db.Column(db.String(100), nullable=False)
    motivo_responsable = db.Column(db.String(200), nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    equipo_rel = db.relationship('InventarioEquipo', backref=db.backref('movimientos', lazy='dynamic'))

    @property
    def codigo(self):
        return f'#MOV-{self.id_movimiento:03d}'

    @property
    def codigo_equipo(self):
        return self.equipo_rel.codigo_interno if self.equipo_rel else '—'


class InventarioEquipo(db.Model):
    __tablename__ = 'equipo'  # Nombre oficial en Postgres
    __table_args__ = {'extend_existing': True}

    # Columnas REALES de la tabla equipo
    id_equipo = db.Column(db.Integer, primary_key=True)
    id_modelos_equipos = db.Column(db.Integer, db.ForeignKey('modelos_equipo.id_modelos_equipo'), nullable=False)
    id_ubicacion_actual = db.Column(db.Integer, db.ForeignKey('ubicacion.id_ubicacion'), nullable=True)
    codigo_interno = db.Column(db.String(50), nullable=False, unique=True)
    numero_serie = db.Column(db.String(250), nullable=True)
    estado = db.Column(db.String(30), nullable=False)  # Estado de flujo: Disponible / En Uso / En Mantenimiento
    condicion = db.Column(db.String(30), nullable=False, default='Operativo')  # Condición: Operativo / Requiere Mantenimiento / Dañado
    fecha_ingreso = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    ultimo_mantenimiento = db.Column(db.Date, nullable=True)
    responsable = db.Column(db.String(120), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)

    # Relaciones
    modelo_rel = db.relationship('ModeloEquipo', backref=db.backref('equipos', lazy='dynamic'))
    ubicacion_rel = db.relationship('UbicacionEquipo', backref=db.backref('equipos', lazy='dynamic'))

    # Sinónimos para compatibilidad con controladores y plantillas existentes
    id = synonym('id_equipo')
    codigo = synonym('codigo_interno')
    estado_operativo = synonym('condicion')
    creado_en = synonym('fecha_ingreso')

    # Propiedades derivadas (lectura) que resuelven las vistas y reportes
    @property
    def tipo_equipo(self):
        return self.modelo_rel.nombre_modelos_equipo if self.modelo_rel else 'Sin Modelo'

    @property
    def ubicacion(self):
        return self.ubicacion_rel.nombre_ubicacion if self.ubicacion_rel else 'Sin Ubicación'

    @property
    def estado_flujo(self):
        return self.estado

    @property
    def actualizado_en(self):
        return self.ultimo_mantenimiento or self.fecha_ingreso
