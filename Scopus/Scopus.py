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
    # URL con todos los campos posibles a extraer
    url = (f"https://api.elsevier.com/content/search/author?"
           f"query=authlast({apellido})%20and%20authfirst({nombre})"
           f"&field=dc:identifier,eid,orcid,document-count,subject-area,"
           f"preferred-name,surname,given-name,initials,name-variant,"
           f"affiliation-current.affiliation-name,affiliation-current.affiliation-city,"
           f"affiliation-current.affiliation-country,affiliation-current.affiliation-id,"
           f"affiliation-current.affiliation-url,"
           f"affiliation-history.affiliation-name,"
           f"affiliation-history.affiliation-country,"
           f"affiliation-history.affiliation-id,"
           f"coauthor-count")  # Incluye el campo de coautoría
    
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
                cited_by_count = autor.get('cited-by-count', 0)  # Puede no estar siempre presente
                citation_count = autor.get('citation-count', 0)  # Puede no estar siempre presente
                
                # Información sobre la afiliación actual
                afiliacion_actual = autor.get('affiliation-current', {}).get('affiliation-name', '')
                afiliacion_ciudad = autor.get('affiliation-current', {}).get('affiliation-city', '')
                afiliacion_pais = autor.get('affiliation-current', {}).get('affiliation-country', '')
                afiliacion_id = autor.get('affiliation-current', {}).get('affiliation-id', '')
                afiliacion_url = autor.get('affiliation-current', {}).get('affiliation-url', '')

                # Historial de afiliaciones
                historial_afiliaciones = ", ".join(
                    [afiliacion.get('affiliation-name', '') for afiliacion in autor.get('affiliation-history', {}).get('affiliation', [])])
                historial_paises = ", ".join(
                    [afiliacion.get('affiliation-country', '') for afiliacion in autor.get('affiliation-history', {}).get('affiliation', [])])

                # Coautoría (número de coautores)
                numero_coautores = autor.get('coauthor-count', 0)

                # Áreas temáticas
                subject_areas = autor.get('subject-area', [])
                if isinstance(subject_areas, list):
                    areas_tematicas = ", ".join([area.get('subject-area', {}).get('$', '') for area in subject_areas])
                else:
                    areas_tematicas = ''

                # Nombres completos y variantes
                nombre_completo_scopus = autor.get('preferred-name', {}).get('given-name', '') + ' ' + autor.get('preferred-name', {}).get('surname', '')
                iniciales = autor.get('preferred-name', {}).get('initials', '')
                variantes_nombre = ", ".join(
                    [variante.get('given-name', '') + ' ' + variante.get('surname', '') for variante in autor.get('name-variant', [])])

                # Añadir los resultados
                resultados.append({
                    'scopus_id': scopus_id,
                    'eid': eid,
                    'orcid': orcid,
                    'numero_publicaciones': numero_publicaciones,
                    'cited_by_count': cited_by_count,
                    'citation_count': citation_count,
                    'afiliacion_actual': afiliacion_actual,
                    'afiliacion_ciudad': afiliacion_ciudad,
                    'afiliacion_pais': afiliacion_pais,
                    'afiliacion_id': afiliacion_id,
                    'afiliacion_url': afiliacion_url,
                    'historial_afiliaciones': historial_afiliaciones,
                    'historial_paises': historial_paises,
                    'numero_coautores': numero_coautores,
                    'areas_tematicas': areas_tematicas,
                    'nombre_completo_scopus': nombre_completo_scopus,
                    'iniciales': iniciales,
                    'variantes_nombre': variantes_nombre,
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
file_path = r'C:\Users\Rodrigo\Desktop\Roxana Files\Scopus\maestra.xlsx'
df_base_maestra = pd.read_excel(file_path, sheet_name='BaseMaestra')

# Parámetros de control
realizar_todas = False  # Cambiar a True para procesar todos los registros
num_solicitudes = 5  # Número de solicitudes a realizar (solo si realizar_todas es False)
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
    
    # Guardar los resultados en un archivo CSV
    df_resultados_finales.to_csv("scopus_resultados.csv", index=False)
    print(f"Resultados guardados en 'scopus_resultados.csv'. Total de solicitudes realizadas: {total_solicitudes}")
else:
    print("No se encontraron resultados.")
