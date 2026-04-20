from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'  # nombre exacto de tu tabla en MySQL
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    clave = db.Column(db.String(255), nullable=False)  # guarda el HASH, no la clave
    nombre_usuario = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    es_admin = db.Column(db.Boolean, default=False)
    imagen = db.Column(db.String(255), nullable=True)
    
    def set_password(self, password_plano):
        """Hashea la contraseña antes de guardarla."""
        self.clave = generate_password_hash(password_plano)
    
    def check_password(self, password_plano):
        """Verifica si la contraseña ingresada coincide con el hash."""
        return check_password_hash(self.clave, password_plano)
    
    # Flask-Login necesita saber cuál es el ID. Como tu columna se llama
    # id_usuario y no id, sobrescribimos el método get_id.
    def get_id(self):
        return str(self.id_usuario)
    
    def avatar_url(self):
        if self.imagen:
            from flask import url_for
            return url_for('static', filename=f'uploads/avatars/{self.imagen}')
        return None


# Flask-Login necesita esta función para recuperar usuarios por ID
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))