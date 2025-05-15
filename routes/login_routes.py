from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from Validations import AuthValidations
import firebase_admin 
from firebase_admin import credentials, auth, firestore

app = Flask(__name__)
CORS(app)
    
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/login', methods=['POST'])
def login():
    # 1. Validar formato del request
    if error := AuthValidations.validate_request(request):
        return error

    data = request.get_json()
    
    # 2. Validar credenciales básicas
    if error := AuthValidations.validate_credentials(data):
        return error

    email = data.get('email', '').strip().lower()
    
    try:
        # 3. Buscar usuario en Firebase Auth
        user = auth.get_user_by_email(email)
        
        # 4. Validar estado de la cuenta
        if error := AuthValidations.validate_user_account(user):
            return error

        # 5. Obtener y validar datos de Firestore
        user_ref = db.collection('users').document(user.uid)
        if isinstance(user_data := AuthValidations.validate_firestore_user(user_ref), tuple):
            return user_data

        # 6. Actualizar métricas de login
        AuthValidations.update_login_metrics(user_ref)

        # 7. Preparar respuesta exitosa
        return jsonify({
            "success": True
        }), 200

    except auth.UserNotFoundError:
        return jsonify({
            "success": False,
            "message": "Credenciales incorrectas"
        }), 401
        
    except auth.UserDisabledError:
        return jsonify({
            "success": False,
            "message": "Cuenta deshabilitada"
        }), 403
        
    except FirebaseError as e:
        return jsonify({
            "success": False,
            "message": f"Error de autenticación: {str(e)}",
            "code": "firebase_error"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error inesperado: {str(e)}",
            "code": "server_error"
        }), 500

