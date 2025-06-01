import os
from functools import wraps
from flask import Flask, g, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth


# Definición de permisos
PERMISSIONS = {
    'admin': {
        'listar_usuarios': True,
        'crear_usuario': True,
        'actualizar_usuario': True,
        'eliminar_usuario': True,
        'obtener_usuario': True,
        'administrar_sistema': True,
        'eliminar_Proyecto': True,
        'actualizar_proyecto': True
    },
    'usuario': {
        'listar_usuarios': False,
        'crear_usuario': False,
        'actualizar_usuario': 'self',  # Solo puede actualizar su propio perfil
        'eliminar_usuario': 'self',    # Solo puede eliminar su propia cuenta
        'obtener_usuario': 'self',
        'actualizar_usuario': False,  # Solo puede actualizar su propio perfil
        'eliminar_usuario': False,
        'obtener_usuario': True,     # Solo puede obtener su propio perfil
        'administrar_sistema': False,
        'eliminar_Proyecto': True,
        'actualizar_proyecto': True
    }
}

# Inicializar Firebase
cred = credentials.Certificate("/etc/secrets/cocreando.json")
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
                user_role = user_data.get('role', 'usuario')
                
                if user_role not in PERMISSIONS:
                    return jsonify({"error": "Rol de usuario no válido"}), 403

                request.user = {
                    'uid': uid,
                    'email': decoded_token.get('email'),
                    **user_data
                }

                # Verificación de permisos mejorada
                if permission:
                    permission_value = PERMISSIONS[user_role].get(permission, False)
                
                    # Lógica para permisos especiales 'self'
                    if permission_value == 'self':
                        # Obtener el ID del recurso objetivo (ej: user_id en la URL)
                        target_id = kwargs.get('id') or request.json.get('id')
                    
                        # Permitir si el usuario está actuando sobre sí mismo
                        if target_id == uid:
                            return f(*args, **kwargs)
                        return jsonify({"error": "Solo puedes realizar esta acción sobre tu propia cuenta"}), 403
                
                    # Lógica para permisos booleanos tradicionales
                    elif not permission_value:
                        return jsonify({"error": f"Permiso denegado para la acción '{permission}'"}), 403

                return f(*args, **kwargs)

            except auth.InvalidIdTokenError:
                return jsonify({"error": "Token de Firebase inválido"}), 401
            except auth.ExpiredIdTokenError:
                return jsonify({"error": "Token de Firebase expirado"}), 401
            except auth.RevokedIdTokenError:
                return jsonify({"error": "Token de Firebase revocado"}), 401
            except Exception as e:
                return jsonify({"error": f"Error de autenticación: {str(e)}"}), 401

        return decorated_function
    return decorator

def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        user_doc = db.collection('users').document(decoded_token['uid']).get()
        if not user_doc.exists:
            return None
            
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            **user_doc.to_dict()
        }
    except Exception as e:
        print(f"Error getting current user: {str(e)}")
        return None

print("Firebase inicializado correctamente.")