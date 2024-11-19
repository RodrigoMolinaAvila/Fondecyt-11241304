import requests
import pandas as pd
import time
from requests.utils import quote

# Credenciales API
API_KEY = '
INST_TOKEN = 

# Definir los headers
headers = {
    'X-ELS-APIKey': API_KEY,
    'X-ELS-Insttoken': INST_TOKEN,
    'Accept': 'application/json'
}

# Función para verificar los límites de cuota de la API
def revisar_cuota(response):
    if 'X-RateLimit-Limit' in response.headers:
        print(f"Cuota total: {response.headers['X-RateLimit-Limit']}")
    if 'X-RateLimit-Remaining' in response.headers:
        print(f"Cuota restante: {response.headers['X-RateLimit-Remaining']}")
    if 'X-RateLimit-Reset' in response.headers:
        reset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(response.headers['X-RateLimit-Reset'])))
        print(f"La cuota se restablece a las: {reset_time}")

# Función para buscar autores en Scopus usando nombre completo, con reintento en caso de error 429
def buscar_autor_por_nombre(nombre_completo, max_reintentos=3):
    nombre_codificado = quote(nombre_completo)
    url = f"https://api.elsevier.com/content/search/author?query=authname({nombre_codificado})&view=STANDARD"
    intentos = 0
    
    while intentos < max_reintentos:
        response = requests.get(url, headers=headers)
        
        # Verificar cuota tras cada request
        revisar_cuota(response)
        
        if response.status_code == 200:
            try:
                data = response.json()
                autores = data.get('search-results', {}).get('entry', [])
                resultados = []

                for autor in autores:
                    scopus_id = autor.get('dc:identifier', '').replace('AUTHOR_ID:', '')
                    nombre_completo_scopus = autor.get('preferred-name', {}).get('given-name', '') + ' ' + autor.get('preferred-name', {}).get('surname', '')

                    resultados.append({
                        'scopus_id': scopus_id,
                        'nombre_completo_scopus': nombre_completo_scopus,
                        'nombre_busqueda': nombre_completo
                    })
                
                return pd.DataFrame(resultados)
            
            except ValueError:
                print("Error en la decodificación de JSON.")
                return pd.DataFrame()
        
        elif response.status_code == 429:
            # Error 429: esperar y reintentar
            print(f"Error 429: Límite de solicitudes superado para {nombre_completo}. Esperando para reintentar...")
            time.sleep(10 + intentos * 5)  # Incrementar tiempo de espera en cada intento
            intentos += 1
        else:
            print(f"Error {response.status_code} en la API para {nombre_completo}")
            return pd.DataFrame()
    
    print(f"No se pudo completar la solicitud para {nombre_completo} tras {max_reintentos} reintentos.")
    return pd.DataFrame()

# Cargar archivo Excel
file_path = './Scopus/maestra_procesada.xlsx'
df_maestra = pd.read_excel(file_path)

# Parámetros de ejecución
realizar_todas = False  # Cambiar a True para procesar todos los registros
num_solicitudes = 2    # Número de solicitudes a realizar si realizar_todas es False
tiempo_pausa = 3        # Pausa entre cada solicitud (en segundos)

# Determinar el número de registros a procesar
if realizar_todas:
    max_solicitudes = len(df_maestra)
else:
    max_solicitudes = min(num_solicitudes, len(df_maestra))

resultados_busqueda = []
total_solicitudes = 0

# Bucle para realizar las solicitudes
for index, row in df_maestra.iterrows():
    if total_solicitudes >= max_solicitudes:
        break
    
    nombre_completo = f"{row['Primer_Nombre']} {row['Segundo_Nombre'] or ''} {row['Apellido_Paterno']} {row['Apellido_Materno'] or ''}".strip()
    print(f"Buscando en Scopus: {nombre_completo} ({total_solicitudes+1}/{max_solicitudes})")
    
    # Realizar la búsqueda
    df_resultado = buscar_autor_por_nombre(nombre_completo)
    time.sleep(tiempo_pausa)  # Pausa entre solicitudes para evitar límite de frecuencia
    
    # Si hay resultados, añadirlos
    if not df_resultado.empty:
        resultados_busqueda.append(df_resultado)
        total_solicitudes += 1

# Combinar todos los resultados en un DataFrame
if resultados_busqueda:
    df_resultados_final = pd.concat(resultados_busqueda, ignore_index=True)
    output_path = './Scopus/scopus_resultados_optimizado.xlsx'
    df_resultados_final.to_excel(output_path, index=False)
    print(f"Resultados guardados en '{output_path}'.")
else:
    print("No se encontraron resultados.")
