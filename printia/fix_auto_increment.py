from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Arreglar la columna id_suscripcion para que tenga AUTO_INCREMENT
        db.session.execute(text("ALTER TABLE suscripciones MODIFY id_suscripcion INT AUTO_INCREMENT;"))
        db.session.commit()
        print("La columna 'id_suscripcion' ahora tiene AUTO_INCREMENT.")
    except Exception as e:
        print(f"Error al alterar la tabla: {e}")
