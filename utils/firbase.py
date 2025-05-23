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
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# cred_path = os.path.join(BASE_DIR, '/etc/secrets/cocreando.json')

# Inicializar Firebase
cred = credentials.Certificate("/etc/secrets/cocreando.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()


def firebase_auth_required(permission=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "Token no proporcionado"}), 401
            
            id_token = auth_header.split('Bearer ')[1]
            
            try:
                # Verificar token con Firebase
                decoded_token = auth.verify_id_token(id_token)
                uid = decoded_token['uid']
                
                # Obtener usuario de Firestore
                user_doc = db.collection('users').document(uid).get()  # Corregido aquí
                if not user_doc.exists:
                    return jsonify({"error": "Usuario no registrado"}), 404
                
                user_data = user_doc.to_dict()
                user_role = user_data.get('rol', 'usuario')  # Rol por defecto: usuario
                
                # Verificar permiso si se especificó
                if permission:
                    # Permisos especiales para usuarios normales
                    if permission == 'actualizar_usuario' and 'id' in kwargs and kwargs['id'] == uid:
                        return f(*args, **kwargs)
                    if permission == 'obtener_usuario' and 'id' in kwargs and kwargs['id'] == uid:
                        return f(*args, **kwargs)
                    
                    # Verificar permiso según rol
                    if not PERMISSIONS.get(user_role, {}).get(permission, False):
                        return jsonify({"error": "Acceso no autorizado"}), 403
                
                # Agregar información del usuario al contexto
                request.user = {
                    'uid': uid,
                    'rol': user_role,
                    'email': decoded_token.get('email'),
                    **user_data
                }
                
                return f(*args, **kwargs)
            
            except Exception as e:
                return jsonify({"error": f"Error de autenticación: {str(e)}"}), 401
                
        return decorated_function
    return decorator

print("Firebase inicializado correctamente.")