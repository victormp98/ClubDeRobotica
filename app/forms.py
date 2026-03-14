from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

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

class AdminLoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')
