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

# Generar un DataFrame con los nombres que no hicieron "match" con Scopus
df_no_match = df_maestra[~df_maestra['FOLIO'].isin(df_merged_comb['FOLIO'])]

# Guardar el DataFrame de los nombres no encontrados en Scopus en un archivo CSV y XLSX
df_no_match_csv_path = 'nombres_no_identificados.csv'
df_no_match_xlsx_path = 'nombres_no_identificados.xlsx'
df_no_match.to_csv(df_no_match_csv_path, index=False)
df_no_match.to_excel(df_no_match_xlsx_path, index=False)

print(f"Datos de los nombres no identificados guardados en: {df_no_match_csv_path} y {df_no_match_xlsx_path}")
