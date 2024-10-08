library(readxl)
library(dplyr)
library(stringr)

# Cargar las dos hojas Excel desde el directorio especificado
maestra <- read_excel("C:/Users/rodri/OneDrive/Escritorio/Roxana Files/bases_maestra_complementada.xlsx")
anid <- read_excel("C:/Users/rodri/OneDrive/Escritorio/Roxana Files/BDH_HISTORICA.xlsx")

# Filtrar los datos de la base ANID según los criterios indicados
anid_filtrada <- anid %>%
  filter(PROGRAMA == "FONDECYT", 
         INSTRUMENTO %in% c("REGULAR", "POSTDOCTORADO"),
         AGNO_FALLO %in% 2014:2024)

# Normalizar nombres a mayúsculas en ambas bases y limpiar espacios
maestra <- maestra %>%
  mutate(across(c(Primer_Nombre, Segundo_Nombre, Apellido_Paterno, Apellido_Materno), 
                ~ toupper(gsub("\\s+", " ", .)))) 

anid_filtrada <- anid_filtrada %>%
  mutate(NOMBRE_RESPONSABLE = toupper(gsub("\\s+", " ", NOMBRE_RESPONSABLE)))

# Crear todas las combinaciones de nombres en la base maestra
maestra <- maestra %>%
  mutate(
    comb_1 = paste(Primer_Nombre, Segundo_Nombre, Apellido_Paterno, Apellido_Materno),
    comb_2 = paste(Primer_Nombre, Segundo_Nombre, Apellido_Materno, Apellido_Paterno),
    comb_3 = paste(Primer_Nombre, Apellido_Paterno, Apellido_Materno),
    comb_4 = paste(Primer_Nombre, Apellido_Materno, Apellido_Paterno),
    comb_5 = paste(Segundo_Nombre, Primer_Nombre, Apellido_Paterno, Apellido_Materno),
    comb_6 = paste(Segundo_Nombre, Primer_Nombre, Apellido_Materno, Apellido_Paterno),
    comb_7 = paste(Segundo_Nombre, Apellido_Paterno, Apellido_Materno),
    comb_8 = paste(Segundo_Nombre, Apellido_Materno, Apellido_Paterno),
    comb_9 = paste(Primer_Nombre, Segundo_Nombre, Apellido_Materno),  
    comb_10 = paste(Segundo_Nombre, Primer_Nombre, Apellido_Materno), 
    comb_11 = paste(Primer_Nombre, Segundo_Nombre, Apellido_Paterno), 
    comb_12 = paste(Segundo_Nombre, Primer_Nombre, Apellido_Paterno)  
  )

# Modificar la función hacer_join para aceptar relaciones muchos a muchos
hacer_join <- function(maestra, anid, comb_name) {
  maestra %>%
    inner_join(anid, by = setNames("NOMBRE_RESPONSABLE", comb_name), relationship = "many-to-many")
}

# Realizar el join para cada combinación sin advertencia
resultados_1 <- hacer_join(maestra, anid_filtrada, "comb_1")
resultados_2 <- hacer_join(maestra, anid_filtrada, "comb_2")
resultados_3 <- hacer_join(maestra, anid_filtrada, "comb_3")
resultados_4 <- hacer_join(maestra, anid_filtrada, "comb_4")
resultados_5 <- hacer_join(maestra, anid_filtrada, "comb_5")
resultados_6 <- hacer_join(maestra, anid_filtrada, "comb_6")
resultados_7 <- hacer_join(maestra, anid_filtrada, "comb_7")
resultados_8 <- hacer_join(maestra, anid_filtrada, "comb_8")
resultados_9 <- hacer_join(maestra, anid_filtrada, "comb_9")
resultados_10 <- hacer_join(maestra, anid_filtrada, "comb_10")
resultados_11 <- hacer_join(maestra, anid_filtrada, "comb_11")
resultados_12 <- hacer_join(maestra, anid_filtrada, "comb_12")

# Calcular el total de coincidencias en todos los joins
total_coincidencias <- nrow(resultados_1) + nrow(resultados_2) + nrow(resultados_3) + 
  nrow(resultados_4) + nrow(resultados_5) + nrow(resultados_6) + 
  nrow(resultados_7) + nrow(resultados_8) + nrow(resultados_9) + 
  nrow(resultados_10) + nrow(resultados_11) + nrow(resultados_12)

# Mostrar el total de coincidencias encontradas
print(paste("Total de coincidencias en todas las combinaciones:", total_coincidencias))
# Unir todas las combinaciones de coincidencias en una sola base de datos
resultados_unidos <- bind_rows(resultados_1, resultados_2, resultados_3, 
                               resultados_4, resultados_5, resultados_6, 
                               resultados_7, resultados_8, resultados_9, 
                               resultados_10, resultados_11, resultados_12)

# Eliminar duplicados si es necesario
resultados_unidos <- distinct(resultados_unidos)

# Unir los resultados con la base de datos maestra manteniendo todas las filas de la maestra
maestra_completa <- left_join(maestra, resultados_unidos, by = c("Primer_Nombre", "Segundo_Nombre", "Apellido_Paterno", "Apellido_Materno"))

# Guardar la base de datos maestra completa con los complementos en formato .xlsx
write_xlsx(maestra_completa, "C:/Users/rodri/OneDrive/Escritorio/Roxana Files/Base Maestra + ANID.xlsx")

# Mensaje de confirmación
print("Base de datos maestra completa exportada con los complementos encontrados como maestra_completa_con_complementos.xlsx")