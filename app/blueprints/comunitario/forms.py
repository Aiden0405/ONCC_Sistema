from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField
from wtforms.validators import DataRequired

class FormacionForm(FlaskForm):
    # Menú desplegable para el Nivel de Instrucción
    id_nivel = SelectField(
        'Nivel de Instrucción',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar el nivel de instrucción.')]
    )
    # Campo libre para el tema (por ahora)
    nombre_formacion = StringField(
        'Tema o Contenido de la Formación',
        validators=[DataRequired(message='El tema de la formación es obligatorio.')]
    )
    # Menú desplegable para las Instituciones
    id_institucion = SelectField(
        'Institución Educativa / Ente Sede',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar una institución.')]
    )
    # Campo de fecha (calendario)
    fecha = DateField(
        'Fecha de Ejecución',
        format='%Y-%m-%d',
        validators=[DataRequired(message='La fecha es obligatoria.')]
    )
   # Campo libre para escribir el nombre del facilitador (por ahora)
    tecnico = StringField(
        'Técnico / Facilitador',
        validators=[DataRequired(message='Debe ingresar el nombre del facilitador.')]
    )
    

class SensibilizacionForm(FlaskForm):
    # Menú desplegable para el Nivel de Instrucción
    id_nivel = SelectField(
        'Nivel de Instrucción',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar el nivel de instrucción.')]
    )
    # Campo para el nombre o campaña de la sensibilización
    nombre_sensibilizacion = StringField(
        'Nombre del Taller / Campaña de Sensibilización',
        validators=[DataRequired(message='El nombre de la sensibilización es obligatorio.')]
    )
    # Menú desplegable para las Comunidades (Territorio)
    id_comunidad = SelectField(
        'Comunidad / Territorio',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar una comunidad.')]
    )
    # Campo de fecha (calendario)
    fecha = DateField(
        'Fecha de Ejecución',
        format='%Y-%m-%d',
        validators=[DataRequired(message='La fecha es obligatoria.')]
    )
    # Campo para el técnico / facilitador
    facilitador = StringField(
        'Técnico / Facilitador',
        validators=[DataRequired(message='Debe ingresar el nombre del técnico.')]
    )

    

    
