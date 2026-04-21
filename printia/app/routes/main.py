from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Modelo, Metrica, Usuario
from app.utils import guardar_avatar, eliminar_avatar
import time
import random

main_bp = Blueprint('main', __name__)

@main_bp.route('/generador')
@login_required
def generador():
    return render_template('generador.html')

@main_bp.route('/galeria')
@login_required
def galeria():
    # Obtener modelos del usuario (o todos los públicos, según corresponda)
    modelos = Modelo.query.filter_by(id_usuario=current_user.id_usuario).order_by(Modelo.fecha_creacion.desc()).all()
    return render_template('galeria.html', modelos=modelos)

@main_bp.route('/generar', methods=['POST'])
@login_required
def generar():
    prompt = request.form.get('prompt')
    if not prompt:
        flash('Debes ingresar una descripción.', 'error')
        return redirect(url_for('main.generador'))
    
    # Aquí iría la llamada real a la API de IA. Por ahora hacemos un mock.
    # Simulamos un tiempo de procesamiento
    time.sleep(2)
    
    nuevo_modelo = Modelo(
        id_usuario=current_user.id_usuario,
        prompt_texto=prompt,
        titulo=f"Modelo basado en: {prompt[:20]}...",
        archivo_url="mock_model.stl",  # URL del archivo 3D mock
        imagen_url="mock_image.png",   # Imagen previa mock
        es_publico=False
    )
    db.session.add(nuevo_modelo)
    db.session.commit()
    
    # Guardamos también la métrica de éxito
    metrica = Metrica(
        id_modelo=nuevo_modelo.id_modelo,
        duracion=2.5,
        exitoso=True
    )
    db.session.add(metrica)
    db.session.commit()
    
    flash('¡Modelo generado exitosamente!', 'success')
    return redirect(url_for('main.modelo', id_modelo=nuevo_modelo.id_modelo))

@main_bp.route('/modelo/<int:id_modelo>')
@login_required
def modelo(id_modelo):
    modelo_obj = Modelo.query.get_or_404(id_modelo)
    # Solo el dueño puede verlo si no es público (simplificación por ahora)
    if not modelo_obj.es_publico and modelo_obj.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para ver este modelo.', 'error')
        return redirect(url_for('main.galeria'))
    return render_template('modelo.html', modelo=modelo_obj)

@main_bp.route('/planes')
def planes():
    return render_template('planes.html')

@main_bp.route('/como-funciona')
def como_funciona():
    return render_template('como_funciona.html')

@main_bp.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')

@main_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        email = request.form.get('email')
        imagen = request.files.get('imagen')
        
        password_actual = request.form.get('password_actual')
        nueva_password = request.form.get('nueva_password')
        confirmar_password = request.form.get('confirmar_password')
        
        # Validar si el email ya existe en otro usuario
        usuario_existente = Usuario.query.filter(Usuario.email == email, Usuario.id_usuario != current_user.id_usuario).first()
        if usuario_existente:
            flash('El correo electrónico ya está en uso por otra cuenta.', 'error')
            return redirect(url_for('main.editar_perfil'))
        
        # Procesar cambio de contraseña si envió algo
        if password_actual or nueva_password or confirmar_password:
            if not password_actual:
                flash('Debes ingresar tu contraseña actual para cambiarla.', 'error')
                return redirect(url_for('main.editar_perfil'))
            if not current_user.check_password(password_actual):
                flash('La contraseña actual es incorrecta.', 'error')
                return redirect(url_for('main.editar_perfil'))
            if nueva_password != confirmar_password:
                flash('Las contraseñas nuevas no coinciden.', 'error')
                return redirect(url_for('main.editar_perfil'))
            if len(nueva_password) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'error')
                return redirect(url_for('main.editar_perfil'))
                
            current_user.set_password(nueva_password)
        
        current_user.nombre_usuario = nombre_usuario
        current_user.email = email
        
        # Procesar nueva imagen de perfil
        if imagen and imagen.filename != '':
            nombre_archivo = guardar_avatar(imagen, current_user.id_usuario)
            if nombre_archivo:
                # Eliminar la imagen vieja si tenía una
                if current_user.imagen:
                    eliminar_avatar(current_user.imagen)
                current_user.imagen = nombre_archivo
            else:
                flash('Archivo de imagen no válido. Formatos permitidos: png, jpg, jpeg, webp.', 'error')
                return redirect(url_for('main.editar_perfil'))
                
        db.session.commit()
        flash('Datos actualizados exitosamente.', 'success')
        return redirect(url_for('main.perfil'))
        
    return render_template('editar_perfil.html')
