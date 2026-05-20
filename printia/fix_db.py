from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE metricas ADD COLUMN total_descargas INT DEFAULT 0;"))
        db.session.commit()
        print("Columna 'total_descargas' agregada exitosamente.")
    except Exception as e:
        print(f"Error al alterar la tabla: {e}")
