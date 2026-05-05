from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Modelo, Metrica, Usuario, Plan, Suscripcion
from app.utils import guardar_avatar, eliminar_avatar, mejorar_prompt_con_ia
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
    limite_gratis = 1
    
    if suscripcion:
        plan = Plan.query.get(suscripcion.id_plan)
        if plan:
            plan_nombre = plan.nombre_plan
            if plan_nombre == 'PRO':
                creditos_restantes = suscripcion.modelos_restantes
            else:
                # Otros planes si existieran
                creditos_restantes = suscripcion.modelos_restantes
    else:
        creditos_restantes = max(0, limite_gratis - total_modelos)

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
    suscripcion = Suscripcion.query.filter_by(id_usuario=current_user.id_usuario, estado='Activa').first()
    
    if not suscripcion:
        total_modelos = Modelo.query.filter_by(id_usuario=current_user.id_usuario).count()
        if total_modelos >= 1:
            flash('Has alcanzado el límite de 1 modelo gratuito. ¡Pásate a PRO para crear hasta 15 por mes!', 'info')
            return redirect(url_for('main.planes'))
    else:
        # Límite basado en columna modelos_restantes
        if suscripcion.modelos_restantes <= 0:
            flash('Has alcanzado tu límite de modelos contratados.', 'info')
            return redirect(url_for('main.dashboard'))
        
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
    titulo_usuario = request.form.get('titulo')
    
    if not prompt or not titulo_usuario:
        flash('Debes ingresar un título y una descripción.', 'error')
        return redirect(url_for('main.generador'))
    
    # Validación de seguridad: verificar créditos
    suscripcion = Suscripcion.query.filter_by(id_usuario=current_user.id_usuario, estado='Activa').first()
    
    if not suscripcion:
        total_modelos = Modelo.query.filter_by(id_usuario=current_user.id_usuario).count()
        if total_modelos >= 1:
            flash('Límite de créditos alcanzado (1/1). Pásate a PRO para continuar.', 'error')
            return redirect(url_for('main.planes'))
    else:
        # Límite basado en columna modelos_restantes
        if suscripcion.modelos_restantes <= 0:
            flash('Límite de créditos alcanzado (0/15).', 'error')
            return redirect(url_for('main.dashboard'))
    
    import requests
    from flask import current_app

    api_key = current_app.config.get('MESHY_API_KEY')
    if not api_key:
        flash('Error de configuración: API Key de Meshy no encontrada.', 'error')
        return redirect(url_for('main.generador'))

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "mode": "preview",
        "prompt": prompt,
        "target_formats": ["stl", "glb"]
    }
    
    # --- MEJORA DEL PROMPT CON GEMINI ---
    prompt_mejorado, fue_mejorado_por_ia = mejorar_prompt_con_ia(prompt)

    # Actualizar el payload con el prompt mejorado
    payload['prompt'] = prompt_mejorado

    try:
        response = requests.post('https://api.meshy.ai/openapi/v2/text-to-3d', headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        task_id = data.get('result')
        
        # Restar un crédito si es PRO
        if suscripcion:
            suscripcion.modelos_restantes = max(0, suscripcion.modelos_restantes - 1)
            
        # Generar recomendaciones de impresión con IA
        from app.utils import generar_recomendaciones_ia
        recomendaciones_html = generar_recomendaciones_ia(prompt)
        
        nuevo_modelo = Modelo(
            id_usuario=current_user.id_usuario,
            prompt_texto=prompt,           # Prompt original del usuario (para mostrar)
            titulo=titulo_usuario,
            archivo_url=f"task:{task_id}",
            meshy_task_id=task_id,         # ID real de Meshy (para resiliencia)
            imagen_url="",                 # Se llenará cuando finalice
            es_publico=False
        )
        db.session.add(nuevo_modelo)
        db.session.flush() # Para obtener el id_modelo antes del commit final
        
        # Guardar recomendaciones en la tabla de métricas
        nueva_metrica = Metrica(
            id_modelo=nuevo_modelo.id_modelo,
            recomendaciones=recomendaciones_html
        )
        db.session.add(nueva_metrica)
        
        db.session.commit()
        
        flash('¡Generación iniciada! Por favor, espera mientras procesamos el modelo 3D.', 'success')
        return redirect(url_for('main.modelo', id_modelo=nuevo_modelo.id_modelo))
        
    except Exception as e:
        flash(f'Ocurrió un error al contactar la API de generación: {str(e)}', 'error')
        return redirect(url_for('main.generador'))

@main_bp.route('/modelo/<int:id_modelo>')
@login_required
def modelo(id_modelo):
    modelo_obj = Modelo.query.get_or_404(id_modelo)
    # Solo el dueño puede verlo si no es público (simplificación por ahora)
    if not modelo_obj.es_publico and modelo_obj.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para ver este modelo.', 'error')
        return redirect(url_for('main.galeria'))
        
    generando = False
    error_generacion = False
    
    if modelo_obj.meshy_task_id and (not modelo_obj.archivo_url or modelo_obj.archivo_url.startswith("task:")):
        generando = True
        task_id = modelo_obj.meshy_task_id
        
        from flask import current_app
        import requests
        import os
        api_key = current_app.config.get('MESHY_API_KEY')
        headers = {'Authorization': f'Bearer {api_key}'}
        
        try:
            # Intentar primero con el endpoint de generación (V2)
            response = requests.get(f'https://api.meshy.ai/openapi/v2/text-to-3d/{task_id}', headers=headers)
            
            # Si no se encuentra en V2, podría ser una tarea de Rigging o Animación (V1)
            if response.status_code == 404:
                # Probar Rigging
                response = requests.get(f'https://api.meshy.ai/openapi/v1/rigging/{task_id}', headers=headers)
                if response.status_code == 404:
                    # Probar Animación
                    response = requests.get(f'https://api.meshy.ai/openapi/v1/animations/{task_id}', headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status == 'SUCCEEDED':
                    result_data = data.get('result', {})
                    # Extraer URLs según el tipo de tarea
                    stl_url = result_data.get('stl') or result_data.get('rigged_character_glb_url') or result_data.get('animation_glb_url')
                    thumb_url = data.get('thumbnail_url') or result_data.get('thumbnail_url')
                    
                    # Para tareas de rigging/animation, el STL/GLB está en una estructura distinta
                    if not stl_url and 'model_urls' in data:
                        stl_url = data.get('model_urls', {}).get('stl')

                    if stl_url:
                        # Determinar extensión (glb para rigging/anim, stl para generación)
                        ext = "glb" if "glb" in stl_url.lower() else "stl"
                        stl_filename = f"modelo_{id_modelo}_{task_id[:8]}.{ext}"
                        stl_path = os.path.join(current_app.config['UPLOAD_FOLDER_MODELOS'], stl_filename)
                        os.makedirs(os.path.dirname(stl_path), exist_ok=True)
                        with open(stl_path, 'wb') as f:
                            f.write(requests.get(stl_url).content)
                        modelo_obj.archivo_url = stl_filename
                    
                    if thumb_url:
                        thumb_filename = f"thumb_{id_modelo}_{task_id[:8]}.png"
                        thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER_THUMBNAILS'], thumb_filename)
                        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                        with open(thumb_path, 'wb') as f:
                            f.write(requests.get(thumb_url).content)
                        modelo_obj.imagen_url = thumb_filename
                    else:
                        modelo_obj.imagen_url = "mock_image.png"
                    
                    # --- ACTUALIZACIÓN DE MÉTRICAS ---
                    metrica = Metrica.query.filter_by(id_modelo=id_modelo).order_by(Metrica.fecha_generacion.desc()).first()
                    if metrica:
                        ahora = datetime.datetime.utcnow()
                        duracion_segundos = (ahora - modelo_obj.fecha_creacion).total_seconds()
                        metrica.duracion = duracion_segundos
                        metrica.exitoso = True
                    
                    db.session.commit()
                    generando = False
                    
                elif status == 'FAILED':
                    modelo_obj.archivo_url = None
                    
                    # --- ACTUALIZACIÓN DE MÉTRICAS EN FALLO ---
                    metrica = Metrica.query.filter_by(id_modelo=id_modelo).order_by(Metrica.fecha_generacion.desc()).first()
                    if metrica:
                        metrica.exitoso = False
                        error_msg = data.get('task_error', {}).get('message', data.get('error', {}).get('message', 'Error desconocido en Meshy'))
                        metrica.detalle_error = (error_msg[:250] + '...') if len(error_msg) > 250 else error_msg
                    
                    db.session.commit()
                    generando = False
                    error_generacion = True
        except Exception as e:
            print(f"Error consultando Meshy: {e}")
            
    return render_template('modelo.html', modelo=modelo_obj, generando=generando, error_generacion=error_generacion)

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
    
    flash('Visibilidad del modelo actualizada.', 'success')
    return redirect(url_for('main.modelo', id_modelo=modelo_obj.id_modelo))

@main_bp.route('/modelo/<int:id_modelo>/editar', methods=['POST'])
@login_required
def editar_modelo(id_modelo):
    modelo_obj = Modelo.query.get_or_404(id_modelo)
    if modelo_obj.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para modificar este modelo.', 'error')
        return redirect(url_for('main.galeria'))
    
    nuevo_titulo = request.form.get('titulo')
    
    if nuevo_titulo and len(nuevo_titulo.strip()) > 0:
        modelo_obj.titulo = nuevo_titulo.strip()
        db.session.commit()
        flash('Modelo actualizado correctamente.', 'success')
    else:
        flash('El título no puede estar vacío.', 'error')
        
    return redirect(url_for('main.modelo', id_modelo=modelo_obj.id_modelo))

@main_bp.route('/modelo/<int:id_modelo>/eliminar', methods=['POST'])
@login_required
def eliminar_modelo(id_modelo):
    modelo_obj = Modelo.query.get_or_404(id_modelo)
    if modelo_obj.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para eliminar este modelo.', 'error')
        return redirect(url_for('main.galeria'))
    
    db.session.delete(modelo_obj)
    db.session.commit()
    flash('Modelo eliminado correctamente.', 'success')
    return redirect(url_for('main.galeria'))


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
            plan_pro = Plan(nombre_plan='PRO', limite_exportaciones_mensual=15, precio=10.00)
            db.session.add(plan_pro)
            db.session.commit()
        else:
            # Asegurar que el precio y límite estén actualizados si ya existía
            plan_pro.precio = 10.00
            plan_pro.limite_exportaciones_mensual = 15
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
