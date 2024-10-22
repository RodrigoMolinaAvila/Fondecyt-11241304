import requests
import pandas as pd
import time

# Credenciales API
API_KEY = 'd39ffc2cebca1f889ca33a5e4a2faca0'
INST_TOKEN = '6be954154f4ae63ee238d46af2be2dd1'

# Definir los headers con tu API Key y token
headers = {
    'X-ELS-APIKey': API_KEY,
    'X-ELS-Insttoken': INST_TOKEN
}

# Función para buscar autores en Scopus usando apellido y nombre en la consulta
def buscar_autor_por_nombre(nombre, apellido):
    # URL con la estructura que mencionas, donde buscamos por apellido y nombre
    url = f"https://api.elsevier.com/content/search/author?query=authlast({apellido})%20and%20authfirst({nombre})"
    
    # Hacer la solicitud a la API de Scopus
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            autores = data.get('search-results', {}).get('entry', [])
            resultados = []
            for autor in autores:
                # Extracción de todas las variables posibles
                scopus_id = autor.get('dc:identifier', '').replace('AUTHOR_ID:', '')
                eid = autor.get('eid', '')
                orcid = autor.get('orcid', '')
                numero_publicaciones = autor.get('document-count', 0)
                cited_by_count = autor.get('cited-by-count', 0)
                citation_count = autor.get('citation-count', 0)
                afiliacion_actual = autor.get('affiliation-current', {}).get('affiliation-name', '')
                pais_afiliacion = autor.get('affiliation-current', {}).get('affiliation-country', '')
                nombre_completo_scopus = autor.get('preferred-name', {}).get('given-name', '') + ' ' + autor.get('preferred-name', {}).get('surname', '')

                # Rango de publicación
                publication_range_start = autor.get('publication-range', {}).get('start', '')
                publication_range_end = autor.get('publication-range', {}).get('end', '')

                # Áreas temáticas, manejo del caso en que subject-area no sea una lista/dict
                subject_areas = autor.get('subject-area', [])
                if isinstance(subject_areas, list):
                    areas_tematicas = ", ".join([area.get('subject-area', {}).get('$', '') for area in subject_areas])
                else:
                    areas_tematicas = ''  # Si no hay áreas temáticas o el formato es incorrecto

                # Historial de afiliaciones
                historial_afiliaciones = ", ".join([afiliacion.get('affiliation-name', '') for afiliacion in autor.get('affiliation-history', {}).get('affiliation', [])])

                # Añadir los resultados
                resultados.append({
                    'scopus_id': scopus_id,
                    'eid': eid,
                    'orcid': orcid,
                    'numero_publicaciones': numero_publicaciones,
                    'cited_by_count': cited_by_count,
                    'citation_count': citation_count,
                    'afiliacion_actual': afiliacion_actual,
                    'pais_afiliacion': pais_afiliacion,
                    'nombre_completo_scopus': nombre_completo_scopus,
                    'publication_range_start': publication_range_start,
                    'publication_range_end': publication_range_end,
                    'areas_tematicas': areas_tematicas,
                    'historial_afiliaciones': historial_afiliaciones,
                    'nombre_busqueda': f"{nombre} {apellido}"  # Para saber qué nombre generó el resultado
                })
            return pd.DataFrame(resultados)
        except ValueError:
            print("Error: La respuesta no es un JSON válido.")
            return pd.DataFrame()
    else:
        print(f"Error al buscar autores: Código de estado {response.status_code}")
        return pd.DataFrame()

# Función para generar todas las combinaciones de nombres
def generar_combinaciones(row):
    combinaciones = [
        (row['Primer_Nombre'], row['Apellido_Paterno']),
        (row['Primer_Nombre'], row['Apellido_Materno']),
        (row['Segundo_Nombre'], row['Apellido_Paterno']),
        (row['Segundo_Nombre'], row['Apellido_Materno']),
        (f"{row['Primer_Nombre']} {row['Segundo_Nombre']}", row['Apellido_Paterno']),
        (f"{row['Primer_Nombre']} {row['Segundo_Nombre']}", row['Apellido_Materno'])
    ]
    return combinaciones

# Cargar el archivo Excel
file_path = r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\Scopus\maestra.xlsx'
df_base_maestra = pd.read_excel(file_path, sheet_name='BaseMaestra')

# Parámetros de control
realizar_todas = False  # Cambiar a True para procesar todos los registros
num_solicitudes = 15  # Número de solicitudes a realizar (solo si realizar_todas es False)
tiempo_pausa = 1  # Pausa entre cada solicitud (en segundos)

# Determinar el número de registros a procesar
if realizar_todas:
    max_solicitudes = len(df_base_maestra)  # Procesar todos los registros
else:
    max_solicitudes = min(num_solicitudes, len(df_base_maestra))  # Limitar a las primeras 'num_solicitudes'

# Almacenar todos los resultados de búsqueda
resultados_busqueda = []
total_solicitudes = 0  # Contador de solicitudes realizadas

# Bucle para realizar las solicitudes usando todas las combinaciones
for index, row in df_base_maestra.iterrows():
    if total_solicitudes >= max_solicitudes:
        break

    combinaciones_nombres = generar_combinaciones(row)

    for nombre, apellido in combinaciones_nombres:
        print(f"Buscando en Scopus: {nombre} {apellido} ({total_solicitudes+1}/{max_solicitudes})")

        # Realizar la búsqueda
        df_resultados = buscar_autor_por_nombre(nombre, apellido)
        time.sleep(tiempo_pausa)  # Pausa entre solicitudes

        # Si hay resultados, añadirlos
        if not df_resultados.empty:
            resultados_busqueda.append(df_resultados)

    # Incrementar el contador de solicitudes
    total_solicitudes += 1

# Si hay resultados de búsqueda, combinarlos en un DataFrame
if resultados_busqueda:
    df_resultados_finales = pd.concat(resultados_busqueda, ignore_index=True)
    
    # Guardar los resultados en un archivo Excel
    df_resultados_finales.to_excel("scopus_resultados.xlsx", index=False)
    print(f"Resultados guardados en 'scopus_resultados.xlsx'. Total de solicitudes realizadas: {total_solicitudes}")
else:
    print("No se encontraron resultados.")
