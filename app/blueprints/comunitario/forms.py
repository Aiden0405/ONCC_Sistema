from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField
from wtforms.validators import DataRequired, Length, ValidationError


class RegistroComunitarioForm(FlaskForm):
    # 🌟 CAMPO AÑADIDO: Vínculo con la actividad de campo padre
    id_actividad = SelectField(
        'Actividad Origen', 
        coerce=int,
        validators=[DataRequired(message='Debe vincular a una actividad de campo existente.')]
    )
    
    tipo_actividad = SelectField(
        'Tipo de registro',
        choices=[('FORMACION', 'Formación'), ('SENSIBILIZACION', 'Sensibilización')],
        validators=[DataRequired(message='Debe seleccionar el tipo de registro.')],
        default='FORMACION',
    )
    tipo_destino = SelectField(
        'Destino',
        choices=[('COMUNIDAD', 'Comunidad'), ('INSTITUCION', 'Institución')],
        validators=[DataRequired(message='Debe seleccionar el destino.')],
        default='COMUNIDAD',
    )
    
    nombre = StringField(
        'Tema / campaña', 
        validators=[DataRequired(message='Debe indicar el tema o campaña.'), Length(max=180)],
    )
    tecnico = SelectField(
        'Técnico / Facilitador', 
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar el técnico o facilitador.')],
    )
    id_institucion = SelectField('Institución / Sede', coerce=int)

    def validate_id_institucion(self, field):
        if self.tipo_destino.data == 'INSTITUCION' and not field.data:
            raise ValidationError('Debe seleccionar una institución para ese destino.')


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
    tecnico = SelectField(
        'Técnico / Facilitador',
        validators=[DataRequired(message='Debe ingresar el nombre del facilitador.'), Length(max=120)],
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
    facilitador = SelectField(
        'Técnico / Facilitador',
        validators=[DataRequired(message='Debe ingresar el nombre del técnico.'), Length(max=120)],
    )