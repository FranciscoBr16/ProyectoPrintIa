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
        return None
        
    api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    prompt_text = f"[INST] Eres un experto en impresión 3D. Voy a imprimir un modelo de: '{prompt_modelo}'. Dame exactamente 4 recomendaciones cortas en español (Escala, Material, Relleno, Soportes) en formato de viñetas HTML (<li>...</li>). No incluyas explicaciones ni etiquetas <ul>, solo los 4 <li>. [/INST]"
    
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.5,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                texto_generado = result[0].get("generated_text", "").strip()
                
                lineas = [line.strip() for line in texto_generado.split('\n') if line.strip()]
                html_recs = ""
                for line in lineas[:4]: # Solo tomamos 4 max
                    if "<li>" in line:
                        html_recs += line + "\n"
                    else:
                        line = line.lstrip("-* ").strip()
                        html_recs += f"<li>{line}</li>\n"
                        
                if html_recs:
                    return html_recs
    except Exception as e:
        print(f"Error IA: {e}")
        
    return None
