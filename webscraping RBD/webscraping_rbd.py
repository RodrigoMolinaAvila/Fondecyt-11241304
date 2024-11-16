import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración del EdgeDriver
edge_driver_path = 'webscraping RBD/msedgedriver.exe'
service = Service(edge_driver_path)
options = Options()
options.use_chromium = True

# Leer la lista de RBDs desde el archivo CSV
rbd_list = pd.read_csv('C:/Users/Rodrigo/Desktop/Roxana Files/webscraping RBD/rbd.csv')

# Inicializar el navegador
driver = webdriver.Edge(service=service, options=options)

# Crear una lista para almacenar los resultados
results = []

# Contador para el progreso
total_rbd = len(rbd_list)
for index, rbd in enumerate(rbd_list['RBD'], start=1):
    print(f"Procesando {index} de {total_rbd}: RBD {rbd}")
    try:
        # Navegar a la página objetivo
        driver.get('https://simce.cl/')

        # Esperar a que el cuadro de búsqueda esté presente y escribir el RBD
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "myInput"))
        )
        search_box.send_keys(str(rbd))

        # Esperar a que aparezca el cuadro de autocompletar y hacer clic en la opción correcta
        autocomplete_item = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='myInputautocomplete-list']//div[contains(text(), '[{rbd}]')]"))
        )

        # Desplazarse hasta el elemento antes de hacer clic
        driver.execute_script("arguments[0].scrollIntoView(true);", autocomplete_item)
        time.sleep(1)  # Esperar un momento para asegurarse de que el desplazamiento se complete
        autocomplete_item.click()

        try:
            # Esperar a que el botón "Estudiante" esté presente y hacer clic
            student_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnEstudiante"))
            )
            # Desplazarse hasta el elemento antes de hacer clic
            driver.execute_script("arguments[0].scrollIntoView(true);", student_button)
            time.sleep(1)  # Esperar un momento para asegurarse de que el desplazamiento se complete
            student_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"El botón 'Estudiante' no está disponible para RBD {rbd}, continuando con el siguiente paso. Detalles del error: {e}")

        # Esperar a que el botón "Seguir a resultados educativos" esté presente y hacer clic
        results_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//center/a[contains(@href, 'indicador') and contains(text(), 'Seguir a resultados educativos')]"))
        )
        # Desplazarse hasta el elemento antes de hacer clic
        driver.execute_script("arguments[0].scrollIntoView(true);", results_button)
        time.sleep(1)  # Esperar un momento para asegurarse de que el desplazamiento se complete
        results_button.click()

        # Extraer la información deseada
        establecimiento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "establecimiento"))
        ).text
        comuna = driver.find_element(By.ID, "comuna").text
        region = driver.find_element(By.ID, "region").text
        gse = driver.find_element(By.ID, "selectedOption").text
        # Extraer el GSE correcto
        gse_elements = driver.find_elements(By.ID, "selectedOption")
        for element in gse_elements:
            if "GSE:" in element.find_element(By.XPATH, "./..").text:
                gse = element.text
                break

        # Agregar los resultados a la lista
        results.append({
            'RBD': rbd,
            'Nombre': establecimiento,
            'Comuna': comuna,
            'Región': region,
            'GSE': gse
        })

    except Exception as e:
        print(f"Error procesando RBD {rbd}: {e}")

# Cerrar el navegador
driver.quit()

# Crear un DataFrame con los resultados y guardarlo en un archivo CSV
df = pd.DataFrame(results)
df.to_csv('C:/Users/Rodrigo/Desktop/Roxana Files/webscraping RBD/resultados.csv', index=False)

print("Proceso completado. Los resultados se han guardado en 'resultados.csv'.")