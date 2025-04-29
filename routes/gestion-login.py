from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'uptc2025'  
jwt = JWTManager(app)

proyectos = []

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username == "admin" and password == "admin":
     access_token = create_access_token(identity=username)
     return jsonify(access_token=access_token), 200
    else:
        return jsonify({"mensaje": "Credenciales incorrectas"}), 401