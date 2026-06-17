from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, SelectField, StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, AnyOf, NumberRange

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
    confirm = PasswordField('Confirmar contraseña', validators=[DataRequired(), Length(min=6, max=128)])


class PublicacionForm(FlaskForm):
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

    # Campos transaccionales vinculados
    id_divulgacion = SelectField(
        'Monitoreo / Actividad de Origen',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un monitoreo de origen.')]
    )
    prioridad = IntegerField(
        'Prioridad de Alerta (1-10)',
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        default=1
    )