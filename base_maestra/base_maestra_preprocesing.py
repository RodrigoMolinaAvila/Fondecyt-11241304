import pandas as pd

def estandarizar_nombre(nombre):
    """Estandariza nombres a mayúsculas, elimina espacios innecesarios y corrige dobles espacios."""
    if pd.isnull(nombre):
        return ""
    return (
        " ".join(nombre.strip().upper().split())  # Elimina dobles espacios
        .replace(".", "")
        .replace(",", "")
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ú", "U")
    )

def hacer_joins_y_consolidar(maestra, anid):
    """
    Realiza el join para cada combinación de nombres, asegura que la hoja principal
    contiene todos los nombres de la maestra, y separa proyectos adicionales.

    Args:
    maestra (pd.DataFrame): DataFrame de la base de datos maestra con combinaciones de nombres.
    anid (pd.DataFrame): DataFrame filtrado de la base ANID.

    Returns:
    tuple: DataFrame consolidado con la base maestra actualizada, DataFrame con detalles adicionales.
    """
    resultados = []
    
    # Iterar sobre las combinaciones para hacer joins
    for i in range(1, 13):
        comb_name = f'comb_{i}'
        resultado = pd.merge(maestra, anid, how='left', left_on=comb_name, right_on='NOMBRE_RESPONSABLE')
        resultados.append(resultado)

    # Unir los resultados en un solo DataFrame y eliminar duplicados
    resultados_unidos = pd.concat(resultados, ignore_index=True).drop_duplicates()
    
    # Asegurar que todos los nombres de la maestra estén presentes
    base_maestra_actualizada = pd.merge(
        maestra, 
        resultados_unidos, 
        how='left', 
        on='comb_1',  # Usamos `comb_1` como referencia principal
        suffixes=('', '_drop')
    )

    # Limpiar columnas duplicadas después del merge
    base_maestra_actualizada = base_maestra_actualizada.loc[:, ~base_maestra_actualizada.columns.str.endswith('_drop')]

    # Separar proyectos adicionales
    proyectos_adicionales = resultados_unidos[~resultados_unidos.index.isin(base_maestra_actualizada.index)]

    # Renombrar columnas relevantes de ANID
    columnas_renombradas = {
        'PROGRAMA': 'Programa',
        'INSTRUMENTO': 'Instrumento',
        'NOMBRE_CONCURSO': 'Nombre_concurso',
        'AGNO_CONCURSO': 'Año_concurso',
        'AGNO_FALLO': 'Año_fallo',
        'NOMBRE_PROYECTO': 'Nombre_proyecto',
        'MONTO_ADJUDICADO': 'Monto_adjudicado'
    }

    base_maestra_actualizada.rename(columns=columnas_renombradas, inplace=True, errors="ignore")
    proyectos_adicionales.rename(columns=columnas_renombradas, inplace=True, errors="ignore")

    # Crear la variable 'Tiene fondecyt'
    base_maestra_actualizada['Tiene fondecyt'] = base_maestra_actualizada['Programa'].eq('FONDECYT').astype(int)
    base_maestra_actualizada['Tiene fondecyt'].fillna(0, inplace=True)

    # Eliminar columnas innecesarias
    columnas_a_eliminar = [f'comb_{i}' for i in range(2, 13)]
    base_maestra_actualizada.drop(columns=columnas_a_eliminar, inplace=True, errors='ignore')
    proyectos_adicionales.drop(columns=columnas_a_eliminar, inplace=True, errors='ignore')

    return base_maestra_actualizada, proyectos_adicionales

# Cargar las bases
path_anid = r"C:\Users\Rodrigo\Desktop\Roxana Files\Add databases\Github ANID\BDH_HISTORICA.xlsx"
path_maestra = r"C:\Users\Rodrigo\Desktop\Roxana Files\base_maestra\base_maestra.xlsx"

anid = pd.read_excel(path_anid)
maestra = pd.read_excel(path_maestra)

# Preprocesar la base ANID
anid['NOMBRE_RESPONSABLE'] = anid['NOMBRE_RESPONSABLE'].apply(estandarizar_nombre)

# Filtrar por criterios FONDECYT e INSTRUMENTO
anid = anid[(anid['PROGRAMA'] == 'FONDECYT') &
            (anid['INSTRUMENTO'].isin(['REGULAR', 'POSTDOCTORADO', 'INICIACION'])) &
            (anid['AGNO_FALLO'].between(2014, 2024))]

# Preprocesar la base maestra
columnas_nombres = ['Primer_Nombre', 'Segundo_Nombre', 'Apellido_Paterno', 'Apellido_Materno']
maestra[columnas_nombres] = maestra[columnas_nombres].apply(lambda x: x.str.upper().str.strip())
maestra = maestra.assign(
    comb_1=maestra['Primer_Nombre'] + " " + maestra['Segundo_Nombre'] + " " + maestra['Apellido_Paterno'] + " " + maestra['Apellido_Materno'],
    comb_2=maestra['Primer_Nombre'] + " " + maestra['Segundo_Nombre'] + " " + maestra['Apellido_Materno'] + " " + maestra['Apellido_Paterno'],
    comb_3=maestra['Primer_Nombre'] + " " + maestra['Apellido_Paterno'] + " " + maestra['Apellido_Materno'],
    comb_4=maestra['Primer_Nombre'] + " " + maestra['Apellido_Materno'] + " " + maestra['Apellido_Paterno'],
    comb_5=maestra['Segundo_Nombre'] + " " + maestra['Primer_Nombre'] + " " + maestra['Apellido_Paterno'] + " " + maestra['Apellido_Materno'],
    comb_6=maestra['Segundo_Nombre'] + " " + maestra['Primer_Nombre'] + " " + maestra['Apellido_Materno'] + " " + maestra['Apellido_Paterno'],
    comb_7=maestra['Segundo_Nombre'] + " " + maestra['Apellido_Paterno'] + " " + maestra['Apellido_Materno'],
    comb_8=maestra['Segundo_Nombre'] + " " + maestra['Apellido_Materno'] + " " + maestra['Apellido_Paterno'],
    comb_9=maestra['Primer_Nombre'] + " " + maestra['Segundo_Nombre'] + " " + maestra['Apellido_Materno'],
    comb_10=maestra['Segundo_Nombre'] + " " + maestra['Primer_Nombre'] + " " + maestra['Apellido_Materno'],
    comb_11=maestra['Primer_Nombre'] + " " + maestra['Segundo_Nombre'] + " " + maestra['Apellido_Paterno'],
    comb_12=maestra['Segundo_Nombre'] + " " + maestra['Primer_Nombre'] + " " + maestra['Apellido_Paterno']
)

# Realizar el join y consolidar los proyectos
base_maestra_actualizada, proyectos_adicionales = hacer_joins_y_consolidar(maestra, anid)

# Exportar a Excel
output_path = r"C:\Users\Rodrigo\Desktop\Roxana Files\base_maestra\proyectos_consolidados_actualizados.xlsx"
with pd.ExcelWriter(output_path) as writer:
    base_maestra_actualizada.to_excel(writer, sheet_name='Base Maestra Actualizada', index=False)
    proyectos_adicionales.to_excel(writer, sheet_name='Proyectos Adicionales', index=False)

print(f"Proyectos consolidados guardados en: {output_path}")
