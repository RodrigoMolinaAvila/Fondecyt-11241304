
library(dplyr)
library(stringr)

# Revisar algunas filas para ver la estructura de la columna 'Universidad Título Profesional'
cat("Ejemplos de la columna 'Universidad Título Profesional':\n")
print(head(df_maestra_completa$`Universidad Título Profesional`, 10))

# Extraer el nombre de la universidad utilizando patrones comunes (ajusta según tu estructura)
df_maestra_completa <- df_maestra_completa %>%
  mutate(
    Universidad = str_extract(`Universidad Título Profesional`, "^[^,]+")  # Extrae la parte antes de la primera coma
  )

# Verificar los resultados
cat("Ejemplos de la columna extraída 'Universidad':\n")
print(head(df_maestra_completa$Universidad, 10))

# Limpiar los nombres de las universidades (opcional)
df_maestra_completa <- df_maestra_completa %>%
  mutate(Universidad = str_trim(Universidad))  # Elimina espacios en blanco al principio y final

# Verificar los resultados después de la limpieza
cat("Ejemplos de la columna 'Universidad' después de la limpieza:\n")
print(head(df_maestra_completa$Universidad, 10))

# Guardar los resultados en un nuevo archivo Excel
output_path_universidad <- "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/bases_maestra_con_universidad.xlsx"
write_xlsx(df_maestra_completa, output_path_universidad)

cat("Archivo guardado en:", output_path_universidad, "\n")
