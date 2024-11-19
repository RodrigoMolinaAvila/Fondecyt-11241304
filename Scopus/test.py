import requests
import time

# Configuración de credenciales y headers
API_KEY = 
INST_TOKEN = 

headers = {
    'X-ELS-APIKey': API_KEY,
    'X-ELS-Insttoken': INST_TOKEN,
    'Accept': 'application/json'
}

# Función para verificar la cuota
def revisar_cuota(response):
    if 'X-RateLimit-Limit' in response.headers:
        print(f"Cuota total: {response.headers['X-RateLimit-Limit']}")
    if 'X-RateLimit-Remaining' in response.headers:
        print(f"Cuota restante: {response.headers['X-RateLimit-Remaining']}")
    if 'X-RateLimit-Reset' in response.headers:
        reset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(response.headers['X-RateLimit-Reset'])))
        print(f"La cuota se restablece a las: {reset_time}")

# Función para buscar autor por nombre y apellido
def buscar_autor_por_nombre_apellido(nombre, apellido):
    nombre_codificado = requests.utils.quote(f"authlast({apellido}) and authfirst({nombre})")
    url = f"https://api.elsevier.com/content/search/author?query={nombre_codificado}&view=STANDARD&count=1"

    # Realizar solicitud
    response = requests.get(url, headers=headers)
    revisar_cuota(response)  # Verificar cuota después de la solicitud

    if response.status_code == 200:
        try:
            data = response.json()
            autores = data.get('search-results', {}).get('entry', [])
            if autores:
                autor = autores[0]  # Solo mostramos el primer resultado encontrado
                resultado = {
                    'scopus_id': autor.get('dc:identifier', '').replace('AUTHOR_ID:', ''),
                    'nombre_completo_scopus': autor.get('preferred-name', {}).get('given-name', '') + ' ' + autor.get('preferred-name', {}).get('surname', ''),
                    'afiliacion_actual': autor.get('affiliation-current', {}).get('affiliation-name', ''),
                }
                print("Resultado encontrado:", resultado)
            else:
                print("No se encontraron autores con ese nombre y apellido.")
        except ValueError:
            print("Error en la decodificación de JSON.")
    else:
        print(f"Error {response.status_code} al acceder a la API.")
        print("Detalles adicionales de la respuesta:", response.text)

# Realizar búsqueda de ejemplo
buscar_autor_por_nombre_apellido("Roxana", "Chiappa")
