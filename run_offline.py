import eventlet
eventlet.monkey_patch()

import os
import sys
import webbrowser
import threading
from app import create_app
from app.extensions import socketio

# Truco para asegurar que la app sepa dónde está al estar congelada por PyInstaller
if getattr(sys, 'frozen', False):
    # Si corre como ejecutable de PyInstaller
    application_path = sys._MEIPASS
    # Forzar la BD local en la carpeta donde está el .exe original (no en el temporal _MEIPASS)
    # pero como usaremos ONE-DIR, la carpeta raíz es sys.executable directory.
    db_path = os.path.join(os.path.dirname(sys.executable), 'app.db')
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Forzar el modo Offline sin necesidad de archivo .env
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'
os.environ.setdefault('SECRET_KEY', 'offline-usb-token-robotica-2026')

app = create_app()

def open_browser():
    """Abre el navegador tras un breve segundo de espera para asegurar que el puerto esté activo."""
    import time
    time.sleep(1.5)
    print("\n[USB OFFLINE] Abriendo el navegador automáticamente...")
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("="*60)
    print("🤖 INICIANDO SERVIDOR OFFLINE - CLUB DE ROBÓTICA")
    print("="*60)
    print("No cierres esta ventana negra mientras usas el sistema.")
    print("Si la ventana se cierra, el sistema se apaga.")
    print("="*60)
    
    # Inicia el hilo que abrirá el navegador
    threading.Thread(target=open_browser, daemon=True).start()
    
    # El servidor asíncrono eventlet toma el control
    socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False)
