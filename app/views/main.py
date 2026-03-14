from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from app.forms import RegistrationForm
from app.models import User
from app.extensions import db

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
            flash('¡Registro exitoso! Tu cuenta está pendiente de aprobación por un administrador.', 'success')
            return redirect(url_for('main.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Ya existe una cuenta con este correo electrónico.', 'error')
            
    return render_template('registro.html', form=form)
