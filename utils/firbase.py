import os
from functools import wraps
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Definición de permisos
PERMISSIONS = {
    'administrador': {
        'listar_usuarios': True,
        'crear_usuario': True,
        'actualizar_usuario': True,
        'eliminar_usuario': True,
        'obtener_usuario': True,
        'administrar_sistema': True
    },
    'usuario': {
        'listar_usuarios': False,
        'crear_usuario': False,
        'actualizar_usuario': False,  # Solo puede actualizar su propio perfil
        'eliminar_usuario': False,
        'obtener_usuario': True,     # Solo puede obtener su propio perfil
        'administrar_sistema': False
    }
}

# Construir la ruta absoluta al JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, 'cocreando.json')

# Inicializar Firebase
cred = credentials.Certificate(cred_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()


def firebase_auth_required(permission=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'OPTIONS':
                return '', 200
            

            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "Token no proporcionado"}), 401

            id_token = auth_header.split('Bearer ')[1].strip()


            try:
                # Verifica token con Firebase
                decoded_token = auth.verify_id_token(id_token)
                uid = decoded_token['uid']
                # Obtiene usuario desde Firestore
                user_doc = db.collection('users').document(uid).get()
                if not user_doc.exists:
                    return jsonify({"error": "Usuario no registrado"}), 404

                user_data = user_doc.to_dict()
                user_role = user_data.get('rol')

                request.user = {
                    'uid': uid,
                    'email': decoded_token.get('email'),
                    **user_data
                }

                # Verificación de permisos
                if permission:
                    role_permissions = PERMISSIONS[user_role]
                    if not role_permissions.get(permission, False):
                        return jsonify({"error": f"Permiso denegado para la acción '{permission}'"}), 403

                return f(*args, **kwargs)

            except Exception as e:
                return jsonify({"error": f"Error de autenticación: {str(e)}"}), 401

        return decorated_function
    return decorator

print("Firebase inicializado correctamente.")