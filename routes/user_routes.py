from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify
from models.user import User
from utils import firbase, firebase_auth_required
from flask_cors import CORS
from utils.firbase import get_current_user

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)

user_bp = Blueprint('user', __name__)  # nombre e identificador

colection_ref = firbase.db.collection('users')


@user_bp.route('/listarUsuarios', methods=['GET'])
@firebase_auth_required('listar_usuarios')
def listar_usuarios():
    try:
        # Obtener el usuario actual desde el contexto de g
        current_user = get_current_user()
        print(f"Usuario actual: {current_user}")  # Log para depuración
        
        # Verificar si el usuario es administrador
        if current_user.get('role') != 'admin':
            print("Usuario no es admin")  # Log para depuración
            return jsonify({"error": "No autorizado"}), 403

        usuarios_ref = colection_ref.stream()
        usuarios = []
        for doc in usuarios_ref:
            user_data = doc.to_dict()
            user_data["id"] = doc.id  # Asegurar que el ID está incluido
            usuarios.append(user_data)
        
        print(f"Usuarios encontrados: {len(usuarios)}")  # Log para depuración
        return jsonify(usuarios), 200
    except Exception as e:
        print(f"Error en listar_usuarios: {str(e)}")  # Log detallado
        return jsonify({"error": str(e)}), 500

@user_bp.route('/crearUsuario', methods=['POST'])
@firebase_auth_required('crear_usuario')
def crear_usuario():
    data = request.get_json()
    
    id = data.get('id')
    doc_ref = colection_ref.document(id)
    doc_ref.set(data)
    return jsonify({"mensaje": "Usuario creado"}), 201

@user_bp.route('/actualizarUsuario/<string:id>', methods=['PUT'])
@firebase_auth_required('actualizar_usuario')
def actualizar_usuarios(id):
    data = request.get_json()
    
    # Verificar si el usuario que hace la petición es admin
    current_user = get_current_user()  # Necesitarías implementar esta función
    if current_user.get('role') != 'admin':
        return jsonify({"error": "No autorizado"}), 403
    
    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"error": "No encontrado"}), 404

    # Solo permitir actualizar ciertos campos
    allowed_fields = ['role', 'status', 'name', 'email_verified']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    doc_ref.update(update_data)
    return jsonify({"mensaje": "Usuario actualizado"}), 200

#UNICA FUNCIÓN EJECUTADA EN ESTE COMMIT - USO DE DECORADOR FUNCIONALIDAD - AÚN NO SE ESTABLECEN ROLES
@user_bp.route('/obtenerUsuario/<string:id>', methods=['GET'])
#@firebase_auth_required('obtener_usuario')
def obtener_usuario(id):
    try:
        # Obtener referencia al documento del usuario
        doc_ref = colection_ref.document(id)
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        
        #Esto para nada es FUNCIONAL
        # if not doc.exists:
        #     # Si no existe en la colección 'usuarios', verificar en auth de Firebase
        #     try:
        #         user_record = auth.get_user(id)
        #         # Crear documento básico si no existe
        #         user_data = {
        #             'uid': user_record.uid,
        #             'email': user_record.email,
        #             'email_verified': user_record.email_verified,
        #             'name': user_record.display_name or user_record.email.split('@')[0],
        #             'role': 'usuario',  # Valor por defecto
        #             'status': 'active',  # Valor por defecto
        #             'login_count': 0  # Valor por defecto
        #         }
        #         doc_ref.set(user_data)
        #         return jsonify(user_data), 200
        #     except Exception as auth_error:
        #         return jsonify({"error": "Usuario no encontrado"}), 404
        
        user_data = doc.to_dict()
        # Asegurarse de que el campo de rol esté presente
        if 'rol' not in user_data:
            user_data['role'] = 'usuario'  # Valor por defecto
            
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@user_bp.route('/eliminarUsuario/<string:id>', methods=['DELETE'])
@firebase_auth_required('eliminar_usuario')
def eliminar_usuario(id):

    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"error": "No encontrado"}), 404

    doc_ref.delete()
    return jsonify({"mensaje": "Usuario eliminado"}), 200



@user_bp.route('/listarUsuariosRole/<string:role>', methods=['GET'])
def obtener_usuarios_role(role):
    try:
        usuarios = filtro_usuarios('role', role)
        return jsonify(usuarios), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
   
@user_bp.route('/listarUsuariosStatus/<string:status>', methods=['GET'])
def obtener_usuarios_status(status):
    try:
        usuarios = filtro_usuarios('status', status)
        return jsonify(usuarios), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def filtro_usuarios(campo, valor):
    usuarios_ref = colection_ref.stream()
    usuarios = []
    for doc in usuarios_ref:
        usuario = doc.to_dict()
        usuario["id"] = doc.id
        if usuario.get(campo) == valor:
            usuarios.append(usuario)
    return usuarios

def obtener_datos_usuarios(id):
    doc = colection_ref.document(id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None