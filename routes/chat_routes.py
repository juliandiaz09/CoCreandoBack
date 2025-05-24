from flask import Flask, request, jsonify
from firebase_admin import firestore
from flask_cors import CORS
from flask import Blueprint, request, jsonify


app = Flask(__name__)
CORS(app)

chat_bp = Blueprint('chat_bp', __name__)  # nombre e identificador

db = firestore.client()

@chat_bp.route('/chat/<chat_id>/mensajes', methods=['GET'])
def obtener_mensajes(chat_id):
    # Leer parámetros opcionales de la query
    limit = int(request.args.get('limit', 20))
    start_after = request.args.get('start_after')  # timestamp ISO8601

    mensajes_ref = db.collection("chats").document(chat_id).collection("mensajes").order_by("timestamp")

    # Si se recibe start_after, continuar desde ahí
    if start_after:
        try:
            # Buscar el documento con ese timestamp exacto
            mensajes_previos = mensajes_ref.where("timestamp", "==", start_after).limit(1).stream()
            last_doc = next(mensajes_previos, None)
            if last_doc:
                mensajes_ref = mensajes_ref.start_after(last_doc)
        except Exception as e:
            print("⚠️ Error en paginación:", e)

    # Aplicar límite
    mensajes = mensajes_ref.limit(limit).stream()

    return jsonify([m.to_dict() for m in mensajes])
