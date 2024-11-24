import pandas as pd

# Función para estandarizar nombres
def estandarizar_nombre(nombre):
    if pd.isnull(nombre):
        return ""
    return (
        nombre.strip()
        .upper()
        .replace(".", "")
        .replace(",", "")
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ú", "U")
        .replace(" D ", " ")  # Manejo de partículas
    )

# Cargar las bases
path_anid = r"C:\Users\Rodrigo\Desktop\Roxana Files\Add databases\Github ANID\anid_filtrada_consolidada.xlsx"
path_maestra = r"C:\Users\Rodrigo\Desktop\Roxana Files\base_maestra\base_maestra.xlsx"

anid_filtrada = pd.read_excel(path_anid)
base_maestra = pd.read_excel(path_maestra)

# Estandarizar nombres
anid_filtrada['NOMBRE_RESPONSABLE'] = anid_filtrada['NOMBRE_RESPONSABLE'].apply(estandarizar_nombre)
base_maestra['NOMBRE_ESTANDARIZADO'] = base_maestra['NOMBRE'].apply(estandarizar_nombre)

# Crear conjunto de nombres únicos estandarizados
nombres_anid = set(anid_filtrada['NOMBRE_RESPONSABLE'])
nombres_maestra = set(base_maestra['NOMBRE_ESTANDARIZADO'])

# Identificar nombres coincidentes
coincidencias = nombres_maestra.intersection(nombres_anid)

# Crear DataFrame de coincidencias
df_coincidencias = pd.DataFrame({'Nombre Maestra': list(coincidencias)})

# Exportar las coincidencias
output_path_coincidencias = r"C:\Users\Rodrigo\Desktop\Roxana Files\base_maestra\coincidencias.xlsx"
df_coincidencias.to_excel(output_path_coincidencias, index=False)

print(f"Coincidencias guardadas en: {output_path_coincidencias}")
