import pandas as pd

# Leer el archivo CSV de resultados
resultados_df = pd.read_csv('webscraping RBD/resultados.csv')

# Exportar el DataFrame a un archivo Excel
resultados_df.to_excel('resultados.xlsx', index=False)