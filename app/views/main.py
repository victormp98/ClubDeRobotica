from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_mail import Message
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import os
import uuid
import threading
import traceback
import sys
import json
from werkzeug.utils import secure_filename

from app.forms import RegistrationForm, NoticiaForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm, ChangePasswordForm
from app.models import Noticia, Album, Foto, Horario, User, Columna
from app.models.page import Page
from app.models.configuracion import Configuracion
from app.models.proyecto import Proyecto
from app.models.equipo import Equipo
from app.models.tarea import Tarea
from app.models.miembro_equipo import MiembroEquipo
from app.models.checklist_item import ChecklistItem
from app.models.comentario import Comentario
from app.models.adjunto import Adjunto
from functools import wraps
from app.extensions import db, mail
from flask_login import login_user, logout_user, current_user, login_required

def miembro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para ver este contenido.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        # BA-04: Los admins siempre tienen acceso.
        if current_user.rol == 'admin':
            return f(*args, **kwargs)

        # Verificar si el usuario está aprobado
        if not current_user.aprobado:
            flash('Tu cuenta aún no ha sido aprobada por un administrador.', 'error')
            return redirect(url_for('main.index'))

        # SE-01: Verificar si pertenece a al menos un equipo activo
        if not current_user.es_miembro_equipo:
            flash('Acceso restringido: Solo los miembros vinculados a un equipo activo pueden acceder a esta zona.', 'warning')
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
    # Fetch 5 most recent active photos from PUBLIC albums (v2)
    ultimas_fotos = Foto.query.join(Album).filter(Foto.activo==True, Album.es_publico==True).order_by(Foto.fecha_subida.desc()).limit(5).all()
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
    
    # Configuración de Live Editor para la sección Torneo
    lotos_config = {}
    keys = [
        'INDEX_TORNEO_BADGE', 'INDEX_TORNEO_TITULO', 'INDEX_TORNEO_DESC', 
        'INDEX_TORNEO_LINK_TEXT', 'INDEX_TORNEO_LINK_URL', 'INDEX_TORNEO_TARGET', 'INDEX_TORNEO_TARGET_SUB'
    ]
    for key in keys:
        cfg = Configuracion.query.get(key)
        lotos_config[key] = cfg.valor if cfg else None
        
    return render_template('index.html', 
                           page=page, 
                           ultimas_noticias=noticias, 
                           ultimas_fotos=ultimas_fotos, 
                           proyectos=proyectos,
                           img_equipo=img_equipo,
                           total_miembros=total_miembros,
                           total_proyectos=total_proyectos,
                           anios_activos=anios_activos,
                           lotos_config=lotos_config)

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

@main_bp.route('/proyectos')
def proyectos():
    # Obtener todos los proyectos activos ordenados por fecha de forma descendente
    proyectos = Proyecto.query.filter_by(activo=True).order_by(Proyecto.fecha_creacion.desc()).all()
    return render_template('proyectos/index.html', proyectos=proyectos)

@main_bp.route('/noticias/<int:id>')
def noticia_detalle(id):
    noticia = Noticia.query.filter_by(id=id, activo=True).first_or_404()
    return render_template('noticias/detalle.html', noticia=noticia)

@main_bp.route('/proyectos/<int:id>')
def proyecto_detalle(id):
    proyecto = Proyecto.query.filter_by(id=id, activo=True).first_or_404()
    
    # Lógica de acceso a álbumes del proyecto (v2)
    # 1. Si el álbum es público, cualquiera lo ve.
    # 2. Si el álbum es privado del proyecto, solo miembros del equipo o admin lo ven.
    
    es_miembro_o_admin = False
    if current_user.is_authenticated:
        if current_user.rol == 'admin':
            es_miembro_o_admin = True
        elif proyecto.equipo:
            # Verificar si el usuario está en el equipo del proyecto
            es_miembro_o_admin = MiembroEquipo.query.filter_by(
                user_id=current_user.id, 
                equipo_id=proyecto.equipo_id,
                activo=True
            ).first() is not None

    if es_miembro_o_admin:
        # Ver todos los álbumes del proyecto
        albumes_proyecto = [a for a in proyecto.albumes if a.activo]
    else:
        # Ver solo álbumes públicos vinculados a este proyecto
        albumes_proyecto = [a for a in proyecto.albumes if a.activo and a.es_publico]

    return render_template('proyectos/detalle.html', proyecto=proyecto, albumes=albumes_proyecto)

@main_bp.route('/galeria')
def galeria():
    # Obtener todos los Álbumes activos y PÚBLICOS (v2), ordenados por fecha de creación desc
    albumes = Album.query.filter_by(activo=True, es_publico=True).order_by(Album.fecha_creacion.desc()).all()
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
            # SE-02: Bloquear login si no está aprobado (excepto si es admin)
            if user.rol != 'admin' and not user.aprobado:
                flash('Tu cuenta aún no ha sido aprobada por un administrador. No puedes iniciar sesión todavía.', 'warning')
                return redirect(url_for('main.login'))
                
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

@main_bp.route('/api/certamen/update', methods=['POST'])
@login_required
def update_certamen_config():
    if current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    data = request.get_json()
    if isinstance(data, dict):
        data = [data]
        
    try:
        keys_updated = []
        for item in data:
            clave = item.get('clave')
            valor = item.get('valor')
            if not clave:
                continue
                
            # Serializar arrays a JSON
            if isinstance(valor, (list, dict)):
                valor = json.dumps(valor)
                
            config = Configuracion.query.get(clave)
            if config:
                config.valor = str(valor)
            else:
                config = Configuracion(clave=clave, valor=str(valor), descripcion=f"Config dynamically created: {clave}")
                db.session.add(config)
            keys_updated.append(clave)
            
        db.session.commit()
        return jsonify({'success': True, 'keys': keys_updated})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
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
    
    # Obtener proyectos vinculados al usuario para el acceso rápido al Kanban
    proyectos_usuario = []
    if current_user.rol == 'admin':
        proyectos_usuario = Proyecto.query.filter_by(activo=True).all()
    else:
        # Encontrar proyectos donde el usuario es miembro del equipo
        proyectos_usuario = [m.equipo.proyectos[0] for m in current_user.membresias_equipo if m.activo and m.equipo.proyectos]
    
    return render_template('miembros/index.html', drive_virtual_url=drive_url, proyectos_usuario=proyectos_usuario)

@main_bp.route('/kanban/<int:proyecto_id>')
@miembro_required
def kanban_tablero(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    
    # Seguridad: Un miembro solo puede ver el tablero de su proyecto (a menos que sea admin)
    if current_user.rol != 'admin':
        es_miembro = any(m.equipo_id == proyecto.equipo_id for m in current_user.membresias_equipo if m.activo)
        if not es_miembro:
            flash('No tienes permiso para acceder al tablero de este proyecto.', 'error')
            return redirect(url_for('main.miembros_index'))
            
    tareas = Tarea.query.filter_by(proyecto_id=proyecto_id).order_by(Tarea.fecha_creacion.desc()).all()
    # Ya no es necesario agrupar manualmente, el template usa proyecto.columnas
    # Obtener usuarios del equipo para asignación
    usuarios_equipo = []
    if proyecto.equipo:
        usuarios_equipo = [{'id': m.user_id, 'nombre': m.user.nombre, 'cargo': m.cargo} for m in proyecto.equipo.miembros if m.activo and m.user]
    elif current_user.rol == 'admin':
        # Si es admin y no hay equipo, permitir asignar a cualquier admin o a sí mismo
        usuarios_equipo = [{'id': u.id, 'nombre': u.nombre, 'cargo': u.rol.capitalize()} for u in User.query.filter_by(rol='admin').all()]

    return render_template('kanban/tablero.html', 
                           proyecto=proyecto, 
                           usuarios_equipo=usuarios_equipo)

@main_bp.route('/api/kanban/update_status', methods=['POST'])
@login_required
def update_task_status():
    data = request.get_json()
    tarea_id = data.get('tarea_id')
    nueva_columna_id = data.get('columna_id')
    
    tarea = Tarea.query.get_or_404(tarea_id)
    
    # Seguridad básica
    if current_user.rol != 'admin':
        es_miembro = any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo)
        if not es_miembro:
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
            
    tarea.columna_id = nueva_columna_id
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/kanban/tarea/<int:tarea_id>', methods=['GET'])
@login_required
def get_task_details(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    
    # Seguridad básica
    if current_user.rol != 'admin':
        es_miembro = any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo)
        if not es_miembro:
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
            
    return jsonify({
        'success': True,
        'tarea': {
            'id': tarea.id,
            'titulo': tarea.titulo,
            'descripcion': tarea.descripcion,
            'columna': tarea.columna_obj.titulo,
            'columna_id': tarea.columna_id,
            'prioridad': tarea.prioridad,
            'color': tarea.color,
            'asignado': tarea.asignado.nombre if tarea.asignado else 'Sin asignar',
            'asignado_id': tarea.asignado_id,
            'fecha_creacion': tarea.fecha_creacion.strftime('%d/%m/%Y'),
            'fecha_limite': tarea.fecha_limite.strftime('%Y-%m-%d') if tarea.fecha_limite else None,
            'etiquetas': json.loads(tarea.etiquetas) if tarea.etiquetas else {},
            'checklist': [{
                'id': item.id,
                'texto': item.texto,
                'completado': item.completado
            } for item in tarea.checklist],
            'comentarios': [{
                'id': c.id,
                'autor': c.autor.nombre,
                'cuerpo': c.cuerpo,
                'fecha': c.fecha_creacion.strftime('%d/%m/%Y %H:%M')
            } for c in tarea.comentarios],
            'adjuntos': [{
                'id': a.id,
                'nombre': a.nombre_archivo,
                'ruta': url_for('static', filename=f'uploads/kanban/{a.ruta}'),
                'fecha': a.fecha_subida.strftime('%d/%m/%Y')
            } for a in tarea.adjuntos],
            'miembros': [{'id': m.user_id, 'nombre': m.user.nombre, 'cargo': m.cargo} for m in tarea.proyecto.equipo.miembros if m.activo and m.user] if tarea.proyecto.equipo else [],
            'columnas_proyecto': [{'id': c.id, 'titulo': c.titulo} for c in tarea.proyecto.columnas]
        }
    })

@main_bp.route('/api/kanban/tarea/<int:tarea_id>/color', methods=['POST'])
@login_required
def update_task_color(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    data = request.get_json()
    tarea.color = data.get('color', 'default')
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/kanban/tarea/<int:tarea_id>/checklist', methods=['POST'])
@login_required
def add_checklist_item(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    data = request.get_json()
    item = ChecklistItem(tarea_id=tarea_id, texto=data.get('texto'))
    db.session.add(item)
    db.session.commit()
    return jsonify({'success': True, 'item': {'id': item.id, 'texto': item.texto, 'completado': item.completado}})

@main_bp.route('/api/kanban/checklist/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_checklist_item(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    tarea = item.tarea
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    item.completado = not item.completado
    db.session.commit()
    return jsonify({'success': True, 'completado': item.completado})

@main_bp.route('/api/kanban/checklist/<int:item_id>', methods=['DELETE'])
@login_required
def delete_checklist_item(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    tarea = item.tarea
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/kanban/tarea/<int:tarea_id>/comentar', methods=['POST'])
@login_required
def add_comment(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    data = request.get_json()
    comentario = Comentario(tarea_id=tarea_id, autor_id=current_user.id, cuerpo=data.get('cuerpo'))
    db.session.add(comentario)
    db.session.commit()
    return jsonify({
        'success': True, 
        'comentario': {
            'autor': current_user.nombre, 
            'cuerpo': comentario.cuerpo, 
            'fecha': comentario.fecha_creacion.strftime('%d/%m/%Y %H:%M')
        }
    })

@main_bp.route('/api/kanban/tarea/<int:tarea_id>/adjuntar', methods=['POST'])
@login_required
def add_attachment(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    if 'archivo' not in request.files:
        return jsonify({'success': False, 'message': 'No hay archivo'}), 400
        
    file = request.files['archivo']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nombre vacío'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        # Generar nombre único para evitar colisiones
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'kanban')
        
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        file.save(os.path.join(upload_path, unique_filename))
        
        adjunto = Adjunto(
            tarea_id=tarea_id, 
            nombre_archivo=filename, 
            ruta=unique_filename,
            tipo_mimetype=file.mimetype
        )
        db.session.add(adjunto)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'adjunto': {
                'id': adjunto.id, 
                'nombre': adjunto.nombre_archivo, 
                'ruta': url_for('static', filename=f'uploads/kanban/{unique_filename}'),
                'fecha': adjunto.fecha_subida.strftime('%d/%m/%Y')
            }
        })

@main_bp.route('/api/kanban/tarea/<int:tarea_id>/edit', methods=['POST'])
@login_required
def edit_task_details(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    data = request.get_json()
    if 'titulo' in data and data.get('titulo').strip():
        tarea.titulo = data.get('titulo')
    if 'descripcion' in data:
        tarea.descripcion = data.get('descripcion')
    if 'asignado_id' in data:
        val = data.get('asignado_id')
        tarea.asignado_id = int(val) if val else None
        
    if 'prioridad' in data:
        tarea.prioridad = data.get('prioridad')
    if 'fecha_limite' in data:
        val = data.get('fecha_limite')
        try:
            from datetime import datetime
            tarea.fecha_limite = datetime.strptime(val, '%Y-%m-%d') if val else None
        except: pass
    if 'etiquetas' in data:
        tarea.etiquetas = json.dumps(data.get('etiquetas'))
        
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/kanban/adjunto/<int:adjunto_id>', methods=['DELETE'])
@login_required
def delete_attachment(adjunto_id):
    adjunto = Adjunto.query.get_or_404(adjunto_id)
    tarea = adjunto.tarea
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    try:
        file_path = os.path.join(current_app.root_path, 'static', 'uploads', 'kanban', adjunto.ruta)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        db.session.delete(adjunto)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/kanban/tarea/<int:tarea_id>', methods=['DELETE'])
@login_required
def delete_kanban_task(tarea_id):
    tarea = Tarea.query.get_or_404(tarea_id)
    if current_user.rol != 'admin' and not any(m.equipo_id == tarea.proyecto.equipo_id for m in current_user.membresias_equipo if m.activo):
        return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
    try:
        for adjunto in tarea.adjuntos:
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', 'kanban', adjunto.ruta)
            if os.path.exists(file_path):
                try: os.remove(file_path)
                except: pass
                
        db.session.delete(tarea)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/kanban/tarea/nueva', methods=['POST'])
@login_required
def create_task_direct(proyecto_id=None):
    # El proyecto_id viene en el body
    data = request.get_json()
    p_id = data.get('proyecto_id')
    proyecto = Proyecto.query.get_or_404(p_id)
    
    # Solo admins pueden crear tareas (según requerimiento original)
    if current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'Solo administradores pueden crear tareas'}), 403
        
    # Si no se envía columna_id, usar la primera del proyecto
    c_id = data.get('columna_id')
    if not c_id:
        primera_col = Columna.query.filter_by(proyecto_id=p_id).order_by(Columna.orden).first()
        if primera_col:
            c_id = primera_col.id
            
    nueva_tarea = Tarea(
        titulo=data.get('titulo'),
        descripcion=data.get('descripcion'),
        proyecto_id=p_id,
        columna_id=c_id,
        prioridad=data.get('prioridad', 'media'),
        color=data.get('color', 'default'),
        asignado_id=data.get('asignado_id') if data.get('asignado_id') else None
    )
    
    if data.get('fecha_limite'):
        try:
            from datetime import datetime
            nueva_tarea.fecha_limite = datetime.strptime(data.get('fecha_limite'), '%Y-%m-%d')
        except:
            pass

    db.session.add(nueva_tarea)
    
    # Guardar etiquetas si las hay
    if data.get('etiquetas'):
        import json
        nueva_tarea.etiquetas = json.dumps(data.get('etiquetas'))
    db.session.flush() # Para obtener el ID
    
    # Agregar ítems de checklist inicial si los hay
    items_iniciales = data.get('checklist', [])
    for txt in items_iniciales:
        if txt.strip():
            item = ChecklistItem(tarea_id=nueva_tarea.id, texto=txt)
            db.session.add(item)

    # Guardar comentario inicial si lo hay
    comentario_texto = data.get('comentario_inicial', '').strip()
    if comentario_texto:
        comentario = Comentario(
            tarea_id=nueva_tarea.id,
            autor_id=current_user.id,
            cuerpo=comentario_texto
        )
        db.session.add(comentario)
            
    db.session.commit()
    
    return jsonify({'success': True, 'tarea_id': nueva_tarea.id})

# --- APIs de Columnas (Kanban Dinámico) ---

@main_bp.route('/api/kanban/columna/nueva', methods=['POST'])
@login_required
def create_column():
    if current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'Solo administradores'}), 403
        
    data = request.get_json()
    proyecto_id = data.get('proyecto_id')
    titulo = data.get('titulo', 'Nueva Columna')
    
    # Obtener el último orden
    ultimo_orden = db.session.query(db.func.max(Columna.orden)).filter(Columna.proyecto_id == proyecto_id).scalar() or 0
    
    nueva_col = Columna(
        titulo=titulo,
        orden=ultimo_orden + 1,
        proyecto_id=proyecto_id
    )
    db.session.add(nueva_col)
    db.session.commit()
    
    return jsonify({'success': True, 'columna_id': nueva_col.id, 'titulo': nueva_col.titulo})

@main_bp.route('/api/kanban/columna/reordenar', methods=['POST'])
@login_required
def reorder_columns():
    if current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'Solo administradores'}), 403
        
    data = request.get_json()
    # data debe ser una lista de {id: x, orden: y}
    ordenes = data.get('ordenes', [])
    
    for item in ordenes:
        col = Columna.query.get(item['id'])
        if col:
            col.orden = item['orden']
            
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/kanban/columna/<int:columna_id>/edit', methods=['POST'])
@login_required
def edit_column_title(columna_id):
    col = Columna.query.get_or_404(columna_id)
    if current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'Solo administradores'}), 403
    data = request.get_json()
    if 'titulo' in data and data['titulo'].strip():
        col.titulo = data['titulo'].strip()
        db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/api/kanban/columna/<int:columna_id>', methods=['DELETE'])
@login_required
def delete_column(columna_id):
    if current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'Solo administradores'}), 403
        
    col = Columna.query.get_or_404(columna_id)
    proyecto_id = col.proyecto_id
    
    # Verificar si quedan más columnas
    otras_cols = Columna.query.filter(Columna.proyecto_id == proyecto_id, Columna.id != columna_id).all()
    if not otras_cols:
        return jsonify({'success': False, 'message': 'No se puede eliminar la última columna'}), 400
        
    # Mover tareas a la primera columna disponible
    primera_disponible = otras_cols[0]
    for tarea in col.tareas:
        tarea.columna_id = primera_disponible.id
        
    db.session.delete(col)
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/wro')
def wro():
    # Intenta buscar una página dinámica con slug 'wro'
    page = Page.query.filter_by(slug='wro').first()
    if page:
        return render_template('wro_dynamic.html', page=page)
    
    # Si no existe, usa la plantilla estática pero con datos dinámicos de Configuración
    configs = {}
    keys = [
        'WRO_TITULO', 'WRO_SLOGAN', 'WRO_SUBTITULO', 'WRO_HERO_DESC',
        'WRO_FECHA_COUNTDOWN', 'WRO_COUNTDOWN_LABEL', 'WRO_INFO_TITULO',
        'WRO_INFO_DESC', 'WRO_FECHAS', 'WRO_RECUADROS', 'WRO_CATEGORIAS',
        'WRO_REQUISITOS', 'WRO_PROYECTOS', 'WRO_CTA_TITULO', 'WRO_CTA_DESC',
        'WRO_SECTION_CAT_TITULO', 'WRO_SECTION_FECHAS_TITULO',
        'WRO_SECTION_REQ_TITULO', 'WRO_SECTION_PROY_TITULO',
        'WRO_SECTION_CAT_SUB', 'WRO_SECTION_FECHAS_SUB',
        'WRO_SECTION_REQ_SUB', 'WRO_SECTION_PROY_SUB',
        'WRO_HERO_BTN1_LABEL', 'WRO_HERO_BTN2_LABEL', 'WRO_CTA_BTN1_LABEL', 'WRO_CTA_BTN2_LABEL'
    ]
    for key in keys:
        cfg = Configuracion.query.get(key)
        configs[key] = cfg.valor if cfg else None

    import json
    def safe_json(val, default):
        try:
            return json.loads(val) if val else default
        except:
            return default

    fechas_json = safe_json(configs.get('WRO_FECHAS'), [])
    recuadros_json = safe_json(configs.get('WRO_RECUADROS'), [])
    categorias_json = safe_json(configs.get('WRO_CATEGORIAS'), [])
    requisitos_json = safe_json(configs.get('WRO_REQUISITOS'), [])
    proyectos_json = safe_json(configs.get('WRO_PROYECTOS'), [])

    return render_template('wro.html', 
                           config_wro=configs, lotos_config=configs, fechas_wro=fechas_json,
                           recuadros_wro=recuadros_json,
                           categorias_wro=categorias_json,
                           requisitos_wro=requisitos_json,
                           proyectos_wro=proyectos_json)

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

@main_bp.route('/api/admin/proyecto/<int:proyecto_id>/users', methods=['GET'])
@login_required
def api_proyecto_users(proyecto_id):
    if current_user.rol != 'admin':
        return jsonify({'success': False}), 403
    from app.models.proyecto import Proyecto
    from app.models.miembro_equipo import MiembroEquipo
    p = Proyecto.query.get_or_404(proyecto_id)
    if not p.equipo_id:
        return jsonify({'success': True, 'users': {}})
    
    miembros = MiembroEquipo.query.filter_by(equipo_id=p.equipo_id, activo=True).all()
    user_data = {str(m.user_id): m.cargo for m in miembros if m.user_id}
    return jsonify({'success': True, 'users': user_data})

