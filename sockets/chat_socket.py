from socketio_app import socketio
from flask_socketio import emit, join_room
from firebase_admin import firestore
from datetime import datetime
from utils.chat import obtener_chat_id, obtener_chat_grupal_id
import uuid

db = firestore.client()


@socketio.on('join_chat')
def handle_join_chat(data):
    # Si es chat privado
    chat_id = obtener_chat_id(data['user1_id'], data['user2_id'])
    join_room(chat_id)
    print(f"🧑‍🤝‍🧑 Usuario se unió a {chat_id}")

@socketio.on('send_message')
def handle_send_message(data):
    chat_id = data.get("chat_id")
    sender_id = data.get("sender_id")
    message = data.get("message")
    timestamp = datetime.utcnow().isoformat()

    # Guardar mensaje en Firestore
    mensaje_id = str(uuid.uuid4())
    db.collection("chats").document(chat_id).collection("mensajes").document(mensaje_id).set({
        "sender_id": sender_id,
        "message": message,
        "timestamp": timestamp
    })

    # Emitir a todos los de la sala
    emit('receive_message', {
        "sender_id": sender_id,
        "message": message,
        "timestamp": timestamp
    }, room=chat_id)
