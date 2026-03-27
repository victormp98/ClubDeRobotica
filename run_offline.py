import eventlet
eventlet.monkey_patch()

import os
import sys
import webbrowser
import threading

# Configuramos la ruta de la aplicación antes de importar 'app'
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
    db_path = os.path.join(os.path.dirname(sys.executable), 'app.db')
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(application_path, 'app.db')

# FORZAR DATABASE_URL de SQLite antes de que Flask cargue la configuración
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'
os.environ.setdefault('SECRET_KEY', 'offline-usb-token-robotica-2026')

# Ahora sí, importamos la app una vez que el entorno está listo
from app import create_app
from app.extensions import socketio

app = create_app()

def open_browser():
    """Abre el navegador tras un breve segundo de espera para asegurar que el puerto esté activo."""
    import time
    time.sleep(1.5)
    print("\n[USB OFFLINE] Abriendo el navegador automáticamente...")
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    try:
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
    except Exception as e:
        print("\n" + "!"*60)
        print("❌ ERROR CRÍTICO AL INICIAR LA APLICACIÓN:")
        print(f"   {str(e)}")
        print("!"*60)
        print("\nPosibles causas:")
        print("1. El puerto 5000 ya está siendo usado por otro programa.")
        print("2. Faltan librerías en tu entorno de Python.")
        print("3. No tienes permisos para escribir en esta carpeta.")
        print("\nPresiona ENTER para cerrar esta ventana...")
        input()
