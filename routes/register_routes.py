from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore
from firebase_admin.exceptions import FirebaseError
from utils.Validations import AuthValidations

register_bp = Blueprint('register_bp', __name__)

@register_bp.route('', methods=['POST'])
def register_user():
    try:
        if error := AuthValidations.validate_request(request):
            return error

        data = request.get_json()
        if error := AuthValidations.validate_registration_data(data):
            return error

        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()

        # Verificar si el correo ya existe en Firestore (opcional)
        db = firestore.client()
        existing = db.collection('users').where('email', '==', email).get()
        if existing:
            return jsonify({
                "success": False,
                "message": "El correo ya está registrado"
            }), 409

        return jsonify({
            "success": True,
            "message": "Validación exitosa, continúa en el cliente"
        }), 200

    except auth.EmailAlreadyExistsError:
        return jsonify({
            "success": False,
            "message": "El correo electrónico ya está registrado",
            "code": "email_already_exists"
        }), 409
    except Exception as e:
        # Manejo de otros errores
        return jsonify({
            "success": False,
            "message": "Error en el registro",
            "code": "registration_error",
            "details": str(e)
        }), 500