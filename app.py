
from flask import Flask
from flask_cors import CORS
from routes.login_routes import login_bp

app = Flask(__name__)

# CORS global (solo para pruebas locales, en producción usa origen específico)
CORS(app, supports_credentials=True)

# Registro del blueprint en /login
app.register_blueprint(login_bp, url_prefix='/login')

if __name__ == '__main__':
    app.run(debug=True)

