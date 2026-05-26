import os
import uuid
import requests
import re
import base64
from werkzeug.utils import secure_filename
from flask import current_app


def extension_permitida(filename):
    """Verifica que la extensión esté en la lista blanca."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_IMAGE_EXTENSIONS']


def guardar_avatar(archivo, id_usuario):
    """
    Guarda un archivo de imagen con un nombre seguro y único.
    Devuelve el nombre del archivo guardado, o None si no es válido.
    """
    if not archivo or archivo.filename == '':
        return None
    
    if not extension_permitida(archivo.filename):
        return None
    
    # secure_filename limpia el nombre original (sin "../", caracteres raros, etc.)
    nombre_limpio = secure_filename(archivo.filename)
    extension = nombre_limpio.rsplit('.', 1)[1].lower()
    
    # Nombre único: user_{id}_{hash_corto}.{ext}
    # Usamos uuid para evitar colisiones y que no se cachee una imagen vieja
    nombre_final = f"user_{id_usuario}_{uuid.uuid4().hex[:8]}.{extension}"
    
    carpeta = current_app.config['UPLOAD_FOLDER_AVATARS']
    os.makedirs(carpeta, exist_ok=True)  # crea la carpeta si no existe
    
    ruta_completa = os.path.join(carpeta, nombre_final)
    archivo.save(ruta_completa)
    
    return nombre_final


def eliminar_avatar(nombre_archivo):
    """Elimina un avatar del disco si existe (para cuando se reemplaza)."""
    if not nombre_archivo:
        return
    
    ruta = os.path.join(current_app.config['UPLOAD_FOLDER_AVATARS'], nombre_archivo)
    if os.path.exists(ruta):
        try:
            os.remove(ruta)
        except OSError:
            pass 

def generar_recomendaciones_ia(prompt_modelo):
    """
    Llama a la API de HuggingFace para generar recomendaciones de impresión 3D
    basadas en el nombre/prompt del modelo.
    """
    hf_token = os.getenv('HF_TOKEN')
    if not hf_token:
        print("Error: HF_TOKEN no configurado.")
        return None
        
    # Usamos Zephyr-7b-beta que suele ser muy fiable en la API gratuita
    api_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json",
        "X-Wait-For-Model": "true"
    }
    
    prompt_text = f"<|system|>\nEres un experto en impresión 3D. Dame 4 recomendaciones cortas para imprimir este objeto. Solo devuelve las viñetas HTML <li>.</s>\n<|user|>\nObjeto: '{prompt_modelo}'</s>\n<|assistant|>\n"
    
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "top_p": 0.95,
            "return_full_text": False
        }
    }
    
    fallback_recs = "<li>Escala: 100%</li>\n<li>Material: PLA</li>\n<li>Relleno: 20%</li>\n<li>Soportes: Sí</li>"
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                texto_generado = result[0].get("generated_text", "").strip()
                
                # Limpieza mejorada
                lineas = [line.strip() for line in texto_generado.split('\n') if line.strip()]
                html_recs = ""
                count = 0
                for line in lineas:
                    if count >= 4: break
                    
                    line_lower = line.lower()
                    if "<li>" in line_lower:
                        # Extraer solo el contenido dentro de <li> si hay basura alrededor
                        match = re.search(r"<li>(.*?)</li>", line, re.IGNORECASE)
                        if match:
                            html_recs += f"<li>{match.group(1)}</li>\n"
                        else:
                            html_recs += line + "\n"
                        count += 1
                    elif line.startswith(('-', '*', '1.', '2.', '3.', '4.')) or ":" in line:
                        clean_line = re.sub(r'^[ \-*1-4.\d]+', '', line).strip()
                        if clean_line:
                            html_recs += f"<li>{clean_line}</li>\n"
                            count += 1
                        
                if html_recs:
                    return html_recs
        else:
            print(f"Error API HuggingFace ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Excepción en generar_recomendaciones_ia: {e}")
        
    return fallback_recs


def generar_recomendaciones_vision(ruta_imagen, prompt_modelo=""):

    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("Error: GEMINI_API_KEY no configurada para recomendaciones con visión.")
        return None

    # Leer y codificar la imagen en base64
    if not os.path.exists(ruta_imagen):
        print(f"Error: No se encontró la imagen del modelo en {ruta_imagen}")
        return None

    try:
        with open(ruta_imagen, 'rb') as f:
            imagen_bytes = f.read()
        imagen_b64 = base64.b64encode(imagen_bytes).decode('utf-8')
    except Exception as e:
        print(f"Error leyendo la imagen del modelo: {e}")
        return None

    # Determinar mime type real leyendo los primeros bytes (magic bytes)
    if imagen_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        mime_type = 'image/png'
    elif imagen_bytes.startswith(b'\xff\xd8\xff'):
        mime_type = 'image/jpeg'
    elif imagen_bytes.startswith(b'RIFF') and imagen_bytes[8:12] == b'WEBP':
        mime_type = 'image/webp'
    else:
        # Fallback por defecto si no lo reconoce, jpeg suele ser más perdonador
        mime_type = 'image/jpeg'

    system_instruction = (
        "Eres un ingeniero experto en impresión 3D FDM con más de 10 años de experiencia práctica. "
        "Tu tarea es analizar visualmente la imagen de un modelo 3D y generar recomendaciones técnicas "
        "precisas, específicas y accionables para lograr una impresión exitosa.\n\n"

        "ANÁLISIS VISUAL QUE DEBES REALIZAR:\n"
        "Antes de responder, evalúa mentalmente estos aspectos del modelo:\n"
        "- Geometría general: ¿Es sólido, hueco, orgánico, geométrico, decorativo o funcional?\n"
        "- Voladizos y puentes: ¿Hay ángulos mayores a 45° sin soporte debajo?\n"
        "- Estabilidad: ¿Tiene una base plana natural o necesita orientación especial?\n"
        "- Nivel de detalle: ¿Tiene texturas finas, inscripciones, partes delgadas o frágiles?\n"
        "- Tamaño inferido: ¿La forma sugiere una pieza pequeña, mediana o grande?\n\n"

        "RECOMENDACIONES QUE DEBES INCLUIR (en este orden):\n\n"

        "1. ORIENTACIÓN EN LA CAMA:\n"
        "   Indica exactamente cómo posicionar la pieza (qué cara hacia abajo) y por qué. "
        "Considera minimizar voladizos, maximizar adhesión y reducir la necesidad de soportes.\n\n"

        "2. SOPORTES:\n"
        "   Especifica si se necesitan o no. Si se necesitan, indica:\n"
        "   - Tipo recomendado: lineales, arbóreos (tree supports) o personalizados.\n"
        "   - Densidad sugerida: entre 10% y 25% según la complejidad.\n"
        "   - Zonas críticas donde aplicarlos.\n"
        "   - Si no se necesitan, explica brevemente por qué.\n\n"

        "3. MATERIAL:\n"
        "   Recomienda el filamento más adecuado considerando la forma y uso probable:\n"
        "   - PLA: piezas decorativas, prototipos, fácil impresión.\n"
        "   - PETG: piezas funcionales, algo de flexibilidad, resistencia a la humedad.\n"
        "   - ABS/ASA: resistencia mecánica y térmica, uso exterior.\n"
        "   - TPU: piezas flexibles o con necesidad de amortiguación.\n"
        "   - Resina (si aplica): alto detalle, piezas pequeñas.\n"
        "   Justifica tu elección según lo observado.\n\n"

        "4. ALTURA DE CAPA:\n"
        "   Recomienda un valor concreto en mm y explica el balance entre calidad y tiempo:\n"
        "   - 0.10–0.15 mm: máximo detalle, piezas pequeñas con texturas finas.\n"
        "   - 0.20 mm: balance estándar, recomendado para la mayoría de piezas.\n"
        "   - 0.25–0.30 mm: piezas grandes sin detalle fino, impresión rápida.\n\n"

        "5. GROSOR DE PARED (Perímetros / Wall loops):\n"
        "   Indica cuántos perímetros o el grosor en mm recomendado:\n"
        "   - Piezas decorativas: 2–3 perímetros (0.8–1.2 mm).\n"
        "   - Piezas funcionales o con roscas: 4–6 perímetros (1.6–2.4 mm).\n"
        "   - Piezas que soportan carga: ≥6 perímetros o hasta paredes sólidas.\n\n"

        "6. RELLENO (Infill):\n"
        "   Especifica porcentaje y patrón según el uso inferido:\n"
        "   - 0–10%: piezas puramente decorativas o huecas.\n"
        "   - 15–25%: uso general, buena relación resistencia/material.\n"
        "   - 30–50%: piezas funcionales con algo de carga.\n"
        "   - >50%: piezas estructurales o con alta carga mecánica.\n"
        "   Patrones: Grid/Lines para velocidad, Gyroid/Honeycomb para resistencia isotrópica, "
        "Cubic para resistencia omnidireccional.\n\n"

        "7. VELOCIDAD DE IMPRESIÓN:\n"
        "   Sugiere un rango en mm/s adecuado al nivel de detalle y material:\n"
        "   - Piezas con mucho detalle: 30–40 mm/s.\n"
        "   - Impresión estándar: 50–60 mm/s.\n"
        "   - Piezas grandes sin detalle: 80–100 mm/s.\n"
        "   Menciona si alguna zona (perímetros exteriores, puentes) requiere velocidad reducida.\n\n"

        "8. TEMPERATURA (si el material lo justifica):\n"
        "   Solo incluir si hay algo específico a destacar según la geometría "
        "(ej: puentes largos → bajar temperatura para mejor retracción, "
        "piezas con detalle fino → extremo inferior del rango del fabricante).\n\n"

        "9. POSPROCESADO (si aplica):\n"
        "    Solo si la geometría lo justifica: lijado, pintura, ensamblaje de partes, "
        "relleno de huecos con resina, acetona (ABS), etc.\n\n"

        "REGLAS DE FORMATO — MUY IMPORTANTE:\n"
        "- Devuelve entre 6 y 8 recomendaciones (prioriza las más relevantes para ESTE modelo específico).\n"
        "- Formato estricto: <li><b>Título:</b> Detalle técnico específico y justificado</li>\n"
        "- Cada recomendación debe ser concreta: incluye valores numéricos cuando corresponda.\n"
        "- NO repitas recomendaciones genéricas que apliquen a cualquier modelo. "
        "Cada punto debe estar justificado por algo que VEAS en la imagen.\n"
        "- Responde ÚNICAMENTE con los elementos <li>. Sin texto introductorio ni final.\n"
        "- Responde en español."
    )

    contexto_extra = f"\nContexto: el modelo fue generado con el prompt '{prompt_modelo}'." if prompt_modelo else ""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": gemini_key}
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": imagen_b64
                        }
                    },
                    {
                        "text": f"Analiza visualmente este modelo 3D y dame recomendaciones técnicas detalladas para imprimirlo en FDM.{contexto_extra}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1500,
            "topP": 0.9
        }
    }

    try:
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=45)
        if response.status_code == 200:
            data = response.json()
            texto_generado = (
                data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                    .strip()
            )

            if texto_generado:
                # Extraer todos los <li>...</li>
                items = re.findall(r'<li>(.*?)</li>', texto_generado, re.IGNORECASE | re.DOTALL)
                if items:
                    html_recs = "\n".join(f"<li>{item.strip()}</li>" for item in items[:7])
                    return html_recs
                
                # Fallback: si no encontró <li>, intentar parsear líneas
                lineas = [l.strip() for l in texto_generado.split('\n') if l.strip()]
                html_recs = ""
                count = 0
                for line in lineas:
                    if count >= 7:
                        break
                    clean = re.sub(r'^[\-*\d.]+\s*', '', line).strip()
                    if clean and len(clean) > 10:
                        html_recs += f"<li>{clean}</li>\n"
                        count += 1
                if html_recs:
                    return html_recs
                
                # Último recurso: si no se pudo parsear como lista, devolver el texto completo
                return f"<li><b>Análisis General:</b><br>{texto_generado}</li>"
            else:
                # Si no hay texto, comprobar si fue por bloqueo de seguridad
                finish_reason = data.get("candidates", [{}])[0].get("finishReason", "")
                if finish_reason == "SAFETY":
                    return "<li><b>Bloqueo de Seguridad:</b><br>La IA de Google no pudo analizar este modelo debido a sus políticas de seguridad (a veces ocurre con diseños cyberpunk o con partes puntiagudas por falso positivo).</li>"
                elif finish_reason:
                    return f"<li><b>Análisis Interrumpido:</b><br>La IA detuvo la generación (Motivo: {finish_reason}).</li>"
        else:
            print(f"Error Gemini Vision API ({response.status_code}): {response.text[:300]}")
    except Exception as e:
        print(f"Excepción en generar_recomendaciones_vision: {e}")

    return None


def mejorar_prompt_con_ia(prompt_usuario):
    """
    Usa Gemini Flash para transformar el prompt del usuario en un prompt técnico
    optimizado para generar modelos 3D imprimibles en FDM con Meshy AI.
    Si la llamada a Gemini falla, devuelve el prompt original con sufijo técnico.

    Retorna una tupla: (prompt_mejorado: str, fue_mejorado: bool)
    """
    SUFIJO_TECNICO = (
        ", 3D printable, single solid mesh, flat stable base, "
        "no floating parts, no overhangs, manifold geometry, "
        "optimized for FDM 3D printing"
    )

    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("GEMINI_API_KEY no configurada, usando sufijo técnico de fallback.")
        return (prompt_usuario.strip() + SUFIJO_TECNICO, False)

    system_instruction = (
        "You are an expert in 3D modeling, text-to-3D AI generation (like Meshy), and FDM 3D printing. "
        "Your task is to take a short user description and expand it into a HIGHLY DETAILED, extremely descriptive, "
        "and precise English prompt optimized for Meshy AI text-to-3D generation and FDM printability.\n\n"

        "STEP 1 - STRICT ADHERENCE TO USER INTENT (CRITICAL):\n"
        "1. NO UNREQUESTED OBJECTS: Focus 100% on the user's core request. DO NOT hallucinate extra props, scenery, backgrounds, humans, hands, or environments. If the user asks for a sword, generate ONLY the sword, not a warrior holding it. If the user asks for a hat, generate ONLY the hat, not a head wearing it.\n"
        "2. MAINTAIN IDENTITY: You can expand the visual style and textures, but NEVER change the core function or fundamental identity of the object.\n"
        "3. FRONT-LOAD SUBJECT: The very first sentence of your prompt MUST clearly declare the exact main object being modeled.\n\n"

        "STEP 2 - EXTREME DETAIL EXPANSION (VISUALS & STYLE):\n"
        "Expand the user's idea into a rich, vivid paragraph. Describe the exact shape, physical structure, surface texture, "
        "style (e.g., realistic, low-poly, sci-fi, fantasy, cartoon), and specific features. "
        "Include power keywords for 3D generation like: 'highly detailed', 'intricate design', 'masterpiece', "
        "'professional 3D model', 'clear defined geometry', 'sharp details'. "
        "Leave no visual detail to the imagination. The more descriptive you are about the geometry, the better Meshy will perform.\n\n"

        "STEP 3 - UNDERSTAND THE OBJECT'S PURPOSE:\n"
        "1. HOLDERS & CONTAINERS (CRITICAL): If the object is meant to hold things (pen holder, vase, cup, bowl, pot), it MUST be shaped like a thick-walled container. You MUST explicitly describe it with strong phrases like 'a very deep, wide, empty cylindrical hole carved perfectly into the top center, extending downwards to form a cup-like hollow interior for holding items'. If you just say 'a castle', the AI will make a solid castle. You must explicitly say 'a thick-walled cup/container shaped like a castle on the outside'. NEVER describe the top as flat or closed. The empty cavity is the most important feature.\n"
        "2. STANDS & MOUNTS (CRITICAL): If the object is a stand, mount, or holder for a device (like a phone stand), DO NOT generate the device itself! Describe ONLY the stand. To prevent AI from generating disconnected floating arms, you MUST describe stands as a 'single solid monolithic block', 'wedge shape', or 'thick unibody pyramid structure' with a groove or resting slot carved into it. Do not describe thin backrests or separate legs.\n\n"

        "STEP 4 - APPLY STRICT FDM PRINTABILITY RULES:\n"
        "1. NO FLOATING PARTS: Every element must be physically fused. No disconnected pieces.\n"
        "2. NATURAL STABILITY: The model must stand on its own geometry with a flat, stable bottom/base.\n"
        "3. SELF-SUPPORTING: Avoid severe overhangs; slope angles upwards.\n"
        "4. UNIFIED MANIFOLD MESH: One single coherent solid object.\n"
        "5. THICK & STURDY: No paper-thin walls or fragile, spindly protrusions.\n"
        "6. STATIC POSE: Characters/creatures must be in a grounded, stable, static pose.\n\n"

        "Combine the adherence rules, extreme visual detail, and structural rules into a single, cohesive, highly descriptive English prompt. "
        "Respond with ONLY the improved prompt text. No explanations, no quotes, no conversational filler."
    )

    user_message = f"User description (may be in Spanish): \"{prompt_usuario}\""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": gemini_key}
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        ],
        "generationConfig": {
            "temperature": 0.6,
            "maxOutputTokens": 400,
            "topP": 0.9
        }
    }

    try:
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            prompt_mejorado = (
                data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                    .strip()
            )
            if prompt_mejorado:
                return (prompt_mejorado, True)
        else:
            print(f"Error Gemini API ({response.status_code}): {response.text[:200]}")
    except Exception as e:
        print(f"Excepción al llamar a Gemini: {e}")

    # Fallback: sufijo técnico directo
    return (prompt_usuario.strip() + SUFIJO_TECNICO, False)

