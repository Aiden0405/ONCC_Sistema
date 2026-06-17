from collections import Counter
from datetime import datetime

from flask import render_template, session, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.core.forms import PublicacionForm
from app.services.notificacion import ServicioNotificacion
from app.services.auditoria import registrar_accion
from app.utils.authorization import role_required
from sqlalchemy.exc import OperationalError

from app import db
from app.blueprints.core import core_bp
from app.models.divulgacion import Publicacion
from app.models.geomatica import MapaRegistro
from app.models.visita_portal import VisitaPortal


def _registrar_visita_mensual():
    mes_actual = datetime.utcnow().strftime('%Y-%m')
    if session.get('public_visit_month') != mes_actual:
        session['public_visit_month'] = mes_actual
        db.session.add(VisitaPortal(mes=mes_actual))
        db.session.commit()
    return VisitaPortal.query.filter_by(mes=mes_actual).count()


# ==============================================================================
# VISTAS PÚBLICAS REQUERIDAS POR EL __INIT__.PY (Con conteo aislado de métricas)
# ==============================================================================

@core_bp.route('/')
def home():
    comunidades = []
    mapas_registrados = MapaRegistro.query.count()
    visitas_mensuales = _registrar_visita_mensual()
    publicaciones = []

    if not current_user.is_authenticated:
        cant_borradores = 0
        cant_publicados = Publicacion.query.filter_by(estado='publicado').count()
    else:
        rol_id_actual = int(current_user.id_rol)
        usuario_id_actual = int(current_user.get_id())

        if rol_id_actual == 3:  # Técnico
            cant_borradores = Publicacion.query.filter_by(id_usuario=usuario_id_actual, estado='borrador').count()
            cant_publicados = Publicacion.query.filter_by(id_usuario=usuario_id_actual, estado='publicado').count()
        else:  # Director o Admin
            cant_borradores = Publicacion.query.filter_by(estado='borrador').count()
            cant_publicados = Publicacion.query.filter_by(estado='publicado').count()

    try:
        publicaciones = (
            Publicacion.query.filter_by(estado='publicado')
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
    publicacion = Publicacion.query.filter_by(id=pub_id, estado='publicado').first_or_404()
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
# PANEL ADMINISTRATIVO (Gobernanza de Métricas e Índice de Divulgación)
# ==============================================================================

@core_bp.route('/admin/divulgacion/')
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional', 'Tecnico')
def divulgacion_admin_index():
    usuario_id_actual = int(current_user.get_id())
    rol_id_actual = int(current_user.id_rol)

    if rol_id_actual == 3:
        cant_borradores = Publicacion.query.filter_by(id_usuario=usuario_id_actual, estado='borrador').count()
        cant_publicados = Publicacion.query.filter_by(id_usuario=usuario_id_actual, estado='publicado').count()
        publicaciones = (
            Publicacion.query
            .filter(Publicacion.id_usuario == usuario_id_actual)
            .order_by(Publicacion.creado_en.desc())
            .all()
        )
    else:
        cant_borradores = Publicacion.query.filter_by(estado='borrador').count()
        cant_publicados = Publicacion.query.filter_by(estado='publicado').count()
        publicaciones = Publicacion.query.order_by(Publicacion.prioridad.desc(), Publicacion.creado_en.desc()).all()
        
    # 🌟 CORREGIDO: Se agregó 'divulgacion/'
    return render_template(
        'divulgacion/admin_index.html', 
        publicaciones=publicaciones,
        cant_borradores=cant_borradores,  
        cant_publicados=cant_publicados   
    )


@core_bp.route('/admin/divulgacion/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional', 'Tecnico')
def divulgacion_admin_nuevo():
    form = PublicacionForm()
    if form.validate_on_submit():
        usuario_id_actual = int(current_user.get_id())
        rol_id_actual = int(current_user.id_rol)

        pub = Publicacion(
            tipo=form.tipo.data,
            titulo=form.titulo.data,
            resumen=form.resumen.data,
            contenido=form.contenido.data,
            prioridad=form.prioridad.data if form.prioridad.data else 1,
            id_usuario=usuario_id_actual
        )
        
        if rol_id_actual in [1, 2]:
            pub.estado = form.estado.data
            if form.estado.data == 'publicado':
                pub.publicado_en = datetime.utcnow()
        else:
            pub.estado = 'borrador'

        db.session.add(pub)
        db.session.commit()

        registrar_accion('Divulgación', pub.id, 'Crear', current_user.nombre_usuario, detalle=f'Creado contenido: {pub.titulo[:40]}...', estado_nuevo=pub.estado)
        flash('Publicación guardada de forma exitosa.', 'success')
        return redirect(url_for('core.divulgacion_admin_index'))
        
    # 🌟 CORREGIDO: Se agregó 'divulgacion/'
    return render_template('divulgacion/admin_form.html', form=form, es_edicion=False)


@core_bp.route('/admin/divulgacion/<int:pub_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional', 'Tecnico')
def divulgacion_admin_editar(pub_id):
    pub = Publicacion.query.get_or_404(pub_id)
    
    if pub.estado == 'publicado' and int(current_user.id_rol) == 3:
        flash('No puedes modificar una publicación que ya está activa en la web.', 'error')
        return redirect(url_for('core.divulgacion_admin_index'))

    form = PublicacionForm(obj=pub)
    if form.validate_on_submit():
        rol_id_actual = int(current_user.id_rol)
        form.populate_obj(pub)
        pub.actualizado_en = datetime.utcnow()
        
        if rol_id_actual not in [1, 2]:
            pub.estado = 'borrador'

        db.session.commit()
        registrar_accion('Divulgación', pub.id, 'Modificar', current_user.nombre_usuario, detalle=f'Actualizado ID: {pub.id}', estado_nuevo=pub.estado)
        flash('Publicación actualizada correctamente.', 'success')
        return redirect(url_for('core.divulgacion_admin_index'))
        
    return render_template('divulgacion/admin_form.html', form=form, es_edicion=True)


@core_bp.route('/admin/divulgacion/<int:pub_id>/eliminar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional', 'Tecnico')
def divulgacion_admin_eliminar(pub_id):
    pub = Publicacion.query.get_or_404(pub_id)
    rol_id_actual = int(current_user.id_rol)
    
    if pub.estado == 'publicado' and rol_id_actual not in [1, 2]:
        flash('No se permite la eliminación de un contenido activo en el portal institucional.', 'error')
        return redirect(url_for('core.divulgacion_admin_index'))

    titulo_eliminado = pub.titulo
    db.session.delete(pub)
    db.session.commit()

    registrar_accion('Divulgación', pub_id, 'Eliminar', current_user.nombre_usuario, detalle=f'Eliminado permanentemente: {titulo_eliminado[:40]}...')
    flash('Publicación removida con éxito de la base de datos.', 'success')
    return redirect(url_for('core.divulgacion_admin_index'))


@core_bp.route('/admin/divulgacion/<int:pub_id>/aprobar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def divulgacion_admin_aprobar(pub_id):
    pub = Publicacion.query.get_or_404(pub_id)
    pub.estado = 'publicado'
    pub.publicado_en = datetime.utcnow()
    db.session.commit()

    ServicioNotificacion.disparar_a_main_page(pub)
    registrar_accion('Divulgación', pub.id, 'Modificar', current_user.nombre_usuario, detalle=f'Aprobada para la Web: {pub.titulo[:40]}...', estado_nuevo='publicado')
    flash('Publicación aprobada y publicada exitosamente.', 'success')
    return redirect(url_for('core.divulgacion_admin_index'))


@core_bp.route('/admin/divulgacion/<int:pub_id>/despublicar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def divulgacion_admin_despublicar(pub_id):
    pub = Publicacion.query.get_or_404(pub_id)
    
    pub.estado = 'borrador'
    pub.publicado_en = None
    db.session.commit()

    registrar_accion('Divulgación', pub.id, 'Modificar', current_user.nombre_usuario, detalle=f'Retirada de la web (Devuelta a borrador): {pub.titulo[:40]}...', estado_nuevo='borrador')
    flash('El contenido ha sido retirado de la web pública y devuelto a borrador.', 'success')
    return redirect(url_for('core.divulgacion_admin_index'))