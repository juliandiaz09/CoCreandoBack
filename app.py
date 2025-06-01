
from flask import Flask
from flask_cors import CORS
from routes.login_routes import login_bp
from routes.register_routes import register_bp
from routes.project_routes import project_bp, obtener_datos_proyecto
from routes.payment_routes import payment_bp
from routes.user_routes import user_bp
from flask import Flask, request, jsonify
from flask_cors import CORS
from sockets.notifications_socket import init_socketio, socketio
import os

app = Flask(__name__)

# CORS global (solo para pruebas locales, en producción usa origen específico)
CORS(app, supports_credentials=True)


# Registro del blueprint en /login
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(register_bp, url_prefix='/registro')
app.register_blueprint(project_bp, url_prefix='/proyecto')
app.register_blueprint(payment_bp, url_prefix='/pasarela')
app.register_blueprint(user_bp, url_prefix='/usuario')

# 👇 Inicializa socketio con Flask
init_socketio(app)

@app.route('/conexiones-activas')
def conexiones_activas():
    try:
        # Accede directamente al manager de Socket.IO
        manager = socketio.server.manager
        return jsonify({
            "total_connections": len(manager.rooms.get('/', {})),
            "namespaces": list(manager.rooms.keys()),
            "room_details": {
                room: len(sids) for room, sids in manager.rooms.items() if room != '/'
            },
            "debug_info": {
                "engineio_version": getattr(socketio.server.eio, "engineio_version", None),
                "active_sockets": list(manager.rooms.get('/', {}).keys())
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecuta con socketio.run para permitir WebSocket
if __name__ == '__main__':
    # Para Render (con advertencia desactivada)
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5000)),
        debug=False,
        allow_unsafe_werkzeug=True  # Desactiva la protección
    )