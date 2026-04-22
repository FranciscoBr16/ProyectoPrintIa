from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Modelo, Metrica, Usuario, Plan, Suscripcion
from app.utils import guardar_avatar, eliminar_avatar
import time
import datetime
import random

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas generales
    total_modelos = Modelo.query.filter_by(id_usuario=current_user.id_usuario).count()
    
    # Modelos de este mes
    primer_dia_mes = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    modelos_mes = Modelo.query.filter(
        Modelo.id_usuario == current_user.id_usuario,
        Modelo.fecha_creacion >= primer_dia_mes
    ).count()
    
    # Último modelo para el mini-visor
    ultimo_modelo = Modelo.query.filter_by(id_usuario=current_user.id_usuario).order_by(Modelo.fecha_creacion.desc()).first()
    
    # Información de suscripción
    suscripcion = Suscripcion.query.filter_by(id_usuario=current_user.id_usuario, estado='Activa').first()
    plan_nombre = 'GRATIS'
    limite_gratis = 5
    creditos_restantes = max(0, limite_gratis - total_modelos)
    
    if suscripcion:
        plan = Plan.query.get(suscripcion.id_plan)
        if plan:
            plan_nombre = plan.nombre_plan
            if plan_nombre == 'PRO':
                creditos_restantes = -1 # Ilimitado
            else:
                creditos_restantes = suscripcion.modelos_restantes

    return render_template('dashboard.html', 
                           total_modelos=total_modelos, 
                           modelos_mes=modelos_mes, 
                           ultimo_modelo=ultimo_modelo,
                           plan_nombre=plan_nombre,
                           creditos_restantes=creditos_restantes)

@main_bp.route('/generador')
@login_required
def generador():
    # Verificar créditos antes de dejar entrar al generador
    total_modelos = Modelo.query.filter_by(id_usuario=current_user.id_usuario).count()
    suscripcion = Suscripcion.query.filter_by(id_usuario=current_user.id_usuario, estado='Activa').first()
    
    if not suscripcion and total_modelos >= 5:
        flash('Has alcanzado el límite de 5 modelos gratuitos. ¡Pásate a PRO para seguir creando!', 'info')
        return redirect(url_for('main.planes'))
        
    return render_template('generador.html')

@main_bp.route('/galeria')
@login_required
def galeria():
    modelos = Modelo.query.filter_by(id_usuario=current_user.id_usuario).order_by(Modelo.fecha_creacion.desc()).all()
    return render_template('galeria.html', modelos=modelos)

@main_bp.route('/explorar')
def explorar():
    q = request.args.get('q', '')
    if q:
        # Buscar en título o prompt si hay una consulta
        modelos = Modelo.query.filter(
            Modelo.es_publico == True,
            (Modelo.titulo.like(f'%{q}%')) | (Modelo.prompt_texto.like(f'%{q}%'))
        ).order_by(Modelo.fecha_creacion.desc()).all()
    else:
        # Mostrar todos los públicos por defecto
        modelos = Modelo.query.filter_by(es_publico=True).order_by(Modelo.fecha_creacion.desc()).all()
    
    return render_template('explorar.html', modelos=modelos, search_query=q)

@main_bp.route('/generar', methods=['POST'])
@login_required
def generar():
    prompt = request.form.get('prompt')
    if not prompt:
        flash('Debes ingresar una descripción.', 'error')
        return redirect(url_for('main.generador'))
    
    # Validación de seguridad: verificar créditos
    total_modelos = Modelo.query.filter_by(id_usuario=current_user.id_usuario).count()
    suscripcion = Suscripcion.query.filter_by(id_usuario=current_user.id_usuario, estado='Activa').first()
    
    if not suscripcion and total_modelos >= 5:
        flash('Límite de créditos alcanzado. Pásate a PRO para continuar.', 'error')
        return redirect(url_for('main.planes'))
    
    # Aquí iría la llamada real a la API de IA. Por ahora hacemos un mock.
    # Simulamos un tiempo de procesamiento
    import time
    time.sleep(2)
    
    nuevo_modelo = Modelo(
        id_usuario=current_user.id_usuario,
        prompt_texto=prompt,
        titulo=f"Modelo basado en: {prompt[:20]}...",
        imagen_url="mock_image.png",   # Imagen previa mock
        es_publico=False
    )
    
    db.session.add(nuevo_modelo)
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

@main_bp.route('/modelo/<int:id_modelo>/toggle_public', methods=['POST'])
@login_required
def toggle_public(id_modelo):
    modelo_obj = Modelo.query.get_or_404(id_modelo)
    
    # Verificar que el usuario actual sea el dueño
    if modelo_obj.id_usuario != current_user.id_usuario:
        return jsonify({'error': 'No tienes permiso para modificar este modelo.'}), 403
    
    # Cambiar el estado
    modelo_obj.es_publico = not modelo_obj.es_publico
    db.session.commit()
    
    status = "público" if modelo_obj.es_publico else "privado"
    flash(f'El modelo ahora es {status}.', 'success')
    return redirect(url_for('main.modelo', id_modelo=id_modelo))

@main_bp.route('/planes')
def planes():
    plan_nombre = 'GRATIS'
    if current_user.is_authenticated:
        suscripcion = Suscripcion.query.filter_by(id_usuario=current_user.id_usuario, estado='Activa').first()
        if suscripcion:
            plan = Plan.query.get(suscripcion.id_plan)
            if plan:
                plan_nombre = plan.nombre_plan
    return render_template('planes.html', plan_nombre=plan_nombre)

@main_bp.route('/como-funciona')
def como_funciona():
    return render_template('como_funciona.html')

@main_bp.route('/perfil')
@login_required
def perfil():
    from app.models import Suscripcion, Plan
    suscripcion = Suscripcion.query.filter_by(id_usuario=current_user.id_usuario, estado='Activa').first()
    plan_nombre = 'GRATIS'
    if suscripcion:
        plan = Plan.query.get(suscripcion.id_plan)
        if plan:
            plan_nombre = plan.nombre_plan
    return render_template('perfil.html', plan_nombre=plan_nombre, suscripcion=suscripcion)

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

@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Buscamos o creamos el plan PRO
        plan_pro = Plan.query.filter_by(nombre_plan='PRO').first()
        if not plan_pro:
            plan_pro = Plan(nombre_plan='PRO', limite_exportaciones_mensual=-1, precio=9.99)
            db.session.add(plan_pro)
            db.session.commit()
            
        # Actualizamos o creamos la suscripción del usuario
        suscripcion = Suscripcion.query.filter_by(id_usuario=current_user.id_usuario).first()
        hoy = datetime.date.today()
        vencimiento = hoy + datetime.timedelta(days=30)
        
        if suscripcion:
            suscripcion.id_plan = plan_pro.id_plan
            suscripcion.fecha_inicio = hoy
            suscripcion.fecha_fin = vencimiento
            suscripcion.estado = 'Activa'
            suscripcion.metodo_pago = 'Tarjeta'
            suscripcion.modelos_restantes = plan_pro.limite_exportaciones_mensual
        else:
            # Generamos el ID manualmente por si la tabla no tiene AUTO_INCREMENT
            max_id = db.session.query(db.func.max(Suscripcion.id_suscripcion)).scalar() or 0
            
            nueva_suscripcion = Suscripcion(
                id_suscripcion=max_id + 1,
                id_plan=plan_pro.id_plan,
                id_usuario=current_user.id_usuario,
                fecha_inicio=hoy,
                fecha_fin=vencimiento,
                estado='Activa',
                metodo_pago='Tarjeta',
                modelos_restantes=plan_pro.limite_exportaciones_mensual
            )
            db.session.add(nueva_suscripcion)
            
        db.session.commit()
        
        flash('¡Pago exitoso! Ahora eres usuario PRO.', 'success')
        return redirect(url_for('main.planes'))
        
    return render_template('checkout.html')
