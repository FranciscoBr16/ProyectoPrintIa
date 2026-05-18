import datetime
import requests
import os
import mercadopago
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Modelo, Metrica, Usuario, Plan, Suscripcion, Valoracion
from app.utils import (
    guardar_avatar, 
    eliminar_avatar, 
    mejorar_prompt_con_ia, 
    generar_recomendaciones_ia
)

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas generales
    total_modelos = current_user.total_generados
    modelos_mes = current_user.generados_mes
    
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
        if current_user.total_generados >= 1:
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
        if current_user.total_generados >= 1:
            flash('Límite de créditos alcanzado (1/1). Pásate a PRO para continuar.', 'error')
            return redirect(url_for('main.planes'))
    else:
        # Límite basado en columna modelos_restantes
        if suscripcion.modelos_restantes <= 0:
            flash('Límite de créditos alcanzado (0/15).', 'error')
            return redirect(url_for('main.dashboard'))
    
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
            
        # Generar recomendaciones de impresión con IA (solo para usuarios gratuitos)
        # Los usuarios PRO usarán el análisis visual con Gemini Vision después de la generación
        recomendaciones_html = None
        if not current_user.es_pro:
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
        
        # Guardar métrica (con o sin recomendaciones según el tipo de usuario)
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
            
    # Obtener comentarios/valoraciones ordenados del más antiguo al más nuevo
    comentarios = Valoracion.query.filter_by(id_modelo=id_modelo).order_by(Valoracion.fecha.asc()).all()
            
    # Verificar si el usuario actual es PRO (suscripción activa)
    es_pro = current_user.es_pro
    
    return render_template('modelo.html', modelo=modelo_obj, generando=generando, error_generacion=error_generacion, comentarios=comentarios, es_pro=es_pro)

@main_bp.route('/modelo/<int:id_modelo>/generar_recomendaciones', methods=['POST'])
@login_required
def generar_recomendaciones_pro(id_modelo):
    """Genera recomendaciones PRO analizando visualmente el thumbnail del modelo con Gemini Vision."""
    modelo_obj = Modelo.query.get_or_404(id_modelo)
    
    # Solo el dueño puede generar recomendaciones
    if modelo_obj.id_usuario != current_user.id_usuario:
        return jsonify({'error': 'No tienes permiso para generar recomendaciones de este modelo.'}), 403
    
    # Verificar que el usuario sea PRO
    if not current_user.es_pro:
        return jsonify({'error': 'Esta funcionalidad está disponible solo para usuarios PRO.'}), 403
    
    # Verificar que el modelo tenga thumbnail (ya terminó de generar)
    if not modelo_obj.imagen_url or modelo_obj.imagen_url == 'mock_image.png':
        return jsonify({'error': 'El modelo aún no tiene imagen de referencia. Espera a que termine de generarse.'}), 400
    
    from flask import current_app
    import os
    
    # Construir la ruta al archivo thumbnail
    thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER_THUMBNAILS'], modelo_obj.imagen_url)
    
    if not os.path.exists(thumb_path):
        return jsonify({'error': 'No se encontró la imagen del modelo en el servidor.'}), 404
    
    from app.utils import generar_recomendaciones_vision
    recomendaciones_html = generar_recomendaciones_vision(thumb_path, modelo_obj.prompt_texto)
    
    if not recomendaciones_html:
        return jsonify({'error': 'No se pudieron generar las recomendaciones. Intenta de nuevo más tarde.'}), 500
    
    # Guardar en la métrica existente del modelo
    metrica = Metrica.query.filter_by(id_modelo=id_modelo).order_by(Metrica.fecha_generacion.desc()).first()
    if metrica:
        metrica.recomendaciones = recomendaciones_html
    else:
        # Crear nueva métrica si no existe
        metrica = Metrica(
            id_modelo=id_modelo,
            recomendaciones=recomendaciones_html
        )
        db.session.add(metrica)
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'recomendaciones': recomendaciones_html})

@main_bp.route('/modelo/<int:id_modelo>/valorar', methods=['POST'])
@login_required
def valorar_modelo(id_modelo):
    puntuacion = request.form.get('puntuacion')
    comentario_texto = request.form.get('comentario')
    
    if not puntuacion:
        flash('Debes seleccionar una puntuación.', 'error')
        return redirect(url_for('main.modelo', id_modelo=id_modelo))
    
    # Verificar si el usuario ya valoró este modelo
    valoracion = Valoracion.query.filter_by(id_modelo=id_modelo, id_usuario=current_user.id_usuario).first()
    
    if valoracion:
        valoracion.puntuacion = int(puntuacion)
        valoracion.comentario = comentario_texto
        valoracion.fecha = datetime.datetime.utcnow()
        flash('Tu valoración ha sido actualizada.', 'success')
    else:
        nueva_valoracion = Valoracion(
            id_modelo=id_modelo,
            id_usuario=current_user.id_usuario,
            puntuacion=int(puntuacion),
            comentario=comentario_texto
        )
        db.session.add(nueva_valoracion)
        flash('¡Gracias por tu comentario!', 'success')
        
    db.session.commit()
    return redirect(url_for('main.modelo', id_modelo=id_modelo))

@main_bp.route('/modelo/<int:id_modelo>/feedback', methods=['POST'])
@login_required
def feedback_modelo(id_modelo):
    modelo_obj = Modelo.query.get_or_404(id_modelo)
    
    # Solo el dueño puede dar feedback de la generación
    if modelo_obj.id_usuario != current_user.id_usuario:
        return jsonify({'error': 'No tienes permiso para calificar la generación de este modelo.'}), 403
    
    data = request.get_json()
    feedback = data.get('feedback') # expect 1 or -1
    
    if feedback not in [1, -1, 0]:
        return jsonify({'error': 'Feedback no válido.'}), 400
        
    modelo_obj.feedback_ia = feedback
    db.session.commit()
    
    return jsonify({'status': 'success', 'feedback': feedback})

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

@main_bp.route('/modelo/<int:id_modelo>/descargar')
@login_required
def descargar_modelo(id_modelo):
    modelo_obj = Modelo.query.get_or_404(id_modelo)
    
    # Solo el dueño o modelos públicos pueden descargarse
    if not modelo_obj.es_publico and modelo_obj.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para descargar este modelo.', 'error')
        return redirect(url_for('main.galeria'))
    
    if not modelo_obj.archivo_url:
        flash('El modelo no tiene un archivo asociado.', 'error')
        return redirect(url_for('main.modelo', id_modelo=id_modelo))
    
    # Incrementar contador de descargas en la métrica más reciente
    metrica = Metrica.query.filter_by(id_modelo=id_modelo).order_by(Metrica.fecha_generacion.desc()).first()
    if metrica:
        if metrica.total_descargas is None:
            metrica.total_descargas = 0
        metrica.total_descargas += 1
        db.session.commit()
    
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER_MODELOS'],
        modelo_obj.archivo_url,
        as_attachment=True,
        download_name=f"{modelo_obj.titulo.replace(' ', '_')}.stl"
    )


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

@main_bp.route('/checkout', methods=['GET'])
@login_required
def checkout():
    # Inicializar el SDK de Mercado Pago
    sdk = mercadopago.SDK(current_app.config['MERCADOPAGO_ACCESS_TOKEN'])
    
    # Construir URLs absolutas manualmente para evitar problemas con url_for local
    base_url = request.url_root.rstrip('/')
        
    # Crear los datos de la preferencia
    preference_data = {
        "items": [
            {
                "id": "printia_pro",
                "title": "Suscripción PRO PrintIA (1 Mes)",
                "quantity": 1,
                "unit_price": 1000.0,  # 1000 moneda local (ej. ARS)
                "currency_id": "ARS"
            }
        ],
        "back_urls": {
            "success": f"{base_url}/checkout/success",
            "failure": f"{base_url}/checkout/failure",
            "pending": f"{base_url}/checkout/pending"
        },
        "auto_return": "approved",
        "external_reference": str(current_user.id_usuario),
        "statement_descriptor": "PRINTIA PRO"
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response.get("status") not in (200, 201):
            error_msg = preference_response.get('response', 'Error desconocido de MP')
            raise Exception(f"API Error: {error_msg}")
            
        preference = preference_response["response"]
        
        # Como estamos usando el Token de una Cuenta de Prueba, 
        # debemos usar el init_point normal (MP ya sabe que es falso)
        init_point = preference.get("init_point")
        if not init_point:
            raise Exception("No se recibió ningún init_point válido.")
        
        return render_template('checkout.html', init_point=init_point, preference_id=preference.get("id"))
    except Exception as e:
        print(f"Error creando preferencia de Mercado Pago: {e}")
        flash(f'Error MP: {str(e)}', 'error')
        return redirect(url_for('main.planes'))

@main_bp.route('/checkout/success')
@login_required
def checkout_success():
    # Ya no actualizamos la base de datos aquí, eso lo hace el Webhook.
    # Solo le damos un mensaje amable al usuario.
    flash('¡Pago procesado en Mercado Pago! Si fue aprobado, tu cuenta se actualizará a PRO en breves instantes.', 'success')
    return redirect(url_for('main.planes'))

@main_bp.route('/checkout/failure')
@login_required
def checkout_failure():
    flash('El pago fue rechazado. Intenta con otro medio de pago o revisa el saldo de tu tarjeta.', 'error')
    return redirect(url_for('main.checkout'))

@main_bp.route('/checkout/pending')
@login_required
def checkout_pending():
    flash('El pago está pendiente de aprobación por Mercado Pago. Te notificaremos pronto.', 'info')
    return redirect(url_for('main.checkout'))

@main_bp.route('/webhook-mercadopago', methods=['POST'])
def webhook_mercadopago():
    """
    Ruta que Mercado Pago llama cuando hay una actualización en el pago.
    """
    # Mercado Pago puede mandar info por query params (topic/id) o JSON
    data = request.json
    action = data.get("action")
    
    if action == "payment.created" or data.get("type") == "payment":
        payment_id = data.get("data", {}).get("id")
        if payment_id:
            try:
                sdk = mercadopago.SDK(current_app.config['MERCADOPAGO_ACCESS_TOKEN'])
                payment_response = sdk.payment().get(payment_id)
                payment_info = payment_response.get("response", {})
                
                # Si el pago fue aprobado, buscamos a qué usuario pertenece
                if payment_info.get("status") == "approved":
                    user_id = payment_info.get("external_reference")
                    
                    if user_id:
                        # Buscamos o creamos el plan PRO
                        plan_pro = Plan.query.filter_by(nombre_plan='PRO').first()
                        if not plan_pro:
                            plan_pro = Plan(nombre_plan='PRO', limite_exportaciones_mensual=15, precio=10.00)
                            db.session.add(plan_pro)
                            db.session.commit()
                        else:
                            plan_pro.precio = 10.00
                            plan_pro.limite_exportaciones_mensual = 15
                            db.session.commit()
                            
                        # Actualizamos la suscripción del usuario
                        suscripcion = Suscripcion.query.filter_by(id_usuario=int(user_id)).first()
                        hoy = datetime.date.today()
                        vencimiento = hoy + datetime.timedelta(days=30)
                        
                        if suscripcion:
                            suscripcion.id_plan = plan_pro.id_plan
                            suscripcion.fecha_inicio = hoy
                            suscripcion.fecha_fin = vencimiento
                            suscripcion.estado = 'Activa'
                            suscripcion.metodo_pago = 'Mercado Pago'
                            suscripcion.modelos_restantes = plan_pro.limite_exportaciones_mensual
                        else:
                            nueva_suscripcion = Suscripcion(
                                id_plan=plan_pro.id_plan,
                                id_usuario=int(user_id),
                                fecha_inicio=hoy,
                                fecha_fin=vencimiento,
                                estado='Activa',
                                metodo_pago='Mercado Pago',
                                modelos_restantes=plan_pro.limite_exportaciones_mensual
                            )
                            db.session.add(nueva_suscripcion)
                            
                        db.session.commit()
                        print(f"WEBHOOK: Usuario {user_id} actualizado a PRO exitosamente.")
            except Exception as e:
                print(f"WEBHOOK ERROR: {e}")
                
    # Siempre debemos responder 200 OK a Mercado Pago para que sepan que recibimos la notificación
    return jsonify({"status": "ok"}), 200

def distribucion_tiempos():
    rangos = [
        {"label": "< 20s", "min": 0, "max": 20},
        {"label": "20-30s", "min": 20, "max": 30},
        {"label": "30-40s", "min": 30, "max": 40},
        {"label": "40-50s", "min": 40, "max": 50},
        {"label": "50-60s", "min": 50, "max": 60},
        {"label": "60-70s", "min": 60, "max": 70},
        {"label": "70-80s", "min": 70, "max": 80},
        {"label": "80-90s", "min": 80, "max": 90},
        {"label": "90-100s", "min": 90, "max": 100},
        {"label": "100-110s", "min": 100, "max": 110},
        {"label": "110-120s", "min": 110, "max": 120},
        {"label": "> 120s", "min": 120, "max": 99999}
    ]
    resultados = []
    for r in rangos:
        count = Metrica.query.filter(Metrica.duracion >= r['min'], Metrica.duracion < r['max'], Metrica.exitoso == True).count()
        resultados.append(count)
    return {"labels": [r['label'] for r in rangos], "data": resultados}

def get_datos_semana():
    hoy = datetime.datetime.utcnow().date()
    labels = []
    valores = []
    for i in range(6, -1, -1):
        fecha = hoy - datetime.timedelta(days=i)
        count = Metrica.query.filter(func.date(Metrica.fecha_generacion) == fecha).count()
        labels.append(fecha.strftime('%d/%m'))
        valores.append(count)
    return {"labels": labels, "valores": valores}

def get_datos_anuales():
    hoy = datetime.datetime.utcnow()
    anio_actual = hoy.year
    labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    valores = [0] * 12
    
    # Consulta agrupada por mes
    res = db.session.query(
        func.month(Metrica.fecha_generacion),
        func.count(Metrica.id_metrica)
    ).filter(func.year(Metrica.fecha_generacion) == anio_actual).group_by(func.month(Metrica.fecha_generacion)).all()
    
    for mes, cant in res:
        if mes is not None:
            valores[int(mes)-1] = cant
            
    return {"labels": labels, "valores": valores}

@main_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.es_admin:
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('main.dashboard'))
    
    tiempos = db.session.query(
        func.avg(Metrica.duracion),
        func.max(Metrica.duracion),
        func.min(Metrica.duracion)
    ).filter(Metrica.exitoso == True).first()
    
    tiempo_promedio = float(tiempos[0] or 0)
    tiempo_max = float(tiempos[1] or 0)
    tiempo_min = float(tiempos[2] or 0)
    
    exitos = Metrica.query.filter_by(exitoso=True).count()
    errores = Metrica.query.filter_by(exitoso=False).count()
    
    # Total de descargas
    total_descargas = db.session.query(func.sum(Metrica.total_descargas)).scalar() or 0
    
    hoy_dt = datetime.datetime.utcnow()
    inicio_semana = hoy_dt - datetime.timedelta(days=hoy_dt.weekday())
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
    modelos_semana = Metrica.query.filter(Metrica.fecha_generacion >= inicio_semana).count()
    
    inicio_mes = hoy_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ultimo_dia_mes_ant = inicio_mes - datetime.timedelta(days=1)
    inicio_mes_ant = ultimo_dia_mes_ant.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    suscritos_mes_actual = Suscripcion.query.filter(Suscripcion.fecha_inicio >= inicio_mes.date()).count()
    suscritos_mes_anterior = Suscripcion.query.filter(
        Suscripcion.fecha_inicio >= inicio_mes_ant.date(),
        Suscripcion.fecha_inicio <= ultimo_dia_mes_ant.date()
    ).count()
    
    inicio_hoy = hoy_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    modelos_hoy_query = db.session.query(
        func.hour(Metrica.fecha_generacion),
        func.count(Metrica.id_metrica)
    ).filter(Metrica.fecha_generacion >= inicio_hoy).group_by(func.hour(Metrica.fecha_generacion)).all()
    
    labels_hoy = [f"{i:02d}:00" for i in range(24)]
    valores_hoy = [0] * 24
    for hora, cant in modelos_hoy_query:
        if hora is not None:
            valores_hoy[int(hora)] = cant

    likes = Modelo.query.filter_by(feedback_ia=1).count()
    dislikes = Modelo.query.filter_by(feedback_ia=-1).count()
    
    total_usuarios = Usuario.query.count()
    total_modelos = Modelo.query.count()
    usuarios_pro = Suscripcion.query.filter_by(estado='Activa').count()

    dist_tiempos = distribucion_tiempos()
    datos_semana = get_datos_semana()
    datos_anuales = get_datos_anuales()
    
    # Recomendaciones
    con_recom = Metrica.query.filter(Metrica.recomendaciones.isnot(None), Metrica.recomendaciones != "").count()
    sin_recom = Metrica.query.filter((Metrica.recomendaciones == None) | (Metrica.recomendaciones == "")).count()

    return render_template('admin_dashboard.html',
                           tiempo_promedio=round(tiempo_promedio, 2),
                           tiempo_max=round(tiempo_max, 2),
                           tiempo_min=round(tiempo_min, 2),
                           exitos=exitos,
                           errores=errores,
                           modelos_semana=modelos_semana,
                           suscritos_mes_actual=suscritos_mes_actual,
                           suscritos_mes_anterior=suscritos_mes_anterior,
                           labels_hoy=labels_hoy,
                           valores_hoy=valores_hoy,
                           likes=likes,
                           dislikes=dislikes,
                           total_usuarios=total_usuarios,
                           total_modelos=total_modelos,
                           usuarios_pro=usuarios_pro,
                           dist_labels=dist_tiempos['labels'],
                           dist_data=dist_tiempos['data'],
                           labels_semana=datos_semana['labels'],
                           valores_semana=datos_semana['valores'],
                           labels_anio=datos_anuales['labels'],
                           valores_anio=datos_anuales['valores'],
                           con_recom=con_recom,
                           total_descargas=total_descargas,
                           sin_recom=sin_recom)
