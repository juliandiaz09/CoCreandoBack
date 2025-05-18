
from flask import Flask
from routes.project_routes import project_bp
from routes.payment_routes import payment_bp
from routes.login_routes import auth_bp
from routes.user_routes import user_bp


app = Flask(__name__)
app.register_blueprint(project_bp, url_prefix="/proyectos")
app.register_blueprint(payment_bp, url_prefix='/pagos')
app.register_blueprint(user_bp, url_prefix='/usuarios')
app.register_blueprint(auth_bp,url_prefix='/login')

if __name__ == "__main__":
    app.run()
