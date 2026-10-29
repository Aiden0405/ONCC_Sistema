from collections import Counter
from datetime import datetime, date
from xml.sax.saxutils import escape

from flask import current_app, Response
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from app import db
from app.models.bitacora import BitacoraTransaccion
from app.models.inventario import InventarioEquipo, MovimientoEquipo
from app.services.notificacion import ServicioNotificacion
from app.utils.validation import normalize_text


class InventarioService:

    CATEGORIA_DEFAULT = 'General'
    TIPOS_EQUIPO_INVALIDOS = {
        '',
        'Seleccione...',
        'Seleccione un tipo de equipo...',
        '__nuevo_equipo__',
    }

    @staticmethod
    def listar_equipos():
        return InventarioEquipo.query.order_by(InventarioEquipo.creado_en.desc()).all()

    @staticmethod
    def serializar(equipos):
        return [{
            'id': e.id,
            'tipo_equipo': e.tipo_equipo,
            'codigo': e.codigo,
            'ubicacion': e.ubicacion,
            'responsable': e.responsable,
            'estado_operativo': e.estado_operativo,
            'estado_flujo': e.estado_flujo,
            'ultimo_mantenimiento': e.ultimo_mantenimiento.strftime('%Y-%m-%d') if e.ultimo_mantenimiento else None,
        } for e in equipos]

    @staticmethod
    def listar_movimientos():
        return MovimientoEquipo.query.order_by(MovimientoEquipo.fecha_movimiento.desc(), MovimientoEquipo.id_movimiento.desc()).all()

    @staticmethod
    def serializar_movimientos(movimientos):
        return [{
            'id': m.id_movimiento,
            'codigo': m.codigo,
            'equipo': m.codigo_equipo,
            'fecha': m.fecha_movimiento.strftime('%Y-%m-%d'),
            'origen': m.ubicacion_origen,
            'destino': m.ubicacion_destino,
            'motivo': m.motivo_responsable,
        } for m in movimientos]

    @staticmethod
    def listar_modelos():
        from app.models.inventario import ModeloEquipo

        return ModeloEquipo.query.order_by(ModeloEquipo.nombre_modelos_equipo).all()

    @staticmethod
    def serializar_modelos(modelos):
        return [{'id': m.id_modelos_equipo, 'nombre': m.nombre_modelos_equipo} for m in modelos]

    @staticmethod
    def crear_modelo(nombre, usuario):
        try:
            nombre = normalize_text(nombre, max_length=100, field='El nombre del tipo de equipo')
        except ValueError as error:
            return {'ok': False, 'error': str(error)}

        modelo = InventarioService._obtener_o_crear_modelo(nombre)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {'ok': False, 'error': 'No se pudo registrar el tipo de equipo.'}

        mensaje = f"Se registró el tipo de equipo {modelo.nombre_modelos_equipo}."
        ServicioNotificacion.notificar_por_permiso(
            'gestionar_inventario', mensaje, emisor_id=usuario.id_usuario
        )
        ServicioNotificacion.crear_aviso(
            id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Inventario'
        )

        return {'ok': True, 'modelo': modelo}

    @staticmethod
    def eliminar_modelo(modelo_id, usuario):
        from app.models.inventario import ModeloEquipo

        modelo = ModeloEquipo.query.get(modelo_id)
        if not modelo:
            return {'ok': False, 'error': 'El tipo de equipo no existe.'}

        equipo_asociado = InventarioEquipo.query.filter_by(id_modelos_equipos=modelo.id_modelos_equipo).first()
        if equipo_asociado:
            return {'ok': False, 'error': 'No se puede eliminar: hay equipos registrados con este tipo.'}

        nombre = modelo.nombre_modelos_equipo
        db.session.delete(modelo)
        db.session.commit()

        mensaje = f"Se eliminó el tipo de equipo {nombre}."
        ServicioNotificacion.notificar_por_permiso(
            'gestionar_inventario', mensaje, emisor_id=usuario.id_usuario
        )
        ServicioNotificacion.crear_aviso(
            id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Inventario'
        )

        return {'ok': True, 'nombre': nombre}

    @staticmethod
    def _obtener_o_crear_modelo(nombre):
        from app.models.inventario import CategoriaEquipo, ModeloEquipo

        modelo = ModeloEquipo.query.filter_by(nombre_modelos_equipo=nombre).first()
        if modelo:
            return modelo

        categoria = CategoriaEquipo.query.filter_by(nombre_categoria=InventarioService.CATEGORIA_DEFAULT).first()
        if not categoria:
            categoria = CategoriaEquipo(nombre_categoria=InventarioService.CATEGORIA_DEFAULT)
            db.session.add(categoria)
            db.session.flush()

        modelo = ModeloEquipo(
            id_categoria=categoria.id_categoria,
            nombre_modelos_equipo=nombre,
        )
        db.session.add(modelo)
        db.session.flush()
        return modelo

    @staticmethod
    def _obtener_o_crear_ubicacion(nombre):
        from app.models.inventario import UbicacionEquipo

        ubicacion = UbicacionEquipo.query.filter_by(nombre_ubicacion=nombre).first()
        if ubicacion:
            return ubicacion

        ubicacion = UbicacionEquipo(
            id_parroquia=InventarioService._obtener_parroquia_por_defecto(),
            nombre_ubicacion=nombre,
        )
        db.session.add(ubicacion)
        db.session.flush()
        return ubicacion

    @staticmethod
    def _obtener_parroquia_por_defecto():
        from app.models.esquema_activo import EstadoActivo, MunicipioActivo, ParroquiaActiva

        parroquia = ParroquiaActiva.query.first()
        if parroquia:
            return parroquia.id_parroquia

        estado = EstadoActivo.query.first()
        if not estado:
            estado = EstadoActivo(nombre_estado='Sin Estado')
            db.session.add(estado)
            db.session.flush()

        municipio = MunicipioActivo.query.first()
        if not municipio:
            municipio = MunicipioActivo(id_estado=estado.id_estado, nombre_municipio='Sin Municipio')
            db.session.add(municipio)
            db.session.flush()

        parroquia = ParroquiaActiva(id_municipio=municipio.id_municipio, nombre_parroquia='Sin Parroquia')
        db.session.add(parroquia)
        db.session.flush()
        return parroquia.id_parroquia

    @staticmethod
    def _solo_letras_y_espacios(valor):
        return all(caracter.isalpha() or caracter == ' ' for caracter in valor)

    @staticmethod
    def _validar_datos_equipo(datos):
        """Valida que ningún campo obligatorio del equipo llegue vacío.

        Devuelve (valores, error). Solo uno de los dos será distinto de None.
        """
        campos_texto = {
            'tipo_equipo': 'El tipo de equipo',
            'codigo': 'El código del equipo',
            'ubicacion': 'La ubicación',
            'responsable': 'El responsable',
            'estado_operativo': 'La condición',
            'estado': 'El estado',
            'ultimo_mantenimiento': 'La fecha de última modificación',
        }
        for campo, etiqueta in campos_texto.items():
            valor = datos.get(campo)
            if valor is not None and not isinstance(valor, str):
                return None, f'{etiqueta} debe ser texto.'

        tipo = (datos.get('tipo_equipo') or '').strip()
        if tipo in InventarioService.TIPOS_EQUIPO_INVALIDOS:
            return None, 'Debe seleccionar un tipo de equipo.'

        codigo = (datos.get('codigo') or '').strip()
        if not codigo:
            return None, 'Debe indicar el código del equipo.'
        if not any(caracter.isalpha() for caracter in codigo):
            return None, 'El código del equipo debe contener al menos una letra (ej: EMA-005).'
        if not any(caracter.isdigit() and caracter != '0' for caracter in codigo):
            return None, 'El código del equipo debe incluir un número mayor que cero (ej: EMA-005).'

        ubicacion = (datos.get('ubicacion') or '').strip()
        if not ubicacion:
            return None, 'Debe indicar la ubicación del equipo.'
        if not InventarioService._solo_letras_y_espacios(ubicacion):
            return None, 'La ubicación solo puede contener letras y espacios.'

        responsable = (datos.get('responsable') or '').strip()
        if not responsable:
            return None, 'Debe seleccionar un responsable.'

        condicion = (datos.get('estado_operativo') or '').strip()
        if not condicion:
            return None, 'Debe seleccionar una condición.'

        estado = (datos.get('estado') or '').strip()
        if not estado:
            return None, 'Debe seleccionar un estado.'

        ultimo_mantenimiento, error_fecha = InventarioService._parsear_fecha(datos)
        if error_fecha:
            return None, error_fecha
        if ultimo_mantenimiento is None:
            return None, 'Debe indicar la fecha de última modificación.'

        try:
            codigo = normalize_text(codigo, max_length=50, field='El código')
            tipo = normalize_text(tipo, max_length=100, field='El tipo de equipo')
            ubicacion = normalize_text(ubicacion, max_length=100, field='La ubicación')
            condicion = normalize_text(condicion, max_length=30, field='La condición')
            estado = normalize_text(estado, max_length=30, field='El estado')
            responsable = normalize_text(responsable, max_length=120, field='El responsable')
        except ValueError as error:
            return None, str(error)

        return {
            'codigo': codigo,
            'tipo': tipo,
            'ubicacion': ubicacion,
            'condicion': condicion,
            'estado': estado,
            'responsable': responsable,
            'ultimo_mantenimiento': ultimo_mantenimiento,
        }, None

    @staticmethod
    def _parsear_fecha(datos, campo='ultimo_mantenimiento'):
        """Devuelve (fecha, error). Solo uno de los dos será distinto de None."""
        valor = datos.get(campo)
        if valor is not None and not isinstance(valor, str):
            return None, 'La fecha debe ser texto.'
        fecha_str = (valor or '').strip()
        if not fecha_str:
            return None, None
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return None, 'Formato de fecha inválido.'
        if fecha > datetime.utcnow().date():
            return None, 'La fecha no puede ser posterior a hoy.'
        return fecha, None

    @staticmethod
    def crear_equipo(datos, usuario):
        valores, error = InventarioService._validar_datos_equipo(datos)
        if error:
            return {'ok': False, 'error': error}

        codigo = valores['codigo']
        if InventarioEquipo.query.filter_by(codigo_interno=codigo).first():
            return {'ok': False, 'error': 'Ya existe un equipo con ese código.'}

        modelo = InventarioService._obtener_o_crear_modelo(valores['tipo'])
        ubicacion = InventarioService._obtener_o_crear_ubicacion(valores['ubicacion'])

        equipo = InventarioEquipo(
            id_modelos_equipos=modelo.id_modelos_equipo,
            id_ubicacion_actual=ubicacion.id_ubicacion,
            codigo_interno=codigo,
            estado=valores['estado'],
            condicion=valores['condicion'],
            fecha_ingreso=datetime.utcnow().date(),
            ultimo_mantenimiento=valores['ultimo_mantenimiento'],
            responsable=valores['responsable'],
        )
        db.session.add(equipo)
        db.session.flush()

        db.session.add(BitacoraTransaccion(
            modulo='inventario',
            registro_id=equipo.id,
            accion='creacion',
            estado_nuevo=equipo.estado_flujo,
            usuario=usuario.nombre,
            detalle=f'Registro del equipo {equipo.codigo}',
        ))
        db.session.commit()

        mensaje = f"Se registró el equipo {equipo.codigo} en el inventario."
        ServicioNotificacion.notificar_por_permiso(
            'gestionar_inventario', mensaje, emisor_id=usuario.id_usuario
        )
        ServicioNotificacion.crear_aviso(
            id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Inventario'
        )

        return {'ok': True, 'equipo': equipo, 'mensaje': 'Equipo registrado exitosamente en el inventario.'}

    @staticmethod
    def _validar_datos_movimiento(datos):
        """Devuelve (valores, error). Solo uno de los dos es distinto de None."""
        campos_texto = {
            'equipo': 'El equipo',
            'fecha_hora': 'La fecha',
            'ubicacion_origen': 'La ubicación de origen',
            'ubicacion_destino': 'La ubicación de destino',
            'motivo_responsable': 'El motivo',
        }
        for campo, etiqueta in campos_texto.items():
            valor = datos.get(campo)
            if valor is not None and not isinstance(valor, str):
                return None, f'{etiqueta} debe ser texto.'

        codigo_equipo = (datos.get('equipo') or '').strip()
        if not codigo_equipo:
            return None, 'Debe seleccionar un equipo.'
        equipo = InventarioEquipo.query.filter_by(codigo_interno=codigo_equipo).first()
        if not equipo:
            return None, 'El equipo seleccionado no existe en el inventario.'

        fecha_str = (datos.get('fecha_hora') or '').strip()
        if not fecha_str:
            return None, 'Debe indicar la fecha y hora.'
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return None, 'Formato de fecha inválido.'
        if fecha > datetime.utcnow().date():
            return None, 'La fecha no puede ser posterior a hoy.'

        origen = (datos.get('ubicacion_origen') or '').strip()
        if not origen:
            return None, 'Debe indicar la ubicación de origen.'
        if not InventarioService._solo_letras_y_espacios(origen):
            return None, 'La ubicación de origen solo puede contener letras y espacios.'
        destino = (datos.get('ubicacion_destino') or '').strip()
        if not destino:
            return None, 'Debe indicar la ubicación de destino.'
        if not InventarioService._solo_letras_y_espacios(destino):
            return None, 'La ubicación de destino solo puede contener letras y espacios.'
        motivo = (datos.get('motivo_responsable') or '').strip()
        if not motivo:
            return None, 'Debe indicar el motivo y responsable.'
        try:
            origen = normalize_text(origen, max_length=100, field='La ubicación de origen')
            destino = normalize_text(destino, max_length=100, field='La ubicación de destino')
            motivo = normalize_text(motivo, max_length=200, field='El motivo')
        except ValueError as error:
            return None, str(error)

        return {'equipo': equipo, 'fecha': fecha, 'origen': origen, 'destino': destino, 'motivo': motivo}, None

    @staticmethod
    def crear_movimiento(datos, usuario):
        valores, error = InventarioService._validar_datos_movimiento(datos)
        if error:
            return {'ok': False, 'error': error}

        equipo = valores['equipo']
        movimiento = MovimientoEquipo(
            id_equipo=equipo.id,
            fecha_movimiento=valores['fecha'],
            ubicacion_origen=valores['origen'],
            ubicacion_destino=valores['destino'],
            motivo_responsable=valores['motivo'],
        )
        db.session.add(movimiento)

        # La ubicación actual del equipo pasa a ser el destino del traslado
        if valores['destino'] != equipo.ubicacion:
            ubicacion_destino = InventarioService._obtener_o_crear_ubicacion(valores['destino'])
            equipo.id_ubicacion_actual = ubicacion_destino.id_ubicacion

        db.session.flush()

        db.session.add(BitacoraTransaccion(
            modulo='inventario',
            registro_id=movimiento.id_movimiento,
            accion='movimiento',
            estado_nuevo='Transferencia',
            usuario=usuario.nombre,
            detalle=f'{movimiento.codigo} | {equipo.codigo}: {movimiento.ubicacion_origen} -> {movimiento.ubicacion_destino} | {movimiento.motivo_responsable}',
        ))
        db.session.commit()

        mensaje = (
            f"Se registró el movimiento {movimiento.codigo} del equipo {equipo.codigo}: "
            f"{movimiento.ubicacion_origen} -> {movimiento.ubicacion_destino}."
        )
        ServicioNotificacion.notificar_por_permiso(
            'gestionar_inventario', mensaje, emisor_id=usuario.id_usuario
        )
        ServicioNotificacion.crear_aviso(
            id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Inventario'
        )

        return {'ok': True, 'movimiento': movimiento, 'mensaje': 'Movimiento registrado exitosamente.'}

    @staticmethod
    def actualizar_movimiento(movimiento_id, datos, usuario):
        movimiento = MovimientoEquipo.query.get(movimiento_id)
        if not movimiento:
            return {'ok': False, 'error': 'El movimiento no existe.'}

        valores, error = InventarioService._validar_datos_movimiento(datos)
        if error:
            return {'ok': False, 'error': error}

        movimiento.id_equipo = valores['equipo'].id
        movimiento.fecha_movimiento = valores['fecha']
        movimiento.ubicacion_origen = valores['origen']
        movimiento.ubicacion_destino = valores['destino']
        movimiento.motivo_responsable = valores['motivo']

        db.session.add(BitacoraTransaccion(
            modulo='inventario',
            registro_id=movimiento.id_movimiento,
            accion='movimiento_editado',
            estado_nuevo='Transferencia',
            usuario=usuario.nombre,
            detalle=f'Movimiento #{movimiento.id_movimiento:03d} actualizado: {valores["equipo"].codigo} | {valores["origen"]} -> {valores["destino"]}',
        ))
        db.session.commit()

        mensaje = f"Se actualizó el movimiento #{movimiento.id_movimiento:03d} del inventario."
        ServicioNotificacion.notificar_por_permiso(
            'gestionar_inventario', mensaje, emisor_id=usuario.id_usuario
        )
        ServicioNotificacion.crear_aviso(
            id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Inventario'
        )

        return {'ok': True, 'movimiento': movimiento, 'mensaje': 'Movimiento actualizado exitosamente.'}

    @staticmethod
    def eliminar_movimiento(movimiento_id, usuario):
        movimiento = MovimientoEquipo.query.get(movimiento_id)
        if not movimiento:
            return {'ok': False, 'error': 'El movimiento no existe.'}

        detalle = f'{movimiento.codigo} | {movimiento.codigo_equipo}: {movimiento.ubicacion_origen} -> {movimiento.ubicacion_destino}'
        db.session.delete(movimiento)

        db.session.add(BitacoraTransaccion(
            modulo='inventario',
            registro_id=movimiento_id,
            accion='movimiento_eliminado',
            estado_nuevo='Eliminado',
            usuario=usuario.nombre,
            detalle=f'{detalle} eliminado del historial.',
        ))
        db.session.commit()

        mensaje = f"Se eliminó el movimiento {detalle} del inventario."
        ServicioNotificacion.notificar_por_permiso(
            'gestionar_inventario', mensaje, emisor_id=usuario.id_usuario
        )
        ServicioNotificacion.crear_aviso(
            id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Inventario'
        )

        return {'ok': True, 'mensaje': 'Movimiento eliminado del historial.'}

    @staticmethod
    def actualizar_equipo(equipo_id, datos, usuario):
        equipo = InventarioEquipo.query.get_or_404(equipo_id)

        valores, error = InventarioService._validar_datos_equipo(datos)
        if error:
            return {'ok': False, 'error': error}

        codigo = valores['codigo']
        existe = InventarioEquipo.query.filter_by(codigo_interno=codigo).first()
        if existe and existe.id != equipo.id:
            return {'ok': False, 'error': 'Ya existe otro equipo con ese código.'}

        tipo = valores['tipo']
        nombre_ubicacion = valores['ubicacion']

        if tipo != equipo.tipo_equipo:
            modelo = InventarioService._obtener_o_crear_modelo(tipo)
            equipo.id_modelos_equipos = modelo.id_modelos_equipo
        if nombre_ubicacion != equipo.ubicacion:
            ubicacion = InventarioService._obtener_o_crear_ubicacion(nombre_ubicacion)
            equipo.id_ubicacion_actual = ubicacion.id_ubicacion

        equipo.codigo_interno = codigo
        equipo.estado = valores['estado']
        equipo.condicion = valores['condicion']
        equipo.ultimo_mantenimiento = valores['ultimo_mantenimiento']
        equipo.responsable = valores['responsable']

        db.session.add(BitacoraTransaccion(
            modulo='inventario',
            registro_id=equipo.id,
            accion='modificacion',
            estado_nuevo=equipo.estado_flujo,
            usuario=usuario.nombre,
            detalle=f'Datos del equipo {equipo.codigo} actualizados',
        ))
        db.session.commit()

        mensaje = f"Se actualizaron los datos del equipo {equipo.codigo} en el inventario."
        ServicioNotificacion.notificar_por_permiso(
            'gestionar_inventario', mensaje, emisor_id=usuario.id_usuario
        )
        ServicioNotificacion.crear_aviso(
            id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Inventario'
        )

        return {'ok': True, 'equipo': equipo, 'mensaje': 'Equipo actualizado exitosamente.'}

    @staticmethod
    def eliminar_equipo(equipo_id, usuario):
        equipo = InventarioEquipo.query.get_or_404(equipo_id)

        MovimientoEquipo.query.filter_by(id_equipo=equipo.id).delete()

        db.session.add(BitacoraTransaccion(
            modulo='inventario',
            registro_id=equipo.id,
            accion='eliminacion',
            estado_nuevo=equipo.estado_flujo,
            usuario=usuario.nombre,
            detalle=f'Equipo {equipo.codigo} eliminado del inventario',
        ))
        codigo_equipo = equipo.codigo
        db.session.delete(equipo)
        db.session.commit()

        mensaje = f"Se eliminó el equipo {codigo_equipo} del inventario."
        ServicioNotificacion.notificar_por_permiso(
            'gestionar_inventario', mensaje, emisor_id=usuario.id_usuario
        )
        ServicioNotificacion.crear_aviso(
            id_usuario=usuario.id_usuario, mensaje=mensaje, categoria='Inventario'
        )

        return {'ok': True, 'mensaje': 'Equipo eliminado del inventario.'}

    @staticmethod
    def _filtrar_por_ids(items, ids, atributo_id):
        if ids is None:
            return items
        id_list = {int(valor) for valor in ids.split(',') if valor.strip().isdigit()}
        return [item for item in items if getattr(item, atributo_id) in id_list]

    @staticmethod
    def _tabla_frecuencias(titulo, datos, total, estilo_cabecera,
                           estilo_celda_izq, estilo_celda_centro, ancho,
                           color_cabecera='#16a34a', color_fila='#f0fdf4'):
        verde = colors.HexColor(color_cabecera)
        verde_claro = colors.HexColor(color_fila)
        gris_borde = colors.HexColor('#d1d5db')

        filas = [[
            Paragraph(f'<b>{titulo}</b>', estilo_cabecera),
            Paragraph('<b>CANTIDAD</b>', estilo_cabecera),
            Paragraph('<b>PORCENTAJE</b>', estilo_cabecera),
        ]]
        for etiqueta, cantidad in datos:
            porcentaje = (cantidad / total * 100) if total else 0
            filas.append([
                Paragraph(escape(str(etiqueta)), estilo_celda_izq),
                Paragraph(str(cantidad), estilo_celda_centro),
                Paragraph(f'{porcentaje:.1f} %', estilo_celda_centro),
            ])
        if len(filas) == 1:
            filas.append([
                Paragraph('Sin datos', estilo_celda_izq),
                Paragraph('0', estilo_celda_centro),
                Paragraph('0.0 %', estilo_celda_centro),
            ])

        tabla = Table(filas, colWidths=[ancho - 1.7 * inch, 0.85 * inch, 0.85 * inch], repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), verde),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, gris_borde),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, verde_claro]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        return tabla

    @staticmethod
    def _grafico_barras(titulo, datos, ancho=7.0 * inch):
        datos = [(str(etiqueta), int(valor)) for etiqueta, valor in datos] or [('Sin datos', 0)]
        alto = max(1.3 * inch, 0.26 * inch * len(datos) + 0.45 * inch)
        dibujo = Drawing(ancho, alto)

        verde = colors.HexColor('#93EDA3')
        naranja = colors.HexColor('#f59e0b')
        rojo = colors.HexColor('#dc2626')

        valores_unicos = sorted({valor for _, valor in datos}, reverse=True)
        total_unicos = len(valores_unicos)
        colores_por_valor = {}
        for posicion, valor in enumerate(valores_unicos):
            if total_unicos == 1:
                colores_por_valor[valor] = verde
            elif total_unicos == 2:
                colores_por_valor[valor] = verde if posicion == 0 else rojo
            elif posicion < total_unicos / 3:
                colores_por_valor[valor] = verde
            elif posicion >= 2 * total_unicos / 3:
                colores_por_valor[valor] = rojo
            else:
                colores_por_valor[valor] = naranja

        margen_izq = 2.05 * inch
        margen_der = 0.45 * inch
        margen_sup = 0.30 * inch
        margen_inf = 0.06 * inch
        max_valor = max((valor for _, valor in datos), default=0) or 1
        ancho_disponible = ancho - margen_izq - margen_der
        alto_filas = (alto - margen_sup - margen_inf) / len(datos)
        alto_barra = min(0.15 * inch, alto_filas * 0.55)

        dibujo.add(String(
            margen_izq, alto - 0.18 * inch, titulo,
            fontName='Helvetica-Bold', fontSize=9,
            fillColor=colors.HexColor('#15803d'),
        ))

        for indice, (etiqueta, valor) in enumerate(datos):
            y = alto - margen_sup - (indice + 1) * alto_filas + (alto_filas - alto_barra) / 2
            texto = etiqueta if len(etiqueta) <= 34 else etiqueta[:31] + '...'
            dibujo.add(String(
                0, y + 2, texto,
                fontName='Helvetica', fontSize=7,
                fillColor=colors.HexColor('#374151'),
            ))
            ancho_barra = ancho_disponible * valor / max_valor
            if ancho_barra > 0:
                dibujo.add(Rect(
                    margen_izq, y, ancho_barra, alto_barra,
                    fillColor=colores_por_valor[valor],
                    strokeColor=colors.black,
                    strokeWidth=0.5,
                ))
            dibujo.add(String(
                margen_izq + ancho_barra + 4, y + 2, str(valor),
                fontName='Helvetica-Bold', fontSize=7,
                fillColor=colors.HexColor('#111827'),
            ))
        return dibujo

    @staticmethod
    def _grafico_torta(titulo, datos, ancho=7.0 * inch, max_categorias=6):
        datos = [(str(etiqueta), int(valor)) for etiqueta, valor in datos if int(valor) > 0]
        if not datos:
            datos = [('Sin datos', 1)]
        total = sum(valor for _, valor in datos)

        datos = sorted(datos, key=lambda item: item[1], reverse=True)
        if len(datos) > max_categorias:
            principales = datos[:max_categorias - 1]
            otros = sum(valor for _, valor in datos[max_categorias - 1:])
            datos = principales + [('Otros', otros)]

        paleta = ['#93EDA3', '#3b82f6', '#f59e0b', '#8b5cf6',
                  '#ec4899', '#14b8a6', '#f97316', '#9ca3af']

        alto = max(2.4 * inch, 0.24 * inch * len(datos) + 0.65 * inch)
        diametro = min(1.9 * inch, alto - 0.5 * inch)
        dibujo = Drawing(ancho, alto)

        dibujo.add(String(
            0.4 * inch, alto - 0.18 * inch, titulo,
            fontName='Helvetica-Bold', fontSize=9,
            fillColor=colors.HexColor('#15803d'),
        ))

        torta = Pie()
        torta.x = 0.4 * inch
        torta.y = (alto - 0.35 * inch - diametro) / 2
        torta.width = diametro
        torta.height = diametro
        torta.data = [valor for _, valor in datos]
        torta.startAngle = 90
        torta.direction = 'clockwise'
        for indice, (etiqueta, _) in enumerate(datos):
            slice_ = torta.slices[indice]
            slice_.fillColor = colors.HexColor(
                '#9ca3af' if etiqueta == 'Otros' else paleta[indice % len(paleta)])
            slice_.strokeColor = colors.black
            slice_.strokeWidth = 0.5
        dibujo.add(torta)

        leyenda_x = torta.x + diametro + 0.5 * inch
        leyenda_y = alto - 0.55 * inch
        ancho_texto = ancho - leyenda_x - 0.2 * inch
        max_caracteres = max(18, int(ancho_texto / 3.6))
        for indice, (etiqueta, valor) in enumerate(datos):
            color_slice = colors.HexColor(
                '#9ca3af' if etiqueta == 'Otros' else paleta[indice % len(paleta)])
            y = leyenda_y - indice * 0.22 * inch
            dibujo.add(Rect(
                leyenda_x, y + 1, 0.12 * inch, 0.12 * inch,
                fillColor=color_slice, strokeColor=colors.black, strokeWidth=0.5,
            ))
            texto = etiqueta if len(etiqueta) <= max_caracteres else etiqueta[:max_caracteres - 3] + '...'
            porcentaje = (valor / total * 100) if total else 0
            dibujo.add(String(
                leyenda_x + 0.2 * inch, y + 2,
                f'{texto} ({porcentaje:.1f} %)',
                fontName='Helvetica', fontSize=7,
                fillColor=colors.HexColor('#374151'),
            ))
        return dibujo

    @staticmethod
    def generar_reporte_pdf(equipos):
        import io, os

        buf = io.BytesIO()

        def footer_pagina(canvas, doc):
            canvas.saveState()
            margen_x = 0.75 * inch
            ancho_pag = letter[0]
            footer_y = 0.4 * inch
            canvas.setStrokeColor(colors.HexColor('#d1d5db'))
            canvas.setLineWidth(0.3)
            canvas.line(margen_x, footer_y + 0.15 * inch, ancho_pag - margen_x, footer_y + 0.15 * inch)
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.HexColor('#9ca3af'))
            canvas.drawString(margen_x, footer_y - 2, 'Código: REG-INV-042 | Versión 2.1')
            canvas.drawRightString(ancho_pag - margen_x, footer_y - 2, f'Página {doc.page}')
            canvas.restoreState()

        doc = SimpleDocTemplate(buf, pagesize=letter,
                                title='Reporte de Inventario',
                                topMargin=0.7 * inch, bottomMargin=0.65 * inch,
                                leftMargin=0.75 * inch, rightMargin=0.75 * inch)
        doc.onFirstPage = footer_pagina
        doc.onLaterPages = footer_pagina
        styles = getSampleStyleSheet()
        ancho = letter[0] - 1.5 * inch

        estilo_titulo = ParagraphStyle('TituloActa', parent=styles['Title'],
                                       fontSize=18, leading=22, textColor=colors.HexColor('#15803d'),
                                       spaceAfter=2, alignment=1)
        estilo_linea_titulo = ParagraphStyle('LineaTit', parent=styles['Normal'],
                                             fontSize=6, textColor=colors.HexColor('#16a34a'), alignment=1)
        estilo_info_label = ParagraphStyle('InfoLabel', parent=styles['Normal'],
                                           fontSize=8, leading=10, textColor=colors.HexColor('#4b5563'))
        estilo_info_valor = ParagraphStyle('InfoValor', parent=styles['Normal'],
                                           fontSize=9, leading=11, textColor=colors.HexColor('#111827'))
        estilo_tabla_titulo = ParagraphStyle('TabTit', parent=styles['Normal'],
                                             fontSize=7, leading=9, textColor=colors.white, alignment=1)
        estilo_tabla_celda = ParagraphStyle('TabCel', parent=styles['Normal'],
                                            fontSize=7, leading=9, alignment=1)

        verde = colors.HexColor('#16a34a')
        verde_claro = colors.HexColor('#f0fdf4')
        gris_borde = colors.HexColor('#d1d5db')

        elementos = []
        logo_path = os.path.join(current_app.root_path, 'static', 'img', 'oncc_logo.png')
        logo_celda = []
        if os.path.exists(logo_path):
            img = Image(logo_path, width=1.3 * inch, height=0.5 * inch)
            logo_celda.append(img)
        logo_celda.append(Spacer(1, 6))
        logo_celda.append(Paragraph("<b>ONCC</b> - Región Nororiental",
                         ParagraphStyle('LogoTxt', parent=styles['Normal'], fontSize=7, textColor=colors.grey)))

        titulo_celda = [
            Paragraph("REPORTE DE INVENTARIO DE EQUIPOS", estilo_titulo),
            Paragraph("──────────────────────────────────────", estilo_linea_titulo),
        ]

        tbl_enc = Table([[logo_celda, titulo_celda]], colWidths=[2.0 * inch, ancho - 2.0 * inch])
        tbl_enc.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tbl_enc)
        elementos.append(Spacer(1, 0.25 * inch))

        fecha_reporte = date.today().strftime('%d de %B, %Y')
        meses_es = {'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
                    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
                    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'}
        for eng, esp in meses_es.items():
            fecha_reporte = fecha_reporte.replace(eng, esp)

        def info_fila(label, valor, label2, valor2):
            return [
                Paragraph(f'<font size=8 color="#4b5563"><b>{label}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor}</font>', estilo_info_valor),
                Paragraph(f'<font size=8 color="#4b5563"><b>{label2}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor2}</font>', estilo_info_valor),
            ]

        datos_reporte = [
            info_fila('Total Equipos', str(len(equipos)), 'Fecha Emisión', fecha_reporte),
            info_fila('Departamento', 'Tecnología e Información', 'Tipo Reporte', 'Inventario General'),
        ]
        t_datos = Table(datos_reporte, colWidths=[1.2 * inch, 2.0 * inch, 1.2 * inch, 2.0 * inch])
        t_datos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), verde_claro),
            ('BOX', (0, 0), (-1, -1), 0.5, gris_borde),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, gris_borde),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_datos)
        elementos.append(Spacer(1, 0.25 * inch))

        detalle_data = [
            [Paragraph('<b>ID EQUIPO</b>', estilo_tabla_titulo),
             Paragraph('<b>NOMBRE DEL EQUIPO</b>', estilo_tabla_titulo),
             Paragraph('<b>UBICACIÓN</b>', estilo_tabla_titulo),
             Paragraph('<b>RESPONSABLE</b>', estilo_tabla_titulo),
             Paragraph('<b>ÚLT. MODIFICACIÓN</b>', estilo_tabla_titulo),
             Paragraph('<b>CONDICIÓN</b>', estilo_tabla_titulo),
             Paragraph('<b>ESTADO</b>', estilo_tabla_titulo)],
        ]
        for e in equipos:
            detalle_data.append([
                Paragraph(e.codigo, estilo_tabla_celda),
                Paragraph(e.tipo_equipo, estilo_tabla_celda),
                Paragraph(e.ubicacion, estilo_tabla_celda),
                Paragraph(e.responsable, estilo_tabla_celda),
                Paragraph(e.ultimo_mantenimiento.strftime('%d/%m/%Y') if e.ultimo_mantenimiento else 'N/D', estilo_tabla_celda),
                Paragraph(e.estado_operativo, estilo_tabla_celda),
                Paragraph(e.estado_flujo, estilo_tabla_celda),
            ])

        cols_tabla = [0.75 * inch, 1.15 * inch, 1.0 * inch, 1.0 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch]
        t_det = Table(detalle_data, colWidths=cols_tabla, repeatRows=1)
        t_det.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), verde),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, gris_borde),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, verde_claro]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elementos.append(Paragraph('<b>DETALLE DE EQUIPOS</b>', estilo_info_label))
        elementos.append(Spacer(1, 4))
        elementos.append(t_det)

        doc.build(elementos)
        buf.seek(0)
        return buf

    @staticmethod
    def generar_acta_pdf(equipo_id):
        equipo = InventarioEquipo.query.get_or_404(equipo_id)
        import io, os

        buf = io.BytesIO()

        def footer_pagina(canvas, doc):
            canvas.saveState()
            margen_x = 0.75 * inch
            ancho_pag = letter[0]
            footer_y = 0.4 * inch
            canvas.setStrokeColor(colors.HexColor('#d1d5db'))
            canvas.setLineWidth(0.3)
            canvas.line(margen_x, footer_y + 0.15 * inch, ancho_pag - margen_x, footer_y + 0.15 * inch)
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.HexColor('#9ca3af'))
            canvas.drawString(margen_x, footer_y - 2, 'Código: REG-INV-042 | Versión 2.1')
            canvas.drawRightString(ancho_pag - margen_x, footer_y - 2, f'Página {doc.page}')
            canvas.restoreState()

        doc = SimpleDocTemplate(buf, pagesize=letter,
                                title='Acta de Responsabilidad',
                                topMargin=0.7 * inch, bottomMargin=0.65 * inch,
                                leftMargin=0.75 * inch, rightMargin=0.75 * inch)
        doc.onFirstPage = footer_pagina
        doc.onLaterPages = footer_pagina
        styles = getSampleStyleSheet()
        ancho = letter[0] - 1.5 * inch

        estilo_titulo = ParagraphStyle('TituloActa', parent=styles['Title'],
                                       fontSize=18, leading=22, textColor=colors.HexColor('#15803d'),
                                       spaceAfter=2, alignment=1)
        estilo_subtitulo = ParagraphStyle('SubActa', parent=styles['Normal'],
                                          fontSize=10, leading=13, textColor=colors.HexColor('#6b7280'),
                                          alignment=1, spaceAfter=4)
        estilo_linea_titulo = ParagraphStyle('LineaTit', parent=styles['Normal'],
                                             fontSize=6, textColor=colors.HexColor('#16a34a'), alignment=1)
        estilo_info_label = ParagraphStyle('InfoLabel', parent=styles['Normal'],
                                           fontSize=8, leading=10, textColor=colors.HexColor('#4b5563'))
        estilo_info_valor = ParagraphStyle('InfoValor', parent=styles['Normal'],
                                           fontSize=9, leading=11, textColor=colors.HexColor('#111827'))
        estilo_cuerpo = ParagraphStyle('CuerpoActa', parent=styles['Normal'],
                                       fontSize=9, leading=13, textColor=colors.HexColor('#374151'),
                                       alignment=4)
        estilo_tabla_titulo = ParagraphStyle('TabTit', parent=styles['Normal'],
                                             fontSize=8, leading=10, textColor=colors.white, alignment=1)
        estilo_tabla_celda = ParagraphStyle('TabCel', parent=styles['Normal'],
                                            fontSize=8, leading=10, alignment=1)
        estilo_termino = ParagraphStyle('TermActa', parent=styles['Normal'],
                                        fontSize=8.5, leading=12, leftIndent=14, textColor=colors.HexColor('#374151'))
        estilo_firma_nombre = ParagraphStyle('FirmaNom', parent=styles['Normal'],
                                             fontSize=10, leading=13, alignment=1)
        estilo_firma_cargo = ParagraphStyle('FirmaCar', parent=styles['Normal'],
                                            fontSize=8.5, leading=11, textColor=colors.HexColor('#6b7280'), alignment=1)

        verde = colors.HexColor('#16a34a')
        verde_claro = colors.HexColor('#f0fdf4')
        gris_borde = colors.HexColor('#d1d5db')

        elementos = []

        logo_path = os.path.join(current_app.root_path, 'static', 'img', 'oncc_logo.png')
        logo_celda = []
        if os.path.exists(logo_path):
            img = Image(logo_path, width=1.3 * inch, height=0.5 * inch)
            logo_celda.append(img)
        logo_celda.append(Spacer(1, 6))
        logo_celda.append(Paragraph("<b>ONCC</b> - Región Nororiental",
                         ParagraphStyle('LogoTxt', parent=styles['Normal'], fontSize=7, textColor=colors.grey)))

        titulo_celda = [
            Paragraph("ACTA DE ASIGNACIÓN Y RESPONSABILIDAD", estilo_titulo),
            Paragraph("Gestión de Inventario de Equipos", estilo_subtitulo),
            Paragraph("──────────────────────────────────────", estilo_linea_titulo),
        ]

        tbl_enc = Table([[logo_celda, titulo_celda]], colWidths=[2.0 * inch, ancho - 2.0 * inch])
        tbl_enc.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tbl_enc)
        elementos.append(Spacer(1, 0.25 * inch))

        codigo_acta = f"ACT-{datetime.now().year}-{equipo.id:05d}"
        fecha_acta = datetime.now().strftime('%d de %B, %Y')
        meses_es = {'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
                    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
                    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'}
        for eng, esp in meses_es.items():
            fecha_acta = fecha_acta.replace(eng, esp)

        def info_fila(label, valor, label2, valor2):
            return [
                Paragraph(f'<font size=8 color="#4b5563"><b>{label}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor}</font>', estilo_info_valor),
                Paragraph(f'<font size=8 color="#4b5563"><b>{label2}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor2}</font>', estilo_info_valor),
            ]

        datos_acta = [
            info_fila('Código Acta', codigo_acta, 'Fecha Emisión', fecha_acta),
            info_fila('Responsable', equipo.responsable, 'Departamento', 'Tecnología e Información'),
            info_fila('Documento ID', '—', 'Ubicación', equipo.ubicacion),
        ]
        t_datos = Table(datos_acta, colWidths=[1.2 * inch, 2.0 * inch, 1.2 * inch, 2.0 * inch])
        t_datos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), verde_claro),
            ('BOX', (0, 0), (-1, -1), 0.5, gris_borde),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, gris_borde),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_datos)
        elementos.append(Spacer(1, 0.25 * inch))

        elementos.append(Paragraph(
            "Por medio del presente documento, se hace entrega formal del/los equipo(s) de trabajo que "
            "se detallan a continuación. El trabajador/colaborador mencionado declara "
            "recibir el equipo en óptimas condiciones de funcionamiento y uso, obligándose a utilizarlos "
            "exclusivamente para el desempeño de sus funciones laborales.",
            estilo_cuerpo))
        elementos.append(Spacer(1, 0.25 * inch))

        detalle_data = [
            [Paragraph('<b>ID EQUIPO</b>', estilo_tabla_titulo),
             Paragraph('<b>NOMBRE DEL EQUIPO</b>', estilo_tabla_titulo),
             Paragraph('<b>UBICACIÓN ACTUAL</b>', estilo_tabla_titulo),
             Paragraph('<b>RESPONSABLE</b>', estilo_tabla_titulo),
             Paragraph('<b>ÚLT. MODIFICACIÓN</b>', estilo_tabla_titulo),
             Paragraph('<b>CONDICIÓN</b>', estilo_tabla_titulo),
             Paragraph('<b>ESTADO</b>', estilo_tabla_titulo)],
            [Paragraph(equipo.codigo, estilo_tabla_celda),
             Paragraph(equipo.tipo_equipo, estilo_tabla_celda),
             Paragraph(equipo.ubicacion, estilo_tabla_celda),
             Paragraph(equipo.responsable, estilo_tabla_celda),
             Paragraph(equipo.ultimo_mantenimiento.strftime('%d/%m/%Y') if equipo.ultimo_mantenimiento else 'N/D', estilo_tabla_celda),
             Paragraph(equipo.estado_operativo, estilo_tabla_celda),
             Paragraph(equipo.estado_flujo, estilo_tabla_celda)],
        ]
        cols_tabla = [0.85 * inch, 1.2 * inch, 1.05 * inch, 1.05 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch]
        t_det = Table(detalle_data, colWidths=cols_tabla)
        t_det.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), verde),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, gris_borde),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, verde_claro]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(Paragraph('<b>DETALLE DEL EQUIPO(S)</b>', estilo_info_label))
        elementos.append(Spacer(1, 4))
        elementos.append(t_det)
        elementos.append(Spacer(1, 0.25 * inch))

        elementos.append(Paragraph('<b>TÉRMINOS Y OBLIGACIONES DEL RESPONSABLE</b>', estilo_info_label))
        elementos.append(Spacer(1, 6))

        terminos = [
            "1. <b>Custodia y Cuidado:</b> El empleado se compromete a velar por la seguridad, conservación y correcto uso de los equipos asignados, evitando pérdidas, deterioros por negligencia o configuraciones de software no autorizadas.",
            "2. <b>Uso Profesional:</b> Los activos asignados son herramientas exclusivas para el cumplimiento de las responsabilidades asignadas por la organización, quedando prohibido su uso para fines personales o comerciales ajenos a la empresa.",
            "3. <b>Reporte de Incidencias:</b> Cualquier falla técnica, daño físico, pérdida, hurto o robo del material debe ser reportado inmediatamente (en un lapso no mayor a 24 horas) al Departamento de TI o Inventario. En caso de robo, se debe adjuntar la denuncia policial respectiva.",
            "4. <b>Devolución de Activos:</b> Al término de la relación laboral o cuando la organización lo requiera, el trabajador se obliga a restituir la totalidad de los bienes descritos en este documento en las mismas condiciones en que los recibió, salvo el desgaste natural por uso legítimo.",
            "5. <b>Sanciones:</b> El incumplimiento de estas normas o el daño por uso negligente comprobado podrá facultar a la empresa a realizar los cobros respectivos de reparación o reposición, según la legislación laboral vigente.",
        ]
        for t in terminos:
            elementos.append(Paragraph(t, estilo_termino))
            elementos.append(Spacer(1, 3))

        elementos.append(Spacer(1, 0.4 * inch))
        elementos.append(HRFlowable(width="100%", thickness=0.5, color=gris_borde))
        elementos.append(Spacer(1, 0.25 * inch))

        firma_data = [
            [Paragraph('<b>Recibí Conforme (Trabajador)</b>', estilo_firma_cargo)],
            [Spacer(1, 0.5 * inch)],
            [Paragraph('_________________________', estilo_firma_nombre)],
            [Paragraph(f'<b>{equipo.responsable}</b>', estilo_firma_nombre)],
        ]
        t_firmas = Table(firma_data, colWidths=[ancho])
        t_firmas.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elementos.append(t_firmas)
        elementos.append(Spacer(1, 0.3 * inch))

        doc.build(elementos)
        buf.seek(0)
        return buf

    @staticmethod
    def generar_reporte_movimientos_pdf(ids=None):
        import io, os

        buf = io.BytesIO()

        def footer_pagina(canvas, doc):
            canvas.saveState()
            margen_x = 0.75 * inch
            ancho_pag = letter[0]
            footer_y = 0.4 * inch
            canvas.setStrokeColor(colors.HexColor('#d1d5db'))
            canvas.setLineWidth(0.3)
            canvas.line(margen_x, footer_y + 0.15 * inch, ancho_pag - margen_x, footer_y + 0.15 * inch)
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.HexColor('#9ca3af'))
            canvas.drawString(margen_x, footer_y - 2, 'Código: REG-INV-042 | Versión 2.1')
            canvas.drawRightString(ancho_pag - margen_x, footer_y - 2, f'Página {doc.page}')
            canvas.restoreState()

        doc = SimpleDocTemplate(buf, pagesize=letter,
                                title='Reporte de Movimientos',
                                topMargin=0.7 * inch, bottomMargin=0.65 * inch,
                                leftMargin=0.75 * inch, rightMargin=0.75 * inch)
        doc.onFirstPage = footer_pagina
        doc.onLaterPages = footer_pagina
        styles = getSampleStyleSheet()
        ancho = letter[0] - 1.5 * inch

        estilo_titulo = ParagraphStyle('TituloActa', parent=styles['Title'],
                                       fontSize=18, leading=22, textColor=colors.HexColor('#15803d'),
                                       spaceAfter=2, alignment=1)
        estilo_linea_titulo = ParagraphStyle('LineaTit', parent=styles['Normal'],
                                             fontSize=6, textColor=colors.HexColor('#16a34a'), alignment=1)
        estilo_info_label = ParagraphStyle('InfoLabel', parent=styles['Normal'],
                                           fontSize=8, leading=10, textColor=colors.HexColor('#4b5563'))
        estilo_info_valor = ParagraphStyle('InfoValor', parent=styles['Normal'],
                                           fontSize=9, leading=11, textColor=colors.HexColor('#111827'))
        estilo_tabla_titulo = ParagraphStyle('TabTit', parent=styles['Normal'],
                                             fontSize=7, leading=9, textColor=colors.white, alignment=1)
        estilo_tabla_celda = ParagraphStyle('TabCel', parent=styles['Normal'],
                                            fontSize=7, leading=9, alignment=1)

        verde = colors.HexColor('#16a34a')
        verde_claro = colors.HexColor('#f0fdf4')
        gris_borde = colors.HexColor('#d1d5db')

        elementos = []
        logo_path = os.path.join(current_app.root_path, 'static', 'img', 'oncc_logo.png')
        logo_celda = []
        if os.path.exists(logo_path):
            img = Image(logo_path, width=1.3 * inch, height=0.5 * inch)
            logo_celda.append(img)
        logo_celda.append(Spacer(1, 6))
        logo_celda.append(Paragraph("<b>ONCC</b> - Región Nororiental",
                         ParagraphStyle('LogoTxt', parent=styles['Normal'], fontSize=7, textColor=colors.grey)))

        titulo_celda = [
            Paragraph("REPORTE DE HISTORIAL DE MOVIMIENTOS", estilo_titulo),
            Paragraph("──────────────────────────────────────", estilo_linea_titulo),
        ]

        tbl_enc = Table([[logo_celda, titulo_celda]], colWidths=[2.0 * inch, ancho - 2.0 * inch])
        tbl_enc.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tbl_enc)
        elementos.append(Spacer(1, 0.25 * inch))

        fecha_reporte = date.today().strftime('%d de %B, %Y')
        meses_es = {'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
                    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
                    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'}
        for eng, esp in meses_es.items():
            fecha_reporte = fecha_reporte.replace(eng, esp)

        def info_fila(label, valor, label2, valor2):
            return [
                Paragraph(f'<font size=8 color="#4b5563"><b>{label}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor}</font>', estilo_info_valor),
                Paragraph(f'<font size=8 color="#4b5563"><b>{label2}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor2}</font>', estilo_info_valor),
            ]

        movimientos_db = InventarioService.listar_movimientos()

        if ids:
            id_list = [int(x) for x in ids.split(',') if x.strip().isdigit()]
            if id_list:
                movimientos_db = [m for m in movimientos_db if m.id_movimiento in id_list]

        movimientos = [
            [m.codigo, m.codigo_equipo, m.fecha_movimiento.strftime('%Y-%m-%d'),
             m.ubicacion_origen, m.ubicacion_destino, m.motivo_responsable]
            for m in movimientos_db
        ]

        datos_reporte = [
            info_fila('Total Movimientos', str(len(movimientos)), 'Fecha Emisión', fecha_reporte),
            info_fila('Departamento', 'Tecnología e Información', 'Tipo Reporte', 'Historial de Movimientos'),
        ]
        t_datos = Table(datos_reporte, colWidths=[1.2 * inch, 2.0 * inch, 1.2 * inch, 2.0 * inch])
        t_datos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), verde_claro),
            ('BOX', (0, 0), (-1, -1), 0.5, gris_borde),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, gris_borde),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_datos)
        elementos.append(Spacer(1, 0.25 * inch))

        detalle_data = [
            [Paragraph('<b>MOVIMIENTO ID</b>', estilo_tabla_titulo),
             Paragraph('<b>EQUIPO</b>', estilo_tabla_titulo),
             Paragraph('<b>FECHA</b>', estilo_tabla_titulo),
             Paragraph('<b>UBICACIÓN ORIGEN</b>', estilo_tabla_titulo),
             Paragraph('<b>UBICACIÓN DESTINO</b>', estilo_tabla_titulo),
             Paragraph('<b>MOTIVO / RESPONSABLE</b>', estilo_tabla_titulo)],
        ]
        for m in movimientos:
            detalle_data.append([Paragraph(c, estilo_tabla_celda) for c in m])

        cols_tabla = [0.85 * inch, 0.75 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.4 * inch]
        t_det = Table(detalle_data, colWidths=cols_tabla, repeatRows=1)
        t_det.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), verde),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, gris_borde),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, verde_claro]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elementos.append(Paragraph('<b>DETALLE DE MOVIMIENTOS</b>', estilo_info_label))
        elementos.append(Spacer(1, 4))
        elementos.append(t_det)

        doc.build(elementos)
        buf.seek(0)
        return buf

    @staticmethod
    def generar_estadistica_equipos_pdf(ids=None):
        import io, os

        buf = io.BytesIO()

        def footer_pagina(canvas, doc):
            canvas.saveState()
            margen_x = 0.75 * inch
            ancho_pag = letter[0]
            footer_y = 0.4 * inch
            canvas.setStrokeColor(colors.HexColor('#d1d5db'))
            canvas.setLineWidth(0.3)
            canvas.line(margen_x, footer_y + 0.15 * inch, ancho_pag - margen_x, footer_y + 0.15 * inch)
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.HexColor('#9ca3af'))
            canvas.drawString(margen_x, footer_y - 2, 'Código: REG-INV-042 | Versión 2.1')
            canvas.drawRightString(ancho_pag - margen_x, footer_y - 2, f'Página {doc.page}')
            canvas.restoreState()

        doc = SimpleDocTemplate(buf, pagesize=letter,
                                title='Reporte Estadístico de Equipos',
                                topMargin=0.7 * inch, bottomMargin=0.65 * inch,
                                leftMargin=0.75 * inch, rightMargin=0.75 * inch)
        doc.onFirstPage = footer_pagina
        doc.onLaterPages = footer_pagina
        styles = getSampleStyleSheet()
        ancho = letter[0] - 1.5 * inch

        estilo_titulo = ParagraphStyle('TituloEst', parent=styles['Title'],
                                       fontSize=17, leading=21, textColor=colors.HexColor('#15803d'),
                                       spaceAfter=2, alignment=1)
        estilo_linea_titulo = ParagraphStyle('LineaTit', parent=styles['Normal'],
                                             fontSize=6, textColor=colors.HexColor('#16a34a'), alignment=1)
        estilo_info_label = ParagraphStyle('InfoLabel', parent=styles['Normal'],
                                           fontSize=8, leading=10, textColor=colors.HexColor('#4b5563'))
        estilo_info_valor = ParagraphStyle('InfoValor', parent=styles['Normal'],
                                           fontSize=9, leading=11, textColor=colors.HexColor('#111827'))
        estilo_tabla_titulo = ParagraphStyle('TabTit', parent=styles['Normal'],
                                             fontSize=7, leading=9, textColor=colors.white, alignment=1)
        estilo_tabla_celda = ParagraphStyle('TabCel', parent=styles['Normal'],
                                            fontSize=7, leading=9, alignment=1)
        estilo_tabla_celda_izq = ParagraphStyle('TabCelIzq', parent=styles['Normal'],
                                                fontSize=7, leading=9, alignment=0)

        verde_claro = colors.HexColor('#f0fdf4')
        gris_borde = colors.HexColor('#d1d5db')

        equipos = InventarioService._filtrar_por_ids(InventarioService.listar_equipos(), ids, 'id')
        total = len(equipos)
        por_tipo = Counter(e.tipo_equipo or 'Sin dato' for e in equipos).most_common()
        por_condicion = Counter(e.estado_operativo or 'Sin dato' for e in equipos).most_common()
        por_estado = Counter(e.estado_flujo or 'Sin dato' for e in equipos).most_common()
        por_ubicacion = Counter(e.ubicacion or 'Sin dato' for e in equipos).most_common()
        por_responsable = Counter(e.responsable or 'Sin dato' for e in equipos).most_common()

        elementos = []
        logo_path = os.path.join(current_app.root_path, 'static', 'img', 'oncc_logo.png')
        logo_celda = []
        if os.path.exists(logo_path):
            img = Image(logo_path, width=1.3 * inch, height=0.5 * inch)
            logo_celda.append(img)
        logo_celda.append(Spacer(1, 6))
        logo_celda.append(Paragraph("<b>ONCC</b> - Región Nororiental",
                         ParagraphStyle('LogoTxt', parent=styles['Normal'], fontSize=7, textColor=colors.grey)))

        titulo_celda = [
            Paragraph("REPORTE ESTADÍSTICO DE EQUIPOS", estilo_titulo),
            Paragraph("──────────────────────────────────────", estilo_linea_titulo),
        ]

        tbl_enc = Table([[logo_celda, titulo_celda]], colWidths=[2.0 * inch, ancho - 2.0 * inch])
        tbl_enc.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tbl_enc)
        elementos.append(Spacer(1, 0.2 * inch))

        fecha_reporte = date.today().strftime('%d de %B, %Y')
        meses_es = {'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
                    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
                    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'}
        for eng, esp in meses_es.items():
            fecha_reporte = fecha_reporte.replace(eng, esp)

        def info_fila(label, valor, label2, valor2):
            return [
                Paragraph(f'<font size=8 color="#4b5563"><b>{label}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor}</font>', estilo_info_valor),
                Paragraph(f'<font size=8 color="#4b5563"><b>{label2}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor2}</font>', estilo_info_valor),
            ]

        operativos = sum(1 for e in equipos if (e.estado_operativo or '').lower() == 'operativo')
        en_mantenimiento = sum(1 for e in equipos if 'mantenimiento' in (e.estado_operativo or '').lower())
        datos_reporte = [
            info_fila('Total Equipos', str(total), 'Fecha Emisión', fecha_reporte),
            info_fila('Ubicaciones', str(len(por_ubicacion)), 'Responsables', str(len(por_responsable))),
            info_fila('Operativos', str(operativos), 'Requieren Mantenimiento', str(en_mantenimiento)),
        ]
        t_datos = Table(datos_reporte, colWidths=[1.2 * inch, 2.0 * inch, 1.5 * inch, 1.8 * inch])
        t_datos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), verde_claro),
            ('BOX', (0, 0), (-1, -1), 0.5, gris_borde),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, gris_borde),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_datos)
        elementos.append(Spacer(1, 0.2 * inch))

        def seccion(titulo_tabla, datos, titulo_grafico, max_grafico=10, tipo_grafico='barras'):
            elementos.append(InventarioService._tabla_frecuencias(
                titulo_tabla, datos, total, estilo_tabla_titulo,
                estilo_tabla_celda_izq, estilo_tabla_celda, ancho))
            elementos.append(Spacer(1, 6))
            if tipo_grafico == 'torta':
                grafico = InventarioService._grafico_torta(
                    titulo_grafico, datos, ancho=ancho)
            else:
                grafico = InventarioService._grafico_barras(
                    titulo_grafico, datos[:max_grafico], ancho=ancho)
            elementos.append(grafico)
            elementos.append(Spacer(1, 0.12 * inch))

        seccion('TIPO DE EQUIPO', por_tipo, 'Equipos por tipo', tipo_grafico='torta')
        seccion('CONDICIÓN', por_condicion, 'Equipos por condición', tipo_grafico='torta')
        seccion('ESTADO', por_estado, 'Equipos por estado', tipo_grafico='torta')
        seccion('UBICACIÓN (TOP 10)', por_ubicacion[:10], 'Equipos por ubicación (top 10)')
        seccion('RESPONSABLE (TOP 10)', por_responsable[:10], 'Equipos por responsable (top 10)')

        doc.build(elementos)
        buf.seek(0)
        return buf

    @staticmethod
    def generar_estadistica_movimientos_pdf(ids=None):
        import io, os

        buf = io.BytesIO()

        def footer_pagina(canvas, doc):
            canvas.saveState()
            margen_x = 0.75 * inch
            ancho_pag = letter[0]
            footer_y = 0.4 * inch
            canvas.setStrokeColor(colors.HexColor('#d1d5db'))
            canvas.setLineWidth(0.3)
            canvas.line(margen_x, footer_y + 0.15 * inch, ancho_pag - margen_x, footer_y + 0.15 * inch)
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.HexColor('#9ca3af'))
            canvas.drawString(margen_x, footer_y - 2, 'Código: REG-INV-042 | Versión 2.1')
            canvas.drawRightString(ancho_pag - margen_x, footer_y - 2, f'Página {doc.page}')
            canvas.restoreState()

        doc = SimpleDocTemplate(buf, pagesize=letter,
                                title='Reporte Estadístico de Movimientos',
                                topMargin=0.7 * inch, bottomMargin=0.65 * inch,
                                leftMargin=0.75 * inch, rightMargin=0.75 * inch)
        doc.onFirstPage = footer_pagina
        doc.onLaterPages = footer_pagina
        styles = getSampleStyleSheet()
        ancho = letter[0] - 1.5 * inch

        estilo_titulo = ParagraphStyle('TituloEst', parent=styles['Title'],
                                       fontSize=17, leading=21, textColor=colors.HexColor('#15803d'),
                                       spaceAfter=2, alignment=1)
        estilo_linea_titulo = ParagraphStyle('LineaTit', parent=styles['Normal'],
                                             fontSize=6, textColor=colors.HexColor('#16a34a'), alignment=1)
        estilo_info_label = ParagraphStyle('InfoLabel', parent=styles['Normal'],
                                           fontSize=8, leading=10, textColor=colors.HexColor('#4b5563'))
        estilo_info_valor = ParagraphStyle('InfoValor', parent=styles['Normal'],
                                           fontSize=9, leading=11, textColor=colors.HexColor('#111827'))
        estilo_tabla_titulo = ParagraphStyle('TabTit', parent=styles['Normal'],
                                             fontSize=7, leading=9, textColor=colors.white, alignment=1)
        estilo_tabla_celda = ParagraphStyle('TabCel', parent=styles['Normal'],
                                            fontSize=7, leading=9, alignment=1)
        estilo_tabla_celda_izq = ParagraphStyle('TabCelIzq', parent=styles['Normal'],
                                                fontSize=7, leading=9, alignment=0)

        verde_claro = colors.HexColor('#f0fdf4')
        gris_borde = colors.HexColor('#d1d5db')

        movimientos = InventarioService._filtrar_por_ids(
            InventarioService.listar_movimientos(), ids, 'id_movimiento')
        total = len(movimientos)

        nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                         'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        conteo_meses = Counter((m.fecha_movimiento.year, m.fecha_movimiento.month) for m in movimientos)
        por_mes = [
            (f'{nombres_meses[mes - 1]} {anio}', cantidad)
            for (anio, mes), cantidad in sorted(conteo_meses.items())
        ]
        por_destino = Counter(m.ubicacion_destino or 'Sin dato' for m in movimientos).most_common()
        por_equipo = Counter(m.codigo_equipo or 'Sin dato' for m in movimientos).most_common()

        equipos_involucrados = len({m.codigo_equipo for m in movimientos if m.codigo_equipo})
        destinos_distintos = len({m.ubicacion_destino for m in movimientos if m.ubicacion_destino})
        if movimientos:
            fechas = [m.fecha_movimiento for m in movimientos]
            rango_fechas = f"{min(fechas).strftime('%d/%m/%Y')} - {max(fechas).strftime('%d/%m/%Y')}"
        else:
            rango_fechas = 'Sin datos'

        elementos = []
        logo_path = os.path.join(current_app.root_path, 'static', 'img', 'oncc_logo.png')
        logo_celda = []
        if os.path.exists(logo_path):
            img = Image(logo_path, width=1.3 * inch, height=0.5 * inch)
            logo_celda.append(img)
        logo_celda.append(Spacer(1, 6))
        logo_celda.append(Paragraph("<b>ONCC</b> - Región Nororiental",
                         ParagraphStyle('LogoTxt', parent=styles['Normal'], fontSize=7, textColor=colors.grey)))

        titulo_celda = [
            Paragraph("REPORTE ESTADÍSTICO DE MOVIMIENTOS", estilo_titulo),
            Paragraph("──────────────────────────────────────", estilo_linea_titulo),
        ]

        tbl_enc = Table([[logo_celda, titulo_celda]], colWidths=[2.0 * inch, ancho - 2.0 * inch])
        tbl_enc.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tbl_enc)
        elementos.append(Spacer(1, 0.2 * inch))

        fecha_reporte = date.today().strftime('%d de %B, %Y')
        meses_es = {'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
                    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
                    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'}
        for eng, esp in meses_es.items():
            fecha_reporte = fecha_reporte.replace(eng, esp)

        def info_fila(label, valor, label2, valor2):
            return [
                Paragraph(f'<font size=8 color="#4b5563"><b>{label}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor}</font>', estilo_info_valor),
                Paragraph(f'<font size=8 color="#4b5563"><b>{label2}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor2}</font>', estilo_info_valor),
            ]

        datos_reporte = [
            info_fila('Total Movimientos', str(total), 'Fecha Emisión', fecha_reporte),
            info_fila('Equipos Involucrados', str(equipos_involucrados), 'Destinos Distintos', str(destinos_distintos)),
            info_fila('Rango de Fechas', rango_fechas, 'Tipo Reporte', 'Estadística de Movimientos'),
        ]
        t_datos = Table(datos_reporte, colWidths=[1.2 * inch, 2.0 * inch, 1.5 * inch, 1.8 * inch])
        t_datos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), verde_claro),
            ('BOX', (0, 0), (-1, -1), 0.5, gris_borde),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, gris_borde),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_datos)
        elementos.append(Spacer(1, 0.2 * inch))

        def seccion(titulo_tabla, datos, titulo_grafico, max_grafico=10,
                    desde_final=False, tipo_grafico='barras'):
            elementos.append(InventarioService._tabla_frecuencias(
                titulo_tabla, datos, total, estilo_tabla_titulo,
                estilo_tabla_celda_izq, estilo_tabla_celda, ancho))
            elementos.append(Spacer(1, 6))
            if tipo_grafico == 'torta':
                grafico = InventarioService._grafico_torta(
                    titulo_grafico, datos, ancho=ancho)
            else:
                datos_grafico = datos[-max_grafico:] if desde_final else datos[:max_grafico]
                grafico = InventarioService._grafico_barras(
                    titulo_grafico, datos_grafico, ancho=ancho)
            elementos.append(grafico)
            elementos.append(Spacer(1, 0.12 * inch))

        titulo_mes = ('Movimientos por mes (últimos 12)' if len(por_mes) > 12
                      else 'Movimientos por mes')
        seccion('MOVIMIENTOS POR MES', por_mes, titulo_mes,
                max_grafico=12, desde_final=True)
        seccion('DESTINOS (TOP 10)', por_destino[:10], 'Movimientos por destino (top 10)',
                tipo_grafico='torta')
        seccion('EQUIPOS CON MÁS MOVIMIENTOS (TOP 10)', por_equipo[:10],
                'Movimientos por equipo (top 10)')

        doc.build(elementos)
        buf.seek(0)
        return buf
