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
    # Extensiones permitidas
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    # Tamaño máximo: 2 MB
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024