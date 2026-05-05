from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    clave = db.Column(db.String(255), nullable=False)
    nombre_usuario = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    es_admin = db.Column(db.Boolean, default=False, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)
    
    # Relaciones
    modelos = db.relationship('Modelo', backref='creador', lazy=True)
    suscripciones = db.relationship('Suscripcion', backref='usuario', lazy=True)
    valoraciones = db.relationship('Valoracion', backref='usuario', lazy=True)

    @property
    def total_generados(self):
        from app.models import Modelo
        return Modelo.query.filter_by(id_usuario=self.id_usuario).count()
    
    @property
    def generados_mes(self):
        from app.models import Modelo
        import datetime
        primer_dia_mes = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return Modelo.query.filter(
            Modelo.id_usuario == self.id_usuario,
            Modelo.fecha_creacion >= primer_dia_mes
        ).count()

    def set_password(self, password_plano):
        self.clave = generate_password_hash(password_plano)
    
    def check_password(self, password_plano):
        return check_password_hash(self.clave, password_plano)
    
    def get_id(self):
        return str(self.id_usuario)
    
    def avatar_url(self):
        if self.imagen:
            from flask import url_for
            return url_for('static', filename=f'uploads/avatars/{self.imagen}')
        return None

class Modelo(db.Model):
    __tablename__ = 'modelos'

    id_modelo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    prompt_texto = db.Column(db.String(255), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    archivo_url = db.Column(db.String(255), nullable=True)
    imagen_url = db.Column(db.String(255), nullable=True)
    es_publico = db.Column(db.Boolean, default=False, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meshy_task_id = db.Column(db.String(255), nullable=True) # ID de la tarea en Meshy para edición/rigging
    
    # Dimensiones en cm
    dim_x = db.Column(db.Float, default=9.0)
    dim_y = db.Column(db.Float, default=3.0)
    dim_z = db.Column(db.Float, default=3.0)

    # Relaciones
    metricas = db.relationship('Metrica', backref='modelo', lazy=True)
    valoraciones = db.relationship('Valoracion', backref='modelo_evaluado', lazy=True)

class Metrica(db.Model):
    __tablename__ = 'metricas'

    id_metrica = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_modelo = db.Column(db.Integer, db.ForeignKey('modelos.id_modelo', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    duracion = db.Column(db.Numeric(8, 2), nullable=True)
    detalle_error = db.Column(db.String(255), nullable=True)
    exitoso = db.Column(db.Boolean, nullable=True)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    recomendaciones = db.Column(db.Text, nullable=True)

class Plan(db.Model):
    __tablename__ = 'planes'

    id_plan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_plan = db.Column(db.String(50), nullable=False)
    limite_exportaciones_mensual = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)

    suscripciones = db.relationship('Suscripcion', backref='plan', lazy=True)

class Suscripcion(db.Model):
    __tablename__ = 'suscripciones'

    id_suscripcion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_plan = db.Column(db.Integer, db.ForeignKey('planes.id_plan', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(50), nullable=True)
    metodo_pago = db.Column(db.String(255), nullable=True)
    modelos_restantes = db.Column(db.Integer, nullable=False)

class Valoracion(db.Model):
    __tablename__ = 'valoraciones'

    id_valoracion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_modelo = db.Column(db.Integer, db.ForeignKey('modelos.id_modelo', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    puntuacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.String(255), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))