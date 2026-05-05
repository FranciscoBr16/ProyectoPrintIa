import os
import uuid
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
    import requests
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
                        import re
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
        "You are an expert in 3D modeling and FDM 3D printing. "
        "Your task is to rewrite a user's description into a precise, technical English prompt "
        "for Meshy AI text-to-3D generation, optimized for FDM printability. "

        "STEP 1 - UNDERSTAND THE OBJECT'S PURPOSE: "
        "Before writing the prompt, identify what the object IS and what it needs to DO. "
        "If the object is a container, holder, vase, cup, bowl, organizer, or any vessel meant to hold things, "
        "it MUST have an open hollow interior cavity. Describe this cavity explicitly in the prompt "
        "(e.g. 'hollow interior', 'open top cavity', 'cylindrical hollow body'). "
        "Never fill in a functional cavity - that would destroy the object's purpose. "

        "STEP 2 - APPLY FDM PRINTABILITY RULES: "
        "1. NO FLOATING PARTS: every structural element must be physically fused to the main body. "
        "Separate pieces that float in mid-air or connect at a single thin point must be avoided. "
        "Attachments like loops or rings should be integrated as through-holes carved into the body. "
        "2. NATURAL STABILITY: the model must be able to stand on its own geometry on the print bed. "
        "Use the object's natural form to achieve this (e.g. a sitting dog rests on its haunches and tail, "
        "a vase rests on its base, a figure stands on its feet). "
        "Do NOT add a separate circular pedestal, display base, or platform unless the user explicitly requested one "
        "or the object has absolutely no natural flat contact area. "
        "If a minimal base is truly needed, describe it as a subtle integrated extension of the object itself, "
        "not as a generic disc. "
        "3. SELF-SUPPORTING GEOMETRY: avoid overhangs steeper than 45 degrees where possible. "
        "4. UNIFIED MANIFOLD MESH: describe one coherent watertight object, not an assembly of separate parts. "
        "5. PRINTABLE DETAILS: avoid extremely thin walls or fragile protrusions that would break when printed. "
        "6. STATIC STABLE POSE: for figures or characters, use a grounded, stable, static pose. "

        "Respond with ONLY the improved prompt text. No explanations, no quotes, no extra text."
    )

    user_message = f"User description (may be in Spanish): \"{prompt_usuario}\""

    import requests as req
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": gemini_key}
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 200,
            "topP": 0.9
        }
    }

    try:
        response = req.post(url, headers=headers, params=params, json=payload, timeout=15)
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
