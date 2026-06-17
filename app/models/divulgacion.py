from datetime import datetime
from app import db
from sqlalchemy.orm import synonym

class Publicacion(db.Model):
    __tablename__ = 'publicaciones'

    # Columnas según database/sql.sql y actualización en Postgres
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(40), nullable=False, default='boletin')
    titulo = db.Column(db.String(180), nullable=False)
    # 🌟 AQUÍ AGREGAMOS LA PRIORIDAD QUE FALTABA
    prioridad = db.Column(db.Integer, default=1, nullable=False)
    
    resumen = db.Column(db.Text, nullable=True)
    contenido = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    publicado_en = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # === CORRECCIÓN DE LLAVE FORÁNEA INTER-BD ===
    # 1. Quitamos el db.ForeignKey físico en Python para evitar el colapso de mappers
    id_usuario = db.Column(db.Integer, nullable=False)
    
    # 2. Hacemos la relación lógica cruzando las bases de datos en memoria
    autor = db.relationship(
        'Usuario', 
        foreign_keys=[id_usuario],
        primaryjoin="Publicacion.id_usuario == Usuario.id_usuario",
        backref='publicaciones'
    )

    # Sinónimos para compatibilidad con el código que esperaba otros nombres
    id_divulgacion = synonym('id')
    titulo_publicidad = synonym('titulo')
    estatus_revision = synonym('estado')
    created_at = synonym('creado_en')
    updated_at = synonym('actualizado_en')

    def __repr__(self):
        return f"<Publicacion {self.titulo}>"