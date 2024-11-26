import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración del EdgeDriver
edge_driver_path = 'webscraping RBD/msedgedriver.exe'
service = Service(edge_driver_path)
options = Options()
options.use_chromium = True

# Leer la lista de RBDs desde el archivo CSV
rbd_list = pd.read_csv(r'C:\Users\Rodrigo\Desktop\Roxana Files\webscraping RBD\missing_rbds_nongse.csv')

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
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "myInput"))
        )
        search_box.send_keys(str(rbd))

        # Esperar a que aparezca el cuadro de autocompletar y hacer clic en la opción correcta
        autocomplete_item = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='myInputautocomplete-list']//div[contains(text(), '[{rbd}]')]"))
        )

        # Desplazarse hasta el elemento antes de hacer clic
        driver.execute_script("arguments[0].scrollIntoView(true);", autocomplete_item)
        time.sleep(1)  # Esperar un momento para asegurarse de que el desplazamiento se complete
        autocomplete_item.click()

        try:
            # Intentar hacer clic en el botón "Estudiante"
            student_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "btnEstudiante"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", student_button)
            time.sleep(1)
            student_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"El botón 'Estudiante' no está disponible para RBD {rbd}, continuando con el siguiente paso. Detalles del error: {e}")

        # Extraer la información después de intentar hacer clic en el botón "Estudiante"
        establecimiento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "establecimiento"))
        ).text
        dependencia = driver.find_element(By.ID, "dependencia").text
        comuna = driver.find_element(By.ID, "comuna").text
        region = driver.find_element(By.ID, "region").text

        # Agregar los resultados a la lista
        results.append({
            'RBD': rbd,
            'Nombre': establecimiento,
            'Comuna': comuna,
            'Región': region,
            'Dependencia': dependencia
        })

    except Exception as e:
        print(f"Error procesando RBD {rbd}: {e}")

# Cerrar el navegador
driver.quit()

# Crear un DataFrame con los resultados y guardarlo en un archivo CSV
df = pd.DataFrame(results)
df.to_csv(r'./webscraping RBD/resultados_nongse.csv', index=False)

print("Proceso completado. Los resultados se han guardado en 'resultados_nongse2.csv'.")
