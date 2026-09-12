import pytest

from app.utils.validation import parse_positive_int, validate_password, validate_person_text


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