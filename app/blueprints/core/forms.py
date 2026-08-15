from flask_wtf import FlaskForm
from wtforms import FileField, HiddenField, PasswordField, SelectField, StringField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional, AnyOf, NumberRange, EqualTo, InputRequired

class LoginForm(FlaskForm):
    correo = StringField(
        'Correo institucional',
        validators=[DataRequired(message='Debe ingresar su correo institucional.'), Email(message='Ingrese un correo válido.'), Length(max=120)],
    )
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(message='Debe ingresar su contraseña.'), Length(min=6, max=128)],
    )
    next = HiddenField()


class ResetRequestForm(FlaskForm):
    correo = StringField('Correo institucional', validators=[DataRequired(), Email(), Length(max=120)])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6, max=128)])
    confirm = PasswordField('Confirmar contraseña', validators=[DataRequired(), Length(min=6, max=128), EqualTo('password', message='Las contraseñas no coinciden.')])


class PublicacionForm(FlaskForm):
    # Selector de la Actividad Padre Registrada
    id_actividad = SelectField(
        'Actividad de Campo (Origen)',
        coerce=int,
        validators=[InputRequired(message='Debe seleccionar una actividad de origen.')]
    )
    nombre_divulgacion = StringField(
        'Nombre de la Divulgación',
        validators=[DataRequired(message='El nombre de la divulgación es obligatorio.'), Length(max=100)]
    )
    descripcion_divulgacion = TextAreaField(
        'Descripción de la Divulgación',
        validators=[DataRequired(message='La descripción de la divulgación es obligatoria.')]
    )
    permiso_divulgacion = StringField(
        'Permiso / Alcance',
        validators=[DataRequired(message='Debe indicar el permiso de la divulgación.'), Length(max=50)],
        default='Público'
    )
    
    tipo = SelectField(
        'Tipo de publicación',
        choices=[
            ('boletin', 'Boletín'),
            ('informe', 'Informe'),
            ('resumen', 'Resumen'),
            ('noticia', 'Noticia'),
            ('alerta', 'Alerta Climática'),
        ],
        validators=[DataRequired(), AnyOf(['boletin', 'informe', 'resumen', 'noticia', 'alerta'])],
        default='boletin',
    )
    titulo = StringField(
        'Título',
        validators=[DataRequired(message='El título es obligatorio.'), Length(max=180)],
    )
    resumen = TextAreaField(
        'Resumen',
        validators=[Optional(), Length(max=1000)],
    )
    contenido = TextAreaField(
        'Contenido',
        validators=[DataRequired(message='El contenido es obligatorio.')],
    )
    estado = SelectField(
        'Estado',
        choices=[
            ('borrador', 'Borrador'),
            ('publicado', 'Publicado'),
            ('archivado', 'Archivado'),
        ],
        validators=[DataRequired(), AnyOf(['borrador', 'publicado', 'archivado'])],
        default='borrador',
    )
    prioridad = IntegerField(
        'Prioridad de Alerta (1-10)',
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        default=1,
    )


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


class ActividadForm(FlaskForm):
    tecnico_responsable = SelectField(
        'Técnico Responsable',
        coerce=int,
        validators=[InputRequired(message='Debe seleccionar un técnico responsable.')],
    )