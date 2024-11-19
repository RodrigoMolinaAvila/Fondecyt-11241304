import requests
import time

# Credenciales de la API
API_KEY = 
INST_TOKEN = 

# Encabezados para la solicitud
headers = {
    'X-ELS-APIKey': API_KEY,
    'X-ELS-Insttoken': INST_TOKEN,
    'Accept': 'application/json'
}

# Lista de URLs de los distintos servicios a verificar
endpoints = {
    "Serial Title": "https://api.elsevier.com/content/serial/title?query=ISSN(1234-5678)&count=1",
    "Citations Count Metadata": "https://api.elsevier.com/content/abstract/citations?scopus_id=85070690936&count=1",
    "Subject Classifications": "https://api.elsevier.com/content/subject/classification?view=STANDARD",
    "Abstract Retrieval": "https://api.elsevier.com/content/abstract/scopus_id/85070690936",
    "Affiliation Retrieval": "https://api.elsevier.com/content/affiliation/affil(60072108)",
    "Author Retrieval": "https://api.elsevier.com/content/author/author_id/7004212771",
    "Affiliation Search": "https://api.elsevier.com/content/search/affiliation?query=AF-ID(60072108)&count=1",
    "Author Search": "https://api.elsevier.com/content/search/author?query=AU-ID(7004212771)&count=1",
    "Scopus Search": "https://api.elsevier.com/content/search/scopus?query=AU-ID(7004212771)&count=1"
}

# Función para verificar la cuota
def revisar_cuota(endpoint_name, url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"\nCuota para {endpoint_name}:")
        print(f"  Cuota total (X-RateLimit-Limit): {response.headers.get('X-RateLimit-Limit', 'No disponible')}")
        print(f"  Cuota restante (X-RateLimit-Remaining): {response.headers.get('X-RateLimit-Remaining', 'No disponible')}")
        if 'X-RateLimit-Reset' in response.headers:
            reset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(response.headers['X-RateLimit-Reset'])))
            print(f"  La cuota se restablece a las: {reset_time}")
        else:
            print("  No se recibió el encabezado X-RateLimit-Reset en la respuesta.")
    else:
        print(f"\nError {response.status_code} al verificar cuota para {endpoint_name}.")
        if 'X-ELS-Status' in response.headers and response.headers['X-ELS-Status'] == 'QUOTA_EXCEEDED':
            print("  QUOTA_EXCEEDED - La cuota ha sido excedida.")
        print(f"Detalles adicionales de la respuesta: {response.text}")

# Verificar la cuota para cada endpoint
for name, url in endpoints.items():
    print(f"\nIntentando acceder a: {url}")
    revisar_cuota(name, url)
    time.sleep(1)  # Pausa de 1 segundo entre solicitudes para evitar limitaciones de tasa

print("\nVerificación de cuota completada.")
