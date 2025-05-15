import re
from firebase_admin import auth, firestore
from firebase_admin.exceptions import FirebaseError
from datetime import datetime
from flask import jsonify

class AuthValidations:
    @staticmethod
    def validate_request(request):
        """Valida el formato básico del request"""
        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "Content-Type debe ser application/json"
            }), 400
        return None

    @staticmethod
    def validate_credentials(data):
        """Valida email y contraseña"""
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email y contraseña son requeridos"
            }), 400
            
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return jsonify({
                "success": False,
                "message": "Formato de email inválido"
            }), 400
            
        return None

    @staticmethod
    def validate_user_account(user):
        """Valida el estado de la cuenta de usuario"""
        if not user.email_verified:
            return jsonify({
                "success": False,
                "message": "Por favor verifica tu email antes de iniciar sesión",
                "code": "email_not_verified"
            }), 403
        return None

    @staticmethod
    def validate_firestore_user(user_ref):
        """Valida los datos adicionales en Firestore"""
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({
                "success": False,
                "message": "Perfil de usuario no encontrado"
            }), 404

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
        user_ref.update({
            'last_login_attempt': datetime.utcnow(),
            'login_count': firestore.Increment(1)
        })