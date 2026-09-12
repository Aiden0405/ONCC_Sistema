import re

from wtforms.validators import ValidationError


_PERSON_TEXT = re.compile(r"^[\w\s.,'()/-]+$", re.UNICODE)


def normalize_text(value, *, min_length=1, max_length=255, field='Este campo'):
    value = (value or '').strip()
    if not min_length <= len(value) <= max_length:
        raise ValueError(f'{field} debe tener entre {min_length} y {max_length} caracteres.')
    return value


def validate_person_text(value, *, field='Este campo', max_length=120):
    value = normalize_text(value, max_length=max_length, field=field)
    if not _PERSON_TEXT.fullmatch(value):
        raise ValueError(f'{field} contiene caracteres no permitidos.')
    return value


def validate_password(value):
    value = value or ''
    if not 1 <= len(value) <= 128:
        raise ValueError('La contraseña debe tener entre 1 y 128 caracteres.')
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