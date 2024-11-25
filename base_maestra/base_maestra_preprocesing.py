import pandas as pd

# Verificar la integridad inicial
print(f"Base maestra: {maestra.shape[0]} filas.")
print(f"Base ANID filtrada: {anid_filtrada.shape[0]} filas.")

# Iterar sobre todas las combinaciones de nombres
resultados = []
for i in range(1, 13):
    comb_col = f'comb_{i}'
    if comb_col not in maestra.columns:
        print(f"Advertencia: {comb_col} no está presente. Se omite esta combinación.")
        continue
    
    print(f"Procesando combinación: {comb_col}")
    
    # Merge para esta combinación
    resultado = pd.merge(
        maestra,
        anid_filtrada,
        how='left',
        left_on=comb_col,
        right_on='NOMBRE_RESPONSABLE'
    )
    resultados.append(resultado)

# Concatenar todos los resultados
base_combinada = pd.concat(resultados, ignore_index=True)

# Mantener solo la fila más reciente para cada nombre de la maestra
if 'AGNO_FALLO' in base_combinada.columns:
    base_combinada = base_combinada.sort_values(by=['comb_1', 'AGNO_FALLO'], ascending=[True, False])

# Crear una copia para la base maestra principal con una fila única por nombre
base_principal = base_combinada.drop_duplicates(subset='comb_1', keep='first')

# Garantizar la integridad de la muestra original
base_principal = pd.merge(
    maestra,
    base_principal,
    how='left',
    on='comb_1',
    suffixes=('', '_drop')
)

# Limpiar columnas duplicadas del merge
base_principal = base_principal.loc[:, ~base_principal.columns.str.endswith('_drop')]

# Añadir la columna 'Tiene fondecyt' (coincidencia con ANID)
base_principal['Tiene fondecyt'] = base_principal['NOMBRE_RESPONSABLE'].notnull().astype(int)

# Filtrar registros adicionales
proyectos_adicionales = base_combinada[~base_combinada['comb_1'].isin(base_principal['comb_1'])]

# Verificar integridad final
print(f"Filas en la base maestra actualizada: {base_principal.shape[0]} (deben ser 3166).")
print(f"Proyectos adicionales: {proyectos_adicionales.shape[0]} filas.")

# Exportar resultados a Excel
output_path = "proyectos_consolidados_ajustados.xlsx"
with pd.ExcelWriter(output_path) as writer:
    base_principal.to_excel(writer, sheet_name='Base Maestra Actualizada', index=False)
    proyectos_adicionales.to_excel(writer, sheet_name='Proyectos Adicionales', index=False)

print(f"Resultados exportados a {output_path}.")
