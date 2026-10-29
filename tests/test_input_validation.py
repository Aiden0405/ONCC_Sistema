from datetime import datetime, timedelta, timezone

import pytest

from app.services.inventario_service import InventarioService
from app.utils.validation import parse_positive_int, validate_password, validate_person_text


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