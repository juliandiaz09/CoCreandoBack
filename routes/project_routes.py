from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify
from models.project import project
from utils import firbase
from flask_cors import CORS
from flask_cors import cross_origin
from datetime import datetime
from utils.cloudinary_bd import cloudinary 
from utils.firbase import firebase_auth_required, get_current_user

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
@cross_origin(supports_credentials=True)
def crear_proyecto():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['title', 'description', 'goal', 'category', 'deadline', 'creator']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400
                
         # Convertir la fecha deadline a formato ISO si es una cadena
        deadline = data["deadline"]
        if isinstance(deadline, str):
            try:
                deadline = datetime.fromisoformat(deadline).isoformat()
            except ValueError:
                return jsonify({"error": "Formato de fecha inválido"}), 400
            
        # # Subir múltiples imágenes
        # urls_fotos = []
        # for foto_base64 in data["photos"]:
        #     url = cloudinary.subir_a_cloudinary(foto_base64)
        #     urls_fotos.append(url)

                # Crear documento en Firestore
        doc_ref = colection_ref.document()
        project_id = doc_ref.id
        
        # Estructurar datos del proyecto
        project_data = {
            "id": project_id,
            "title": data["title"],
            "description": data["description"],
            "longDescription": data.get("longDescription", ""),
            "goal": float(data["goal"]),
            "collected": 0.0,
            "category": data["category"],
            "deadline": data["deadline"],
            "location": data.get("location", ""),
            "creator": data["creator"],
            "risksAndChallenges": data.get("risksAndChallenges", ""),
            "rewards": data.get("rewards", []),
            "updates": data.get("updates", []),
            "supporters": [],
            "status": "pending",
            "createdAt": datetime.now().isoformat()
            # "file": cloudinary.subir_a_cloudinary(data['file']), # Esto es requerido
            # "photos": urls_fotos  # Guarda las URLs #Esto tambien .... pero al menos uno
        }
        
        doc_ref.set(project_data)
        
        return jsonify({
            "mensaje": "Proyecto creado exitosamente",
            "projectId": project_id
        }), 201
        
    except Exception as e:
        print(f"Error al crear proyecto: {str(e)}")
        return jsonify({"error": str(e)}), 500

@project_bp.route('/actualizarProyecto/<string:id>', methods=['PUT'])
@firebase_auth_required('actualizar_proyecto')
def actualizar_proyecto(id):
    data = request.get_json()
    
    # Verificar si el usuario que hace la petición es admin o el creador del proyecto
    current_user = get_current_user()
    project = colection_ref.document(id).get().to_dict()
    
    if current_user.get('role') != 'admin' and current_user.get('uid') != project.get('creator'):
        return jsonify({"error": "No autorizado"}), 403
    
    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

    # Solo permitir actualizar ciertos campos
    allowed_fields = ['status', 'title', 'description', 'category']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    doc_ref.update(update_data)
    return jsonify({"mensaje": "Proyecto actualizado exitosamente"}), 200

@project_bp.route('/obtenerProyecto/<string:id>', methods=['GET'])
def obtener_proyecto(id):
    doc = colection_ref.document(id).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    else:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

@project_bp.route('/listarProyectosCategoria/<string:categoria>', methods=['GET'])
def obtener_proyectos_categoria(categoria):
    try:
        proyectos = filtro_proyectos('category', categoria)
        return jsonify(proyectos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
   
@project_bp.route('/listarProyectosStatus/<string:status>', methods=['GET'])
def obtener_proyecto_status(status):
    try:
        proyectos = filtro_proyectos('status', status)
        return jsonify(proyectos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@project_bp.route('/listarProyectosLocation/<string:location>', methods=['GET'])
def obtener_proyecto_location(location):
    try:
        proyectos = filtro_proyectos('location', location)
        return jsonify(proyectos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@project_bp.route('/listarProyectosCreator/<string:creator>', methods=['GET'])
def obtener_proyecto_creator(creator):
    try:
        proyectos = filtro_proyectos('creator', creator)
        return jsonify(proyectos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def filtro_proyectos(campo, valor):
    proyectos_ref = colection_ref.stream()
    proyectos = []
    for doc in proyectos_ref:
        proyecto = doc.to_dict()
        proyecto["id"] = doc.id
        if proyecto.get(campo) == valor:
            proyectos.append(proyecto)
    return proyectos

@project_bp.route('/eliminarProyecto/<string:id>', methods=['DELETE'])
@firebase_auth_required('eliminar_Proyecto')
def eliminar_proyecto(id):
    doc_ref = colection_ref.document(id)
    if not doc_ref.get().exists:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

    doc_ref.delete()
    return jsonify({"mensaje": "Proyecto eliminado exitosamente"}), 200

@project_bp.route('/aprobarProyecto/<string:id>', methods=['PUT'])
@firebase_auth_required('administrar_sistema')
def aprobar_proyecto(id):
    try:
        doc_ref = colection_ref.document(id)
        if not doc_ref.get().exists:
            return jsonify({"error": "Proyecto no encontrado"}), 404
            
        doc_ref.update({"status": "approved"})
        return jsonify({"mensaje": "Proyecto aprobado exitosamente"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@project_bp.route('/rechazarProyecto/<string:id>', methods=['PUT'])
@firebase_auth_required('administrar_sistema')
def rechazar_proyecto(id):
    try:
        doc_ref = colection_ref.document(id)
        if not doc_ref.get().exists:
            return jsonify({"error": "Proyecto no encontrado"}), 404
            
        doc_ref.update({"status": "rejected"})
        return jsonify({"mensaje": "Proyecto rechazado exitosamente"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def obtener_datos_proyecto(id):
    doc = colection_ref.document(id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None