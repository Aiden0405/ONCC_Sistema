from collections import Counter
from datetime import datetime

from flask import render_template, session, request, redirect, url_for, flash
from flask_login import login_required

from app.utils.authorization import role_required
from app.blueprints.core.forms import PublicacionForm
from app.services.notificacion import ServicioNotificacion
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


@core_bp.route('/')
def home():
    comunidades = []
    mapas_registrados = MapaRegistro.query.count()
    visitas_mensuales = _registrar_visita_mensual()
    publicaciones = []

    try:
        publicaciones = (
            Publicacion.query.filter_by(estado='publicado')
            .order_by(Publicacion.publicado_en.desc(), Publicacion.creado_en.desc())
            .limit(4)
            .all()
        )
    except OperationalError:
        db.session.rollback()

    comunidades_por_estado = Counter()

    monitoreo = [
        {
            'estado': 'Lara',
            'lat': 10.073,
            'lng': -69.322,
            'temperatura': 28.4,
            'lluvia': 12,
            'humedad': 61,
            'riesgo': 'Medio',
            'comunidades': comunidades_por_estado.get('Lara', 0),
        },
        {
            'estado': 'Yaracuy',
            'lat': 10.339,
            'lng': -68.745,
            'temperatura': 27.1,
            'lluvia': 18,
            'humedad': 67,
            'riesgo': 'Medio-Alto',
            'comunidades': comunidades_por_estado.get('Yaracuy', 0),
        },
        {
            'estado': 'Falcón',
            'lat': 11.062,
            'lng': -69.681,
            'temperatura': 30.2,
            'lluvia': 4,
            'humedad': 48,
            'riesgo': 'Bajo',
            'comunidades': comunidades_por_estado.get('Falcón', 0),
        },
    ]

    return render_template(
        'public/home.html',
        visitas_mensuales=visitas_mensuales,
        monitoreo=monitoreo,
        mapas_registrados=mapas_registrados,
        publicaciones=publicaciones,
    )


@core_bp.route('/acerca')
def acerca():
    return render_template('public/acerca.html')


@core_bp.route('/servicios')
def servicios():
    return render_template('public/servicios.html')


@core_bp.route('/contacto')
def contacto():
    return render_template('public/contacto.html')


# -----------------------
# Panel administrativo
# -----------------------
@core_bp.route('/admin/divulgacion/')
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def divulgacion_admin_index():
    publicaciones = Publicacion.query.order_by(Publicacion.creado_en.desc()).all()
    return render_template('divulgacion/admin_index.html', publicaciones=publicaciones)


@core_bp.route('/admin/divulgacion/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def divulgacion_admin_nuevo():
    form = PublicacionForm()
    if form.validate_on_submit():
        pub = Publicacion(
            tipo=form.tipo.data,
            titulo=form.titulo.data,
            resumen=form.resumen.data,
            contenido=form.contenido.data,
            estado=form.estado.data,
        )
        if pub.estado == 'publicado':
            pub.publicado_en = datetime.utcnow()
        db.session.add(pub)
        db.session.commit()
        flash('Publicación guardada.', 'success')
        return redirect(url_for('core.divulgacion_admin_index'))
    return render_template('divulgacion/admin_form.html', form=form)


@core_bp.route('/admin/divulgacion/<int:pub_id>/aprobar', methods=['POST'])
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def divulgacion_admin_aprobar(pub_id):
    pub = Publicacion.query.get_or_404(pub_id)
    pub.estado = 'publicado'
    pub.publicado_en = datetime.utcnow()
    db.session.commit()

    # Notificar al servicio externo (stub)
    ServicioNotificacion.disparar_a_main_page(pub)

    flash('Publicación aprobada y publicada.', 'success')
    return redirect(url_for('core.divulgacion_admin_index'))