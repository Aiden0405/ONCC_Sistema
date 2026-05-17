from app import db
from app.models.bitacora import BitacoraTransaccion


def registrar_accion(modulo, registro_id, accion, usuario_nombre, detalle=None, estado_nuevo=None):
    try:
        bit = BitacoraTransaccion(
            modulo=modulo,
            registro_id=registro_id or 0,
            accion=accion,
            estado_nuevo=estado_nuevo,
            usuario=usuario_nombre or 'Sistema',
            detalle=detalle,
        )
        db.session.add(bit)
        db.session.commit()
    except Exception:
        db.session.rollback()
