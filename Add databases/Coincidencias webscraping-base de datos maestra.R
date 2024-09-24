library(dplyr)
library(readxl)
library(writexl)

file_path_maestra <- "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/Bases de datos_maestra_procesada.xlsx"
file_path_extraida <- "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/investigadores_educacion_completa.xlsx"

df_maestra <- read_excel(file_path_maestra)
df_extraida <- read_excel(file_path_extraida)

# Normalizar los nombres para mejorar las coincidencias
df_maestra <- df_maestra %>% mutate(NOMBRE = tolower(trimws(NOMBRE)))
df_extraida <- df_extraida %>% mutate(Nombre = tolower(trimws(Nombre)))

# Identificar las coincidencias
coincidencias <- df_extraida %>% filter(Nombre %in% df_maestra$NOMBRE)
cat("Número de coincidencias encontradas:", nrow(coincidencias), "\n")

# Complementar la columna 'Universidad Título Profesional' en la base maestra
df_maestra_completa <- df_maestra %>%
  left_join(coincidencias, by = c("NOMBRE" = "Nombre")) %>%
  mutate(
    `Universidad Título Profesional` = ifelse(
      is.na(`Universidad Título Profesional`), 
      Educacion, 
      `Universidad Título Profesional`
    )
  )

cat("Número de filas complementadas con la Universidad Título Profesional:", sum(!is.na(df_maestra_completa$Educacion)), "\n")


# Guardamos

output_path_completo <- "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/bases_maestra_complementada.xlsx"
write_xlsx(df_maestra_completa, output_path_completo)

cat("Número de coincidencias encontradas:", nrow(coincidencias), "\n")
cat("Número de filas complementadas con la Universidad Título Profesional:", sum(!is.na(df_maestra_completa$Educacion)), "\n")
cat("Archivo guardado en:", output_path_completo, "\n")


# Revisar algunas filas para ver la estructura de la columna 'Universidad Título Profesional'
cat("Ejemplos de la columna 'Universidad Título Profesional':\n")
print(head(df_maestra_completa$`Universidad Título Profesional`, 50))

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



