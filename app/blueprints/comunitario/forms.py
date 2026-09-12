from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField
from wtforms.validators import DataRequired


class FormacionForm(FlaskForm):
    fecha_actividad = DateField(
        'Fecha de ejecución',
        format='%Y-%m-%d',
        validators=[DataRequired(message='La fecha es obligatoria.')],
    )
    id_comunidad = SelectField(
        'Comunidad',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar una comunidad.')],
    )
    id_nivel = SelectField(
        'Nivel de instrucción',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar el nivel de instrucción.')],
    )
    id_institucion = SelectField(
        'Institución / Sede',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar una institución.')],
    )
    nombre_formacion = StringField(
        'Tema de la formación',
        validators=[DataRequired(message='El tema de la formación es obligatorio.')],
    )
    tecnico = StringField(
        'Técnico / Facilitador',
        validators=[DataRequired(message='Debe ingresar el nombre del facilitador.')],
    )


class SensibilizacionForm(FlaskForm):
    fecha_actividad = DateField(
        'Fecha de ejecución',
        format='%Y-%m-%d',
        validators=[DataRequired(message='La fecha es obligatoria.')],
    )
    id_comunidad = SelectField(
        'Comunidad / Territorio',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar una comunidad.')],
    )
    id_nivel = SelectField(
        'Nivel de instrucción',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar el nivel de instrucción.')],
    )
    nombre_sensibilizacion = StringField(
        'Nombre del taller / campaña de sensibilización',
        validators=[DataRequired(message='El nombre de la sensibilización es obligatorio.')],
    )
    facilitador = StringField(
        'Técnico / Facilitador',
        validators=[DataRequired(message='Debe ingresar el nombre del técnico.')],
    )