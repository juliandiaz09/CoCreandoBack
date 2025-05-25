from datetime import datetime
from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
import requests
import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin.exceptions import FirebaseError
import os
from utils.Validations import AuthValidations

app = Flask(__name__)
login_bp = Blueprint('login', __name__)
CORS(login_bp, supports_credentials=True)

# Configuración de Firebase
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, 'cocreando.json')
cred = credentials.Certificate(cred_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def firebase_login(email, password):
    API_KEY = "AIzaSyDnCfzF5psHLcnmbeJGrBuWpxOkUp01Lfo"
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json(), None
    else:
        return None, response.json()

@login_bp.route('', methods=['POST'])
def login():
    try:
        # 1. Validar formato del request
        validation_result = AuthValidations.validate_request(request)
        if validation_result:
            return validation_result

        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password')

        # 2. Validar credenciales básicas (incluye validación de email)
        validation_result = AuthValidations.validate_credentials(data)
        if validation_result:
            return validation_result

        # 3. Verificar si el usuario existe en Firebase Auth
        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            return jsonify({
                "success": False,
                "message": "Tu usuario no existe, por favor regístrate",
                "code": "user_not_found"
            }), 404

        # 4. Autenticar con Firebase
        auth_data, error_info = firebase_login(email, password)
        if not auth_data:
            return jsonify({
                "success": False,
                "message": "Usuario o contraseña incorrectos",
                "code": "wrong_credentials"
            }), 401

        # 5. Verificar/crear perfil en Firestore
        uid = auth_data["localId"]
        user_ref = db.collection('users').document(uid)
        
        # 6. Respuesta exitosa
        return jsonify({
            "success": True,
            "message": "Inicio de sesión exitoso",
            "token": auth_data["idToken"],
            "user": {
                "id": uid,
                "email": email,
                "name": user.display_name or email.split('@')[0]
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error inesperado: {str(e)}",
            "code": "server_error"
        }), 500