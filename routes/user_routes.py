from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify
from models.user import User
from utils import firbase
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)

user_bp = Blueprint('user', __name__)  # nombre e identificador

colection_ref = firbase.db.collection('usuarios')
#app.config['JWT_SECRET_KEY'] = 'uptc2025'  
#jwt = JWTManager(app)

@user_bp.route('/listarUsuarios', methods=['GET'])
# @jwt_required()
def listar_usuarios():
    usuarios_ref = colection_ref.stream()
    usuarios = [doc.to_dict() for doc in usuarios_ref]
    return jsonify(usuarios), 200

@user_bp.route('/crearUsuario', methods=['POST'])
#@jwt_required()
def crear_usuario():
    data = request.get_json()
    id = data.get('id')

    doc_ref = colection_ref.document(id)
    doc_ref.set(data)

    return jsonify({"mensaje": "Proyecto creado exitosamente"}), 201

@user_bp.route('/actualizarUsuario/<string:id>', methods=['PUT'])
# #@jwt_required()
def actualizar_usuarios(id):
    data = request.get_json()
    doc_ref = colection_ref.document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

    doc_ref.update(data)
    return jsonify({"mensaje": "Proyecto actualizado exitosamente"}), 200

@user_bp.route('/obtenerUsuario/<string:id>', methods=['GET'])
def obtener_usuario(id):
    doc = colection_ref.document(id).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    else:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

@user_bp.route('/eliminarUsuario/<string:id>', methods=['DELETE'])
def eliminar_usuario(id):
    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

    doc_ref.delete()
    return jsonify({"mensaje": "Proyecto eliminado exitosamente"}), 200
