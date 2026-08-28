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
                'rol': u.rol,
            })
        return resultado

    @staticmethod
    def serializar_movimientos_tecnico(tecnico_id):
        from app.models.inventario import InventarioEquipo, MovimientoEquipo

        perfiles = TecnicoService._perfiles_por_usuario([tecnico_id])
        tecnico = Usuario.query.get(tecnico_id)
        perfil = perfiles.get(tecnico_id)
        if not tecnico:
            return []

        nombres = [n for n in (tecnico.nombre_usuario, perfil.nombres if perfil else None) if n]

        equipos = InventarioEquipo.query.all()
        ids_equipos = set()
        for eq in equipos:
            responsable = eq.responsable or ''
            if any(nombre and nombre.strip() and nombre.strip().lower() in responsable.lower() for nombre in nombres):
                ids_equipos.add(eq.id)

        if not ids_equipos:
            return []

        movimientos = MovimientoEquipo.query.filter(
            MovimientoEquipo.id_equipo.in_(ids_equipos)
        ).order_by(MovimientoEquipo.fecha_movimiento.desc(), MovimientoEquipo.id_movimiento.desc()).all()

        resultado = []
        for mov in movimientos:
            equipo = mov.equipo_rel
            resultado.append({
                'id': mov.id_movimiento,
                'codigo': mov.codigo,
                'equipo': mov.codigo_equipo,
                'fecha': mov.fecha_movimiento.strftime('%Y-%m-%d'),
                'origen': mov.ubicacion_origen,
                'destino': mov.ubicacion_destino,
                'motivo': mov.motivo_responsable,
                'tipo_equipo': equipo.tipo_equipo if equipo else '—',
                'nombre_equipo': equipo.codigo_interno if equipo else '—',
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

    @staticmethod
    def generar_reporte_pdf(tecnicos):
        import io, os
        from datetime import date
        from flask import current_app
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

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
            canvas.drawString(margen_x, footer_y - 2, 'Código: REG-TEC-001 | Versión 1.0')
            canvas.drawRightString(ancho_pag - margen_x, footer_y - 2, f'Página {doc.page}')
            canvas.restoreState()

        doc = SimpleDocTemplate(buf, pagesize=letter,
                                title='Reporte de Técnicos de Campo',
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
            Paragraph("REPORTE DE TÉCNICOS DE CAMPO", estilo_titulo),
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

        disponibles = sum(1 for t in tecnicos if t.get('estatus'))

        def info_fila(label, valor, label2, valor2):
            return [
                Paragraph(f'<font size=8 color="#4b5563"><b>{label}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor}</font>', estilo_info_valor),
                Paragraph(f'<font size=8 color="#4b5563"><b>{label2}</b></font>', estilo_info_label),
                Paragraph(f'<font size=9 color="#111827">{valor2}</font>', estilo_info_valor),
            ]

        datos_reporte = [
            info_fila('Total Técnicos', str(len(tecnicos)), 'Fecha Emisión', fecha_reporte),
            info_fila('Disponibles', str(disponibles), 'Tipo Reporte', 'Ficha de Técnicos'),
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
            [Paragraph('<b>CÉDULA</b>', estilo_tabla_titulo),
             Paragraph('<b>NOMBRE COMPLETO</b>', estilo_tabla_titulo),
             Paragraph('<b>ESPECIALIDAD</b>', estilo_tabla_titulo),
             Paragraph('<b>ESTATUS</b>', estilo_tabla_titulo)],
        ]
        for t in tecnicos:
            estatus = 'Disponible' if t.get('estatus') else 'No Disponible'
            detalle_data.append([
                Paragraph(t.get('cedula') or '—', estilo_tabla_celda),
                Paragraph(t.get('nombre_usuario') or '—', estilo_tabla_celda),
                Paragraph(t.get('especialidad') or '—', estilo_tabla_celda),
                Paragraph(estatus, estilo_tabla_celda),
            ])

        cols_tabla = [1.2 * inch, 2.2 * inch, 1.8 * inch, 1.2 * inch]
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
        elementos.append(Paragraph('<b>DETALLE DE TÉCNICOS</b>', estilo_info_label))
        elementos.append(Spacer(1, 4))
        elementos.append(t_det)

        doc.build(elementos)
        buf.seek(0)
        return buf
