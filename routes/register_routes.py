from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore
from firebase_admin.exceptions import FirebaseError
from utils.Validations import AuthValidations

register_bp = Blueprint('register_bp', __name__)

@register_bp.route('', methods=['POST'])
def register_user():
    try:
        # 1. Validar formato del request (común)
        if error := AuthValidations.validate_request(request):
            return error

        data = request.get_json()
        
        # 2. Validar datos específicos de registro (nueva validación)
        if error := AuthValidations.validate_registration_data(data):
            return error

        # 3. Extraer datos
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        # 4. Crear usuario en Firebase
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name,
            email_verified=False
        )

        # Resto del código de registro...
        # ... (mantener tu lógica existente de Firestore y respuesta)

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