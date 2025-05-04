from flask import Flask, request, jsonify
from models.project.project import Proyecto
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'uptc2025'  
jwt = JWTManager(app)

proyectos = []

@app.route('/listarProyectos', methods=['GET'])
@jwt_required()
def lista_estudiantes():
    proyecto = Proyecto(
        id=1,   
        titulo="Smartwatch para personas con discapacidad visual",
        descripcion="Un reloj inteligente con asistencia por voz y sensores hápticos.",
        categoria="Tecnología",
        meta_financiera=50000,
        fondos_recaudados=10000,
        fecha_limite="2025-06-30",
        ciudad_desarrollo="",
        id_creador=101,
        estado="activo"
    )

    proyectoTest = next((p for p in proyectos if p['id'] == proyecto.id), None)

    if proyectoTest is None:
        proyectos.append(proyecto.to_json())
  
    return jsonify(proyectos)

@app.route('/crearProyectos', methods=['POST'])
@jwt_required()
def crear_estudiante():
    data = request.get_json()
    id = data.get('id')
    titulo = data.get('titulo')
    descripcion = data.get('descripcion')
    categoria = data.get('categoria')
    meta_financiera = data.get('meta_financiera')
    fondos_recaudados = data.get('fondos_recaudados', 0)
    fecha_limite = data.get('fecha_limite')
    id_creador = data.get('id_creador')
    estado = data.get('estado', "pendiente")
    
    proyecto = Proyecto(id, titulo, descripcion, categoria, meta_financiera, fondos_recaudados, fecha_limite, id_creador, estado)
    proyectos.append(proyecto.to_json())

    return jsonify({"mensaje": "Proyecto creado exitosamente"}), 201

@app.route('/actualizarProyecto/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_proyecto(id):
    data = request.get_json()
    proyecto = next((p for p in proyectos if p['id'] == id), None)

    if proyecto is not None:
        # Actualizar solo los campos enviados en la petición
        proyecto['titulo'] = data.get('titulo', proyecto['titulo'])
        proyecto['descripcion'] = data.get('descripcion', proyecto['descripcion'])
        proyecto['categoria'] = data.get('categoria', proyecto['categoria'])
        proyecto['meta_financiera'] = data.get('meta_financiera', proyecto['meta_financiera'])
        proyecto['fondos_recaudados'] = data.get('fondos_recaudados', proyecto['fondos_recaudados'])
        proyecto['fecha_limite'] = data.get('fecha_limite', proyecto['fecha_limite'])
        proyecto['estado'] = data.get('estado', proyecto['estado'])

        return jsonify({"mensaje": "Proyecto actualizado exitosamente"}), 200
    else:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404
    
@app.route('/obtenerProyecto/<int:id>', methods=['GET'])
@jwt_required()
def obtener_proyecto(id):
    proyecto = next((p for p in proyectos if p['id'] == id), None)

    if proyecto is not None:
        return jsonify(proyecto), 200
    else:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404


@app.route('/eliminarProyecto/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_proyecto(id):
    global proyectos
    proyecto = next((p for p in proyectos if p['id'] == id), None)
    
    if proyecto is not None:
        proyectos = [p for p in proyectos if p['id'] != id]
        return jsonify({"mensaje": "Proyecto eliminado exitosamente"}), 200
    else:
        return jsonify({"mensaje": "Proyecto no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
