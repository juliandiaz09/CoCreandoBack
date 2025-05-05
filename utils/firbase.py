import os
import firebase_admin
from firebase_admin import credentials, firestore

import firebase_admin
from firebase_admin import credentials

# Construir la ruta absoluta al JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, 'cocreando.json')

# Inicializar Firebase
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

print("Firebase inicializado correctamente.")
