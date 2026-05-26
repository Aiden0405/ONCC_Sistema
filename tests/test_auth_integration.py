import pytest

from app import create_app, db
from app.models.usuario import Usuario
from app.models.role import Role


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_login_assign_role(app, client):
    # Crear rol
    with app.app_context():
        r = Role(nombre='Administrador')
        db.session.add(r)
        db.session.commit()

    # Crear usuario
    resp = client.post('/admin/usuarios/nuevo', data={
        'nombre': 'Test Admin',
        'correo': 'admin@oncc.gob.ve',
        'rol': 'Administrador',
        'password': 'AdminONCC2024*'
    }, follow_redirects=True)
    assert resp.status_code in (200, 302)

    # Intentar login
    resp = client.post('/auth/login', data={
        'correo': 'admin@oncc.gob.ve',
        'password': 'AdminONCC2024*'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Perfil' in resp.data or b'dashboard' in resp.data or b'Usuarios' in resp.data
*** End Patch