from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_mail import Message
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import threading
import traceback
import sys

from app.forms import RegistrationForm, AdminLoginForm
from app.models import User
from app.models.noticia import Noticia
from app.extensions import db, mail
from flask_login import login_user, logout_user, login_required, current_user

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
    ultimas_noticias = Noticia.query.filter_by(activo=True).order_by(Noticia.fecha_publicacion.desc()).limit(3).all()
    return render_template('index.html', ultimas_noticias=ultimas_noticias)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/noticias')
def noticias():
    page = request.args.get('page', 1, type=int)
    pagination = Noticia.query.filter_by(activo=True).order_by(Noticia.fecha_publicacion.desc()).paginate(page=page, per_page=9)
    return render_template('noticias/index.html', pagination=pagination)

@main_bp.route('/noticias/<int:id>')
def noticia_detalle(id):
    noticia = Noticia.query.filter_by(id=id, activo=True).first_or_404()
    return render_template('noticias/detalle.html', noticia=noticia)

@main_bp.route('/horarios')
def horarios():
    return render_template('horarios.html')

@main_bp.route('/wro')
def wro():
    return render_template('wro.html')

@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.rol == 'admin':
        return redirect('/admin') # Ruta por defecto de Flask-Admin
        
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.rol == 'admin':
            login_user(user)
            flash('Sesión iniciada correctamente.', 'success')
            return redirect('/admin')
        else:
            flash('Credenciales incorrectas o no tienes permisos de administrador.', 'error')
            
    return render_template('admin_login.html', form=form)

@main_bp.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('main.index'))

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
