from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length


class MapaRiesgoForm(FlaskForm):
    id_actividad = SelectField(
        'Actividad de origen',
        coerce=int,
        validators=[InputRequired(message='Debe seleccionar una actividad válida.')],
    )
    nombre = StringField(
        'Nombre del mapa',
        validators=[DataRequired(message='El nombre del mapa es obligatorio.'), Length(max=100)],
    )
    descripcion = TextAreaField(
        'Descripción',
        validators=[DataRequired(message='La descripción del mapa es obligatoria.')],
    )
    archivo_mapa = FileField('Archivo cartográfico')