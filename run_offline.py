import os
import sys
import traceback
import datetime
import threading
import time
import webbrowser

# Nombre del archivo de log que se creará en la misma carpeta que el ejecutable
if getattr(sys, 'frozen', False):
    LOG_FILE = os.path.join(os.path.dirname(sys.executable), 'startup_log.txt')
else:
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'startup_log.txt')

def log_debug(message):
    """Escribe un mensaje de depuración tanto en la consola como en un archivo log."""
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text = f"[{ts}] {message}"
    print(text)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except:
        pass

def robust_start():
    try:
        log_debug("🤖 INICIANDO PROCESO DE ARRANQUE (ROBUST MODE)...")
        
        # ETAPA 1: Monkey Patching de Eventlet (DEBE ser lo primero)
        log_debug("[ETAPA 1/5] Aplicando parches de Eventlet...")
        try:
            import eventlet
            eventlet.monkey_patch()
            log_debug("   ✓ Eventlet cargado y parcheado.")
        except ImportError:
            log_debug("   ❌ EXCEPCIÓN: No se encontró 'eventlet'. ¿Está instalado?")
            raise

        # ETAPA 2: Configuración de Rutas y Entorno
        log_debug("[ETAPA 2/5] Configurando rutas y base de datos...")
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
            db_path = os.path.join(os.path.dirname(sys.executable), 'app.db')
            log_debug(f"   - Ejecución: Congelado (PyInstaller)")
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(application_path, 'app.db')
            log_debug(f"   - Ejecución: Script de Python")
        
        log_debug(f"   - DB Path: {db_path}")
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        os.environ['FLASK_ENV'] = 'production'
        os.environ['FLASK_DEBUG'] = '0'
        os.environ.setdefault('SECRET_KEY', 'offline-usb-token-robotica-2026')

        # ETAPA 3: Importación de la Aplicación
        log_debug("[ETAPA 3/5] Cargando módulos de la aplicación (Flask)...")
        try:
            from app import create_app
            from app.extensions import socketio
            app = create_app()
            log_debug("   ✓ Aplicación creada exitosamente.")
        except Exception as e:
            log_debug(f"   ❌ ERROR al importar o crear la app: {str(e)}")
            raise

        # ETAPA 4: Preparación del Navegador
        def open_browser():
            time.sleep(2.0)
            log_debug("[INFO] Abriendo navegador en http://127.0.0.1:5000")
            webbrowser.open('http://127.0.0.1:5000')

        threading.Thread(target=open_browser, daemon=True).start()

        # ETAPA 5: Lanzamiento del Servidor
        log_debug("[ETAPA 5/5] Iniciando servidor SocketIO con Eventlet...")
        log_debug("="*60)
        log_debug("🤖 EL SISTEMA ESTÁ ACTIVO - NO CIERRES ESTA VENTANA")
        log_debug("="*60)
        
        socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        log_debug("\n[INFO] Apagado solicitado por el usuario.")
    except Exception as e:
        log_debug("\n" + "!"*60)
        log_debug("❌ ERROR CRÍTICO DETECTADO:")
        log_debug(traceback.format_exc())
        log_debug("!"*60)
        log_debug("\nEl error se ha guardado en 'startup_log.txt'.")
        log_debug("\nPresiona ENTER para cerrar esta ventana...")
        input()

if __name__ == '__main__':
    # Limpiamos el log anterior al iniciar
    if os.path.exists(LOG_FILE):
        try: os.remove(LOG_FILE)
        except: pass
    
    robust_start()
