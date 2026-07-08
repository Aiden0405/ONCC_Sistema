from collections import Counter
from datetime import datetime

from flask import render_template, session, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.blueprints.core.forms import PublicacionForm
from app.services.notificacion import ServicioNotificacion
from app.services.auditoria import registrar_accion
from sqlalchemy.exc import OperationalError

from app import db
from app.blueprints.core import core_bp
from app.models.divulgacion import Publicacion
from app.models.geomatica import MapaRiesgo
from app.models.visita_portal import VisitaPortal


# 🛠️ FUNCIÓN AUXILIAR DE SEGURIDAD DINÁMICA (RBAC) CON BYPASS JERÁRQUICO
def verificar_permiso_dinamico(nombre_permiso):
    """
    Comprueba en PostgreSQL si el rol del usuario autenticado posee el permiso
    solicitado, aplicando bypass inmediato para los roles del Core administrativo (1 y 2).
    """
    if not current_user.is_authenticated:
        abort(403)
        
    # Superusuario (1) y Administrador (2) tienen bypass por jerarquía
    if int(current_user.id_rol) in (1, 2):
        return True
        
    # Mapeo dinámico exclusivo para el rol Técnico u otros roles operativos
    permisos_del_rol = [p.nombre_modulo for p in current_user.role.permissions]
    
    if nombre_permiso not in permisos_del_rol:
        flash('No posee privilegios institucionales para ejecutar esta acción.', 'error')
        abort(403)


def _registrar_visita_mensual():
    mes_actual = datetime.utcnow().strftime('%Y-%m')
    if session.get('public_visit_month') != mes_actual:
        session['public_visit_month'] = mes_actual
        db.session.add(VisitaPortal(mes=mes_actual))
        db.session.commit()
    return VisitaPortal.query.filter_by(mes=mes_actual).count()


# ==============================================================================
# VISTAS PÚBLICAS (Abiertas para todo el mundo)
# ==============================================================================

@core_bp.route('/')
def home():
    mapas_registrados = MapaRiesgo.query.count()
    visitas_mensuales = _registrar_visita_mensual()
    publicaciones = []
    cant_borradores = 0
    cant_publicados = 0

    if not current_user.is_authenticated:
        cant_publicados = Publicacion.query.filter_by(estado_publicacion='publicado').count()
    else:
        rol_id_actual = int(current_user.id_rol)
        usuario_id_actual = int(current_user.get_id())

        if rol_id_actual == 3:  # Técnico operativo
            cant_borradores = Publicacion.query.filter_by(id_usuario=usuario_id_actual, estado_publicacion='borrador').count()
            cant_publicados = Publicacion.query.filter_by(id_usuario=usuario_id_actual, estado_publicacion='publicado').count()
        else:  # Roles administrativos
            cant_borradores = Publicacion.query.filter_by(estado_publicacion='borrador').count()
            cant_publicados = Publicacion.query.filter_by(estado_publicacion='publicado').count()

    try:
        publicaciones = (
            Publicacion.query.filter_by(estado_publicacion='publicado')
            # 🌟 RESTAURADO: Ordena por nivel de criticidad (20 primero) y luego por fecha
            .order_by(Publicacion.prioridad.desc(), Publicacion.publicado_en.desc())
            .limit(4)
            .all()
        )
    except OperationalError:
        db.session.rollback()

    comunidades_por_estado = Counter()

    monitoreo = [
        {"estado": "Lara", "lat": 10.073, "lng": -69.322, "temperatura": 28.4, "lluvia": 12, "humedad": 61, "riesgo": "Medio", "comunidades": comunidades_por_estado.get("Lara", 0)},
        {"estado": "Yaracuy", "lat": 10.339, "lng": -68.745, "temperatura": 27.1, "lluvia": 18, "humedad": 67, "riesgo": "Medio-Alto", "comunidades": comunidades_por_estado.get("Yaracuy", 0)},
        {"estado": "Falcón", "lat": 11.062, "lng": -69.681, "temperatura": 30.2, "lluvia": 4, "humedad": 48, "riesgo": "Bajo", "comunidades": comunidades_por_estado.get("Falcón", 0)}
    ]

    return render_template(
        'public/home.html',
        visitas_mensuales=visitas_mensuales,
        monitoreo=monitoreo,
        mapas_registrados=mapas_registrados,
        publicaciones=publicaciones,
        cant_borradores=cant_borradores,    
        cant_publicados=cant_publicados     
    )


@core_bp.route('/publicaciones/<int:pub_id>')
def divulgacion_detalle(pub_id):
    # 🌟 CORREGIDO: Se ajustó a las columnas oficiales de la Base de Datos
    publicacion = Publicacion.query.filter_by(id_publicacion=pub_id, estado_publicacion='publicado').first_or_404()
    return render_template('public/divulgacion_detalle.html', publicacion=publicacion)


@core_bp.route('/acerca')
def acerca():
    return render_template('public/acerca.html')


@core_bp.route('/servicios')
def servicios():
    return render_template('public/servicios.html')


@core_bp.route('/contacto')
def contacto():
    return render_template('public/contacto.html')


# ==============================================================================
# PANEL ADMINISTRATIVO (Gobernanza de Métricas Dinámica)
# ==============================================================================

@core_bp.route('/admin/divulgacion/')
@login_required
def divulgacion_admin_index():
    usuario_id_actual = int(current_user.get_id())
    rol_id_actual = int(current_user.id_rol)
    
    permisos_del_rol = [p.nombre_modulo for p in current_user.role.permissions]

    # VALIDACIÓN JERÁRQUICA
    if 'aprobar_divulgaciones' not in permisos_del_rol and rol_id_actual not in (1, 2):
        # 🌟 CORREGIDO: 'estado' por 'estado_publicacion'
        cant_borradores = Publicacion.query.filter_by(id_usuario=usuario_id_actual, estado_publicacion='borrador').count()
        cant_publicados = Publicacion.query.filter_by(id_usuario=usuario_id_actual, estado_publicacion='publicado').count()
        
        # 🌟 RESTAURADO: Muestra las publicaciones propias ordenadas por criticidad y creación
        publicaciones = (
            Publicacion.query.filter(Publicacion.id_usuario == usuario_id_actual)
            .order_by(Publicacion.prioridad.desc(), Publicacion.creado_en.desc())
            .all()
        )
    else: 
        # 🌟 CORREGIDO: 'estado' por 'estado_publicacion'
        cant_borradores = Publicacion.query.filter_by(estado_publicacion='borrador').count()
        cant_publicados = Publicacion.query.filter_by(estado_publicacion='publicado').count()
        
        # 🌟 RESTAURADO: Muestra todas las publicaciones ordenadas por criticidad (20 primero)
        publicaciones = Publicacion.query.order_by(Publicacion.prioridad.desc(), Publicacion.creado_en.desc()).all()
        
    return render_template(
        'divulgacion/admin_index.html', 
        publicaciones=publicaciones,
        cant_borradores=cant_borradores,  
        cant_publicados=cant_publicados,
        permisos_activos=permisos_del_rol  
    )


@core_bp.route('/admin/divulgacion/nuevo', methods=['GET', 'POST'])
@login_required
def divulgacion_admin_nuevo():
    verificar_permiso_dinamico('crear_divulgaciones')
    
    form = PublicacionForm()
    if form.validate_on_submit():
        usuario_id_actual = int(current_user.get_id())
        permisos_del_rol = [p.nombre_modulo for p in current_user.role.permissions]

        pub = Publicacion(
            tipo=form.tipo.data,
            titulo_publicacion=form.titulo.data,
            resumen=form.resumen.data,
            contenido=form.contenido.data,
            # 🌟 REAL: Ahora guarda la prioridad del formulario directamente en PostgreSQL
            prioridad=form.prioridad.data if form.prioridad.data else 1,
            id_usuario=usuario_id_actual,
            id_divulgacion=form.id_divulgacion.data
        )
        
        if 'aprobar_divulgaciones' in permisos_del_rol or int(current_user.id_rol) in (1, 2):
            pub.estado_publicacion = form.estado.data
            if form.estado.data == 'publicado':
                pub.publicado_en = datetime.utcnow()
        else:
            pub.estado_publicacion = 'borrador'

        db.session.add(pub)
        db.session.commit()

        registrar_accion('Divulgación', pub.id_publicacion, 'Crear', current_user.nombre_usuario, detalle=f'Creado contenido: {pub.titulo_publicacion[:40]}...', estado_nuevo=pub.estado_publicacion)
        flash('Publicación guardada de forma exitosa.', 'success')
        return redirect(url_for('core.divulgacion_admin_index'))
        
    return render_template('divulgacion/admin_form.html', form=form, es_edicion=False)


@core_bp.route('/admin/divulgacion/<int:pub_id>/editar', methods=['GET', 'POST'])
@login_required
def divulgacion_admin_editar(pub_id):
    verificar_permiso_dinamico('crear_divulgaciones')
    
    pub = Publicacion.query.get_or_404(pub_id)
    permisos_del_rol = [p.nombre_modulo for p in current_user.role.permissions]
    rol_id_actual = int(current_user.id_rol)
    usuario_id_actual = int(current_user.get_id())
    
    # 🛡️ ESCUDO DE PROPIEDAD INTER-OPERADOR: El Técnico solo edita lo SUYO
    if rol_id_actual not in (1, 2) and int(pub.id_usuario) != usuario_id_actual:
        flash('Acceso denegado: No posee los privilegios para modificar esta publicación de otro operador.', 'error')
        return redirect(url_for('core.divulgacion_admin_index'))
    
    if pub.estado_publicacion == 'publicado' and 'aprobar_divulgaciones' not in permisos_del_rol and rol_id_actual not in (1, 2):
        flash('No puedes modificar una publicación que ya está activa en la web.', 'error')
        return redirect(url_for('core.divulgacion_admin_index'))

    form = PublicacionForm(obj=pub)
    if form.validate_on_submit():
        form.populate_obj(pub)
        pub.actualizado_en = datetime.utcnow()
        
        if 'aprobar_divulgaciones' not in permisos_del_rol and rol_id_actual not in (1, 2):
            pub.estado_publicacion = 'borrador'

        db.session.commit()
        registrar_accion('Divulgación', pub.id_publicacion, 'Modificar', current_user.nombre_usuario, detalle=f'Actualizado ID: {pub.id_publicacion}', estado_nuevo=pub.estado_publicacion)
        flash('Publicación actualizada correctamente.', 'success')
        return redirect(url_for('core.divulgacion_admin_index'))
        
    return render_template('divulgacion/admin_form.html', form=form, es_edicion=True)


@core_bp.route('/admin/divulgacion/<int:pub_id>/eliminar', methods=['POST'])
@login_required
def divulgacion_admin_eliminar(pub_id):
    verificar_permiso_dinamico('crear_divulgaciones')
    
    pub = Publicacion.query.get_or_404(pub_id)
    permisos_del_rol = [p.nombre_modulo for p in current_user.role.permissions]
    rol_id_actual = int(current_user.id_rol)
    usuario_id_actual = int(current_user.get_id())
    
    # 🛡️ ESCUDO DE PROPIEDAD EN ELIMINACIÓN
    if rol_id_actual not in (1, 2) and int(pub.id_usuario) != usuario_id_actual:
        flash('Acceso denegado: No posee la autoría para eliminar este expediente.', 'error')
        return redirect(url_for('core.divulgacion_admin_index'))
    
    if pub.estado_publicacion == 'publicado' and 'aprobar_divulgaciones' not in permisos_del_rol and rol_id_actual not in (1, 2):
        flash('No se permite la eliminación de un contenido activo en el portal institucional.', 'error')
        return redirect(url_for('core.divulgacion_admin_index'))

    titulo_eliminado = pub.titulo_publicacion
    db.session.delete(pub)
    db.session.commit()

    registrar_accion('Divulgación', pub_id, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado permanentemente: {titulo_eliminado[:40]}...')
    flash('Publicación removida con éxito de la base de datos.', 'success')
    return redirect(url_for('core.divulgacion_admin_index'))


@core_bp.route('/admin/divulgacion/<int:pub_id>/aprobar', methods=['POST'])
@login_required
def divulgacion_admin_aprobar(pub_id):
    verificar_permiso_dinamico('aprobar_divulgaciones')
    
    pub = Publicacion.query.get_or_404(pub_id)
    pub.estado_publicacion = 'publicado'
    pub.publicado_en = datetime.utcnow()
    db.session.commit()

    ServicioNotificacion.disparar_a_main_page(pub)
    registrar_accion('Divulgación', pub.id_publicacion, 'Modificar', current_user.nombre_usuario, detalle=f'Aprobada para la Web: {pub.titulo_publicacion[:40]}...', estado_nuevo='publicado')
    flash('Publicación aprobada y publicada exitosamente.', 'success')
    return redirect(url_for('core.divulgacion_admin_index'))


@core_bp.route('/admin/divulgacion/<int:pub_id>/despublicar', methods=['POST'])
@login_required
def divulgacion_admin_despublicar(pub_id):
    verificar_permiso_dinamico('aprobar_divulgaciones')
    
    pub = Publicacion.query.get_or_404(pub_id)
    pub.estado_publicacion = 'borrador'
    pub.publicado_en = None
    db.session.commit()

    registrar_accion('Divulgación', pub.id_publicacion, 'Modificar', current_user.nombre_usuario, detalle=f'Retirada de la web (Devuelta a borrador): {pub.titulo_publicacion[:40]}...', estado_nuevo='borrador')
    flash('El contenido ha sido retirado de la web pública y devuelto a borrador.', 'success')
    return redirect(url_for('core.divulgacion_admin_index'))