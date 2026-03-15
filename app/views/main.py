from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_mail import Message
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import threading
import traceback
import sys

from app.forms import RegistrationForm, NoticiaForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm, ChangePasswordForm
from app.models import Noticia, Album, Foto, Horario, User
from app.models.page import Page
from app.models.configuracion import Configuracion
from app.models.proyecto import Proyecto
from app.models.equipo import Equipo
from app.models.miembro_equipo import MiembroEquipo
from functools import wraps
from app.extensions import db, mail
from flask_login import login_user, logout_user, current_user, login_required

def miembro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para ver este contenido.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        # BA-04: Los admins siempre tienen acceso aunque aprobado=False.
        # Esto es intencional: permite au admin recién creado entrar sin aprobarse a sí mismo.
        if current_user.rol != 'admin' and not current_user.aprobado:
            flash('Tu cuenta aún no ha sido aprobada por un administrador.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

main_bp = Blueprint('main', __name__)  # AL-01: única instancia — la segunda (antes en línea 79) fue eliminada

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print(f"[MAIL_SUCCESS] Correo enviado a {msg.recipients}")
        except Exception as e:
            # Capturamos el error silenciosamente (para que no afecte el registro)
            print(f"\n[ATENCIÓN DEV] No se pudo enviar el correo a {msg.recipients} porque el servidor SMTP no está configurado.")
            print(f"[LINK A TUS CORREOS LOCALES]: \n{msg.body}\n")
            # print(traceback.format_exc(), file=sys.stderr)

def enviar_notificacion_admin(user, app):
    """Envia correo al admin en un hilo separado para no bloquear la request."""
    # ME-02: Correo del admin leído de config (configurable via .env ADMIN_EMAIL)
    admin_email = app.config.get('ADMIN_EMAIL', 'admin@clubrobotica.unach.mx')
    msg = Message(
        subject=f"[Club Robótica] Nuevo registro: {user.nombre}",
        sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@clubrobotica.com'),
        recipients=[admin_email]
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

def send_password_reset_email(user, app):
    """Envia correo con el token de recuperacion en un hilo separado."""
    token = user.get_reset_password_token()
    msg = Message(
        subject="[Club Robótica] Restablecer tu contraseña",
        sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@clubrobotica.com'),
        recipients=[user.email]
    )
    msg.body = render_template('email/reset_password.txt', user=user, token=token)
    msg.html = render_template('email/reset_password.html', user=user, token=token)
    
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.start()

# AL-01: Blueprint duplicado eliminado. El Blueprint se declara una sola vez arriba (línea 31).

@main_bp.route('/')
def index():
    page = Page.query.filter_by(slug='about').first()
    noticias = Noticia.query.filter_by(activo=True).order_by(Noticia.fecha_publicacion.desc()).limit(3).all()
    # Fetch 5 most recent active photos
    ultimas_fotos = Foto.query.filter_by(activo=True).order_by(Foto.fecha_subida.desc()).limit(5).all()
    # Fetch active projects
    proyectos = Proyecto.query.filter_by(activo=True).order_by(Proyecto.fecha_creacion.desc()).limit(3).all()
    
    # Fetch home team image config
    img_equipo_config = Configuracion.query.get('IMAGEN_EQUIPO_HOME')
    img_equipo = img_equipo_config.valor if img_equipo_config else None
    
    # --- Estadísticas Dinámicas ---
    total_miembros = User.query.filter_by(aprobado=True, activo=True).count()
    total_proyectos = Proyecto.query.filter_by(activo=True).count()
    
    from datetime import datetime
    # Base: 2026 (Año de inauguración oficial)
    anios_activos = datetime.now().year - 2026
    if anios_activos < 1: 
        # Si es el primer año, pasamos un valor especial o simplemente 2026
        anios_activos = "2026"
    else:
        # Si pasan los años, mostrará "1", "2", etc.
        anios_activos = str(anios_activos + 1)
    
    return render_template('index.html', 
                           page=page, 
                           ultimas_noticias=noticias, 
                           ultimas_fotos=ultimas_fotos, 
                           proyectos=proyectos,
                           img_equipo=img_equipo,
                           total_miembros=total_miembros,
                           total_proyectos=total_proyectos,
                           anios_activos=anios_activos)


@main_bp.route('/about')
def about():
    page = Page.query.filter_by(slug='about').first_or_404()
    # Obtener equipos activos para agrupar a los miembros
    equipos = Equipo.query.filter_by(activo=True).all()
    return render_template('about.html', page=page, equipos=equipos)

@main_bp.route('/noticias')
def noticias():
    page = request.args.get('page', 1, type=int)
    pagination = Noticia.query.filter_by(activo=True).order_by(Noticia.fecha_publicacion.desc()).paginate(page=page, per_page=9)
    return render_template('noticias/index.html', pagination=pagination)

@main_bp.route('/noticias/<int:id>')
def noticia_detalle(id):
    noticia = Noticia.query.filter_by(id=id, activo=True).first_or_404()
    return render_template('noticias/detalle.html', noticia=noticia)

@main_bp.route('/galeria')
def galeria():
    # Obtener todos los Álbumes activos, ordenados por fecha de creación desc
    albumes = Album.query.filter_by(activo=True).order_by(Album.fecha_creacion.desc()).all()
    return render_template('galeria/index.html', albumes=albumes)

@main_bp.route('/galeria/<int:id>')
def galeria_album(id):
    album = Album.query.filter_by(id=id, activo=True).first_or_404()
    # Las fotos se pueden iterar desde `album.fotos` en Jinja, pero validaremos solo foto.activo
    fotos_activas = [foto for foto in album.fotos if foto.activo]
    return render_template('galeria/album.html', album=album, fotos=fotos_activas)

@main_bp.route('/horarios')
def horarios():
    horarios_activos = Horario.query.filter_by(activo=True).all()
    
    # Custom sort by day of the week
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Agrupar por día
    horarios_por_dia = {}
    for dia in dias_orden:
        # Filtrar horarios para este día y ordenarlos por hora de inicio
        slots = [h for h in horarios_activos if h.dia_semana == dia]
        if slots:
            slots.sort(key=lambda x: x.hora_inicio)
            horarios_por_dia[dia] = slots
            
    # Calcular resumen para la tabla
    resumen_semanal = []
    total_general = 0
    for dia, slots in horarios_por_dia.items():
        horas_dia = 0
        for s in slots:
            if s.hora_inicio and s.hora_fin:
                # Cálculo simple de duración en horas
                duracion = (s.hora_fin.hour + s.hora_fin.minute/60) - (s.hora_inicio.hour + s.hora_inicio.minute/60)
                horas_dia += max(0, duracion)
        
        resumen_semanal.append({
            'dia': dia,
            'slots': slots,
            'total_horas': round(horas_dia, 1)
        })
        total_general += horas_dia

    return render_template('horarios.html', 
                           horarios_por_dia=horarios_por_dia, 
                           resumen_semanal=resumen_semanal,
                           total_general=round(total_general, 1))

@main_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Validar que la contraseña actual sea correcta
        if not current_user.check_password(form.old_password.data):
            flash('Error: La contraseña actual es incorrecta. Si te acaban de aprobar, posiblemente sea la contraseña por defecto (robotica2026).', 'error')
            return redirect(url_for('main.perfil'))
        
        # Validar que la nueva contraseña no sea igual a la vieja
        if form.old_password.data == form.new_password.data:
            flash('Tu nueva contraseña no puede ser exactamente igual a la actual.', 'warning')
            return redirect(url_for('main.perfil'))
            
        # Actualizar contraseña
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        # Opcional: Cerrar sesión después de cambiar la clave por seguridad
        logout_user()
        flash('¡Tu contraseña ha sido actualizada con éxito! Por favor inicia sesión con tu nueva clave.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('perfil.html', form=form)

@main_bp.route('/terminos')
def terminos():
    page = Page.query.filter_by(slug='terminos').first_or_404()
    return render_template('terminos.html', page=page)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            # Seguridad: garantizar que la página de redirección sea local
            from urllib.parse import urlsplit
            if not next_page or urlsplit(next_page).netloc != '':
                if current_user.rol == 'admin':
                    next_page = url_for('admin.index')
                else:
                    next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html', form=form)

@main_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user, current_app._get_current_object())
        # Siempre mostramos el mismo mensaje para no revelar si un email existe o no
        flash('Verifica tu correo electrónico para las instrucciones de cómo restablecer tu contraseña', 'info')
        return redirect(url_for('main.login'))
    return render_template('reset_password_request.html', form=form)

@main_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        flash('El enlace para restablecer la contraseña es inválido o ha expirado.', 'error')
        return redirect(url_for('main.reset_password_request'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Tu contraseña ha sido restablecida exitosamente.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('reset_password.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/miembros')
@miembro_required
def miembros_index():
    drive_url_config = Configuracion.query.get('drive_virtual_url')
    drive_url = drive_url_config.valor if drive_url_config else '#'
    return render_template('miembros/index.html', drive_virtual_url=drive_url)

@main_bp.route('/wro')
def wro():
    return render_template('wro.html')

@main_bp.route('/admin/logout')
@login_required
def admin_logout():
    # Redirigir al logout principal para unificar flujos
    return redirect(url_for('main.logout'))

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
