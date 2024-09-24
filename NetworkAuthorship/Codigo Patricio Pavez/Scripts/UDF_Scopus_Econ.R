#################### Proyecto bases de datos Scopus Economía ##################
# Autor    : Patricio Pavez <plpavez@gmail.com>                               #
# Creación : 21-05-2022                                                       #
#                                                                             #
# Descripción : Funciones personalizadas creadas para realización de tareas   #
#               repetitivas y que complejizan la lectura del flujo principal. #
###############################################################################

# Consulta_Autor()
# Función encargada de realizar la consulta a la API de Scopus para obtención del id de autor y otros atributos
# Parámetros: El nombre y apellido del autor, ademas de las credenciales Scopus
# Salida: Dataframe (tibble) de una fila con resultado de la consulta

Consulta_Autor <- function(id_interno, nombre_autor, apellido_autor, credenciales, tot_autores){
  
  pausa <- 0.2
  
  nombre <- iconv(nombre_autor, from = "UTF-8", to="ASCII//TRANSLIT")
  apellido <- iconv(apellido_autor, from = "UTF-8", to="ASCII//TRANSLIT")
  
  message("Procesando autor (", id_interno, "/", tot_autores, "): ", nombre, " ", apellido)
  
  
  Sys.sleep(pausa)
  message("    - Consulta Scopus")
  
  consulta <- get_complete_author_info(last_name = apellido,
                                       first_name = nombre,
                                       api_key = credenciales$api_key,
                                       headers = credenciales$hdr,
                                       verbose = FALSE)
  
  # Número de candidatos encontrados
  candidatos <- as.numeric(consulta$content$`search-results`$`opensearch:totalResults`)
  
  if (candidatos > 200) {
    
    candidatos <- 200
    
  }
  
  message("    - Candidatos encontrados: ", candidatos)
  
  if(consulta$get_statement$status_code == 200 & candidatos > 0){
    
    resultado <- tibble()  
    
    for (candidato in 1:candidatos) {
      
      Sys.sleep(pausa)
      message("        - Procesando candidato ", candidato, " de ", candidatos, " para ", nombre, " ", apellido)    
      
      info_autor <- consulta$content$`search-results`$entry[[candidato]]
      
      scopus_id <- str_replace(info_autor$`dc:identifier`, "AUTHOR_ID:", "")
      orcid <- info_autor$orcid
      
      variantes <- tibble()
      tryCatch({
        
        variantes <- ldply(info_autor$`name-variant`, data.frame)  
        
      },error = function(e){
        
        message("Registro sin nombres variantes")
        
      })
      
      if(nrow(variantes) > 0){
        
        nombre_variantes <- variantes %>% 
          mutate(variante_nombre = paste(given.name, surname),
                 largo = nchar(variante_nombre)) %>% 
          filter(largo > nchar(paste(nombre, apellido))) %>% 
          arrange(desc(largo)) %>% 
          pull(variante_nombre) %>% 
          paste(collapse = ", ")
        
      }else{
        
        nombre_variantes <- ""
        
      }
      
      
      n_publicaciones <- as.numeric(info_autor$`document-count`)
      
      
      if(length(info_autor$`subject-area`[[1]]) == 0){
        
        areas <- ""
        
      }else if(length(info_autor$`subject-area`[[1]]) == 1){
        
        areas <- info_autor$`subject-area`[[1]]
        
      }else{
        
        areas <- ldply(info_autor$`subject-area`, data.frame) %>% 
          pull(`X.abbrev`) %>% 
          paste(collapse = "/")
        
      }
      
      
      # Afiliación actual
      institucion <- info_autor$`affiliation-current`$`affiliation-name`
      ciudad <- info_autor$`affiliation-current`$`affiliation-city`
      pais <- info_autor$`affiliation-current`$`affiliation-country`
      
      
      # Construyendo df final
      Sys.sleep(pausa)
      message("        - Consolidando resultados")
      
      resultado_candidato <- tibble(id = id_interno,
                                    nombre_entregado = paste(nombre_autor, apellido_autor),
                                    nombre_consultado = paste(nombre, apellido),
                                    numero_coincidencias = candidatos,
                                    variantes_nombre = nombre_variantes,
                                    id_scopus = scopus_id,
                                    orcid = ifelse(!is.null(orcid), orcid, ""),
                                    numero_publicaciones = n_publicaciones,
                                    areas_publicacion = ifelse(!is_null(areas), areas, ""),
                                    afiliacion_actual = ifelse(!is_null(institucion), institucion, ""),
                                    ciudad_afiliacion = ifelse(!is_null(ciudad), ciudad, ""),
                                    pais_afiliacion = ifelse(!is_null(pais), pais, ""))
      
      Sys.sleep(pausa)
      message("        - Autor procesado exitosamente")
      
      resultado <- bind_rows(resultado, resultado_candidato)
      
    }
    
  }else{
    
    Sys.sleep(pausa)
    message("Consulta retorna error ", consulta$get_statement$status_code, " para autor ", nombre, " ", apellido)
    
    resultado <- tibble(id = id_interno,
                        nombre_entregado = paste(nombre_autor, apellido_autor),
                        nombre_consultado = paste(nombre, apellido),
                        numero_coincidencias = candidatos)
    
  }
  
  return(resultado)
  
}

#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################

# vinc_aut_afil()
# Función encargada de vincular a cada autor con su institución de afiliación en el momento de la publicación
# Parámetros: El objeto entries de la respuesta de la consulta Scopus author_list
# Salida: Dataframe (tibble) de una todos los autores de la publicación con sus respectivas afiliaciones
vinc_aut_afil <- function(ls_pubs){
  
  autor_afil <- tibble()
  
  #Identifica el número de publicaciones
  n_publicaciones <- length(ls_pubs)
  
  
  # Iteración sobre cada publicación
  for (i in 1:n_publicaciones) {
    
    publicacion <- ls_pubs[[i]]
    
    # Identificando el número de autores 
    n_autores <- as.numeric(publicacion$`author-count`$`@total`)
    
    # Iteración sobre cada autor en la publicación
    for(j in 1:n_autores){
      
      autor <- publicacion$author[[j]]      
      
      n_afiliaciones <- length(autor$afid)
      
      # Iteración sobre cada afiliación del autor en la publicación
      if (n_afiliaciones > 0) {
        
        for(k in 1:n_afiliaciones){
          
          afid <- autor$afid[[k]]$`$`
          
          #Construyendo df salida
          salida <- tibble("dc_identifier" = ls_pubs[[i]]$`dc:identifier`,
                           "authid" = autor$authid,
                           "afid" = afid)
          
          #Anexando resultados a df principal
          autor_afil <- bind_rows(autor_afil, salida)
          
        }
        
      }else{
        
        #Construyendo df salida
        salida <- tibble("dc_identifier" = ls_pubs[[i]]$`dc:identifier`,
                         "authid" = autor$authid,
                         "afid" = "99999999")
        
        #Anexando resultados a df principal
        autor_afil <- bind_rows(autor_afil, salida)
        
      }
      
    }
    
  }
  
  autor_afil <- autor_afil %>% 
    distinct()
  
  return(autor_afil)
  
}


#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################

#autores <- ls_autores
#token <- Token
#api_key <- Api_key 
#id_respaldo <- NULL
#af_hist <- FALSE
#areas_ls <- FALSE


Experiencia_Autor <- function(autores, token, api_key, id_respaldo = NULL, af_hist = TRUE, areas_ls = TRUE){
  
  no_respaldo <- is.null(id_respaldo)
  
  if (no_respaldo) {
    
    
    respuesta <- dlg_message(message = "La funcion Experiencia_Autor() puede recibir como parametro archivos de ejecuciones anteriores.
Seleccione SI solo en caso de ser la primera ejecucion.",
                             type = "yesno")$res
    
    if(respuesta == "no"){
      
      stop("Ejecucion cancelada por el usuario.",
           call. = FALSE)
      
    }
    
    id_respaldo <- paste0(str_replace_all(string = Sys.Date(),
                                          pattern = "-",
                                          replacement = ""),
                          str_replace(string = str_extract(string = Sys.time(),
                                                           pattern = "\\d{2}:\\d{2}"),
                                      pattern = ":",
                                      replacement = ""))
    
    aut_sec_nuevo <- TRUE
    
    message(paste0("Id de respaldo generado: ", id_respaldo))
    
  }else{
    
    #Leyendo archivo con ejecuciones previas
    tryCatch({
      
      anteriores <- vroom(file = paste0("Datos/Output/Data_Experiencia_",id_respaldo,".txt"),
                          delim = "|",
                          col_names = TRUE,
                          col_types = "ccddddccc")
      
    }, error = function(e){
      
      stop("No es posible leer el archivo de respaldo.
       Archivo input  : ", paste0("Datos/Output/Data_Experiencia_",id_respaldo,".txt"), "
       Ruta completa  : ", getwd(), "/", paste0("Datos/Output/Data_Experiencia_",id_respaldo,".txt"),
           call. = FALSE)
      
    })
    
    #Eliminando autores ya procesados anteriormente
    autores <- tibble(authid = autores) %>% 
      anti_join(y = anteriores,
                by = "authid") %>% 
      pull(authid)
    
    rm(anteriores)
    
    aut_sec_nuevo <- FALSE
    
    message(paste0("Anexando resultados en: ", respaldo))
    
  }
  
  n_autores <- length(autores)
  
  T1 <- Sys.time()
  rep_n <- 10
  l_msj <- round(n_autores / rep_n,0)
  
  message(paste0("Iniciando extraccion de experiencia para ", n_autores, " autores. (Hora Inicio: ", T1, ")")) 
  
  hdr = inst_token_header(token)
  set_api_key(api_key)
  
  df_info_autor <- tibble()
  df_afil_hist <- tibble()
  df_area_publ <- tibble()
  
  t_proc <- c()
  
  for(i in 1:length(autores)){
    
    #i <- 8
    
    t_ini <- Sys.time()
    
    autor_id <- autores[i]
    
    print(paste0(i, " - ", autor_id))
    
    
    vroom_write(x = tibble(i = as.character(i), autor = autor_id, chckpt = "1"), file = "Datos/Output/Log_for_autores.txt", delim = ";", append = TRUE)
    
    #autor_id <- "12041275600"
    
    Sys.sleep(1)
    
    #Obteniendo información extra para el autor
    consulta <- author_retrieval(au_id = autor_id,
                                 api_key = api_key,
                                 view = "ENHANCED",
                                 headers = hdr,
                                 verbose = FALSE)
    
    Sys.sleep(1)
    
    hist_afil <- tibble()
    sub_area <- tibble()
    
    if(consulta$get_statement$status_code == 200){
      
      vroom_write(x = tibble(i = as.character(i), autor = autor_id, chckpt = "2"), file = "Datos/Output/Log_for_autores.txt", delim = ";", append = TRUE)
      
      extras <- consulta$content$`author-retrieval-response`
      
      #message(i, " - ", autor_id)
      
      if(length(extras) == 1){
        
        vroom_write(x = tibble(i = as.character(i), autor = autor_id, chckpt = "2.1"), file = "Datos/Output/Log_for_autores.txt", delim = ";", append = TRUE)
        
        n_pub <- extras[[1]]$coredata$`document-count`
        n_citas <- extras[[1]]$coredata$`citation-count`
        n_citby <- extras[[1]]$coredata$`cited-by-count`
        h_index <- ifelse(is.null(extras[[1]]$`h-index`), "0", extras[[1]]$`h-index`)
        n_colab <- ifelse(is.null(extras[[1]]$`coauthor-count`), "0", extras[[1]]$`coauthor-count`)
        primera_pub <- ifelse(is.null(extras[[1]]$`author-profile`$`publication-range`$`@start`), "0", extras[[1]]$`author-profile`$`publication-range`$`@start`)
        ultima_pub <- ifelse(is.null(extras[[1]]$`author-profile`$`publication-range`$`@start`), "0", extras[[1]]$`author-profile`$`publication-range`$`@end`)
        af_curr <- extras[[1]]$`affiliation-current`$`@id`                               # MODIFICACION 1
        
        # Variantes del nombre
        nomb_list <- extras[[1]]$`author-profile`$`name-variant`
        
        if(!is.null(nomb_list) & length(nomb_list) > 2){
          
          nomb_alt <- paste(nomb_list$surname, nomb_list$`given-name`)
          
        }else if(!is.null(nomb_list) & length(nomb_list) == 2){
          
          nomb_alt <- paste(unlist(nomb_list %>% map(~paste(.x$surname, .x$`given-name`))), collapse = " | ")
          
        }else{
          
          nomb_alt <- ""
          
        }
        
        #Corrección nombres alternativos
        if(is_empty(nomb_alt)){
          
          tryCatch({
            
            nomb_alt <- as_tibble(gen_entries_to_df(nomb_list)$df) %>% mutate(nombre = paste(surname, `given-name`)) %>% pull(nombre) %>% paste(collapse = " | ")    
            
          }, error = function(e){
            
            nomb_alt <- ""
            
          })
          
        }
        
        
        # Fecha de creación del autor
        fec_list <- extras[[1]]$`author-profile`$`date-created`
        
        if(!is_null(fec_list)){
          
          fec_creacion <- unlist(list(fec_list) %>% 
                                   map(~paste(.x$`@year`, .x$`@month`, .x$`@day`, sep = "-")))  
          
        }else{
          
          fec_creacion <- ""
          
        }
        
        # Historial de afiliaciones
        if(af_hist & !is.null(extras[[1]]$`author-profile`$`affiliation-history`$affiliation)) {
          
          tryCatch({
            
            hist_afil <- as_tibble(gen_entries_to_df(extras[[1]]$`author-profile`$`affiliation-history`$affiliation)$df)
            
            hist_afil <- hist_afil %>% 
              clean_names() %>%
              mutate(authid = autor_id,
                     id_loop = i) %>% 
              select(any_of(c("id_loop","authid", "affiliation_id", "ip_doc_type", "ip_doc_relationship", "ip_doc_preferred_name", "ip_doc_address_address_part",
                              "ip_doc_address_city", "ip_doc_address_country_2", "ip_doc_address_country")))  
            
          }, error = function(e){
            
            message("Historial de afiliación no pudo ser interpretado para registro ", i)
          })
        }
        
        # Áreas de publicación
        if(areas_ls & !is.null(extras[[1]]$`subject-areas`$`subject-area`)) {
          
          sub_area <- as_tibble(gen_entries_to_df(extras[[1]]$`subject-areas`$`subject-area`)$df)
          
          sub_area <- sub_area %>% 
            clean_names() %>% 
            transmute(id_loop = i,
                      authid = autor_id,
                      area = abbrev,
                      sub_area_cod = code,
                      sub_area_desc = x)
          
        }
        
        reg_coment <- "Registro completo procesado correctamente"
        
      }else{
        
        vroom_write(x = tibble(i = as.character(i), autor = autor_id, chckpt = "2.2"), file = "Datos/Output/Log_for_autores.txt", delim = ";", append = TRUE)
        
        n_pub <- ""
        n_citas <- ""
        n_citby <- ""
        h_index <- ""
        n_colab <- ""
        primera_pub <- ""
        ultima_pub <- ""
        af_curr <- ""
        nomb_alt <- ""
        fec_creacion <- ""
        reg_coment <- "Registro no retorna información extras"
        
      }
      
      vroom_write(x = tibble(i = as.character(i), autor = autor_id, chckpt = "2.3"), file = "Datos/Output/Log_for_autores.txt", delim = ";", append = TRUE)
      
      df <- tibble("id_loop" = i,
                   "authid" = autor_id,
                   "primera_publicacion" = primera_pub,
                   "ultima_publicacion" = ultima_pub,
                   "numero_publicaciones" = n_pub,
                   "numero_citas" = n_citas,
                   "n_citas_docs" = n_citby,
                   "h_index" = h_index,
                   "af_actual" = af_curr,
                   "numero_colaboradores" = n_colab,
                   "otros_nombres" = nomb_alt,
                   "fecha_creacion" = fec_creacion,
                   "comentarios" = reg_coment)
      
      
    }else if(consulta$get_statement$status_code == 300){
      
      vroom_write(x = tibble(i = as.character(i), autor = autor_id, chckpt = "3"), file = "Datos/Output/Log_for_autores.txt", delim = ";", append = TRUE)
      
      #ccddddc
      #Múltiples respuestas
      df <- tibble("id_loop" = i,
                   "authid" = autor_id,
                   "primera_publicacion" = "",
                   "ultima_publicacion" = "",
                   "numero_publicaciones" = "",
                   "numero_citas" = "",
                   "n_citas_docs" = "",
                   "h_index" = "",
                   "af_actual" = "",
                   "numero_colaboradores" = "",
                   "otros_nombres" = "",
                   "fecha_creacion" = "",
                   "comentarios"= "Error 300. Respuesta multiple. Ver archivo detalle")
      
      
      ##############################################################################################
      #Escribiendo archivo de respuestas múltiples
      respaldo_multiple <- paste0("Datos/Output/Data_Experiencia_",id_respaldo,"_resp_mult.txt")
      
      df_aut_secund <- tibble()
      
      #Iterando en listado de autores alternativos
      respuestas <- length(consulta$content$`author-retrieval-response`$alias[[1]])
      
      for (sec in 1:respuestas) {
        
        autor_sec <- str_sub(string = consulta$content$`author-retrieval-response`$alias[[1]][[sec]]$`$`,
                             start = 50,
                             end = 62)  
        
        df_sec <- tibble(principal = autor_id,
                         secundario = autor_sec)
        
        df_aut_secund <- bind_rows(df_aut_secund, df_sec)
        
      }
      
      vroom_write(x = df_aut_secund,
                  path = respaldo_multiple,
                  delim = ";",
                  col_names = aut_sec_nuevo,
                  append = TRUE)
      
      aut_sec_nuevo <- FALSE
      
      message("Respuesta multiple para autor ", autor_id, ". Detalles guardados en ", respaldo_multiple) 
      
      
    }else if(consulta$get_statement$status_code == 429){
      
      vroom_write(x = tibble(i = as.character(i), autor = autor_id, chckpt = "4"), file = "Datos/Output/Log_for_autores.txt", delim = ";", append = TRUE)
      
      stop("Se ha excedido el límite semanal de consultas. 
       Los resultados han sido guardados en archivo de respaldo
       ", paste0("Datos/Output/Data_Experiencia_",id_respaldo,".txt"), "
       Usar el id ", id_respaldo, "  para el parámetro [respaldo] para próximas ejecuciones",
           call. = FALSE) 
      
    }else{
      
      df <- tibble("id_loop" = i,
                   "authid" = autor_id,
                   "primera_publicacion" = "",
                   "ultima_publicacion" = "",
                   "numero_publicaciones" = "",
                   "numero_citas" = "",
                   "n_citas_docs" = "",
                   "h_index" = "",
                   "af_actual" = "",
                   "numero_colaboradores" = "",
                   "otros_nombres" = "",
                   "fecha_creacion" = "",
                   "comentarios"= "API no trae respuesta para este autor")
      
      
      message(paste0("Error", consulta$get_statement$status_code, " para registro ", i, " (author_id: ", autor_id,")"))
      
    }
    
    
    # Recolectando datos extraidos en df principales
    df_info_autor <- bind_rows(df_info_autor, df)
    df_afil_hist <- bind_rows(df_afil_hist, hist_afil)
    df_area_publ <- bind_rows(df_area_publ, sub_area)
    
    
    ######################
    # Reporte de progreso procentaje de registros procesados
    if(n_autores > 10){
      
      T2 <- Sys.time()
      
      if(i %% l_msj == 0){
        
        message((i / l_msj) * rep_n, paste0("% de los registros procesados. (Hora: ", T2, ")"))
      }  
      
    }
    
    t_fin <- Sys.time()
    
    dur <- round(t_fin - t_ini, 1)
    
    t_proc <- c(t_proc, dur)
    
    
    ##################################################################
    # Respaldo en archivo físico con id_respaldo cada 100 registros
    if(i %% 100 == 0 | i == length(autores)){
      
      message(paste0(Sys.time(), " - ", i , " registros procesados. Tiempo promedio por registro: ", mean(t_proc), " segundos. Respaldando registros en archivo ", id_respaldo))
      
      r_pri <- i - 99
      
      wr_autor <- df_info_autor %>% 
        filter(id_loop >= r_pri,
               id_loop <= i)
      
      vroom_write(x = wr_autor,
                  path = paste0("Datos/Output/Data_Experiencia_",id_respaldo,".txt"),
                  delim = "|",
                  col_names = no_respaldo,
                  append = !no_respaldo)
      
      if(af_hist){
        wr_historial <- df_afil_hist %>% 
          filter(id_loop >= r_pri,
                 id_loop <= i)
        
        vroom_write(x = wr_historial,
                    path = paste0("Datos/Output/Historial_Afiliacion_",id_respaldo,".txt"),
                    delim = "|",
                    col_names = no_respaldo,
                    append = !no_respaldo)
      }
      
      if(areas_ls){
        wr_areas <- df_area_publ %>% 
          filter(id_loop >= r_pri,
                 id_loop <= i)
        
        vroom_write(x = wr_areas,
                    path = paste0("Datos/Output/Areas_Publicaciones_",id_respaldo,".txt"),
                    delim = "|",
                    col_names = no_respaldo,
                    append = !no_respaldo)
      
      }
      
      Sys.sleep(1)
      
      rm(wr_autor, wr_historial, wr_areas)
      
      no_respaldo <- FALSE
     
      gc()
       
    }
    
  }
  
  return(df_info_autor)
  
}


#autor_id <- maestro_autores_e1$authid
#nombre <- maestro_autores_e1$aut_nombre
#gen_bd_path <- "Datos/Genderize/Maestro_Genderizer.txt"


Inf_Sexo <- function(autor_id, nombre, gen_bd_path){
  
  #Lectura base maestro genderizer
  BD_GEN_MAESTRO <- vroom(file = gen_bd_path,
                          delim = ";",
                          col_names = TRUE,
                          col_types = "ccddc")
  
  
  #Recodificando y limpiando el nombre. Preparación del la data para detectar nombres previamente procesados
  message("Preparacion de la data...")
  df_Authors <- tibble(autor_id, nombre) %>% 
    mutate(nom_recod = iconv(x = nombre,
                             from = "UTF-8",
                             to = "ASCII//TRANSLIT")) %>% 
    mutate(nom_recod = str_squish(string = tolower(str_replace_all(string = nom_recod,
                                                                   pattern = "[A-Z]\\.",
                                                                   replacement = ""))))
  
  
  #Consolidando el listado de nombres nuevos y paises a procesar, provinientes de df_Autores
  input <- df_Authors %>% #filter(nom_recod == "andrea") %>% 
    filter(nom_recod != "") %>% 
    distinct(nom_recod) %>% 
    filter(!nom_recod %in% BD_GEN_MAESTRO$name) %>% 
    arrange(nom_recod)
  
  
  message(paste0("Procesando género de los autores"))
  message(paste0("Total de registros únicos a procesar: ", nrow(input)))

  obt_sexo <- findGivenNames(x = input$nom_recod,
                             textPrepare = TRUE,
                             #country = pais,
                             progress = FALSE) %>% 
    as_tibble() %>% 
    mutate(probability = as.numeric(probability))
  
  
  # Consolidando nuevos resultados a base maestro
  BD_GEN_MAESTRO <- bind_rows(BD_GEN_MAESTRO, obt_sexo)

  
  #Rescatando los resultados recién obtenidos al maestro 
  message("Anexando resultados obtenidos a BD Maestro para ejecuciones posteriores...")
  
  insertar <- obt_sexo %>% 
    anti_join(BD_GEN_MAESTRO,
              by = "name")
  
  if(nrow(insertar) > 0){
    vroom_write(x = insertar,
                path = gen_bd_path,
                delim = ";",
                col_names = FALSE,
                append = TRUE)
  }
  
  
  # Filtrando mejor registro en maestro
  BD_GEN_MAESTRO <- BD_GEN_MAESTRO %>%  #filter(name == "ricardo") %>% 
    arrange(name, desc(count), desc(probability)) %>% 
    group_by(name) %>% 
    mutate(filtro = row_number()) %>% 
    filter(filtro == 1) %>% 
    select(-filtro)
    
    
  
  
  message("Ejecutando proceso GENDERIZE...")
  res <- genderize(x = df_Authors$nom_recod,
                   genderDB = BD_GEN_MAESTRO,
                   progress = TRUE) %>% 
    distinct(text, gender) %>% 
    filter(!is.na(gender))
  
  
  
  primer_cruce <- df_Authors %>% 
    left_join(y = BD_GEN_MAESTRO,
              by = c("nom_recod" = "name")) %>%
    mutate(sexo = case_when(gender == "male" ~ "Hombre",
                            gender == "female" ~ "Mujer",
                            TRUE ~ ""),
           probabilidad = probability) %>% 
    select(-gender, -probability, -count, -country_id)
  
  
  segundo_cruce <- primer_cruce %>% 
    filter(sexo == "") %>% 
    left_join(y = res,
              by = c("nom_recod" = "text")) %>%
    mutate(sexo = case_when(gender == "male" ~ "Hombre",
                            gender == "female" ~ "Mujer",
                            TRUE ~ "")) %>% 
    select(-gender) 
  
  # Configurando salida
  message("Configurando salida")
  salida <- bind_rows(primer_cruce %>% 
                        filter(sexo != ""),
                      segundo_cruce)
  
  
  arch_salida <- paste0("Datos/Output/Data_Inferencia_Sexo_", format(Sys.time(), "%Y%m%d%H%M"), ".txt")
  
  message("Escribiendo resultados en archivo: ", arch_salida)
  vroom_write(x = salida,
              path = arch_salida,
              delim = ";",
              col_names = TRUE) 
  
  
  return(salida)
  
}


#id_afil <- "57201070146"
#api_key <- Api_key
#token <- Token
#base_acum <- maestro_inst


busca_datos_afil <- function(id_afil, api_key, token, base_acum){
  
  afiliacion <- affiliation_retrieval(id = id_afil,
                                      api_key = api_key,
                                      headers = inst_token_header(token))

    
  if(afiliacion$get_statement$status_code == 429){
    
    stop("***********  Se ha excedido la quota de consultas. Proceso finalizado  ***********")
    
  }
  
  salida_prim <- tibble(af_id = id_afil,
                        af_nombre = ifelse(!is.null(afiliacion$content[[1]]$`affiliation-name`), afiliacion$content[[1]]$`affiliation-name`, ""),
                        af_direccion = ifelse(!is.null(afiliacion$content[[1]]$address), afiliacion$content[[1]]$address, ""),
                        af_ciudad = ifelse(!is.null(afiliacion$content[[1]]$city), afiliacion$content[[1]]$city, ""),
                        af_pais = ifelse(!is.null(afiliacion$content[[1]]$country), afiliacion$content[[1]]$country, ""),
                        af_tipo = ifelse(!is.null(afiliacion$content[[1]]$`institution-profile`$`org-type`), afiliacion$content[[1]]$`institution-profile`$`org-type`, ""))
  
  nom_alt_aff <- ""
  
  if (!is.null(afiliacion$content[[1]]$`name-variants`$`name-variant`)) {
    
    try(nom_alt_aff <- afiliacion$content[[1]]$`name-variants`$`name-variant`$`$`, silent = TRUE)
    try(nom_alt_aff <- paste(gen_entries_to_df(afiliacion$content[[1]]$`name-variants`$`name-variant`)$df %>% pull(`$`), collapse = " | "), silent = TRUE)
    
  }else{
    
    nom_alt_aff <- ""
    
  }
  
  
  # Revisanndo existencia de institución padre
  if(!is_null(afiliacion$content[[1]]$`institution-profile`$`@parent`)){
    
    # Revisión de si ya existe en el df acumulado tanto para campos af como campos inst
    
    id_padre <- afiliacion$content[[1]]$`institution-profile`$`@parent`
    prev_af <- 0
    prev_inst <- 0
    
    
    # Buscando existencia en campos afiliación
    prev_af <- base_acum %>% 
      filter(af_id == id_padre) %>% 
      nrow()
    
    # Buscando existencia en campos institución
    prev_inst <- base_acum %>% 
      filter(inst_id == id_padre) %>% 
      nrow()
    
    if(prev_af > 0){
      
      salida_padre <- base_acum %>% 
        filter(af_id == id_padre) %>% 
        distinct() %>% 
        slice(1)
      
      nom_alt_inst <- salida_padre$nombres_alt_afil
      
      salida_padre <- salida_padre %>% 
        select(inst_id = af_id,
               inst_nombre = af_nombre,
               inst_direccion = af_direccion,
               inst_ciudad = af_ciudad,
               inst_pais = af_pais,
               inst_tipo = af_tipo)
      
    }else if(prev_inst > 0){
      
      salida_padre <- base_acum %>% 
        filter(inst_id == id_padre) %>% 
        distinct() %>% 
        slice(1)
      
      nom_alt_inst <- salida_padre$nombres_alt_inst
      
      salida_padre <- salida_padre %>% 
        select(inst_id,
               inst_nombre,
               inst_direccion,
               inst_ciudad,
               inst_pais,
               inst_tipo)
      
    }else{
      
      af_parent <- affiliation_retrieval(id = afiliacion$content[[1]]$`institution-profile`$`@parent`,
                                         api_key = Api_key,
                                         headers = inst_token_header(Token))  
      
      salida_padre <- tibble(inst_id = afiliacion$content[[1]]$`institution-profile`$`@parent`,
                             inst_nombre = ifelse(!is.null(af_parent$content[[1]]$`affiliation-name`), af_parent$content[[1]]$`affiliation-name`, ""),
                             inst_direccion = ifelse(!is.null(af_parent$content[[1]]$address), af_parent$content[[1]]$address, ""),
                             inst_ciudad = ifelse(!is.null(af_parent$content[[1]]$city), af_parent$content[[1]]$city, ""),
                             inst_pais = ifelse(!is.null(af_parent$content[[1]]$country), af_parent$content[[1]]$country, ""),
                             inst_tipo = ifelse(!is.null(af_parent$content[[1]]$`institution-profile`$`org-type`), af_parent$content[[1]]$`institution-profile`$`org-type`, ""))
      
      nom_alt_inst <- ""
      
      if (!is.null(af_parent$content[[1]]$`name-variants`$`name-variant`)) {
        
        try(nom_alt_inst <- af_parent$content[[1]]$`name-variants`$`name-variant`$`$`, silent = TRUE)
        try(nom_alt_inst <- paste(gen_entries_to_df(af_parent$content[[1]]$`name-variants`$`name-variant`)$df %>% pull(`$`), collapse = " | "), silent = TRUE)
        
      }else{
        
        nom_alt_inst <- ""
        
      } 
      
    }
    
  }else{
    
    salida_padre <- tibble(inst_id = "",
                           inst_nombre = "",
                           inst_direccion = "",
                           inst_ciudad = "",
                           inst_pais = "",
                           inst_tipo = "")
    
    nom_alt_inst <- ""
    
  }
  
  salida <- bind_cols(salida_prim, salida_padre) %>% 
    mutate(nombres_alt_afil = nom_alt_aff,
           nombres_alt_inst = nom_alt_inst)
    
  
  return(salida)
  
}




