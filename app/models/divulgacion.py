from app import db
from sqlalchemy.orm import synonym

class Publicacion(db.Model):
    __tablename__ = 'publicaciones'
    __table_args__ = {'extend_existing': True}

    # 1. Campos REALES (Ahora incluye la prioridad que agregaste con el ALTER TABLE)
    id_publicacion = db.Column(db.Integer, primary_key=True)
    id_divulgacion = db.Column(db.Integer, nullable=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(40), nullable=False)
    titulo_publicacion = db.Column(db.String(180), nullable=False)
    
    # 🌟 AQUÍ ESTÁ: Ahora es una columna física real
    prioridad = db.Column(db.Integer, default=1, nullable=False)
    
    membrete = db.Column(db.Text, nullable=True)
    resumen = db.Column(db.Text, nullable=True)
    contenido = db.Column(db.Text, nullable=True)
    estado_publicacion = db.Column(db.String(20), nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)
    publicado_en = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    actualizado_en = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # 2. SINÓNIMOS (Mantienen tus HTML intactos sin cambiar p.titulo o p.estado)
    id = synonym('id_publicacion')
    titulo = synonym('titulo_publicacion')
    estado = synonym('estado_publicacion')

    # Relación lógica en memoria
    autor = db.relationship(
        'Usuario', 
        foreign_keys=[id_usuario],
        primaryjoin="Publicacion.id_usuario == Usuario.id_usuario",
        backref='publicaciones'
    )

    def __repr__(self):
        return f"<Publicacion {self.titulo_publicacion}>"