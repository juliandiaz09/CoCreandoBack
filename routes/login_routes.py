from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
import requests
import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin.exceptions import FirebaseError
import os

app = Flask(__name__)
login_bp = Blueprint('login', __name__)
CORS(login_bp, supports_credentials=True)

#Solo se requiere una inicialización de base de datos

# Construir la ruta absoluta al JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, 'cocreando.json')

# Inicializar Firebase
cred = credentials.Certificate(cred_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🔐 Función auxiliar para autenticación por correo/contraseña
def firebase_login(email, password):
    #Pasar esto a variables de entorno
    API_KEY = "AIzaSyDnCfzF5psHLcnmbeJGrBuWpxOkUp01Lfo"  # ← Reemplaza con tu API Key de Firebase
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

@login_bp.route('', methods=['POST'])  # NO necesitas OPTIONS explícitamente si usas flask-cors
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "message": "Email y contraseña requeridos"}), 400

        # 1. Autenticación básica
        auth_data, error_info = firebase_login(email, password)

        if not auth_data:
            return jsonify({
                "success": False,
                "message": "Credenciales incorrectas",
                "details": error_info
            }), 401

        uid = auth_data["localId"]
        print("✅ UID que se usará para get_user:", uid)

        # 2. Obtener usuario desde Firebase Admin SDK
        user = auth.get_user(uid)
        print("🧠 Usuario obtenido:", user.email)

        # 4. Respuesta exitosa
        return jsonify({
            "success": True,
            "message": "Inicio de sesión exitoso",
            "token": auth_data["idToken"],  # 👈 incluye el token aquí
            "user": {
                "id": user.uid,
                "email": user.email,
                "name": user.display_name 
            }
        }), 200


    except auth.UserDisabledError:
        return jsonify({"success": False, "message": "Cuenta deshabilitada"}), 403

    except FirebaseError as e:
        return jsonify({
            "success": False,
            "message": f"Error de autenticación: {str(e)}",
            "code": "firebase_error"
        }), 500

    except Exception as e:
        import traceback
        print("🔥 TRACEBACK COMPLETO 🔥")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Error inesperado: {str(e)}",
            "code": "server_error"
        }), 500
