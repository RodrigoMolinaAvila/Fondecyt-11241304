################ Proyecto bases de datos Scopus Economía #################
#* Creación : 28-05-2022
#* Autor    : Patricio Pavez <plpavez@gmail.com>
#*
#* Descripción : Construcción base de datos un conjunto de archivos con
#*               datos para análisis de redes de colaboración
#*               
#* Etapa 2: Extracción y guardado datos desde Scopus para listado de 
#*          autores y sus publicaciones
#*
##########################################################################


#### Configuración Inicial ####
setwd(dir = "C:/Proyectos_R/Scopus_Economia/")
library(tidyverse)
library(vroom)
library(rscopus)
library(janitor)
library(countrycode)
library(svDialogs)

source("Scripts/UDF_Scopus_Econ.R")


Credenciales <- readRDS(file = ".Creds")[[1]]


# Configuración credenciales Scopus
Token <- Credenciales$Crd$Token
Api_key <- Credenciales$Crd$Api_Key
hdr = inst_token_header(Token)
set_api_key(Api_key)


# LECTURA DE ARCHIVO CON AUTORES SELECCIONADOS
autores_sel <- vroom(file = "Datos/autores_sel.csv",
                     delim = ";",
                     col_types = "ic") 



# Evaluando consitencia de datos devueltos
autores_sel %>% 
  group_by(scopus_id) %>% 
  mutate(casos = n()) %>% 
  filter(casos > 1) %>% 
  arrange(scopus_id)
# Existen 3 id de autores duplicados. Necesito conservar solo 1 de ellos

autores_sel <- autores_sel %>%
  distinct() %>% # Había un par id_interno, scopus_id duplicado para id_interno = 187
  arrange(id_interno) %>% 
  group_by(scopus_id) %>% 
  mutate(casos = row_number()) %>% 
  filter(casos == 1) %>% 
  select(-casos)


#* Base de datos de autores seleccionados contenía algunos duplicados.
#* Estos fueron removidos del conjunto a procesar quedando así 237 scopus_id
#* La desduplicación del autor, vinculada al id interno 


publicaciones <- tibble()
colaboradores <- tibble()
afiliaciones <- tibble()
vinculos <- tibble()


# Extracción de registros scopus para cada autor
for(i in 1:nrow(autores_sel)){
  
  #i <- 1
  
  message("Procesando autor ", i, " de ", nrow(autores_sel))
  
  autor <- autores_sel[i,2]
  
  consulta <- author_list(au_id = autor,
                          api_key = Api_key,
                          headers = hdr,
                          verbose = FALSE)
  
  if(is.null(consulta$entries[[1]]$error)){
    
    df <- gen_entries_to_df(consulta$entries)
    
    # Publicaciones
    publi <- as_tibble(df$df) %>% 
      mutate(entry_number = as.numeric(entry_number))
    
    
    # Colaboradores
    colab <- as_tibble(df$author) %>% 
      inner_join(publi %>% 
                   select(entry_number,
                          `dc:identifier`),
                 by = "entry_number") %>% 
      left_join(autores_sel,
                by = c("authid" = "scopus_id"))
    
    
    # Afiliaciones
    afili <- as_tibble(df$affiliation)
    
    if(nrow(afili) > 0){
      
      afili <- afili %>% 
        inner_join(publi %>% 
                     select(entry_number,
                            `dc:identifier`),
                   by = "entry_number")
      
    }
    
    
    
    # Consolidando información extraida
    publicaciones <- bind_rows(publicaciones, publi)
    colaboradores <- bind_rows(colaboradores, colab)
    afiliaciones <- bind_rows(afiliaciones, afili)
    
  }else{
    
    message("Ningun resultado para autor ", autor)
    
  }
  
}

#####################################################################
# Preparando salidas de Etapa 2
#####################################################################


#############################################
### PUBLICACIONES
out_publicaciones <- publicaciones %>% 
  select(-`@_fa`,
         -freetoread.value, 
         -freetoreadLabel.value,
         -entry_number) %>% 
  clean_names() %>%
  filter(!is.na(dc_identifier)) %>% 
  mutate_all(replace_na, "")
# 3.065 publicaciones obtenidas a partir de los 237 autores seleccionados


#############################################
### COLABORADORES
out_colaboradores <- colaboradores %>%
  select(-`@_fa`, -
           `afid.@_fa`,
         -entry_number) %>% 
  clean_names() %>% 
  mutate(id_interno = as.character(id_interno)) %>% 
  mutate_all(replace_na, "")
# 9.105 colaboradores asociados a las publicaciones extraídas


### Validaciones

# Verificando numero de colaboradores
out_publicaciones %>% 
  mutate(author_count_total = as.integer(author_count_total)) %>% 
  summarise(minimo = min(author_count_total),
            maximo = max(author_count_total), # Numero máximo es 93. No hay colaboradores excluidos por exceso de resultados 
            total = sum(author_count_total))  # 9.105 OK


out_colaboradores %>% 
  filter(authid %in% autores_sel) %>% 
  distinct(authid) 
# No hay autores de los iniciales que no aparecen aquí. Ok

autores_c_pub <- out_colaboradores %>% 
  filter(authid %in% autores_sel$scopus_id) %>% 
  distinct(authid) %>% 
  pull()
# Solo hay 1 autor para el cuál no encontró publicaciones. Verificar si esto es correcto

autores_sel %>% 
  filter(!scopus_id %in% autores_c_pub)
#* Corresponde al autor 180: Pablo Gonzalez Socups Id: 1063294 
#*   - Encontre un Pablo Gonzalez con este id scopus: 56225119500
#*   - Revisar https://www.dii.uchile.cl/quien/pablo-gonzalez/
#*   - Si es el caso, inculir Scopus Id en el archivo de entrada



#############################################
### AFILIACIONES
out_afiliacion <- afiliaciones %>%
  select(-`@_fa`,
         -entry_number) %>% 
  clean_names() %>% 
  filter(!is.na(afid)) %>%  # 109 registros sin información para afiliación
  mutate_all(replace_na, "")
# 6.970 registros



##########################################################
### ESCRIBIENDO ARCHIVOS DE SALIDA EN FORMATO CSV

vroom_write(x = out_publicaciones,
            path = paste0("Datos/Output/publicaciones_", format(Sys.Date(), "%Y%m%d"), ".csv"),
            delim = ";",
            col_names = TRUE)

vroom_write(x = out_colaboradores,
            path = paste0("Datos/Output/colaboradores_", format(Sys.Date(), "%Y%m%d"), ".csv"),
            delim = ";",
            col_names = TRUE)

vroom_write(x = out_afiliacion,
            path = paste0("Datos/Output/afiliaciones_", format(Sys.Date(), "%Y%m%d"), ".csv"),
            delim = ";",
            col_names = TRUE)

