setwd("G:/My Drive/01 Elite. Proyect2021-2023/02 Data sets (Cuantitativo)/NetworkAuthorship/GeopoliticalKnowledgesInEconomics")
a = read.csv2("Authors.csv")
b = read.csv2("ScopusPublications.csv")
c = read.csv2("AuthorsJournalAreas.csv")
d=  read.csv2("AuthorsAffiliationHistory.csv")
e = read.csv2("InstitutionsAttributes.csv")
f = read.csv2("Pub_link_Authors.csv")

colnames(a)=c("authid", "id_intern", "aut_lastname", "aut_firstname", "aut_orcid", "first_pub", "last_pub", "n_pub", "n_citations", "n_references", "h_index", 
           "affil_id_today", "n_collab", "other_names", "date_file_created", "gender" )

colnames(e) = c("affil_id", "affil_name", "affil_address", "aff_city", "aff_country", "afill_type", "inst_id2", "instit_name2","inst_address2", "inst_city2", "inst_country2", "inst_type2", "other_names_inst2", "other_names_inst3")

colnames(b) = c("pub_id", "title", "description", "author_creator", "name_journal", "issn", "e_issn", "year_pub", "doi", "n_citations", "n_authors", "cod_subtype", "subtype", "fund_acr", "fund_sponsor" )

colnames(c) =

#### gender authors#######
a$female =ifelse(a$sexo=="Mujer",1,
                 ifelse(a$sexo=="", NA,0))

#### comparing data & identifying authors with missing affiliation########
g = unique(d$authid)
gg = as.data.frame(g)
gg$affiliation= 1
colnames(gg) =c("authid", "affiliationincluded")
aa = subset(a, select= c(authid, id_interno, female))
library(dplyr)
ag1 = merge(x=aa, y=gg, by.x="authid", by.y="authid", all.x= TRUE)


#### publications #####
f$woman <- aa$female[match(f$autor_id, aa$authid)]
head(f)
a$country = e$af_pais[match(a$af_actual, e$af_id)]
f$country = a$country[match(f$autor_id, a$authid)]
f$citation = b$n_cites[match(b$publ_id, $publ_id)]
f$cbi <- ifelse(f$country=="Chile", 1, 0)
f$cbi_usa <- ifelse(f$country=="United States", 1, 0)

fagg <- aggregate(cbi ~ publ_id, data=f, FUN=mean)
fagg_usa <- aggregate(cbi_usa ~ publ_id, data=f, FUN=mean)
fagg_women <- aggregate(woman ~ publ_id, data=f, FUN=mean)

head(fagg_women)



fagg$pubNum <- b$n_citas[match(fagg$publ_id, b$publ_id)]
fagg$usa <- fagg_usa$cbi_usa[match(fagg$publ_id, fagg_usa$publ_id)]
fagg$women <- fagg_women$woman[match(fagg$publ_id, fagg_women$publ_id)]
head(fagg)




### qick lm #######

summary(lm(pubNum ~ usa, data=fagg))
summary(lm(pubNum ~ cbi, data=fagg))
summary(lm(pubNum ~ cbi*women, data=fagg))


------
##Change colname in a
colnames(a)[which(names(a) == "af_actual")] <- "af_id"
##Jose De gregorio (author_id=6701727286) does not have an affiliation on scopus


## working on the network
library(igraph)
g <- graph.data.frame(f[,c("autor_id", "publ_id")]) 
V(g)$type <- V(g)$name %in% d$autor_id
i<-table(V(g)$type)[2]
i

m<-t(as.matrix(get.incidence(g)))##complete matrix

mh<- m%*%t(m) #to one mode
fix(mh)

diagauthor<-diag(mh)
# diag(mh)<-0 #to drop self-selection

g1 <- graph.adjacency(mh, weighted=T,  mode = "upper", diag = FALSE)
g1 ##matrix completa
(dthumans <- data.frame(cbind(get.edgelist(g1),E(g1)$weight)))

g2 <-graph.edgelist(get.edgelist(g1), directed=FALSE)
g2
E(g2)$weight	<- 1
g.c <- simplify(g2)
E(g.c)$weight 


dta<-cbind(get.edgelist(g.c), E(g.c)$weight)
head(dta)
mat2<-as.matrix(as_adjacency_matrix(g.c, attr="weight"))
mat2
eb <- edge.betweenness.community(g.c)

plot(eb, g.c, main="Coauthor network")


#Centrality
cent<-data.frame(bet=betweenness(g1, normalized=F)/max(betweenness(g1, normalized=F)),eig=evcent(g1)$vector) # evcent returns lots of data associated with the EC, but we only need the leading eigenvector
cent$ID <- V(g1)$name #Ids in this case
cent$Freqi <- diagauthor
cent


write.csv(cent, "G:/My Drive/01 Elite. Proyect2021-2023/02 Data sets (Cuantitativo)/NetworkAuthorship/cent.csv")



               


install.packages("tidyverse")
library(tidyverse)
