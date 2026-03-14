from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return '¡Hola desde la ruta de prueba del Club de Robótica!'
