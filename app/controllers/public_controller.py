from collections import Counter
from datetime import datetime

from flask import Blueprint, render_template, session

from app import db
from app.models.geomatica import MapaRegistro
from app.models.visita_portal import VisitaPortal

public_bp = Blueprint('public', __name__)


def _registrar_visita_mensual():
    mes_actual = datetime.utcnow().strftime('%Y-%m')
    if session.get('public_visit_month') != mes_actual:
        session['public_visit_month'] = mes_actual
        db.session.add(VisitaPortal(mes=mes_actual))
        db.session.commit()
    return VisitaPortal.query.filter_by(mes=mes_actual).count()


@public_bp.route('/')
def home():
    comunidades = []
    mapas_registrados = MapaRegistro.query.count()
    visitas_mensuales = _registrar_visita_mensual()

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
    )


@public_bp.route('/acerca')
def acerca():
    return render_template('public/acerca.html')


@public_bp.route('/servicios')
def servicios():
    return render_template('public/servicios.html')


@public_bp.route('/contacto')
def contacto():
    return render_template('public/contacto.html')
