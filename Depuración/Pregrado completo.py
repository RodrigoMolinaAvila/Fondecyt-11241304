import pandas as pd
import re

# Cargar el archivo de Excel con los datos originales
file_path = r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\Depuración\01_BBDD_Ayudante_29_08 - 2.xlsx'
df = pd.read_excel(file_path)

# Paso 1: Procesamiento inicial para encontrar la universidad de pregrado
def extract_university_with_oldest_year(text):
    """
    Esta función toma como entrada el texto completo de la columna 'Universidad Título Profesional'
    y extrae la universidad correspondiente al pregrado. Lo hace buscando el año más antiguo
    asociado a una universidad y devolviendo ese nombre.
    
    1. Divide el texto en varias líneas.
    2. Identifica los años y asocia el más antiguo con su universidad.
    3. Devuelve el nombre de la universidad de pregrado.
    """
    if pd.isna(text):
        return None
    institutions = re.split(r'\n+', text)
    oldest_year = None
    oldest_university = None
    current_university = None
    
    for i, line in enumerate(institutions):
        # Buscar un año en la línea actual
        year_match = re.search(r'(\b\d{4}\b)', line)
        university_match = re.search(r'Universidad|Instituto|Pontificia|University|Universität', line, re.IGNORECASE)
        
        if university_match:
            # Si encontramos una universidad, la guardamos como posible opción
            current_university = line.strip()
        
        if year_match:
            year = int(year_match.group(1))
            if current_university and (oldest_year is None or year < oldest_year):
                oldest_year = year
                oldest_university = current_university
        
        # Si no se encuentra universidad en la línea actual, se revisan líneas anteriores
        if year_match and not current_university:
            for j in range(i - 1, -1, -1):
                if re.search(r'Universidad|Instituto|Pontificia|University|Universität', institutions[j], re.IGNORECASE):
                    current_university = institutions[j].strip()
                    if oldest_year is None or year < oldest_year:
                        oldest_year = year
                        oldest_university = current_university
                    break

    return oldest_university

# Aplicar la función de extracción a la columna 'Universidad Título Profesional'
df['Universidad Pregrado'] = df['Universidad Título Profesional'].apply(extract_university_with_oldest_year)

# Paso 2: Limpieza y estandarización de los nombres de las universidades
def clean_university_name(name):
    """
    Esta función limpia y estandariza los nombres de universidades:
    1. Elimina espacios innecesarios y puntos.
    2. Convierte a formato título (capitalización de cada palabra).
    """
    if pd.isna(name):
        return name
    clean_name = name.strip().replace('.', '').replace(',', '').title()
    return clean_name

# Aplicar la función de limpieza a la columna 'Universidad Pregrado'
df['Universidad Pregrado'] = df['Universidad Pregrado'].apply(clean_university_name)

# Paso 3: Refinar los nombres eliminando el término "Pontificia" pero manteniendo el resto
def refine_university_names(name):
    """
    Esta función elimina únicamente el término 'Pontificia' de los nombres de universidades,
    manteniendo intactos los nombres completos que contienen 'Católica'.
    """
    if pd.isna(name):
        return name
    # Eliminar solo el término "Pontificia"
    refined_name = re.sub(r'Pontificia\s+', '', name)
    return refined_name

# Aplicar la función de refinamiento a la columna 'Universidad Pregrado'
df['Pregrado Final'] = df['Universidad Pregrado'].apply(refine_university_names)

# Paso 4: Combinar la nueva columna con los datos originales donde sea necesario
df['Pregrado Final'] = df['Pregrado Final'].fillna(df['Universidad Título Profesional'])

# Paso 5: Exportar los resultados a un archivo Excel
output_file_path = r'C:\Users\rodri\OneDrive\Escritorio\Roxana Files\Depuración\universidad_prueba.xlsx'
df.to_excel(output_file_path, index=False)

print(f"El archivo ha sido exportado exitosamente a: {output_file_path}")
