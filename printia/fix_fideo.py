from app import create_app, db
from app.models import Modelo
import os
from flask import current_app
from stl import mesh

app = create_app()
with app.app_context():
    modelos = Modelo.query.order_by(Modelo.id_modelo.desc()).limit(5).all()
    for m in modelos:
        print(f"ID: {m.id_modelo}, dim_x: {m.dim_x}, dim_y: {m.dim_y}, dim_z: {m.dim_z}")
        if m.dim_x == 9.0 and m.dim_y < 1.0: # If it's already 9.0 but Y and Z are small (0.3)
            print("Encontrado modelo achatado que fue devuelto a 9.0!")
            ruta = os.path.join(current_app.config['UPLOAD_FOLDER_MODELOS'], m.archivo_url)
            if os.path.exists(ruta):
                malla = mesh.Mesh.from_file(ruta)
                # Expand Y and Z by 11.11 to unsquash
                malla.vectors[:, :, 1] *= 11.11
                malla.vectors[:, :, 2] *= 11.11
                malla.save(ruta)
                
            m.dim_y = 3.0
            m.dim_z = 3.0
            db.session.commit()
            print("Arreglado!")
