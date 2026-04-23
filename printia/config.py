import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # === UPLOADS ===
    # Carpeta absoluta donde se guardan los avatars
    UPLOAD_FOLDER_AVATARS = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app', 'static', 'uploads', 'avatars'
    )
    # Carpeta absoluta donde se guardan los modelos 3D
    UPLOAD_FOLDER_MODELOS = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app', 'static', 'uploads', 'modelos'
    )
    # Extensiones permitidas para imágenes
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    # Extensiones permitidas para modelos 3D
    ALLOWED_MODEL_EXTENSIONS = {'stl', 'obj'}
    # Tamaño máximo: 2 MB (imágenes) — los modelos 3D pueden ser más grandes
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB para soportar STL grandes