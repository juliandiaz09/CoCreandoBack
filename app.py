
from flask import Flask
from flask_cors import CORS
from routes.login_routes import login_bp
from routes.register_routes import register_bp
from routes.project_routes import project_bp
from routes.payment_routes import payment_bp
from routes.user_routes import user_bp


app = Flask(__name__)

# CORS global (solo para pruebas locales, en producción usa origen específico)
CORS(app, supports_credentials=True)

# Registro del blueprint en /login
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(register_bp, url_prefix='/registro')
app.register_blueprint(project_bp, url_prefix='/proyecto')
app.register_blueprint(payment_bp, url_prefix='/pasarela')
app.register_blueprint(user_bp, url_prefix='/usuario')


if __name__ == '__main__':
    app.run(debug=True)

