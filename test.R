library(dplyr)
library(stringr)
library(writexl)

# Revisar algunas filas para ver la estructura de la columna 'Universidad Título Profesional'
cat("Ejemplos de la columna 'Universidad Título Profesional':\n")
print(head(df_maestra_completa$`Universidad Título Profesional`, 10))

# Extraer y limpiar el nombre de la universidad
df_maestra_completa <- df_maestra_completa %>%
  mutate(
    Universidad = str_extract(`Universidad Título Profesional`, "^[^,]+") %>% 
                  str_trim()  # Extrae la parte antes de la primera coma y elimina espacios en blanco
  )

# Verificar los resultados
cat("Ejemplos de la columna 'Universidad' después de la extracción y limpieza:\n")
print(head(df_maestra_completa$Universidad, 10))

# Guardar los resultados en un nuevo archivo Excel
output_path_universidad <- "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/bases_maestra_con_universidad.xlsx"
write_xlsx(df_maestra_completa, output_path_universidad)

cat("Archivo guardado en:", output_path_universidad, "\n")

# Generar el path de la carpeta del script
script_dir <- dirname(normalizePath("C:/Users/rodri/OneDrive/Escritorio/Roxana Files/test.R"))

cat("El path de la carpeta del script es:", script_dir, "\n")
