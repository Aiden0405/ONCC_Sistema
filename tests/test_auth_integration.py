import pytest
from datetime import datetime, timezone

from app import create_app, db
from app.models.usuario import Usuario
from app.models.role import Role


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })

    with app.app_context():
        yield app
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_flow_with_seeded_user(app, client):
    correo = f"pytest_auth_{int(datetime.now(timezone.utc).timestamp())}@oncc.gob.ve"
    password = 'AdminONCC2024*'

    with app.app_context():
        rol = Role.query.filter_by(nombre_rol='Administrador').first()
        if not rol:
            rol = Role(nombre='Administrador')
            db.session.add(rol)
            db.session.flush()

        usuario = Usuario(
            nombre_usuario='Pytest Auth User',
            correo=correo,
            id_rol=rol.id_rol,
            estatus=True,
        )
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()

    # Intentar login con usuario creado para la prueba
    resp = client.post('/auth/login', data={
        'correo': correo,
        'password': password,
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b'dashboard' in resp.data or b'Dashboard' in resp.data or b'monitoreo' in resp.data


def test_unified_formaciones_page_keeps_both_registration_forms(app, client):
    correo = f"pytest_unified_{int(datetime.now(timezone.utc).timestamp())}@oncc.gob.ve"
    password = 'AdminONCC2024*'

    with app.app_context():
        rol = Role.query.filter_by(nombre_rol='Administrador').first()
        if not rol:
            rol = Role(nombre='Administrador')
            db.session.add(rol)
            db.session.flush()

        usuario = Usuario(
            nombre_usuario='Pytest Unified User',
            correo=correo,
            id_rol=rol.id_rol,
            estatus=True,
        )
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()

    client.post('/auth/login', data={'correo': correo, 'password': password}, follow_redirects=True)
    resp = client.get('/formaciones', follow_redirects=True)

    assert resp.status_code == 200
    assert b'Registrar Nueva Jornada de Formaci' in resp.data
    assert b'Registrar Nueva Campa\xc3\xb1a de Sensibilizaci' in resp.data
