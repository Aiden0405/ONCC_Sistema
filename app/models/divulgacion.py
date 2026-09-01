# app/models/divulgacion.py
from datetime import datetime
from datetime import date

from app import db
from sqlalchemy.orm import synonym

class Divulgacion(db.Model):

    __tablename__ = 'divulgacion'

    # Clave primaria mapeada al campo físico de Postgres
    id = db.Column('id_divulgacion', db.Integer, primary_key=True)
    
    # Llave foránea hacia la tabla actividad del mismo módulo local
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False)
    
    # Campos específicos físicos mapeados a nombres limpios de Python
    nombre = db.Column('nombre_divulgacion', db.String(100), nullable=False)
    descripcion = db.Column('descripcion_divulgacion', db.Text, nullable=False)
    permiso = db.Column('permiso_divulgacion', db.String(50), nullable=False)

    # =========================================================================
    # RELACIONES (Navegación del ORM)
    # =========================================================================
    # Relación 1 a 1 con la Actividad base (uselist=False garantiza objeto directo)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False)
    
    # Cambia la relación a back_populates y especifica la foreign_key
    actividad_obj = db.relationship(
    'Actividad', 
    back_populates='divulgacion', # Apunta a la propiedad 'divulgacion' de la clase Actividad
    foreign_keys=[id_actividad])
    # =========================================================================
    # SINÓNIMOS (Para compatibilidad con controladores y consultas existentes)
    # =========================================================================
    id_divulgacion = synonym('id')
    nombre_divulgacion = synonym('nombre')
    descripcion_divulgacion = synonym('descripcion')
    permiso_divulgacion = synonym('permiso')

    def __repr__(self):
        return f"<Divulgacion {self.nombre}>"



class Divulgacion(db.Model):
    __tablename__ = 'divulgacion'
    __table_args__ = {'extend_existing': True}

    id_divulgacion = db.Column(db.Integer, primary_key=True)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False, unique=True)
    nombre_divulgacion = db.Column(db.String(100), nullable=False)
    descripcion_divulgacion = db.Column(db.Text, nullable=False)
    permiso_divulgacion = db.Column(db.String(50), nullable=False)

    # Relación con Actividad que permite eliminación en cascada limpia
    actividad = db.relationship('Actividad', foreign_keys=[id_actividad], backref=db.backref('divulgacion', uselist=False, cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Divulgacion {self.id_divulgacion}: {self.nombre_divulgacion}>"


class Publicacion(db.Model):

    __tablename__ = 'publicaciones'

    id_publicacion = db.Column(db.Integer, primary_key=True)
    id_divulgacion = db.Column(db.Integer, db.ForeignKey('divulgacion.id_divulgacion'), nullable=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(40), nullable=False)
    titulo_publicacion = db.Column(db.String(180), nullable=False)
    prioridad = db.Column(db.Integer, default=1, nullable=False)

    membrete = db.Column(db.Text, nullable=True)
    resumen = db.Column(db.Text, nullable=True)
    contenido = db.Column(db.Text, nullable=True)
    estado_publicacion = db.Column(db.String(20), nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False, default=date.today)
    publicado_en = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    actualizado_en = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    id = synonym('id_publicacion')
    titulo = synonym('titulo_publicacion')
    estado = synonym('estado_publicacion')

    autor = db.relationship(
        'Usuario',
        foreign_keys=[id_usuario],
        primaryjoin="Publicacion.id_usuario == Usuario.id_usuario",
        backref='publicaciones'
    )
    divulgacion = db.relationship(
        'Divulgacion',
        foreign_keys=[id_divulgacion],
        primaryjoin="Publicacion.id_divulgacion == Divulgacion.id_divulgacion",
        backref=db.backref('publicaciones', lazy='dynamic')
    )

    def __repr__(self):
        return f"<Publicacion {self.titulo_publicacion}>"