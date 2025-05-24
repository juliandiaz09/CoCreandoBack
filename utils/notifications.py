from firebase_admin import firestore
from datetime import datetime
import uuid

db = firestore.client()

def enviar_notificacion(user_id, tipo, titulo, mensaje):
    notificacion = {
        "user_id": user_id,
        "type": tipo,
        "title": titulo,
        "message": mensaje,
        "timestamp": datetime.utcnow().isoformat(),
        "read": False
    }
    doc_id = str(uuid.uuid4())
    db.collection("notifications").document(user_id)\
      .collection("user_notifications").document(doc_id).set(notificacion)
