import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Configuración desde .env
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as con:
        # 1. Asegurar que generaciones_usadas exista en usuarios (si no está ya)
        # MySQL no tiene 'IF NOT EXISTS' para columnas fácilmente sin un procedure, 
        # pero podemos intentar agregarlo y capturar el error si ya existe.
        try:
            con.execute(text("ALTER TABLE usuarios ADD COLUMN generaciones_usadas INT NOT NULL DEFAULT 0;"))
            print("- Columna 'generaciones_usadas' añadida a 'usuarios'.")
        except Exception:
            print("- La columna 'generaciones_usadas' ya existía en 'usuarios'.")

        # 2. Mover 'recomendaciones' de 'modelos' a 'metricas'
        # Primero agregar a metricas si no existe
        try:
            con.execute(text("ALTER TABLE metricas ADD COLUMN recomendaciones TEXT;"))
            print("- Columna 'recomendaciones' añadida a 'metricas'.")
        except Exception:
            print("- La columna 'recomendaciones' ya existía en 'metricas'.")

        # Intentar borrar de modelos (si existe)
        try:
            con.execute(text("ALTER TABLE modelos DROP COLUMN recomendaciones;"))
            print("- Columna 'recomendaciones' eliminada de 'modelos'.")
        except Exception:
            print("- La columna 'recomendaciones' ya no existía en 'modelos'.")

        con.commit()
    print("\n[OK] Migracion completada exitosamente.")
except Exception as e:
    print(f"[ERROR] Error durante la migracion: {e}")
