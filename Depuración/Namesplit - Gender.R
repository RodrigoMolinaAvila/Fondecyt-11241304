# Instalar y cargar las librerías necesarias
if (!require("readxl")) install.packages("readxl", dependencies=TRUE)
if (!require("gender")) install.packages("gender", dependencies=TRUE)
if (!require("writexl")) install.packages("writexl", dependencies=TRUE)
if (!require("dplyr")) install.packages("dplyr", dependencies=TRUE)

library(readxl)
library(gender)
library(writexl)
library(dplyr)

# Definir la ruta al archivo Excel
file_path <- "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/Bases de datos Maestra_Becarios 2014,2015,2016/Bases de datos_maestra.xlsx"

# Cargar la hoja 'BaseMaestra' desde el archivo Excel
df <- read_excel(file_path, sheet = "BaseMaestra")

# Eliminar columnas innecesarias
df <- df[ , !grepl("Unnamed", names(df))]

# Separar nombres teniendo en cuenta diferentes longitudes de nombres y apellidos
df <- df %>%
  mutate(
    Primer_Nombre = sapply(strsplit(NOMBRE, " "), `[`, 1),
    Segundo_Nombre = sapply(strsplit(NOMBRE, " "), function(x) ifelse(length(x) >= 2, x[2], NA)),
    Apellido_Paterno = sapply(strsplit(NOMBRE, " "), function(x) ifelse(length(x) >= 3, x[length(x)-1], NA)),
    Apellido_Materno = sapply(strsplit(NOMBRE, " "), function(x) ifelse(length(x) == 4, x[4], NA))
  )

# Realizar la inferencia de género utilizando la librería gender
gender_data <- gender(df$Primer_Nombre, method = "ssa")

# Fusionar los resultados con el dataframe original
df$SEXO_2 <- toupper(gender_data$gender[match(df$Primer_Nombre, gender_data$name)])

# Crear una nueva columna SEXO_COMPLETO para estandarizar los valores de género
df <- df %>%
  mutate(
    SEXO_COMPLETO = case_when(
      !is.na(SEXO) & SEXO %in% c("MASCULINO", "FEMENINO") ~ SEXO,
      SEXO_2 == "MALE" ~ "MASCULINO",
      SEXO_2 == "FEMALE" ~ "FEMENINO",
      TRUE ~ NA_character_
    )
  )

# Reordenar las columnas para que SEXO_2 y SEXO_COMPLETO queden junto a SEXO
df <- df %>%
  select(FOLIO, NOMBRE, Primer_Nombre, Segundo_Nombre, Apellido_Paterno, Apellido_Materno, SEXO, SEXO_2, SEXO_COMPLETO, everything())

# Mostrar las primeras filas para verificar el resultado
print(head(df[, c("NOMBRE", "Primer_Nombre", "SEXO", "SEXO_2", "SEXO_COMPLETO")], 10))

# Guardar el dataframe procesado (opcional)
output_path <- "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/Bases de datos_maestra_procesada.xlsx"
write_xlsx(df, output_path)
