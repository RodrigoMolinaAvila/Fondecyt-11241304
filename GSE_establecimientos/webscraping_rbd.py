import requests
from bs4 import BeautifulSoup

# URL objetivo
url = "https://simce.cl/60/indicador"

# Realizar la solicitud HTTP a la página
response = requests.get(url)
if response.status_code == 200:
    # Analizar el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extraer el valor del GSE
    try:
        gse = soup.find("span", {"id": "selectedOption"}).text.strip()
        print("GSE:", gse)
    except AttributeError:
        print("No se encontró el elemento GSE. Es posible que el HTML de la página haya cambiado o que el elemento no esté presente.")
else:
    print("Error al acceder a la página. Código de estado:", response.status_code)
