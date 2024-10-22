# Librerías necesarias
import pandas as pd
import unicodedata

# Función para normalizar nombres (eliminar tildes, convertir a mayúsculas, etc.)
def normalizar_nombre(nombre):
    if pd.isna(nombre):
        return ""
    nombre = nombre.upper()
    nombre = ''.join(c for c in unicodedata.normalize('NFKD', nombre) if unicodedata.category(c) != 'Mn')
    nombre = nombre.replace("-", " ")  # Reemplazar guiones por espacios
    return nombre.strip()

# Cargar los archivos (Base maestra desde la hoja "BaseMaestra" y Scopus)
df_maestra = pd.read_excel(r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\Scopus\maestra.xlsx', sheet_name='BaseMaestra')
df_scopus = pd.read_excel(r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\Scopus\scopus_resultados_beta.xlsx')

# Aplicar la normalización en la base maestra
df_maestra['Primer_Nombre'] = df_maestra['Primer_Nombre'].apply(normalizar_nombre)
df_maestra['Segundo_Nombre'] = df_maestra['Segundo_Nombre'].apply(normalizar_nombre)
df_maestra['Apellido_Paterno'] = df_maestra['Apellido_Paterno'].apply(normalizar_nombre)
df_maestra['Apellido_Materno'] = df_maestra['Apellido_Materno'].apply(normalizar_nombre)

# Aplicar la normalización en la base Scopus
df_scopus['nombre_completo_scopus'] = df_scopus['nombre_completo_scopus'].apply(normalizar_nombre)

# Crear combinaciones de nombres en la base maestra
df_maestra = df_maestra.assign(
    comb_1=df_maestra['Primer_Nombre'] + " " + df_maestra['Segundo_Nombre'] + " " + df_maestra['Apellido_Paterno'] + " " + df_maestra['Apellido_Materno'],
    comb_2=df_maestra['Primer_Nombre'] + " " + df_maestra['Apellido_Paterno'] + " " + df_maestra['Apellido_Materno'],
    comb_3=df_maestra['Segundo_Nombre'] + " " + df_maestra['Apellido_Paterno'] + " " + df_maestra['Apellido_Materno'],
    comb_4=df_maestra['Primer_Nombre'] + " " + df_maestra['Segundo_Nombre'] + " " + df_maestra['Apellido_Materno'] + " " + df_maestra['Apellido_Paterno'],
    comb_5=df_maestra['Primer_Nombre'] + " " + df_maestra['Apellido_Materno'] + " " + df_maestra['Apellido_Paterno'],
    comb_6=df_maestra['Segundo_Nombre'] + " " + df_maestra['Apellido_Materno'] + " " + df_maestra['Apellido_Paterno'],
    comb_7=df_maestra['Segundo_Nombre'] + " " + df_maestra['Primer_Nombre'] + " " + df_maestra['Apellido_Paterno'] + " " + df_maestra['Apellido_Materno'],
    comb_8=df_maestra['Primer_Nombre'] + " " + df_maestra['Segundo_Nombre'],
    comb_9=df_maestra['Segundo_Nombre'] + " " + df_maestra['Primer_Nombre'],
    comb_10=df_maestra['Primer_Nombre'] + " " + df_maestra['Apellido_Paterno'],
    comb_11=df_maestra['Segundo_Nombre'] + " " + df_maestra['Apellido_Paterno'],
    comb_12=df_maestra['Primer_Nombre'] + " " + df_maestra['Apellido_Materno'],
    comb_13=df_maestra['Segundo_Nombre'] + " " + df_maestra['Apellido_Materno']
)

# Inicializar un DataFrame vacío para almacenar los resultados del merge
df_merged_comb = pd.DataFrame()

# Realizar el merge con cada combinación de nombres
for col in ['comb_1', 'comb_2', 'comb_3', 'comb_4', 'comb_5', 'comb_6', 'comb_7', 'comb_8', 'comb_9', 'comb_10', 'comb_11', 'comb_12', 'comb_13']:
    temp_merged = pd.merge(df_maestra, df_scopus, how='left', left_on=col, right_on='nombre_completo_scopus')
    
    # Filtrar y priorizar registros que tienen Scopus ID válido
    temp_merged_valid_scopus = temp_merged[temp_merged['scopus_id'].notna()]
    
    # Concatena el DataFrame temporal con los resultados de merge previos
    df_merged_comb = pd.concat([df_merged_comb, temp_merged_valid_scopus], ignore_index=True)

# Eliminar duplicados si es necesario
df_merged_comb.drop_duplicates(subset=['FOLIO', 'nombre_completo_scopus'], inplace=True)

# Generar un identificador único para cada nombre entregado
df_merged_comb['ID_interno'] = pd.factorize(df_merged_comb['NOMBRE'])[0] + 1

# Definir un nuevo DataFrame estructurado con las columnas deseadas
df_final_output = pd.DataFrame({
    'ID interno': df_merged_comb['ID_interno'],
    'Nombre entregado': df_merged_comb['NOMBRE'],
    'Nombre consultado': df_merged_comb['nombre_completo_scopus'],
    'Modificación segunda iteración': '',  # Columna que puedes completar manualmente si es necesario
    'Número de coincidencias': df_merged_comb.groupby('ID_interno')['nombre_completo_scopus'].transform('count'),
    'Variantes del nombre': df_merged_comb['nombre_completo_scopus'],
    'Identificador Scopus': df_merged_comb['scopus_id'],
    'Orcid': df_merged_comb['orcid'],
    'Número de publicaciones': df_merged_comb['numero_publicaciones'],
    'Pregrado Final': df_merged_comb['Pregrado Final'],  # Información de la base maestra
    'UNIVERSIDAD_PROGRAMA': df_merged_comb['UNIVERSIDAD_PROGRAMA'],  # Información de la base maestra
    'Pertenece o no': (df_merged_comb['pais_afiliacion'] == 'Chile').astype(int),  # Si pertenece a Chile es 1, de lo contrario 0
    'Pais de afiliación': df_merged_comb['pais_afiliacion']
})

# Mostrar el nuevo DataFrame con el output deseado
print("Primeras filas del nuevo output:")
print(df_final_output.head())

# Guardar el resultado final en un archivo CSV
output_csv_path = 'output_final.csv'
df_final_output.to_csv(output_csv_path, index=False)

# Guardar el resultado en un archivo XLSX
output_xlsx_path = 'output_final.xlsx'
df_final_output.to_excel(output_xlsx_path, index=False)

print(f"Output final guardado en: {output_csv_path} y {output_xlsx_path}")

# Contar cuántos nombres de la base de datos maestra fueron identificados en Scopus
nombres_identificados = df_merged_comb['nombre_completo_scopus'].nunique()

# Total de nombres en la base maestra, utilizando comb_1 como referencia del total de nombres
total_nombres_maestra = df_maestra['comb_1'].nunique()

# Mostrar los resultados de coincidencias e identificación
print(f"Nombres identificados en Scopus: {nombres_identificados} de {total_nombres_maestra}")
print(f"Porcentaje de identificación: {nombres_identificados / total_nombres_maestra * 100:.2f}%")
