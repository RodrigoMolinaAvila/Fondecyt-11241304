import pandas as pd

# Ruta del archivo Excel
file_path = 'C:/Users/rodri/OneDrive/Escritorio/Roxana Files/Scopus/test_completo.xlsx'

# Cargar los datos
df = pd.read_excel(file_path)

# Función para verificar nombres con comparación flexible de tamaño
def nombre_en_maestra(nombre_scopus, nombres_maestra):
    partes_scopus = nombre_scopus.split()
    
    for nombre_maestra in nombres_maestra:
        partes_maestra = nombre_maestra.split()
        
        # Descartar si Scopus tiene más partes que la Maestra
        if len(partes_scopus) > len(partes_maestra):
            continue
        
        # Comparar cada parte de Scopus con la correspondiente en Maestra
        match = True
        i, j = 0, 0  # Índices para recorrer partes_scopus y partes_maestra
        while i < len(partes_scopus) and j < len(partes_maestra):
            part_scopus = partes_scopus[i]
            part_maestra = partes_maestra[j]
            
            if len(part_scopus) == 2 and part_scopus[1] == '.':  # Es una inicial
                if part_scopus[0] != part_maestra[0]:  # Inicial no coincide
                    match = False
                    break
            elif part_scopus != part_maestra:  # Nombre completo no coincide
                match = False
                break
            
            i += 1
            j += 1
        
        # Si todas las partes de Scopus coinciden, retornar True
        if match:
            return True
    
    return False

# Filtrar las filas
nombres_maestra = df['Nombre BBDD Maestra'].tolist()
df_filtrado = df[df['Nombre Scopus'].apply(lambda x: nombre_en_maestra(x, nombres_maestra))]

# Guardar el resultado en un archivo Excel
output_path = 'C:/Users/rodri/OneDrive/Escritorio/Roxana Files/Scopus/resultados_scopus_test8.xlsx'
df_filtrado.to_excel(output_path, index=False)

print(f"Archivo filtrado guardado en: {output_path}")
