# app/models/divulgacion.py
from datetime import datetime
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
    actividad = db.relationship('Actividad', backref=db.backref('divulgacion', uselist=False))

    # =========================================================================
    # SINÓNIMOS (Para compatibilidad con controladores y consultas existentes)
    # =========================================================================
    id_divulgacion = synonym('id')
    nombre_divulgacion = synonym('nombre')
    descripcion_divulgacion = synonym('descripcion')
    permiso_divulgacion = synonym('permiso')

    def __repr__(self):
        return f"<Divulgacion {self.nombre}>"


class Publicacion(db.Model):

    __tablename__ = 'publicaciones'

    # Clave primaria mapeada al campo físico 'id_publicacion'
    id = db.Column('id_publicacion', db.Integer, primary_key=True)
    
    # Enlace de clave foránea física hacia la tabla divulgación que está arriba
    id_divulgacion_fk = db.Column('id_divulgacion', db.Integer, db.ForeignKey('divulgacion.id_divulgacion'), nullable=True)
    
    # Columnas de control y contenido
    tipo = db.Column(db.String(40), nullable=False, default='boletin')
    titulo = db.Column('titulo_publicacion', db.String(180), nullable=False)
    prioridad = db.Column(db.Integer, default=1, nullable=False)
    resumen = db.Column(db.Text, nullable=True)
    contenido = db.Column(db.Text, nullable=True)
    estado = db.Column('estado_publicacion', db.String(20), nullable=False, default='borrador')
    
    # Tiempos de auditoría
    publicado_en = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # =========================================================================
    # RELACIONES (Navegación del ORM)
    # =========================================================================
    # Relación directa uno a muchos con Divulgacion (carga inmediata y segura)
    divulgacion = db.relationship('Divulgacion', backref='publicaciones')

    # =========================================================================
    # SINÓNIMOS (Para compatibilidad con controladores y consultas existentes)
    # =========================================================================
    id_publicacion = synonym('id')
    titulo_publicidad = synonym('titulo')
    estatus_revision = synonym('estado')
    created_at = synonym('creado_en')
    updated_at = synonym('actualizado_en')

    def __repr__(self):
        return f"<Publicacion {self.titulo}>"