import pandas as pd

# Load the two Excel files using relative paths
file1 = r'./GSE_establecimientos/resultados_1iteracion.xlsx'
file2 = r'./GSE_establecimientos/resultados_2iteracion.xlsx'

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# Concatenate the dataframes
combined_df = pd.concat([df1, df2])

# Save the combined dataframe to a new Excel file
combined_df.to_excel(r'./GSE_establecimientos/resultados_combinados.xlsx', index=False)