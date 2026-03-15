from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(message='Correo electrónico inválido')])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Mantener sesión iniciada')
    submit = SubmitField('Ingresar')

class RegistrationForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres.")
    ])
    
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message="El correo es obligatorio."),
        Email(message="Introduce un correo válido."),
        Length(max=120)
    ])
    
    carrera = StringField('Carrera', validators=[
        DataRequired(message="La carrera es obligatoria."),
        Length(max=100)
    ])
    
    area_interes = SelectField('Área de Interés Principal', choices=[
        ('programacion', 'Programación (Python, C++, ROS)'),
        ('electronica', 'Electrónica y Circuitos'),
        ('mecanica', 'Diseño Mecánico y CAD'),
        ('general', 'Aprender de todo un poco')
    ], validators=[DataRequired(message="Selecciona un área de interés.")])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        Length(min=6, message="La contraseña debe tener al menos 6 caracteres.")
    ])
    
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message="Confirma tu contraseña."),
        EqualTo('password', message="Las contraseñas no coinciden.")
    ])
    
    submit = SubmitField('Registrarme')



class NoticiaForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=200)])
    contenido = StringField('Contenido HTML', validators=[DataRequired()])
    submit = SubmitField('Publicar')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar correo de recuperación')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=6, message="La contraseña debe tener al menos 6 caracteres")
    ])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message="Las contraseñas no coinciden")
    ])
    submit = SubmitField('Restablecer Contraseña')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Contraseña Actual', validators=[DataRequired(message="Tu contraseña actual es requerida.")], render_kw={"placeholder": "Ej. robotica2026"})
    new_password = PasswordField('Nueva Contraseña (Mínimo 6 caracteres)', validators=[
        DataRequired(message="Escribe una nueva contraseña segura."),
        Length(min=6, message="Debe tener al menos 6 caracteres.")
    ])
    confirm_new_password = PasswordField('Confirma Nueva Contraseña', validators=[
        DataRequired(message="Confirma la nueva contraseña."),
        EqualTo('new_password', message="Las nuevas contraseñas no coinciden.")
    ])
    submit = SubmitField('Actualizar Contraseña')
