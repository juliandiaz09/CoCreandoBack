from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify
from models.project import project
from utils import firbase
from flask_cors import CORS
from flask_cors import cross_origin
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)

project_bp = Blueprint('project_bp', __name__)  # nombre e identificador

colection_ref = firbase.db.collection('proyectos')


@project_bp.route('/listarProyectos', methods=['GET'])
@cross_origin(supports_credentials=True)
def listar_proyectos():
    try:
        proyectos_ref = colection_ref.stream()
        proyectos = []
        for doc in proyectos_ref:
            proyecto = doc.to_dict()
            proyecto["id"] = doc.id 
            proyectos.append(proyecto)
        return jsonify(proyectos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@project_bp.route('/crearProyecto', methods=['POST'])
#@jwt_required()
def crear_proyecto():
    data = request.get_json()
    id = data.get('id')

    doc_ref = colection_ref.document(id)
    doc_ref.set(data)

    return jsonify({"mensaje": "Proyecto creado exitosamente"}), 201

@project_bp.route('/actualizarProyecto/<string:id>', methods=['PUT'])
# #@jwt_required()
def actualizar_proyecto(id):
    data = request.get_json()
    doc_ref = colection_ref.document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

    doc_ref.update(data)
    return jsonify({"mensaje": "Proyecto actualizado exitosamente"}), 200

@project_bp.route('/obtenerProyecto/<string:id>', methods=['GET'])
def obtener_proyecto(id):
    doc = colection_ref.document(id).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    else:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

@project_bp.route('/eliminarProyecto/<string:id>', methods=['DELETE'])
def eliminar_proyecto(id):
    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

    doc_ref.delete()
    return jsonify({"mensaje": "Proyecto eliminado exitosamente"}), 200
