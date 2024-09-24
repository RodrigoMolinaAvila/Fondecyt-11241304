################ Proyecto bases de datos Scopus Economía #################
#* Creación : 28-05-2022
#* Autor    : Patricio Pavez <plpavez@gmail.com>
#*
#* Descripción : Construcción base de datos un conjunto de archivos con
#*               datos para análisis de redes de colaboración
#*               
#* Etapa 3: Consolidado de datos y configuración de bases de datos 
#*          solicitadas
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
library(genderizeR)


source("Scripts/UDF_Scopus_Econ.R")


Credenciales <- readRDS(file = ".Creds")[[1]]

# Ubicación base de datos Genderize (Para futuras ejecuciones)
genderize_bd <- "Datos/Genderize/Maestro_Genderizer.txt"


# Configuración credenciales Scopus
Token <- Credenciales$Crd$Token
Api_key <- Credenciales$Crd$Api_Key
hdr = inst_token_header(Token)
set_api_key(Api_key)



########################################################
### ********* CONFIGURACIÓN BD SOLICITADAS ********* ###
########################################################

# Carga de datos E2
out_publicaciones <- vroom(file = "Datos/Output/publicaciones_20220709.csv", 
                           delim = ";",
                           col_names = T,
                           col_types = cols(.default = "c"))

out_colaboradores <- vroom(file = "Datos/Output/colaboradores_20220709.csv", 
                           delim = ";",
                           col_names = T,
                           col_types = cols(.default = "c"))

out_afiliacion <- vroom(file = "Datos/Output/afiliaciones_20220709.csv", 
                        delim = ";",
                        col_names = T,
                        col_types = cols(.default = "c"))



#################################################################
### ********** DUPLICADOS DETECTADOS EN EXTRACCION ********** ###
### Esto reducirá el número de publicaciones reportadas en la ###
### estimación original lo que tendrá impacto además en los   ###
### consolidados de autores e afiliaciones                    ###
#################################################################

out_publicaciones <- out_publicaciones %>% distinct() # Reducción de 3.065 a 2.669
out_colaboradores <- out_colaboradores %>% distinct() # Reducción de 9.105 a 7.804
out_afiliacion <- out_afiliacion %>% distinct()       # Reducción de 6.970 a 6.003


#######################################################################################################################
# Construcción base Maestro de autores:
# Para consolidar la base maestro de autores se necesita separar la cosnstrucción en las sigientes dos etapas. 
# Etapa 1:
# En esta etapa, se procede a desduplicar los registros obtenidos en la tabla colaboradores. Un punto a considerar en
# este paso es la ocurrencia de casos donde el mismo autor aparece con distintas versiones del nombre o con atributos
# diferentes. Para estos casos se procederá a seleccionar el registro con más información.
# Etapa 2:
# Se procede a la extracción desde la API Scopus de la información relacionada a la trayectoria del autor mediante la 
# iteración sobre el listado de scopus id obtenidos en la etapa 1.
######################################################################################################################


#########
# Etapa 1
autores_wip <- out_colaboradores %>% 
  select(authid,
         surname,
         given_name,
         id_interno,
         orcid) %>% 
  distinct() %>% 
  group_by(authid) %>% 
  mutate(casos = n()) %>% 
  ungroup() %>% 
  arrange(authid) 

# Algunos ejemplos de autores duplicados:
autores_wip %>% 
  filter(casos > 1)


# Construyendo el registro más completo posible
maestro_autores_e1 <- autores_wip %>% 
  mutate(x_largo_nombre = nchar(str_squish(str_remove_all(paste(surname,given_name), pattern = "[:punct:]"))),
         x_n_ori = str_remove_all(paste(surname, given_name), pattern = "[:punct:]"),
         x_n_rec = str_remove_all(iconv(paste(surname, given_name), to="ASCII//TRANSLIT"), pattern = "[:punct:]"),
         x_mejor_nombre = ifelse(x_n_ori != x_n_rec, 1, 0)) %>% 
  arrange(authid, desc(x_largo_nombre), desc(x_mejor_nombre)) %>% 
  group_by(authid) %>% 
  mutate(x_id_nombre = row_number(),
         x_sel_apellido = ifelse(x_id_nombre == 1, str_squish(surname), ""),
         x_sel_nombre = ifelse(x_id_nombre == 1, str_squish(given_name), "")) %>% 
  mutate(aut_apellido = paste(x_sel_apellido, collapse = ""),
         aut_nombre = paste(x_sel_nombre, collapse = ""),
         aut_orcid = str_squish(paste(unique(orcid), collapse = " "))) %>% 
  ungroup() %>% 
  select(-starts_with("x_"),
         -surname,
         -given_name,
         -orcid,
         -casos) %>% 
  distinct()


maestro_autores_e1
# 3.070 registros únicos obtenidos

# Validación contra base de colaboradores
out_colaboradores %>% distinct(authid)
# OK.



#########
# Etapa 2
ls_autores <- maestro_autores_e1 %>% 
  pull(authid)


# Obteniendo la experiencia de los autores (*** Varias ejecuciones dependiendo del número de autores ***)
# La función Experiencia_Autor está diseñada para iterar sobre el máximo de autores posibles dependiendo
# de la cuota semanal (5.000 consultas). Por defecto, esta crea un archivo txt donde guarda el progreso
# obtenido en iteraciones anteriores. De existir, la ruta de este debe ser entregada en el parámetro
# respaldo, de lo contrario la función iterará sobre el listado completo nuevamente.

df_exp_autor <- Experiencia_Autor(autores = ls_autores,
                                  token = Token,
                                  api_key = Api_key,
                                  id_respaldo = NULL,
                                  af_hist = TRUE,
                                  areas_ls = TRUE) #3 hrs aprox para 3.070 autores
#id_respaldo = "202207091519"


#############################################################################################################


df_exp_autor <- vroom(file = "Datos/Output/Data_Experiencia_202207091519.txt",
                      delim = "|",
                      col_names = TRUE,
                      col_types = "icccccccccccc")

df_hist_afil <- vroom(file = "Datos/Output/Historial_Afiliacion_202207091519.txt",
                      delim = "|",
                      col_names = TRUE,
                      col_types = "icccc")

df_areas_publ <- vroom(file = "Datos/Output/Areas_Publicaciones_202207091519.txt",
                       delim = "|",
                       col_names = TRUE,
                       col_types = "icccc")


df_exp_autor <- df_exp_autor %>% 
  distinct()


maestro_autores_e1 <- maestro_autores_e1 %>% 
  inner_join(df_exp_autor %>% 
               select(-id_loop),
             by = "authid") 


# Inferencia del sexo del autore

df_sex_autor <- Inf_Sexo(autor_id = maestro_autores_e1$authid,
                         nombre = maestro_autores_e1$aut_nombre,
                         gen_bd_path = genderize_bd)


#Revisión de resultados inferencia del sexo
df_sex_autor %>% count(sexo)

df_sex_autor %>% filter(sexo == "") %>% view()  #La mayoría de los registros sin sexo tienen solo la inicial en el campo nombre


# Consolidando en base maestro
maestro_autores_e1 <- maestro_autores_e1 %>% 
  inner_join(df_sex_autor %>% 
               transmute(autor_id,
                         sexo,
                         prob_sexo = probabilidad),
             by = c("authid" = "autor_id"))


#######################################################################################################################################
#######################################################################################################################################
# CONFIGURANDO LAS BASES MAESTRO DE AUTORES 
maestro_autores_final <- maestro_autores_e1 %>% 
  select(-comentarios, -prob_sexo) %>% 
  mutate(aut_orcid = str_squish(str_replace_all(aut_orcid, "NA", ""))) %>% 
  mutate_if(is.character, replace_na, "") %>%
  mutate_if(is.numeric, replace_na, 0)


#Escribiendo salida autores
vroom_write(x = maestro_autores_final,
            file = paste0("Datos/Output/Output_final/Autores_maestro_final_", format(Sys.Date(), "%Y%m%d"), ".csv"),
            delim = ";",
            col_names = TRUE)

# Lectura 
maestro_autores_final <- vroom(file = "Datos/Output/Output_final/Autores_maestro_final_20220709.csv",
                               delim = ";",
                               col_names = TRUE,
                               col_types = "cccccnnnnnncncDc")

#######################################################################################################################################
#######################################################################################################################################
# CONFIGURANDO LAS BASES MAESTRO DE PUBLICACIONES
maestro_publicaciones_final <- out_publicaciones %>% 
  transmute(publ_id = dc_identifier,
            titulo = dc_title,
            descripcion = dc_description,
            autor_creador = dc_creator,
            nombre_revista = prism_publication_name,
            issn = prism_issn,
            e_issn = prism_e_issn,
            anio_publ = str_sub(prism_cover_date, 1, 4),
            doi = prism_doi,
            n_citas = citedby_count,
            n_autores = author_count_total,
            cod_subtipo = subtype,
            subtipo = subtype_description,
            fund_acr,
            fund_sponsor)

#Escribiendo salida publicaciones
vroom_write(x = maestro_publicaciones_final,
            file = paste0("Datos/Output/Output_final/Publicaciones_maestro_final_", format(Sys.Date(), "%Y%m%d"), ".csv"),
            delim = ";",
            col_names = TRUE)

# Lectura 
maestro_publicaciones_final <- vroom(file = "Datos/Output/Output_final/Publicaciones_maestro_final_20220709.csv",
                                     delim = ";",
                                     col_names = TRUE,
                                     col_types = "cccccccccnncccc")


#######################################################################################################################################
#######################################################################################################################################
# CONFIGURANDO LAS BASES MAESTRO DE SCOPUS VINCULO

# Base Scopus vínculos
scopus_vinculo <- out_colaboradores %>% 
  select(publ_id = dc_identifier,
         autor_id = authid,
         id_interno,
         afil_id = afid) %>% 
  arrange(publ_id)


#Escribiendo salida publicaciones
vroom_write(x = scopus_vinculo,
            file = paste0("Datos/Output/Output_final/Scopus_base_vinculo_", format(Sys.Date(), "%Y%m%d"), ".csv"),
            delim = ";",
            col_names = TRUE)

# Lectura 
scopus_vinculo <- vroom(file = "Datos/Output/Output_final/Scopus_base_vinculo_20220709.csv",
                        delim = ";",
                        col_names = TRUE,
                        col_types = "cccc")


#######################################################################################################################################
#######################################################################################################################################
# CONFIGURANDO LAS BASES MAESTRO DE INSTITUCIONES   **** TEMPORAL ****
maestro_instituciones_temp <- out_afiliacion %>% 
  select(afil_id = afid,
         afil_nombre = affilname,
         afil_ciudad = affiliation_city,
         afil_pais = affiliation_country) %>% 
  distinct()



#######################################################################################################################################
#######################################################################################################################################
# CONFIGURANDO LAS BASES MAESTRO DE INSTITUCIONES   **** TEMPORAL ****

# Maestro Instituciones
#Consolidando todas las instituciones de todos los df
ls_aff <- out_afiliacion %>% 
  distinct(afid) %>% 
  bind_rows(df_hist_afil %>% 
              distinct(afid = affiliation_id)) %>% 
  bind_rows(maestro_autores_final %>% 
              distinct(afid = af_actual)) %>% 
  distinct()




########################################################
# Quitar esta parte y luego la lista rds de la carpeta
saveRDS(object = ls_aff,
        file = "Datos/Output/Output_final/LISTA_AFF_BORRAR")

ls_aff <- readRDS(file = "Datos/Output/Output_final/LISTA_AFF_BORRAR")
########################################################




# Maestro instituciones
#maestro_inst <- tibble()

for (i in 1:nrow(ls_aff)) {
  
  #i <- 123
  
  message("Procesando affiliación ", i, " de ", nrow(ls_aff))
  
  id_consulta <- ls_aff[i,]$afid
  
  af_actualizada <- busca_datos_afil(id_consulta, api_key = Api_key, token = Token, base_acum = maestro_inst)
  
  maestro_inst <- bind_rows(maestro_inst, af_actualizada)
  
}

# Guardando resultados parciales
vroom_write(x = maestro_inst, 
            file = "Datos/Output/Output_final/Instituciones_parcial3.csv", 
            delim = ";", 
            col_names = TRUE) # Todos los campos son <chr>




##############################################################################################
# Formateando la salida para bases Historial de afiliación y Áreas de publicación

vroom_write(x = df_hist_afil %>% select(authid, affiliation_id),
            file = "Datos/Output/Output_final/Autores_historial_afiliacion_20220709.csv",
            delim = ";",
            col_names = TRUE)
            
vroom_write(x = df_areas_publ %>% select(-id_loop),
            file = "Datos/Output/Output_final/Autores_areas_publicacion_20220709.csv",
            delim = ";",
            col_names = TRUE)


