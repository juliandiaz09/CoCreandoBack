from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

# Importa y registra eventos
from sockets import notifications_socket, chat_socket  # <-- registra handlers

def init_socketio(app):
    socketio.init_app(app)