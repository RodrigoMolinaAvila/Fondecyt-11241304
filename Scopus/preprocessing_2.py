import pandas as pd

# Cargar la base de datos desde un archivo Excel
file_path = r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\resultados_scopus.xlsx'
df = pd.read_excel(file_path)

# Eliminar filas duplicadas basadas en la columna "Nombre BBDD Maestra"
unique_df = df.drop_duplicates(subset=['Nombre BBDD Maestra'])

# Guardar el nuevo DataFrame en un nuevo archivo Excel
new_file_path = r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\resultados_adicionales.xlsx'
unique_df.to_excel(new_file_path, sheet_name='Valores_Unicos', index=False)
