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
                    # Remove any existing <li> or </li> tags to prevent nesting
                    clean = re.sub(r'</?li>', '', clean, flags=re.IGNORECASE).strip()
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
    optimizado para Meshy AI text-to-3D.
    
    IMPORTANTE: Meshy tiene un límite de 600 caracteres para el prompt.
    El prompt mejorado se trunca inteligentemente si excede ese límite.

    Retorna una tupla: (prompt_mejorado: str, fue_mejorado: bool)
    """
    MESHY_CHAR_LIMIT = 600

    SUFIJO_TECNICO = (
        ", 3D printable, single solid mesh, flat stable base, "
        "no floating parts, manifold geometry, FDM optimized"
    )

    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("GEMINI_API_KEY no configurada, usando sufijo técnico de fallback.")
        fallback = prompt_usuario.strip() + SUFIJO_TECNICO
        return (fallback[:MESHY_CHAR_LIMIT], False)

    system_instruction = (
        "You are an expert prompt engineer specialized in Meshy AI text-to-3D generation.\n\n"

        "YOUR TASK: Transform the user's description into a concise, highly effective English prompt "
        "for Meshy AI. The prompt MUST be under 580 characters (hard limit).\n\n"

        "USE THIS EXACT FORMULA (in this order):\n"
        "[SUBJECT] + [SHAPE & STRUCTURE] + [MATERIAL/TEXTURE] + [ART STYLE] + [3D PRINTING CONSTRAINTS]\n\n"

        "CRITICAL RULES:\n"
        "1. EXACTLY ONE OBJECT: Always describe exactly ONE single object, centered and isolated. "
        "Start with 'A single...' or 'One...'. NEVER use plural nouns. "
        "If the user says 'a dinosaur', write 'A single T-Rex dinosaur' NOT 'dinosaurs'.\n"
        "2. SUBJECT FIRST: The very first words MUST name the exact object. "
        "Example: 'A single medieval broadsword...' not 'A highly detailed masterpiece of...'\n"
        "3. ONLY THE REQUESTED OBJECT: If user says 'sword', output ONLY the sword. "
        "NEVER add humans, hands, holders, pedestals, backgrounds, scenery, or any extra objects. "
        "NEVER duplicate the subject — only one instance of the object.\n"
        "4. DESCRIBE GEOMETRY PRECISELY: Use concrete shape words (cylindrical, tapered, rounded, faceted, "
        "angular, beveled, ribbed, grooved, flat-bottomed). The AI builds from geometry descriptions.\n"
        "5. SPECIFIC MATERIALS: Use precise material names (brushed steel, cracked leather, polished obsidian, "
        "weathered oak wood, matte ceramic) instead of vague words like 'nice' or 'beautiful'.\n"
        "6. INCLUDE ART STYLE: Always specify one clear style (realistic, cartoon, low-poly, stylized, "
        "hand-painted, cel-shaded, Pixar style, anime style, miniature figurine style).\n"
        "7. ABSOLUTELY NO DEBRIS: The output must be ONE clean object with zero scattered fragments, "
        "particles, crumbs, or disconnected tiny pieces around it. Everything must be fused into one mesh.\n"
        "8. END WITH THESE EXACT KEYWORDS: Always end with: 'one single object, centered, clean solid mesh, "
        "flat stable base, no floating parts, no debris, no fragments, no duplicates, watertight, FDM printable'.\n\n"

        "SPECIAL CASES:\n"
        "- CONTAINERS (vase, cup, holder, pot): MUST describe 'hollow interior with thick walls' explicitly. "
        "Say 'thick-walled container shaped like [X] on the outside, with a deep open cavity on top'.\n"
        "- LIDS/CAPS/COVERS (bottle cap, lid, plug, stopper): Describe as 'a short hollow cylinder, "
        "open on one end like a small cup or thimble, with thick walls and a flat closed top. "
        "The outside has knurled/ridged grip texture. The inside is a smooth hollow cavity that fits "
        "over a cylindrical neck.' NEVER describe a cap as solid — it MUST be hollow to fit on something.\n"
        "- STANDS/MOUNTS: Describe as 'single solid monolithic block/wedge with a groove'. "
        "NEVER include the device it holds.\n"
        "- CHARACTERS/CREATURES: Use 'a single [creature], static standing pose, feet flat on ground, "
        "arms close to body, centered composition'. For figurines add 'miniature figurine style'. "
        "NEVER generate multiple creatures or a herd/pack.\n"
        "- KEYCHAINS: Describe the main shape as a small 3D object (not flat!) with a solid closed loop "
        "or ring hole at the top for attaching to a keyring. Example: 'a small cartoon chicken drumstick "
        "with a thick closed ring loop at the bone end for keychain attachment'. The loop must be part of "
        "the same solid mesh, not a separate ring.\n"
        "- FLAT/THIN OBJECTS (badges, coins, coasters): Describe as 'flat disc/rectangle, "
        "X mm thick, with raised/embossed surface details'. Add 'no overhangs, printable flat on bed'.\n\n"

        "QUALITY KEYWORDS (use 2-3 max, not all): highly detailed, clean defined geometry, "
        "sharp details, professional 3D model, intricate surface detail.\n\n"

        "BAD PROMPT EXAMPLE (too vague, too long):\n"
        "'A stunningly beautiful and absolutely magnificent masterpiece of a sword that is incredibly "
        "amazing with wonderful details and epic proportions...'\n\n"

        "GOOD PROMPT EXAMPLE (specific, structured, concise):\n"
        "'A single T-Rex dinosaur in a static standing pose, feet flat on the ground, mouth slightly open "
        "showing teeth. Muscular body with textured scaly skin, small forearms, thick tail for balance. "
        "Realistic style, highly detailed. One single object, centered, solid mesh, flat stable base, "
        "no floating parts, no duplicates, watertight, FDM printable.'\n\n"

        "OUTPUT: Return ONLY the improved prompt. No explanations, no quotes, no formatting."
    )

    user_message = f"User's object description (may be in Spanish): \"{prompt_usuario}\""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers_api = {"Content-Type": "application/json"}
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
            "temperature": 0.3,
            "maxOutputTokens": 200,
            "topP": 0.85
        }
    }

    try:
        response = requests.post(url, headers=headers_api, params=params, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            prompt_mejorado = (
                data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                    .strip()
            )
            # Limpiar comillas envolventes si Gemini las agrega
            if prompt_mejorado.startswith('"') and prompt_mejorado.endswith('"'):
                prompt_mejorado = prompt_mejorado[1:-1].strip()
            if prompt_mejorado.startswith("'") and prompt_mejorado.endswith("'"):
                prompt_mejorado = prompt_mejorado[1:-1].strip()

            if prompt_mejorado:
                # Truncar inteligentemente al límite de Meshy (cortar en último punto o coma)
                if len(prompt_mejorado) > MESHY_CHAR_LIMIT:
                    truncated = prompt_mejorado[:MESHY_CHAR_LIMIT]
                    # Buscar el último punto, coma o punto y coma para cortar limpiamente
                    last_clean_break = max(
                        truncated.rfind('. '),
                        truncated.rfind(', '),
                        truncated.rfind('; ')
                    )
                    if last_clean_break > MESHY_CHAR_LIMIT * 0.6:
                        prompt_mejorado = truncated[:last_clean_break + 1].strip()
                    else:
                        prompt_mejorado = truncated.strip()
                
                return (prompt_mejorado, True)
        else:
            print(f"Error Gemini API ({response.status_code}): {response.text[:200]}")
    except Exception as e:
        print(f"Excepción al llamar a Gemini: {e}")

    # Fallback: prompt original + sufijo técnico, respetando límite
    fallback = prompt_usuario.strip() + SUFIJO_TECNICO
    return (fallback[:MESHY_CHAR_LIMIT], False)

