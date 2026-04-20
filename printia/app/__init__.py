from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Instancias globales (se inicializan adentro de create_app)
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializa extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # a dónde redirige si no estás logueado
    login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
    
    # Importar y registrar rutas
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    # Importar modelos para que SQLAlchemy los conozca
    from app import models
    
    return app