# socketio_app.py
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('join')
def handle_join(data):
    user_id = data.get("user_id")
    join_room(user_id)
    print(f"✅ Usuario {user_id} se unió a su sala de notificaciones")

def emitir_notificacion(user_id, notificacion):
    """Emite una notificación en tiempo real a un usuario"""
    socketio.emit('nueva_notificacion', notificacion, room=user_id)
