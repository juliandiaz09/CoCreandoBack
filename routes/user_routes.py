from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify
from models.user import User
from utils import firbase, firebase_auth_required
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)

user_bp = Blueprint('user', __name__)  # nombre e identificador

colection_ref = firbase.db.collection('users')


@user_bp.route('/listarUsuarios', methods=['GET'])
@firebase_auth_required('listar_usuarios')
def listar_usuarios():
    usuarios_ref = colection_ref.stream()
    usuarios = [doc.to_dict() for doc in usuarios_ref]
    return jsonify(usuarios), 200

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
    
    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"error": "No encontrado"}), 404

    doc_ref.update(data)
    return jsonify({"mensaje": "Usuario actualizado"}), 200

#UNICA FUNCIÓN EJECUTADA EN ESTE COMMIT - USO DE DECORADOR FUNCIONALIDAD - AÚN NO SE ESTABLECEN ROLES
@user_bp.route('/obtenerUsuario/<string:id>', methods=['GET'])
@firebase_auth_required('obtener_usuario')
def obtener_usuario(id):
    try:
        # Obtener referencia al documento del usuario
        doc_ref = colection_ref.document(id)
        doc = doc_ref.get()
        
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
        #             'rol': 'usuario',  # Valor por defecto
        #             'status': 'active',  # Valor por defecto
        #             'login_count': 0  # Valor por defecto
        #         }
        #         doc_ref.set(user_data)
        #         return jsonify(user_data), 200
        #     except Exception as auth_error:
        #         return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify(doc.to_dict()), 200
    except Exception as e:
        print(f"Error al obtener usuario: {str(e)}")
        return jsonify({"error": str(e)}), 500
    



@user_bp.route('/eliminarUsuario/<string:id>', methods=['DELETE'])
@firebase_auth_required('eliminar_usuario')
def eliminar_usuario(id):

    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"error": "No encontrado"}), 404

    doc_ref.delete()
    return jsonify({"mensaje": "Usuario eliminado"}), 200