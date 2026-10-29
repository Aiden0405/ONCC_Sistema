import re

from wtforms.validators import ValidationError


_PERSON_TEXT = re.compile(r"^[\w\s.,'()/-]+$", re.UNICODE)
_EMAIL = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")
_DOCUMENT_ID = re.compile(r"^[VEJPGvejpg]?-?\d{5,15}$")


def normalize_text(value, *, min_length=1, max_length=255, field='Este campo'):
    if value is None:
        value = ''
    elif not isinstance(value, str):
        raise ValueError(f'{field} debe ser texto.')

    value = value.strip()
    if len(value) < min_length:
        if not value:
            raise ValueError(f'{field} es obligatorio.')
        raise ValueError(f'{field} debe tener al menos {min_length} caracteres.')
    if len(value) > max_length:
        raise ValueError(f'{field} no puede superar los {max_length} caracteres.')
    return value


def validate_person_text(value, *, field='Este campo', max_length=120):
    value = normalize_text(value, max_length=max_length, field=field)
    if not _PERSON_TEXT.fullmatch(value):
        raise ValueError(f'{field} contiene caracteres no permitidos.')
    return value


def validate_email(value, *, field='El correo electrónico', max_length=100):
    value = normalize_text(value, max_length=max_length, field=field).lower()
    if not _EMAIL.fullmatch(value):
        raise ValueError(f'{field} no tiene un formato válido.')
    return value


def validate_document_id(value, *, field='La cédula', max_length=15):
    value = normalize_text(value, max_length=max_length, field=field)
    if not _DOCUMENT_ID.fullmatch(value):
        raise ValueError(f'{field} debe contener solo números o el prefijo V/E/J/P (ej: 12345678).')
    return value


def validate_choice(value, allowed, *, field='El valor'):
    if not isinstance(value, str):
        raise ValueError(f'{field} no es válido.')
    value = value.strip()
    if value not in allowed:
        raise ValueError(f'{field} no es válido.')
    return value


def validate_password(value):
    if value is None:
        value = ''
    elif not isinstance(value, str):
        raise ValueError('La contraseña debe ser texto.')
    if not 8 <= len(value) <= 128:
        raise ValueError('La contraseña debe tener entre 8 y 128 caracteres.')
    return value


def password_policy(form, field):
    try:
        validate_password(field.data)
    except ValueError as error:
        raise ValidationError(str(error))


def parse_positive_int(value, *, field='El valor'):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f'{field} debe ser un número entero válido.')
    if parsed <= 0:
        raise ValueError(f'{field} debe ser mayor que cero.')
    return parsed
