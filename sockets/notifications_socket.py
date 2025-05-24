# socketio_app.py
from flask_socketio import SocketIO, emit, join_room
from firebase_admin import firestore
import uuid
from datetime import datetime
from models.notification import Notification

socketio = SocketIO(cors_allowed_origins="*")
db = firestore.client()

@socketio.on('join')
def handle_join(data):
    user_id = data.get("user_id")
    join_room(user_id)
    print(f"✅ Usuario {user_id} se unió a su sala de notificaciones")

def emitir_notificacion(user_id, tipo, titulo, mensaje):
    """Guarda una notificación en Firestore y la emite al cliente en tiempo real"""
    noti = Notification(user_id, tipo, titulo, mensaje)
    db.collection("notifications").document(user_id)\
    .collection("user_notifications").document(noti.id).set(noti.to_dict())

    socketio.emit('nueva_notificacion', noti.to_dict(), room=user_id)

@socketio.on('obtener_notificaciones')
def obtener_notificaciones(data):
    user_id = data.get("user_id")
    docs = db.collection("notifications").document(user_id)\
        .collection("user_notifications").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    
    notificaciones = []
    for doc in docs:
        notificacion = doc.to_dict()
        notificacion["id"] = doc.id
        notificaciones.append(notificacion)

    emit('lista_notificaciones', notificaciones)

@socketio.on('marcar_como_leidas')
def marcar_como_leidas(data):
    user_id = data.get("user_id")
    notif_ref = db.collection("notifications").document(user_id).collection("user_notifications")

    docs = notif_ref.where("read", "==", False).stream()
    updated = []
    for doc in docs:
        notif_ref.document(doc.id).update({"read": True})
        n = doc.to_dict()
        n["id"] = doc.id
        n["read"] = True
        updated.append(n)

    emit('notificaciones_actualizadas', updated, room=user_id)

