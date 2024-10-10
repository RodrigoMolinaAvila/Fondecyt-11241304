# Instalar y cargar las librerías necesarias
if (!require("rvest")) install.packages("rvest", dependencies=TRUE)
if (!require("dplyr")) install.packages("dplyr", dependencies=TRUE)

library(rvest)
library(dplyr)

# Definir el rango de IDs para iterar
start_id <- 101
end_id <- 49242

# Crear un DataFrame vacío para almacenar los resultados
df_investigadores <- data.frame(
  Nombre = character(),
  Educacion = character(),
  Enlace = character(),
  stringsAsFactors = FALSE
)

# Iterar sobre los IDs
for (id in start_id:end_id) {
  # Construir la URL
  url <- paste0("https://investigadores.anid.cl/es/public_search/researcher?id=", id, "#home")
  
  # Intentar extraer la información, manejar errores si la página no existe o hay problemas de extracción
  try({
    page <- read_html(url)
    
    # Extraer el nombre del investigador
    nombre <- page %>%
      html_node("h3 strong") %>%
      html_text(trim = TRUE)
    
    # Extraer la información de educación
    educacion <- page %>%
      html_node(xpath = '//*[@id="home"]/div[3]') %>%
      html_text(trim = TRUE)
    
    # Agregar los resultados al DataFrame
    df_investigadores <- rbind(df_investigadores, data.frame(
      Nombre = nombre,
      Educacion = educacion,
      Enlace = url,
      stringsAsFactors = FALSE
    ))
    
    # Mostrar progreso en la consola
    cat("Extracción exitosa para ID:", id, "\n")
    
  }, silent = TRUE)
}

# Mostrar los resultados finales
print(df_investigadores)

# Guardar los resultados para su posterior uso
output_path <- "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/investigadores_educacion_completa.xlsx"
write_xlsx(df_investigadores, output_path)
