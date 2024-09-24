################ Proyecto bases de datos Scopus Economía #################
#* Creación : 21-05-2022
#* Autor    : Patricio Pavez <plpavez@gmail.com>
#*
#* Descripción : Construcción base de datos un conjunto de archivos con
#*               datos para análisis de redes de colaboración
#*               
#* Etapa 1: Extracción de todos los autores que cuyos nombres coinciden
#*          con listado inicial recibido               
##########################################################################

#### Configuración Inicial ####
setwd(dir = "C:/Proyecto_Scopus/Scopus_Economia/")
library(plyr)
library(tidyverse)
library(vroom)
library(rscopus)
source("Scripts/UDF_E1.R")


# Carga archivo inicial con nombres de los autores de interés
autores <- vroom(file = "Datos/AcadémicosEcon.csv") %>% 
  filter(!is.na(Nombre))


# Configuración credenciales Scopus
Token <- "6afd856cd6a4bbf9601589d089cef526"
Api_key <- "14de13adbc4c8c7cd9e05a2abe0a9412"


# Creación objeto credenciales
Credenciales_Scopus <- list(api_key = Api_key,
                            hdr = inst_token_header(Token))


# Comenzando la extracción de información para autores
base_autores <- tibble()

for(aut in 1:nrow(autores)) {
  
  autor <- autores[aut,]
  
  # Realizando la consulta Scoups
  res_autor <- Consulta_Autor(id_interno = aut,
                              nombre_autor = autor$Nombre,
                              apellido_autor = autor$Apellido1,
                              credenciales = Credenciales_Scopus,
                              tot_autores = nrow(autores))  
  
  
  base_autores <- bind_rows(base_autores, res_autor)
  
}


################################################################################################
# Escribiendo output en formato .rds para evitar re-ejecución
saveRDS(object = base_autores,
        file = "Datos/Seleccion_Autores_It1.rds")

base_autores <- readRDS(file = "Datos/Seleccion_Autores_It1.rds")
################################################################################################


# Extracción casos con 0 coincidencias para modificación manual en .txt
sin_coincidencia <- base_autores %>% 
  filter(numero_coincidencias == 0) %>% 
  inner_join(autores %>% 
               mutate(id = row_number()),
             by = "id") %>% 
  transmute(id,
            nombre_ajustado = Nombre,
            apellido_ajustado = Apellido1,
            comentario = "Modificado a un solo nombre")


# Guardando archivo en formato txt para modificación manual del nombre
vroom_write(x = sin_coincidencia,
            path = "Datos/Sin_Coincidencia_E1.txt",
            delim = ",",
            col_names = TRUE)


#***********************************************************************************
#**** EN ESTA PARTE, SE REVISÓ CADA NOMBRE SIN COINCIDENCIA DE MANERA MANUAL     ***
#**** EL RESULTADO SE GUARDO EN EL MISMO ARCHIVO PARA EJECUCION DE 2DA ITERACIÓN ***
#***********************************************************************************

# Leyendo resultados modificados
autores_mod <- vroom(file = "Datos/Sin_Coincidencia_E1.txt",
                     delim = ",",
                     col_names = TRUE)

# Segunda iteración
base_autores_mod <- tibble()

for(aut in 1:nrow(autores_mod)) {
  
  autor <- autores_mod[aut,]
  
  # Realizando la consulta Scoups
  res_autor <- Consulta_Autor(id_interno = autor$id,
                              nombre_autor = autor$nombre_ajustado,
                              apellido_autor = autor$apellido_ajustado,
                              credenciales = Credenciales_Scopus,
                              tot_autores = nrow(autores_mod))  
  
  
  base_autores_mod <- bind_rows(base_autores_mod, res_autor)
  
}

# Reparando el campo nombre entregado en el df de la segunda iteración, dado que este fue alterado de forma manual
rep_nombre <- base_autores %>% 
  filter(numero_coincidencias == 0) %>% 
  select(id, 
         nombre_fix = nombre_entregado)

base_autores_mod <- base_autores_mod %>% 
  inner_join(rep_nombre,
             by = "id") %>% 
  mutate(nombre_entregado = nombre_fix) %>% 
  select(-nombre_fix)


################################################################################################
# Escribiendo output en formato .rds para segunda iteración
saveRDS(object = base_autores_mod,
        file = "Datos/Seleccion_Autores_It2.rds")

base_autores_mod <- readRDS(file = "Datos/Seleccion_Autores_It2.rds")
################################################################################################



# Consolidando ambas iteraciones
base_autores_final <- bind_rows(base_autores %>% 
                                  filter(numero_coincidencias != 0),
                                base_autores_mod) %>% 
  arrange(id)


base_autores_final <- base_autores_final %>% arrange(id)


# Anexando información de segunda iteración
base_autores_final <- base_autores_final %>% 
  left_join(autores_mod %>% 
              select(id,
                     comentario_i2 = comentario),
            by = "id") %>% 
  mutate_all(replace_na, "") %>% 
  relocate(comentario_i2,
           .before = numero_coincidencias) 



###############################################################################################
# Escribiendo output en formato .rds para segunda iteración
saveRDS(object = base_autores_final,
        file = "Datos/Seleccion_Autores_Final.rds")

base_autores_final <- readRDS(file = "Datos/Seleccion_Autores_Final.rds")
################################################################################################




# Renombrando campos para salida Excel
names(base_autores_final) <- c("ID interno", "Nombre entregado", "Nombre consultado", "Modificación segunda iteración", "Número de coincidencias", "Variantes del nombre", "Identificador Scopus",
  "Orcid", "Número de publicaciones", "Áreas de publicación", "Afiliación actual", "Ciudad de afiliación", "Pais de afiliación")

# Escribiendo output en formato Excel para revisión
xlsx::write.xlsx(x = base_autores_final,
                 file = "Datos/Salida_Autores.xlsx",
                 sheetName = "Resultados",
                 col.names = T,
                 showNA = FALSE)


Consulta_Autor(id_interno = 1,
               nombre_autor = "Borja",
               apellido_autor = "Larrain",
               credenciales = Credenciales_Scopus,
               tot_autores = 1) %>% view()

