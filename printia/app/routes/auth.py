from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from app.utils import guardar_avatar

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    return render_template('index.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(password):
            login_user(usuario)
            flash('Sesión iniciada correctamente.', 'success')
            return redirect(url_for('auth.index'))
        else:
            flash('Email o contraseña incorrectos.', 'error')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre_usuario')
        password = request.form.get('password')
        archivo_imagen = request.files.get('imagen')  # request.files, no request.form
        
        if Usuario.query.filter_by(email=email).first():
            flash('Ese email ya está registrado.', 'error')
            return render_template('register.html')
        
        # Crear usuario primero (necesitamos el ID para nombrar el archivo)
        nuevo_usuario = Usuario(email=email, nombre_usuario=nombre)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.flush()  # genera el ID sin hacer commit todavía
        
        # Procesar imagen si se subió
        if archivo_imagen and archivo_imagen.filename:
            nombre_archivo = guardar_avatar(archivo_imagen, nuevo_usuario.id_usuario)
            if nombre_archivo:
                nuevo_usuario.imagen = nombre_archivo
            else:
                # El archivo era inválido (extensión no permitida, etc.)
                db.session.rollback()
                flash('La imagen no es válida. Usá PNG, JPG o WEBP.', 'error')
                return render_template('register.html')
        
        db.session.commit()
        flash('Cuenta creada. Ya podés iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('auth.index'))