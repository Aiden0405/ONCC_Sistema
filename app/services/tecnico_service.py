import secrets

from sqlalchemy.exc import IntegrityError

from app import db
from app.models.role import Role
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario


class TecnicoService:

    NOMBRES_ROL_TECNICO = ('Técnico', 'Tecnico')

    @staticmethod
    def _obtener_rol_tecnico():
        return Role.query.filter(Role.nombre_rol.in_(TecnicoService.NOMBRES_ROL_TECNICO)).first()

    @staticmethod
    def listar_tecnicos():
        role_tecnico = TecnicoService._obtener_rol_tecnico()
        if not role_tecnico:
            return []
        return Usuario.query.filter_by(id_rol=role_tecnico.id_rol).order_by(Usuario.nombre_usuario).all()

    @staticmethod
    def _perfiles_por_usuario(ids_usuarios):
        perfiles = {}
        ids = [i for i in ids_usuarios if i is not None]
        if ids:
            for perfil in Tecnico.query.filter(Tecnico.id_usuario.in_(ids)).all():
                perfiles[perfil.id_usuario] = perfil
        return perfiles

    @staticmethod
    def serializar(usuarios):
        perfiles = TecnicoService._perfiles_por_usuario([u.id_usuario for u in usuarios])
        resultado = []
        for u in usuarios:
            perfil = perfiles.get(u.id_usuario)
            resultado.append({
                'id_usuario': u.id_usuario,
                'nombre_usuario': u.nombre_usuario,
                'correo': u.correo,
                'cedula': perfil.cedula if perfil else None,
                'especialidad': perfil.especialidad if perfil else None,
                'estatus': u.estatus,
            })
        return resultado

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

        existe_cedula = Tecnico.query.filter_by(cedula=cedula).first()
        if existe_cedula:
            return {'ok': False, 'error': 'Ya existe un técnico con esa cédula.'}

        role_tecnico = TecnicoService._obtener_rol_tecnico()
        if not role_tecnico:
            return {'ok': False, 'error': 'El rol Técnico no existe. Ejecute flask seed primero.'}

        usuario = Usuario(
            nombre_usuario=nombre,
            correo=correo,
            id_rol=role_tecnico.id_rol,
            estatus=estatus,
        )
        usuario.set_password(secrets.token_urlsafe(10))
        db.session.add(usuario)

        try:
            db.session.flush()

            perfil = Tecnico(
                cedula=cedula,
                nombres=nombre,
                apellidos='',
                especialidad=especialidad,
                id_usuario=usuario.id_usuario,
            )
            db.session.add(perfil)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'ok': False, 'error': 'No se pudo registrar el técnico. Verifique que los datos no estén duplicados.'}

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

        existe_cedula = Tecnico.query.filter_by(cedula=cedula).first()
        if existe_cedula and existe_cedula.id_usuario != usuario.id_usuario:
            return {'ok': False, 'error': 'Ya existe otro técnico con esa cédula.'}

        usuario.nombre_usuario = nombre
        usuario.correo = correo
        usuario.estatus = estatus

        perfil = Tecnico.query.filter_by(id_usuario=usuario.id_usuario).first()
        if perfil:
            perfil.cedula = cedula
            perfil.nombres = nombre
            perfil.especialidad = especialidad
        else:
            perfil = Tecnico(
                cedula=cedula,
                nombres=nombre,
                apellidos='',
                especialidad=especialidad,
                id_usuario=usuario.id_usuario,
            )
            db.session.add(perfil)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'ok': False, 'error': 'No se pudo actualizar el técnico. Verifique que los datos no estén duplicados.'}

        return {'ok': True, 'mensaje': 'Técnico actualizado exitosamente.'}

    @staticmethod
    def eliminar_tecnico(tecnico_id):
        usuario = Usuario.query.get_or_404(tecnico_id)
        Tecnico.query.filter_by(id_usuario=usuario.id_usuario).delete()
        db.session.delete(usuario)
        db.session.commit()
