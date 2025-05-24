from datetime import datetime
import uuid

class Notificacion:
    def __init__(self, user_id, tipo, titulo, mensaje):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.type = tipo
        self.title = titulo
        self.message = mensaje
        self.timestamp = datetime.utcnow().isoformat()
        self.read = False

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp,
            "read": self.read
        }
