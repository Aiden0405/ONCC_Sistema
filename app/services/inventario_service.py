from datetime import datetime, date

from flask import current_app, Response
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from app import db
from app.models.bitacora import BitacoraTransaccion
from app.models.inventario import InventarioEquipo, MovimientoEquipo


class InventarioService:

    CATEGORIA_DEFAULT = 'General'

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
            modelo='N/D',
            marca='N/D',
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
    def _parsear_fecha(datos, campo='ultimo_mantenimiento'):
        """Devuelve (fecha, error). Solo uno de los dos será distinto de None."""
        fecha_str = (datos.get(campo) or '').strip()
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
        codigo = datos.get('codigo', '').strip()
        if not codigo:
            return {'ok': False, 'error': 'Debe indicar el codigo del equipo.'}

        if InventarioEquipo.query.filter_by(codigo_interno=codigo).first():
            return {'ok': False, 'error': 'Ya existe un equipo con ese codigo.'}

        try:
            ultimo_mantenimiento, error_fecha = InventarioService._parsear_fecha(datos)
        except ValueError:
            error_fecha = 'Formato de fecha inválido.'
        if error_fecha:
            return {'ok': False, 'error': error_fecha}

        tipo = datos.get('tipo_equipo', '').strip() or 'Equipo Técnico'
        nombre_ubicacion = datos.get('ubicacion', '').strip() or 'Sin Ubicación'
        condicion = datos.get('estado_operativo', 'Operativo').strip() or 'Operativo'
        estado_flujo = datos.get('estado', 'Disponible').strip() or 'Disponible'
        responsable = datos.get('responsable', '').strip() or usuario.nombre

        modelo = InventarioService._obtener_o_crear_modelo(tipo)
        ubicacion = InventarioService._obtener_o_crear_ubicacion(nombre_ubicacion)

        equipo = InventarioEquipo(
            id_modelos_equipos=modelo.id_modelos_equipo,
            id_ubicacion_actual=ubicacion.id_ubicacion,
            codigo_interno=codigo,
            estado=estado_flujo,
            condicion=condicion,
            fecha_ingreso=datetime.utcnow().date(),
            ultimo_mantenimiento=ultimo_mantenimiento,
            responsable=responsable,
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

        return {'ok': True, 'equipo': equipo, 'mensaje': 'Equipo registrado exitosamente en el inventario.'}

    @staticmethod
    def _validar_datos_movimiento(datos):
        """Devuelve (valores, error). Solo uno de los dos es distinto de None."""
        codigo_equipo = datos.get('equipo', '').strip()
        if not codigo_equipo:
            return None, 'Debe seleccionar un equipo.'
        equipo = InventarioEquipo.query.filter_by(codigo_interno=codigo_equipo).first()
        if not equipo:
            return None, 'El equipo seleccionado no existe en el inventario.'

        fecha_str = datos.get('fecha_hora', '').strip()
        if not fecha_str:
            return None, 'Debe indicar la fecha y hora.'
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return None, 'Formato de fecha inválido.'
        if fecha > datetime.utcnow().date():
            return None, 'La fecha no puede ser posterior a hoy.'

        origen = datos.get('ubicacion_origen', '').strip()
        if not origen:
            return None, 'Debe indicar la ubicación de origen.'
        destino = datos.get('ubicacion_destino', '').strip()
        if not destino:
            return None, 'Debe indicar la ubicación de destino.'
        motivo = datos.get('motivo_responsable', '').strip()
        if not motivo:
            return None, 'Debe indicar el motivo y responsable.'

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

        return {'ok': True, 'mensaje': 'Movimiento eliminado del historial.'}

    @staticmethod
    def actualizar_equipo(equipo_id, datos, usuario):
        equipo = InventarioEquipo.query.get_or_404(equipo_id)
        codigo = datos.get('codigo', '').strip()

        if not codigo:
            return {'ok': False, 'error': 'Debe indicar el codigo del equipo.'}

        existe = InventarioEquipo.query.filter_by(codigo_interno=codigo).first()
        if existe and existe.id != equipo.id:
            return {'ok': False, 'error': 'Ya existe otro equipo con ese codigo.'}

        ultimo_mantenimiento, error_fecha = InventarioService._parsear_fecha(datos)
        if error_fecha:
            return {'ok': False, 'error': error_fecha}

        tipo = datos.get('tipo_equipo', '').strip() or equipo.tipo_equipo
        nombre_ubicacion = datos.get('ubicacion', '').strip() or equipo.ubicacion

        if tipo != equipo.tipo_equipo:
            modelo = InventarioService._obtener_o_crear_modelo(tipo)
            equipo.id_modelos_equipos = modelo.id_modelos_equipo
        if nombre_ubicacion != equipo.ubicacion:
            ubicacion = InventarioService._obtener_o_crear_ubicacion(nombre_ubicacion)
            equipo.id_ubicacion_actual = ubicacion.id_ubicacion

        equipo.codigo_interno = codigo
        equipo.estado = datos.get('estado', equipo.estado_flujo).strip() or equipo.estado_flujo
        equipo.condicion = datos.get('estado_operativo', equipo.condicion).strip() or equipo.condicion
        equipo.ultimo_mantenimiento = ultimo_mantenimiento
        equipo.responsable = datos.get('responsable', equipo.responsable).strip() or equipo.responsable

        db.session.add(BitacoraTransaccion(
            modulo='inventario',
            registro_id=equipo.id,
            accion='modificacion',
            estado_nuevo=equipo.estado_flujo,
            usuario=usuario.nombre,
            detalle=f'Datos del equipo {equipo.codigo} actualizados',
        ))
        db.session.commit()

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
        db.session.delete(equipo)
        db.session.commit()

        return {'ok': True, 'mensaje': 'Equipo eliminado del inventario.'}

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
