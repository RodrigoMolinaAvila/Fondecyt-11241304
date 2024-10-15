import os

# Ruta base, debe ser tu carpeta actual 'Roxana Files' en el entorno de trabajo
base_dir = os.path.abspath(".")

# Estructura de carpetas
directories = [
    os.path.join(base_dir, "Scopus"),
    os.path.join(base_dir, "map_visualization"),
    os.path.join(base_dir, "map_visualization", "mapas"),
    os.path.join(base_dir, "map_visualization", "data")
]

# Crear las carpetas si no existen
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Carpeta creada: {directory}")
    else:
        print(f"La carpeta ya existe: {directory}")

print("Estructura de carpetas ajustada correctamente.")
