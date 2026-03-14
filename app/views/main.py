from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_mail import Message
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import threading
import traceback
import sys

from app.forms import RegistrationForm
from app.models import User
from app.extensions import db, mail

main_bp = Blueprint('main', __name__)

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print(f"[MAIL_SUCCESS] Correo enviado a {msg.recipients}")
        except Exception as e:
            # Capturamos el error silenciosamente (para que no afecte el registro)
            print(f"[MAIL_ERROR] No se pudo enviar el correo de registro. Esto es esperado si las credenciales son dummy.")
            print(traceback.format_exc(), file=sys.stderr)

def enviar_notificacion_admin(user, app):
    """Envia correo al admin en un hilo separado para no bloquear la request."""
    msg = Message(
        subject=f"[Club Robótica] Nuevo registro: {user.nombre}",
        sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@clubrobotica.com'),
        recipients=['admin@clubrobotica.unach.mx'] # Reemplazar con correo real admin futuro
    )
    msg.body = f'''
    Nuevo alumno registrado y pendiente de aprobación:
    
    Nombre: {user.nombre}
    Email: {user.email}
    Carrera: {user.carrera}
    Área de Interés: {user.area_interes}
    
    Por favor inicia sesión en el panel de administrador para aprobar o rechazar esta solicitud.
    '''
    
    # Lanzar hilo en background
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.start()

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/horarios')
def horarios():
    return render_template('horarios.html')

@main_bp.route('/wro')
def wro():
    return render_template('wro.html')

@main_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            nombre=form.nombre.data,
            email=form.email.data,
            carrera=form.carrera.data,
            area_interes=form.area_interes.data,
            rol='miembro',
            aprobado=False
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Enviar notificación falsa/dummy en hilo en background enviando el app contexto real
            enviar_notificacion_admin(user, current_app._get_current_object())
            
            flash('¡Registro exitoso! Tu cuenta está pendiente de aprobación por un administrador.', 'success')
            return redirect(url_for('main.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Ya existe una cuenta con este correo electrónico.', 'error')
            
    return render_template('registro.html', form=form)
