from datetime import datetime
from app import db
from sqlalchemy.orm import synonym

class Divulgacion(db.Model):

    __tablename__ = 'divulgacion'

    # Clave primaria mapeada al campo físico de Postgres
    id = db.Column('id_divulgacion', db.Integer, primary_key=True)
    
    # Llave foránea hacia la tabla actividades
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False)
    
    # Campos específicos físicos mapeados a nombres limpios de Python
    nombre = db.Column('nombre_divulgacion', db.String(100), nullable=False)
    descripcion = db.Column('descripcion_divulgacion', db.Text, nullable=False)
    permiso = db.Column('permiso_divulgacion', db.String(50), nullable=False)

    # Relación 1 a 1 con la Actividad base
    actividad_obj = db.relationship(
        'Actividad', 
        back_populates='divulgacion',
        foreign_keys=[id_actividad]
    )

    # Sinónimos
    id_divulgacion = synonym('id')
    nombre_divulgacion = synonym('nombre')
    descripcion_divulgacion = synonym('descripcion')
    permiso_divulgacion = synonym('permiso')

    def __repr__(self):
        return f"<Divulgacion {self.nombre}>"


class Publicacion(db.Model):
    __tablename__ = 'publicaciones'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(40), nullable=False, default='boletin')
    titulo = db.Column(db.String(180), nullable=False)
    resumen = db.Column(db.Text, nullable=True)
    contenido = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    publicado_en = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    autor = db.relationship('Usuario', backref='publicaciones')

    id_divulgacion = synonym('id')
    titulo_publicidad = synonym('titulo')
    estatus_revision = synonym('estado')
    estado_publicacion = synonym('estado')
    created_at = synonym('creado_en')
    updated_at = synonym('actualizado_en')

    def __repr__(self):
        return f"<Publicacion {self.titulo}>"
