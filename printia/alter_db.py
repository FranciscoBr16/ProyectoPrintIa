from sqlalchemy import create_engine, text

try:
    engine = create_engine("mysql+pymysql://root:root@localhost/printia")
    with engine.connect() as con:
        con.execute(text("ALTER TABLE modelos ADD COLUMN recomendaciones TEXT;"))
    print("Columnas agregadas exitosamente con root:root.")
except Exception as e:
    print(f"Error: {e}")
