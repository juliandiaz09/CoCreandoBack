from flask import request, jsonify
from firebase_admin import auth
from functools import wraps

def firebase_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Token faltante"}), 401

        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            return jsonify({"error": "Formato inválido de autorización"}), 401

        token = parts[1]
        try:
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token
        except Exception as e:
            return jsonify({"error": f"Token inválido: {str(e)}"}), 401

        return f(*args, **kwargs)
    return decorated_function
