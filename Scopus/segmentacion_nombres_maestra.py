import pandas as pd
import re

# Lista de términos comunes en nombres y apellidos compuestos
compuestos = [
    "del pilar", "de la fuente", "del rio", "del carmen", "san roman", "del real", 
    "del canto", "de la garza", "dos santos", "de los angeles", "de lourdes", 
    "del rosario", "de la cruz", "de souza", "de queiroz", "de la paz", "de aguilera", 
    "del campo", "von bohlen", "de amesti", "von dossow", "de la maza", "de luna", 
    "de jesus", "de la barra", "san martin", "da silva", "del cisne", "de la caridad", 
    "de dios", "del valle", "mac farlane"
]

# Crear una expresión regular para identificar nombres compuestos
compuesto_regex = re.compile(r'\b(?:' + '|'.join(compuestos) + r')\b', re.IGNORECASE)

def normalizar_nombre(nombre):
    # Normaliza a mayúsculas y elimina espacios adicionales
    return nombre.upper().strip() if pd.notna(nombre) else ""

def procesar_nombre_completo(nombre_completo):
    # Normalizar el nombre completo
    nombre_completo = normalizar_nombre(nombre_completo)
    
    # Unir palabras compuestas
    for compuesto in compuestos:
        nombre_completo = re.sub(rf'\b{compuesto}\b', compuesto.replace(" ", "_"), nombre_completo, flags=re.IGNORECASE)
    
    # Dividir el nombre en partes
    partes = nombre_completo.split()
    
    # Revertir el reemplazo temporal de "_" a espacio
    partes = [parte.replace("_", " ") for parte in partes]
    
    # Clasificar y asignar nombres y apellidos según el número de partes
    if len(partes) == 2:
        return {"Primer_Nombre": partes[0], "Segundo_Nombre": None, "Apellido_Paterno": partes[1], "Apellido_Materno": None}
    elif len(partes) == 3:
        return {"Primer_Nombre": partes[0], "Segundo_Nombre": None, "Apellido_Paterno": partes[1], "Apellido_Materno": partes[2]}
    elif len(partes) == 4:
        # Verificar si las últimas dos palabras forman un apellido compuesto
        if compuesto_regex.search(f"{partes[2]} {partes[3]}"):
            return {"Primer_Nombre": partes[0], "Segundo_Nombre": None, "Apellido_Paterno": f"{partes[2]} {partes[3]}", "Apellido_Materno": None}
        else:
            return {"Primer_Nombre": partes[0], "Segundo_Nombre": partes[1], "Apellido_Paterno": partes[2], "Apellido_Materno": partes[3]}
    elif len(partes) == 5:
        # Asumimos que el formato es tres nombres y dos apellidos
        return {"Primer_Nombre": partes[0], "Segundo_Nombre": f"{partes[1]} {partes[2]}", "Apellido_Paterno": partes[3], "Apellido_Materno": partes[4]}
    else:
        # Manejar casos especiales o nombres largos (más de 5 palabras) aquí
        return {"Primer_Nombre": partes[0], "Segundo_Nombre": ' '.join(partes[1:-2]), "Apellido_Paterno": partes[-2], "Apellido_Materno": partes[-1]}

# Cargar la base de datos maestra
file_path = './Scopus/maestra.xlsx'
df_maestra = pd.read_excel(file_path, sheet_name='BaseMaestra')

# Aplicar el procesamiento de nombres en cada registro
resultados = df_maestra["NOMBRE"].apply(procesar_nombre_completo)
df_nombres_procesados = pd.DataFrame(resultados.tolist())

# Reemplazar columnas originales en la base de datos maestra con las columnas procesadas
df_maestra['Primer_Nombre'] = df_nombres_procesados['Primer_Nombre']
df_maestra['Segundo_Nombre'] = df_nombres_procesados['Segundo_Nombre']
df_maestra['Apellido_Paterno'] = df_nombres_procesados['Apellido_Paterno']
df_maestra['Apellido_Materno'] = df_nombres_procesados['Apellido_Materno']

# Guardar el DataFrame actualizado en un nuevo archivo Excel
output_file_path = './Scopus/maestra_procesada.xlsx'
df_maestra.to_excel(output_file_path, index=False)
print(f"Base de datos maestra procesada y guardada en: {output_file_path}")
