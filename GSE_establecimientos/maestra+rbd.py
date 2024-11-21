import pandas as pd

# Cargar la base de datos maestra
maestra_path = r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\GSE_establecimientos\maestra_procesada.xlsx'
maestra_df = pd.read_excel(maestra_path)

# Depurar la variable "RBD Colegio Secundario" eliminando el .0
maestra_df['RBD Colegio Secundario'] = maestra_df['RBD Colegio Secundario'].astype(str).str.replace('.0', '', regex=False)

# Cargar la segunda base de datos
resultados_path = r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\GSE_establecimientos\resultados_combinados.xlsx'
resultados_df = pd.read_excel(resultados_path)

# Convertir la columna 'RBD' a string
resultados_df['RBD'] = resultados_df['RBD'].astype(str)

# Integrar la información de la segunda base de datos en la base de datos maestra
merged_df = maestra_df.merge(resultados_df, left_on='RBD Colegio Secundario', right_on='RBD', how='left')

# Guardar la base de datos integrada
output_path = r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\GSE_establecimientos\maestra_rbd.xlsx'
merged_df.to_excel(output_path, index=False)