import pandas as pd
from genderize import Genderize

# Cargar la base de datos
file_path = r"C:\Users\rodri\OneDrive\Escritorio\Roxana Files\Bases de datos Maestra_Becarios 2014,2015,2016\Bases de datos_maestra.xlsx"
df = pd.read_excel(file_path, sheet_name='BaseMaestra')

# Eliminar columnas innecesarias (aquellas con 'Unnamed' en su nombre)
df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col])

# Separar nombres
df[['Primer Nombre', 'Segundo Nombre', 'Apellido Paterno', 'Apellido Materno']] = df['NOMBRE'].str.split(' ', n=3, expand=True)

# Usar la API de genderize.io
genderize = Genderize()

def inferir_genero(nombre):
    try:
        response = genderize.get([nombre])
        if response and 'gender' in response[0]:
            return response[0]['gender'].upper()
        else:
            return 'DESCONOCIDO'
    except:
        return 'DESCONOCIDO'

# Aplicar la función para inferir el género
df['SEXO_2'] = df['Primer Nombre'].apply(inferir_genero)

# Mostrar las primeras filas para verificar el resultado
print("Primeras filas después de aplicar genderize.io y procesar SEXO_2:")
print(df[['NOMBRE', 'Primer Nombre', 'SEXO', 'SEXO_2']].head(10))
