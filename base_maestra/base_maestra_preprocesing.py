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
    Realiza el join para cada combinación de nombres, calcula logs,
    conserva las variables de ANID y selecciona el proyecto más reciente.

    Args:
    maestra (pd.DataFrame): DataFrame de la base de datos maestra con combinaciones de nombres.
    anid (pd.DataFrame): DataFrame completo de la base ANID.

    Returns:
    tuple: DataFrame consolidado con la base maestra actualizada, DataFrame con detalles adicionales.
    """
    resultados = []
    
    # Iterar sobre las combinaciones
    for i in range(1, 13):
        comb_name = f'comb_{i}'
        # Realizar el join con la combinación actual
        resultado = pd.merge(maestra, anid, how='left', left_on=comb_name, right_on='NOMBRE_RESPONSABLE')
        resultados.append(resultado)
    
    # Unir todos los resultados en un solo DataFrame
    resultados_unidos = pd.concat(resultados, ignore_index=True).drop_duplicates()
    
    # Añadir el total de proyectos por persona
    resultados_unidos['numero_proyectos'] = resultados_unidos.groupby('NOMBRE_RESPONSABLE')['CODIGO_PROYECTO'].transform('count').fillna(0).astype(int)
    
    # Separar el proyecto más reciente
    if 'AGNO_FALLO' in resultados_unidos.columns:
        resultados_unidos['AGNO_FALLO'] = pd.to_numeric(resultados_unidos['AGNO_FALLO'], errors='coerce')
        resultados_unidos = resultados_unidos.sort_values(by=['NOMBRE_RESPONSABLE', 'AGNO_FALLO'], ascending=[True, False])
    else:
        print("La columna 'AGNO_FALLO' no está presente en los datos.")
    
    # Mantener una fila por persona para la base principal
    base_maestra_actualizada = resultados_unidos.drop_duplicates(subset='NOMBRE_RESPONSABLE', keep='first')

    # Identificar las columnas comunes entre maestra y base_maestra_actualizada
    columnas_comunes = list(set(maestra.columns) & set(base_maestra_actualizada.columns))
    
    # Combinar con los nombres originales de la maestra
    base_maestra_actualizada = pd.merge(
        maestra,
        base_maestra_actualizada,
        how='left',
        on=columnas_comunes,  # Usar solo las columnas comunes
        suffixes=('', '_drop')
    )
    
    # Limpiar columnas innecesarias tras el merge
    base_maestra_actualizada = base_maestra_actualizada.loc[:, ~base_maestra_actualizada.columns.str.endswith('_drop')]
    
    # Guardar proyectos adicionales
    proyectos_adicionales = resultados_unidos[~resultados_unidos.index.isin(base_maestra_actualizada.index)]

    # Renombrar columnas relevantes de ANID
    base_maestra_actualizada = base_maestra_actualizada.copy()
    proyectos_adicionales = proyectos_adicionales.copy()

    base_maestra_actualizada.rename(columns={
        'INSTRUMENTO': 'Instrumento',
        'NOMBRE_CONCURSO': 'Nombre_concurso',
        'AGNO_CONCURSO': 'Año_concurso',
        'AGNO_FALLO': 'Año_fallo',
        'NOMBRE_PROYECTO': 'Nombre_proyecto',
        'MONTO_ADJUDICADO': 'Monto_adjudicado'
    }, inplace=True)

    proyectos_adicionales.rename(columns={
        'INSTRUMENTO': 'Instrumento',
        'NOMBRE_CONCURSO': 'Nombre_concurso',
        'AGNO_CONCURSO': 'Año_concurso',
        'AGNO_FALLO': 'Año_fallo',
        'NOMBRE_PROYECTO': 'Nombre_proyecto',
        'MONTO_ADJUDICADO': 'Monto_adjudicado'
    }, inplace=True)
    
    # Añadir la columna 'Tiene fondecyt'
    base_maestra_actualizada['Tiene fondecyt'] = base_maestra_actualizada['CODIGO_PROYECTO'].notnull().astype(int)
    
    # Eliminar columnas no necesarias
    columnas_a_eliminar = [
        'comb_2', 'comb_3', 'comb_4', 'comb_5', 'comb_6', 'comb_7', 'comb_8',
        'comb_9', 'comb_10', 'comb_11', 'comb_12'
    ]
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
