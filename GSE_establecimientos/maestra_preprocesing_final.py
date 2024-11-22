import pandas as pd

# Cargar los datos desde el archivo Excel
path = r"C:\Users\Rodrigo\Desktop\Roxana Files\GSE_establecimientos\maestra_rbd.xlsx"
data = pd.read_excel(path)

# Seleccionar columnas relevantes
cols_maestra = [
    'FOLIO', 'NOMBRE', 'SEXO_COMPLETO', 'Ano de inicio beca', 'TIPO_BECA',
    'UNIVERSIDAD_PROGRAMA', 'PROGRAMA', 'Pais', 'Tipo de establecimiento secundario',
    'Colegio Publico', 'Colegio Particular Pagado', 'Extranjero',
    'Secundaria en region Chile', 'Nombre', 'Comuna', 'Región', 'GSE', 'RBD',
    'INSTRUMENTO', 'NOMBRE_CONCURSO', 'AGNO_CONCURSO', 'AGNO_FALLO',
    'NOMBRE_PROYECTO', 'MONTO_ADJUDICADO'
]
base_maestra = data[cols_maestra].copy()

# Procesar variables
# Convertir `Ano de inicio beca` a tipo datetime y extraer el año
base_maestra['Ano de inicio beca'] = pd.to_datetime(
    base_maestra['Ano de inicio beca'], errors='coerce'
).dt.year

# Categorizar GSE
def categorizar_gse(valor):
    if valor in ['Bajo', 'Medio Bajo']:
        return 'Bajo + Medio Bajo'
    elif valor == 'Medio':
        return 'Medio'
    elif valor == 'Medio Alto':
        return 'Medio Alto'
    elif valor == 'Alto':
        return 'Alto'
    else:
        return 'Sin Información'

base_maestra['GSE_categoria'] = base_maestra['GSE'].apply(categorizar_gse)

# Crear la columna `Tiene fondecyt`
# Verificar si alguna de las columnas relacionadas con ANID tiene datos
cols_anid = ['INSTRUMENTO', 'NOMBRE_CONCURSO', 'AGNO_CONCURSO', 'AGNO_FALLO',
             'NOMBRE_PROYECTO', 'MONTO_ADJUDICADO']
base_maestra['Tiene fondecyt'] = base_maestra[cols_anid].notnull().any(axis=1).astype(int)

# Seleccionar las columnas finales
cols_finales = [
    'FOLIO', 'NOMBRE', 'SEXO_COMPLETO', 'Ano de inicio beca', 'TIPO_BECA',
    'UNIVERSIDAD_PROGRAMA', 'PROGRAMA', 'Pais', 'Tipo de establecimiento secundario',
    'Colegio Publico', 'Colegio Particular Pagado', 'Extranjero',
    'Secundaria en region Chile', 'Nombre', 'Comuna', 'Región', 'GSE',
    'GSE_categoria', 'RBD', 'INSTRUMENTO', 'NOMBRE_CONCURSO', 'AGNO_CONCURSO',
    'AGNO_FALLO', 'NOMBRE_PROYECTO', 'MONTO_ADJUDICADO', 'Tiene fondecyt'
]
base_final = base_maestra[cols_finales]

# Guardar la base consolidada en un archivo Excel
output_path = r"C:\Users\Rodrigo\Desktop\Roxana Files\base_maestra\base_consolidada.xlsx"
base_final.to_excel(output_path, index=False)

print(f"Base consolidada guardada en: {output_path}")
