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
