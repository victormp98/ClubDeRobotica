import eventlet
eventlet.monkey_patch()

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    try:
        # El servidor asíncrono eventlet toma el control
        socketio.run(app, debug=True, port=5000)
    except Exception as e:
        print(f"\n❌ ERROR EN DESARROLLO: {str(e)}")
        input("\nPresiona ENTER para cerrar...")
