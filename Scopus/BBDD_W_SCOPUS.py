import pandas as pd
import unicodedata

# Función para normalizar nombres (eliminar tildes, convertir a mayúsculas, etc.)
def normalizar_nombre(nombre):
    if pd.isna(nombre):
        return ""
    nombre = nombre.upper()
    nombre = ''.join(c for c in unicodedata.normalize('NFKD', nombre) if unicodedata.category(c) != 'Mn')
    return nombre.replace("-", " ").strip()

# Cargar las bases de datos
df_maestra = pd.read_excel('./Scopus/maestra_procesada.xlsx')
df_scopus = pd.read_excel('./Scopus/scopus_resultados_beta.xlsx')

# Normalizar nombres y afiliaciones en ambas bases de datos
df_maestra['Primer_Nombre'] = df_maestra['Primer_Nombre'].apply(normalizar_nombre)
df_maestra['Segundo_Nombre'] = df_maestra['Segundo_Nombre'].apply(normalizar_nombre)
df_maestra['Apellido_Paterno'] = df_maestra['Apellido_Paterno'].apply(normalizar_nombre)
df_maestra['Apellido_Materno'] = df_maestra['Apellido_Materno'].apply(normalizar_nombre)
df_maestra['UNIVERSIDAD_PROGRAMA'] = df_maestra['UNIVERSIDAD_PROGRAMA'].apply(normalizar_nombre)
df_maestra['Pregrado Final'] = df_maestra['Pregrado Final'].apply(normalizar_nombre)

df_scopus['nombre_completo_scopus'] = df_scopus['nombre_completo_scopus'].apply(normalizar_nombre)
df_scopus['afiliacion_actual'] = df_scopus['afiliacion_actual'].apply(normalizar_nombre)

# Generar un identificador único para cada nombre en la base maestra
df_maestra['ID_interno'] = pd.factorize(df_maestra['NOMBRE'])[0] + 1

# Inicializar DataFrame para almacenar resultados de matches
resultados_matches = []

# Iterar sobre cada registro de la base maestra y buscar coincidencias en Scopus
for _, row in df_maestra.iterrows():
    encontrado = False
    
    # Filtrar los registros de Scopus que podrían coincidir
    df_scopus_match = df_scopus[
        (df_scopus['nombre_completo_scopus'].str.contains(row['Primer_Nombre'])) &
        (df_scopus['nombre_completo_scopus'].str.contains(row['Apellido_Paterno']))
    ]
    
    # Verificar coincidencia con afiliación y detalles de nombres
    for _, scopus_row in df_scopus_match.iterrows():
        # Determinar coincidencia de cada componente del nombre
        coincidencias_nombre = {
            'primer_nombre': int(row['Primer_Nombre'] in scopus_row['nombre_completo_scopus']),
            'segundo_nombre': int(row['Segundo_Nombre'] in scopus_row['nombre_completo_scopus']),
            'apellido_paterno': int(row['Apellido_Paterno'] in scopus_row['nombre_completo_scopus']),
            'apellido_materno': int(row['Apellido_Materno'] in scopus_row['nombre_completo_scopus'])
        }
        
        # Determinar coincidencia en afiliaciones
        coincidencia_afiliacion = {
            'universidad_programa': int(row['UNIVERSIDAD_PROGRAMA'] in scopus_row['afiliacion_actual']),
            'pregrado_final': int(row['Pregrado Final'] in scopus_row['afiliacion_actual'])
        }
        
        # Calcular puntajes
        puntaje_nombre = sum(coincidencias_nombre.values())   # Puntaje basado en coincidencia de nombre
        puntaje_afiliacion = sum(coincidencia_afiliacion.values())  # Puntaje basado en coincidencia de afiliación
        puntaje_total = puntaje_nombre + puntaje_afiliacion  # Puntaje total

        # Clasificación del tipo de match en base al puntaje total
        tipo_match = "Exacto" if puntaje_total == 6 else "Parcial"
        
        # Guardar los detalles de la coincidencia
        resultados_matches.append({
            'ID_interno': row['ID_interno'],
            'Nombre BBDD Maestra': row['NOMBRE'],
            'Nombre Scopus': scopus_row['nombre_completo_scopus'],
            'Afiliación Scopus': scopus_row['afiliacion_actual'],
            'Identificador Scopus': scopus_row['scopus_id'],
            'Orcid': scopus_row['orcid'],
            'Número de publicaciones': scopus_row['numero_publicaciones'],
            'UNIVERSIDAD_PROGRAMA': row['UNIVERSIDAD_PROGRAMA'],
            'Pregrado Final': row['Pregrado Final'],
            'Tipo de Match': tipo_match,
            'Coincidencia Nombre': coincidencias_nombre,
            'Coincidencia Afiliación': coincidencia_afiliacion,
            'Puntaje Nombre': puntaje_nombre,
            'Puntaje Afiliación': puntaje_afiliacion,
            'Puntaje Total': puntaje_total,
            'Pertenece o no': int(scopus_row['pais_afiliacion'] == 'Chile'),
            'Pais de afiliación': scopus_row['pais_afiliacion']
        })
        encontrado = True

    # Si no hay coincidencias, registrar como "No encontrado"
    if not encontrado:
        resultados_matches.append({
            'ID_interno': row['ID_interno'],
            'Nombre BBDD Maestra': row['NOMBRE'],
            'Nombre Scopus': 'No encontrado',
            'Afiliación Scopus': 'N/A',
            'Identificador Scopus': 'N/A',
            'Orcid': 'N/A',
            'Número de publicaciones': 'N/A',
            'UNIVERSIDAD_PROGRAMA': row['UNIVERSIDAD_PROGRAMA'],
            'Pregrado Final': row['Pregrado Final'],
            'Tipo de Match': 'No encontrado',
            'Coincidencia Nombre': {'primer_nombre': 0, 'segundo_nombre': 0, 'apellido_paterno': 0, 'apellido_materno': 0},
            'Coincidencia Afiliación': {'universidad_programa': 0, 'pregrado_final': 0},
            'Puntaje Nombre': 0,
            'Puntaje Afiliación': 0,
            'Puntaje Total': 0,
            'Pertenece o no': 'N/A',
            'Pais de afiliación': 'N/A'
        })

# Convertir resultados a DataFrame
df_resultados = pd.DataFrame(resultados_matches)

# Filtrar resultados únicos por nombre y afiliación
df_distinct_resultados = df_resultados[df_resultados['Nombre Scopus'] != 'No encontrado'].drop_duplicates(
    subset=['ID_interno', 'Nombre Scopus', 'Afiliación Scopus']
)

# Separar registros encontrados y no encontrados
df_encontrados = df_resultados[df_resultados['Nombre Scopus'] != 'No encontrado']
df_no_encontrados = df_resultados[df_resultados['Nombre Scopus'] == 'No encontrado']

# Guardar en un archivo Excel con múltiples hojas
with pd.ExcelWriter("output_final_resultados.xlsx") as writer:
    df_resultados.to_excel(writer, sheet_name="Resultados completos", index=False)
    df_distinct_resultados.to_excel(writer, sheet_name="Resultados únicos", index=False)
    df_no_encontrados.to_excel(writer, sheet_name="No encontrados", index=False)

print("Archivo con resultados guardado en 'output_final_resultados.xlsx'.")

# Resumen de coincidencias y porcentaje de identificación en base a los resultados únicos
total_nombres_maestra = df_maestra['ID_interno'].nunique()
nombres_identificados = df_distinct_resultados['ID_interno'].nunique()

print(f"Nombres identificados en Scopus: {nombres_identificados} de {total_nombres_maestra}")
print(f"Porcentaje de identificación: {nombres_identificados / total_nombres_maestra * 100:.2f}%")
