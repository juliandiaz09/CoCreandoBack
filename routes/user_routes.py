from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify
from models.user import User
from utils import firbase, firebase_auth_required
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)

user_bp = Blueprint('user', __name__)  # nombre e identificador

colection_ref = firbase.db.collection('usuarios')


@user_bp.route('/listarUsuarios', methods=['GET'])
#@firebase_auth_required('listar_usuarios')
def listar_usuarios():
    usuarios_ref = colection_ref.stream()
    usuarios = [doc.to_dict() for doc in usuarios_ref]
    return jsonify(usuarios), 200

@user_bp.route('/crearUsuario', methods=['POST'])
#@firebase_auth_required('crear_usuario')
def crear_usuario():
    data = request.get_json()
    
    if request.user['rol'] != 'administrador':
        return jsonify({"error": "No autorizado"}), 403
    
    id = data.get('id')
    doc_ref = colection_ref.document(id)
    doc_ref.set(data)
    return jsonify({"mensaje": "Usuario creado"}), 201

@user_bp.route('/actualizarUsuario/<string:id>', methods=['PUT'])
#@firebase_auth_required('actualizar_usuario')
def actualizar_usuarios(id):
    data = request.get_json()
        # Usuarios normales solo pueden actualizarse a sí mismos
    if id != request.user['uid'] and request.user['rol'] != 'administrador':
        return jsonify({"error": "No autorizado"}), 403
    
    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"error": "No encontrado"}), 404

    doc_ref.update(data)
    return jsonify({"mensaje": "Usuario actualizado"}), 200

#UNICA FUNCIÓN EJECUTADA EN ESTE COMMIT - USO DE DECORADOR FUNCIONALIDAD - AÚN NO SE ESTABLECEN ROLES
@user_bp.route('/obtenerUsuario/<string:id>', methods=['GET', 'OPTIONS'])
@firebase_auth_required('obtener_usuario')
def obtener_usuario(id):
    doc = colection_ref.document(id).get()
    return jsonify(doc.to_dict() if doc.exists else {"error": "No encontrado"}), 200 if doc.exists else 404

@user_bp.route('/eliminarUsuario/<string:id>', methods=['DELETE'])
#@firebase_auth_required('eliminar_usuario')
def eliminar_usuario(id):
    # Solo administradores pueden eliminar (y no a sí mismos)
    if request.user['rol'] != 'administrador' or id == request.user['uid']:
        return jsonify({"error": "No autorizado"}), 403
    
    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"error": "No encontrado"}), 404

    doc_ref.delete()
    return jsonify({"mensaje": "Usuario eliminado"}), 200