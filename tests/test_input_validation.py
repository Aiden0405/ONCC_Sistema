from datetime import datetime, timedelta, timezone

import pytest

from app.services.inventario_service import InventarioService
from app.services.tecnico_service import TecnicoService
from app.utils.validation import (
    parse_positive_int,
    validate_document_id,
    validate_email,
    validate_password,
    validate_person_text,
)


def _datos_equipo(**overrides):
    datos = {
        'tipo_equipo': 'EMA',
        'codigo': 'EMA-005',
        'ubicacion': 'Bella Vista',
        'responsable': 'Ana Pérez',
        'estado_operativo': 'Operativo',
        'estado': 'Disponible',
        'ultimo_mantenimiento': datetime.now(timezone.utc).date().isoformat(),
    }
    datos.update(overrides)
    return datos


def test_accepts_existing_password_without_complexity_requirements():
    assert validate_password('aaaaahhhhh') == 'aaaaahhhhh'


def test_accepts_password_meeting_policy():
    assert validate_password('AdminONCC2024*') == 'AdminONCC2024*'


def test_rejects_markup_in_person_fields():
    with pytest.raises(ValueError):
        validate_person_text('<script>alert(1)</script>', field='Nombre')


def test_positive_integer_rejects_invalid_values():
    with pytest.raises(ValueError):
        parse_positive_int('no-numero')
    with pytest.raises(ValueError):
        parse_positive_int('0')


def test_equipo_valido_pasa_validacion():
    valores, error = InventarioService._validar_datos_equipo(_datos_equipo())
    assert error is None
    assert valores['codigo'] == 'EMA-005'


@pytest.mark.parametrize('codigo', ['00000', '1234567', 'EMA000', 'EMA-000', 'EMA'])
def test_rechaza_codigos_de_equipo_invalidos(codigo):
    _, error = InventarioService._validar_datos_equipo(_datos_equipo(codigo=codigo))
    assert 'código' in error.lower()


@pytest.mark.parametrize('ubicacion', ['Bella Vista11111', 'Sector 5', 'Vía-01'])
def test_rechaza_ubicaciones_con_numeros_o_simbolos(ubicacion):
    _, error = InventarioService._validar_datos_equipo(_datos_equipo(ubicacion=ubicacion))
    assert 'ubicación' in error.lower()


def test_acepta_ubicacion_con_tildes_y_enie():
    _, error = InventarioService._validar_datos_equipo(_datos_equipo(ubicacion='Vía Ñuñoa'))
    assert error is None


def test_rechaza_fecha_de_mantenimiento_futura():
    fecha_futura = (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()
    _, error = InventarioService._validar_datos_equipo(
        _datos_equipo(ultimo_mantenimiento=fecha_futura)
    )
    assert 'posterior a hoy' in error.lower()


def test_exige_fecha_de_ultimo_mantenimiento():
    _, error = InventarioService._validar_datos_equipo(
        _datos_equipo(ultimo_mantenimiento='')
    )
    assert 'fecha' in error.lower()

def _datos_tecnico(**overrides):
    datos = {
        'nombre': 'Ana Pérez',
        'correo': 'ana.perez@example.com',
        'cedula': '12345678',
        'especialidad': 'Geología',
        'estatus': '1',
    }
    datos.update(overrides)
    return datos


def test_rechaza_password_de_un_caracter():
    with pytest.raises(ValueError):
        validate_password('x')


def test_valida_correo_y_cedula():
    assert validate_email('Usuario@Example.COM') == 'usuario@example.com'
    assert validate_document_id('V-12345678') == 'V-12345678'
    with pytest.raises(ValueError):
        validate_email('correo-sin-arroba')
    with pytest.raises(ValueError):
        validate_document_id('ABC-123')


def test_rechaza_campos_de_texto_con_tipos_incorrectos():
    _, error = InventarioService._validar_datos_equipo(_datos_equipo(codigo=12345))
    assert 'texto' in error.lower()

    _, error = InventarioService._validar_datos_movimiento({
        'equipo': 123,
        'fecha_hora': '2024-01-01',
        'ubicacion_origen': 'Origen',
        'ubicacion_destino': 'Destino',
        'motivo_responsable': 'Motivo',
    })
    assert 'texto' in error.lower()

    _, error = TecnicoService._validar_datos_tecnico(_datos_tecnico(nombre=None))
    assert 'obligatorio' in error.lower()


@pytest.mark.parametrize('campo,valor', [
    ('codigo', 'A1' * 30),
    ('tipo_equipo', 'T' * 101),
    ('ubicacion', 'U' * 101),
    ('estado_operativo', 'C' * 31),
    ('estado', 'E' * 31),
    ('responsable', 'R' * 121),
])
def test_rechaza_equipos_con_longitudes_excesivas(campo, valor):
    _, error = InventarioService._validar_datos_equipo(_datos_equipo(**{campo: valor}))
    assert 'superar' in error.lower()


def test_tecnico_valido_pasa_validacion():
    valores, error = TecnicoService._validar_datos_tecnico(_datos_tecnico())
    assert error is None
    assert valores['cedula'] == '12345678'
    assert valores['estatus'] is True


@pytest.mark.parametrize('campo,valor', [
    ('nombre', '   '),
    ('correo', ''),
    ('cedula', '   '),
    ('especialidad', ''),
])
def test_rechaza_campos_obligatorios_vacios_de_tecnico(campo, valor):
    _, error = TecnicoService._validar_datos_tecnico(_datos_tecnico(**{campo: valor}))
    assert 'obligatorios' in error.lower()


@pytest.mark.parametrize('campo,valor', [
    ('nombre', 'N' * 31),
    ('correo', 'a' * 45 + '@example.com'),
    ('cedula', '1' * 16),
    ('especialidad', 'E' * 101),
])
def test_rechaza_tecnicos_con_longitudes_excesivas(campo, valor):
    _, error = TecnicoService._validar_datos_tecnico(_datos_tecnico(**{campo: valor}))
    assert error is not None


@pytest.mark.parametrize('datos', [
    {'correo': 'correo-invalido'},
    {'cedula': 'ABC123'},
    {'estatus': '2'},
])
def test_rechaza_datos_invalidos_de_tecnico(datos):
    _, error = TecnicoService._validar_datos_tecnico(_datos_tecnico(**datos))
    assert error is not None
