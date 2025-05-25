import re
from firebase_admin import auth, firestore
from firebase_admin.exceptions import FirebaseError
from datetime import datetime
from flask import jsonify

class AuthValidations:
    @staticmethod
    def validate_request(request):
        """Valida el formato básico del request (común para login y registro)"""
        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "Content-Type debe ser application/json",
                "code": "invalid_content_type"
            }), 400
        return None

    @staticmethod
    def validate_credentials(data):
        """Valida email y contraseña (para login - NO MODIFICAR)"""
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email y contraseña son requeridos",
                "code": "missing_credentials"
            }), 400
            
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return jsonify({
                "success": False,
                "message": "Formato de email inválido",
                "code": "invalid_email_format"
            }), 400
            
        return None

    @staticmethod
    def validate_registration_data(data):
        """Valida datos específicos para registro (nueva función)"""
        # Validar campos requeridos
        required_fields = ['name', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "message": f"Campos requeridos faltantes: {', '.join(missing_fields)}",
                "code": "missing_fields"
            }), 400
        
        # Validar contraseña
        password = data.get('password', '')
        errors = []
        
        if len(password) < 6:
            errors.append("La contraseña debe tener al menos 6 caracteres")
        
        if not re.search(r"[A-Z]", password):
            errors.append("Debe contener al menos una letra mayúscula")
            
        if not re.search(r"[a-z]", password):
            errors.append("Debe contener al menos una letra minúscula")
            
        if not re.search(r"[0-9]", password):
            errors.append("Debe contener al menos un número")
            
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Debe contener al menos un carácter especial")
        
        if errors:
            return jsonify({
                "success": False,
                "message": " ".join(errors),
                "code": "weak_password",
                "details": {
                    "requirements": {
                        "min_length": 6,
                        "needs_upper": True,
                        "needs_lower": True,
                        "needs_number": True,
                        "needs_special": True
                    }
                }
            }), 400
            
        return None

    @staticmethod
    def validate_user_account(user):
        """Valida el estado de la cuenta de usuario"""
        return None

    @staticmethod
    def validate_firestore_user(user_ref):
        """Valida los datos adicionales en Firestore"""
        user_doc = user_ref.get()
        if not user_doc.exists:
            return None
            
        user_data = user_doc.to_dict()
        
        if user_data.get('status') == 'banned':
            return jsonify({
                "success": False,
                "message": "Cuenta suspendida. Contacta al soporte.",
                "code": "account_banned"
            }), 403
            
        return user_data

    @staticmethod
    def update_login_metrics(user_ref):
        """Actualiza métricas de login"""
        try:
            user_ref.update({
                'last_login_attempt': datetime.utcnow(),
                'login_count': firestore.Increment(1)
            })
        except Exception as e:
            print(f"Error al actualizar métricas: {str(e)}")