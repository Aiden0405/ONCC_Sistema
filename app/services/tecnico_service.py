import secrets

from sqlalchemy.exc import IntegrityError

from app import db
from app.models.role import Role
from app.models.usuario import Usuario


class TecnicoService:

    @staticmethod
    def listar_tecnicos():
        role_tecnico = Role.query.filter_by(nombre_rol='Técnico').first()
        if not role_tecnico:
            return []
        return Usuario.query.filter_by(id_rol=role_tecnico.id_rol).order_by(Usuario.nombre_usuario).all()

    @staticmethod
    def serializar(tecnicos):
        return [{
            'id_usuario': u.id_usuario,
            'nombre_usuario': u.nombre_usuario,
            'correo': u.correo,
            'cedula': u.cedula,
            'especialidad': u.especialidad,
            'estatus': u.estatus,
        } for u in tecnicos]

    @staticmethod
    def crear_tecnico(datos):
        nombre = datos.get('nombre', '').strip()
        correo = datos.get('correo', '').strip().lower()
        cedula = datos.get('cedula', '').strip()
        especialidad = datos.get('especialidad', '').strip()
        estatus_val = datos.get('estatus', '1')
        estatus = estatus_val == '1'

        if not nombre or not correo or not cedula or not especialidad:
            return {'ok': False, 'error': 'Todos los campos son obligatorios.'}

        existe_correo = Usuario.query.filter_by(correo=correo).first()
        if existe_correo:
            return {'ok': False, 'error': 'Ya existe un usuario con ese correo.'}

        if cedula:
            existe_cedula = Usuario.query.filter_by(cedula=cedula).first()
            if existe_cedula:
                return {'ok': False, 'error': 'Ya existe un usuario con esa cédula.'}

        role_tecnico = Role.query.filter_by(nombre_rol='Técnico').first()
        if not role_tecnico:
            return {'ok': False, 'error': 'El rol Técnico no existe. Ejecute flask seed primero.'}

        usuario = Usuario(
            nombre_usuario=nombre,
            correo=correo,
            cedula=cedula,
            especialidad=especialidad,
            id_rol=role_tecnico.id_rol,
            estatus=estatus,
        )
        usuario.set_password(secrets.token_urlsafe(10))
        db.session.add(usuario)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'ok': False, 'error': 'Esa cédula ya está registrada en el sistema.'}

        return {'ok': True, 'mensaje': 'Técnico registrado exitosamente.'}

    @staticmethod
    def actualizar_tecnico(tecnico_id, datos):
        usuario = Usuario.query.get_or_404(tecnico_id)

        nombre = datos.get('nombre', '').strip()
        correo = datos.get('correo', '').strip().lower()
        cedula = datos.get('cedula', '').strip()
        especialidad = datos.get('especialidad', '').strip()
        estatus_val = datos.get('estatus', '1')
        estatus = estatus_val == '1'

        if not nombre or not correo or not cedula or not especialidad:
            return {'ok': False, 'error': 'Todos los campos son obligatorios.'}

        existe_correo = Usuario.query.filter_by(correo=correo).first()
        if existe_correo and existe_correo.id_usuario != usuario.id_usuario:
            return {'ok': False, 'error': 'Ya existe otro usuario con ese correo.'}

        if cedula:
            existe_cedula = Usuario.query.filter_by(cedula=cedula).first()
            if existe_cedula and existe_cedula.id_usuario != usuario.id_usuario:
                return {'ok': False, 'error': 'Ya existe otro usuario con esa cédula.'}

        usuario.nombre_usuario = nombre
        usuario.correo = correo
        usuario.cedula = cedula
        usuario.especialidad = especialidad
        usuario.estatus = estatus

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'ok': False, 'error': 'Esa cédula ya está registrada en el sistema.'}

        return {'ok': True, 'mensaje': 'Técnico actualizado exitosamente.'}

    @staticmethod
    def eliminar_tecnico(tecnico_id):
        usuario = Usuario.query.get_or_404(tecnico_id)
        db.session.delete(usuario)
        db.session.commit()
