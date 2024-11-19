import requests
import pandas as pd
import time
from requests.utils import quote

# Credenciales de la API
API_KEY = 
INST_TOKEN = 

# Definir los headers
headers = {
    'X-ELS-APIKey': API_KEY,
    'X-ELS-Insttoken': INST_TOKEN,
    'Accept': 'application/json'
}

# Parámetro global para indicar si queremos procesar todos los nombres
procesar_todos = False
num_solicitudes = 4 
tiempo_pausa = 1  

def buscar_autor_por_nombre(nombre, apellido):
    
    nombre = nombre if pd.notna(nombre) else ""
    apellido = apellido if pd.notna(apellido) else ""
    
    nombre_codificado = quote(nombre)
    apellido_codificado = quote(apellido)
    
    url = f"https://api.elsevier.com/content/search/author?query=authlast({apellido_codificado})%20and%20authfirst({nombre_codificado})&view=STANDARD&sort=-pubyear"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            autores = data.get('search-results', {}).get('entry', [])
            resultados = []
            
            for autor in autores:
                scopus_id = autor.get('dc:identifier', '').replace('AUTHOR_ID:', '')
                eid = autor.get('eid', '')
                orcid = autor.get('orcid', '')
                numero_publicaciones = autor.get('document-count', 0)
                cited_by_count = autor.get('cited-by-count', 0)
                afiliacion_actual = autor.get('affiliation-current', {}).get('affiliation-name', '')
                pais_afiliacion = autor.get('affiliation-current', {}).get('affiliation-country', '')
                nombre_completo_scopus = f"{autor.get('preferred-name', {}).get('given-name', '')} {autor.get('preferred-name', {}).get('surname', '')}"
                
                subject_areas = autor.get('subject-area', [])
                areas_tematicas = ", ".join([area.get('$', '') for area in subject_areas if isinstance(area, dict)])
                
                # Historial de afiliaciones
                historial_afiliaciones = autor.get('affiliation-history', {}).get('affiliation', [])
                if isinstance(historial_afiliaciones, list):
                    historial_afiliaciones = ", ".join([afiliacion.get('affiliation-name', '') for afiliacion in historial_afiliaciones])
                else:
                    historial_afiliaciones = ''
                
                resultados.append({
                    'scopus_id': scopus_id,
                    'eid': eid,
                    'orcid': orcid,
                    'numero_publicaciones': numero_publicaciones,
                    'cited_by_count': cited_by_count,
                    'afiliacion_actual': afiliacion_actual,
                    'pais_afiliacion': pais_afiliacion,
                    'nombre_completo_scopus': nombre_completo_scopus,
                    'areas_tematicas': areas_tematicas,
                    'historial_afiliaciones': historial_afiliaciones,
                    'nombre_busqueda': f"{nombre} {apellido}"
                })
            
            return pd.DataFrame(resultados)
        
        except ValueError as e:
            print(f"Error en la decodificación de JSON: {e}")
            return pd.DataFrame()
    else:
        print(f"Error {response.status_code}: No se pudo acceder a la API para {nombre} {apellido}")
        print("Detalles del error:", response.text)
        return pd.DataFrame()


def generar_combinaciones(row):
    combinaciones = [
        (row['Primer_Nombre'], f"{row['Apellido_Paterno']}")
    ]
    return combinaciones


file_path = r'./Scopus/maestra_procesada.xlsx'
df_maestra = pd.read_excel(file_path)

resultados_busqueda = []
total_solicitudes = 0

for index, row in df_maestra.iterrows():
    if not procesar_todos and total_solicitudes >= num_solicitudes:
        break
    
    combinaciones = generar_combinaciones(row)
    
    for nombre, apellido in combinaciones:
        print(f"Buscando: {nombre} {apellido} ({total_solicitudes+1})")
        df_resultado = buscar_autor_por_nombre(nombre, apellido)
        time.sleep(tiempo_pausa)
        
        if not df_resultado.empty:
            resultados_busqueda.append(df_resultado)
        
        total_solicitudes += 1
        if not procesar_todos and total_solicitudes >= num_solicitudes:
            break

if resultados_busqueda:
    df_resultados_final = pd.concat(resultados_busqueda, ignore_index=True)
    output_path = './Scopus/scopus_authorsearch_api.xlsx'
    df_resultados_final.to_excel(output_path, index=False)
    print(f"Resultados guardados en '{output_path}'. Total de solicitudes realizadas: {total_solicitudes}")
else:
    print("No se encontraron resultados.")
