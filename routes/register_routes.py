from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore
from firebase_admin.exceptions import FirebaseError
from utils.Validations import AuthValidations

# Crear Blueprint para las rutas de registro
register_bp = Blueprint('register_bp', __name__)

@register_bp.route('', methods=['POST'])
def register_user():

    try:
        # 1. Validar formato del request
        if error := AuthValidations.validate_request(request):
            return error

        data = request.get_json()
        
        # 3. Extraer y limpiar datos
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        # 4. Crear usuario en Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name,
            email_verified=False
        )

        # Generar token personalizado
        custom_token = auth.create_custom_token(user.uid)

        # 5. Crear registro en Firestore
        user_ref = firestore.client().collection('users').document(user.uid)
        user_data = {
            'uid': user.uid,
            'name': name,
            'email': email,
            'rol': 'usuario',
            'status': 'active',
            'email_verified': False,
            'login_count': 0,
            'last_login': None
        }
        user_ref.set(user_data)

        # 6. Preparar respuesta exitosa
        response_data = {
            "success": True,
            "message": "Registro exitoso",
            "user": {
                "uid": user.uid,
                "name": name,
                "email": email,
                "rol": "usuario",  # Asegurar que el rol se envía
                "status": "active"
            },
            "token": custom_token.decode('utf-8')  # Enviar token generado
        }

        return jsonify(response_data), 201

    except auth.EmailAlreadyExistsError:
        return jsonify({
            "success": False,
            "message": "El correo electrónico ya está registrado",
            "code": "email_already_exists"
        }), 409

    except auth.WeakPasswordError:
        return jsonify({
            "success": False,
            "message": "La contraseña debe tener al menos 6 caracteres",
            "code": "weak_password"
        }), 400

    except FirebaseError as e:
        return jsonify({
            "success": False,
            "message": "Error en el servidor de autenticación",
            "code": "firebase_error",
            "details": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error inesperado en el servidor",
            "code": "server_error",
            "details": str(e)
        }), 500