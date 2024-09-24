setwd("G:/My Drive/01 Elite. Proyect2021-2023/02 Data sets (Cuantitativo)/NetworkAuthorship/GeopoliticalKnowledgesInEconomics")
a <- read.csv2("Authors.csv")
b <- read.csv2("ScopusPublications.csv")
c <- read.csv2("AuthorsJournalAreas.csv")
d <-  read.csv2("AuthorsAffiliationHistory.csv")
e <- read.csv2("InstitutionsAttributes.csv")
f <- read.csv2("Pub_link_Authors.csv")

colnames(a)<- c("authid", "id_author_intern", "aut_lastname", "aut_firstname", "aut_orcid", "first_pub", "last_pub", "n_pub", "n_citations", "n_references", "h_index", 
           "affil_id_today", "n_collab", "other_names", "date_file_created", "gender" )

colnames(b) <- c("pub_id", "title", "description", "author_creator", "name_journal", "issn", "e_issn", "year_pub", "doi", "n_citations", "n_authors", "cod_subtype", "subtype", "fund_acr", "fund_sponsor" )

colnames(c) <- c("authid", "discipline", "sub_discipline", "sub_discipline_code")

colnames(d) <- c("authid", "affil_id")

colnames(e) <- c("affil_id", "affil_name", "affil_address", "aff_city", "aff_country", "afill_type", "inst_id2", "instit_name2","inst_address2", "inst_city2", "inst_country2", "inst_type2", "other_names_inst2", "other_names_inst3")

colnames(f) <- c("pub_id", "autor_id", "id_autor_intern", "affil_id")


#### gender authors#######
a$female <-ifelse(a$gender=="Mujer",1,
                 ifelse(a$gender=="", NA,0))

#### comparing data & identifying authors with missing affiliation########
g <- unique(d$authid)
gg <- as.data.frame(g)
gg$affiliation= 1
colnames(gg) <-c("authid", "affiliationincluded")
aa <- subset(a, select= c(authid, id_author_intern, female))
library(dplyr)
ag1 <- merge(x=aa, y=gg, by.x="authid", by.y="authid", all.x= TRUE)


#### adding columns into publications #####
f$woman <- a$female[match(f$autor_id, a$authid)]
head(f)
a$country <- e$aff_country[match(a$affil_id_today, e$affil_id)] ##the key of the data set that has the largest number of cases goes second
f$country <- a$country[match(f$autor_id, a$authid)]
f$citation <- b$n_citations[match(f$pub_id, b$pub_id)]
f$aut_reputation <- a$n_citations[match(f$autor_id, a$authid)]
f$year_pub <- b$year_pub[match(f$pub_id,b$pub_id,)]
f$n_year <- (2022-f$year_pub)

f$Chile <- ifelse(f$country=="Chile", 1, 0)
f$USA <- ifelse(f$country=="United States", 1, 0)
f$UK <- ifelse(f$country=="United Kingdom", 1,0)
f$Spain <- ifelse(f$country == "Spain", 1,0)
f$LatinAmerica <- ifelse(f$country == "Brazil", 1, 
                  ifelse(f$country == "Argentina", 1, 
                  ifelse(f$country == "Mexico",1,
                  ifelse(f$country == "El Salvador",1,
                  ifelse(f$country == "Panama", 1,
                  ifelse(f$country == "Paraguay",1,
                  ifelse(f$country == "Puerto Rico", 1,
                  ifelse(f$country == "Guatemala", 1,
                  ifelse(f$country == "Bolivia", 1,
                  ifelse(f$country == "Cuba",1, 
                  ifelse(f$country == "Venezuela", 1, 
                  ifelse(f$country == "Costa Rica",1,
                  ifelse(f$country == "Colombia", 1, 
                  ifelse(f$country == "Peru", 1, 
                  ifelse(f$country == "Ecuador",1, 
                  ifelse(f$country== "Chile",1,0))))))))))))))))


##Dataframe to obtain score per key indicators
### f_agg are unique publications
f_agg <- aggregate(Chile ~ pub_id, data=f, FUN=mean)
fagg_usa <- aggregate(USA ~ pub_id, data=f, FUN=mean)
fagg_women <- aggregate(woman ~ pub_id, data=f, FUN=mean)
fagg_LatinAmerica <- aggregate(LatinAmerica~ pub_id, data=f, FUN=mean)

##adding the columns  to f_agg (f aggregate)
f_agg$citation <- f$citation[match(f_agg$pub_id, f$pub_id,)]
f_agg$usa <- fagg_usa$USA[match(f_agg$pub_id, fagg_usa$pub_id)]
f_agg$women <- fagg_women$woman[match(f_agg$pub_id, fagg_women$pub_id)]
f_agg$women1 <-ifelse(f_agg$women>=0.01,1,0)
f_agg$LatinAmerica <- fagg_LatinAmerica$LatinAmerica[match(fagg_LatinAmerica$pub_id,f_agg$pub_id)]
f_agg$n_year <- f$n_year[match(f_agg$pub_id, f$pub_id)]
f_agg$n_authors <-b$n_authors[match(b$pub_id, f_agg$pub_id)]
f_agg$onlywomen <-ifelse(f_agg$women ==1,1,0)
f_agg$onlymen <-ifelse(f_agg$women == 0,1,0)

### quick lm ####### 
summary(lm(citation ~ woman, data = f)) 
summary(lm(citation ~ woman, data = f)) 

summary(lm(citation ~ women,  data=f_agg)) ##I am struck. Female does not have effects on number of citations
summary(lm(citation ~ women + LatinAmerica, data=f_agg))
summary(lm(citation ~ usa + LatinAmerica + women,  data=f_agg))
summary(lm(citation ~ usa + LatinAmerica + n_year + n_authors + women,  data=f_agg))

------
##Change colname in a
colnames(a)[which(names(a) == "af_actual")] <- "af_id"
##Jose De gregorio (author_id=6701727286) does not have an affiliation on scopus


## working on the network
library(igraph)
Get("https://raw.githubusercontent.com/szhorvat/IGraphM/master/IGInstaller.m")

g <- graph.data.frame(f[,c("autor_id", "pub_id")]) 
V(g)$type <- V(g)$name %in% d$authid ## match whether the id in the g are the same in the d (affiliation history table)
i<-table(V(g)$type)[2]
i

m<-t(as.matrix(get.incidence(g)))##complete matrix

mh<- m%*%t(m) #to one mode
dim(mh)
#fix(mh)

diagauthor<-diag(mh)
# diag(mh)<-0 #to drop self-selection

g1 <- graph.adjacency(mh, weighted=T,  mode = "upper", diag = FALSE)
g1 ##matrix completa
(dthumans <- data.frame(cbind(get.edgelist(g1),E(g1)$weight)))
g.c <- g1 #simplify(g1)
E(g.c)$weight 

#Adding country
V(g.c)$country <- f$country[match(V(g.c)$name, f$autor_id)]
head(V(g.c)$country)

##adding affiliation econ dept Chile --linea
V(g.c)$econaff <-a$id_author_intern[match(V(g.c)$label, a$authid)]###name before running the code. Change label
####
cent<-data.frame(bet=betweenness(g1, normalized=F)/max(betweenness(g1, normalized=F)),eig=evcent(g1)$vector) # evcent returns lots of data associated with the EC, but we only need the leading eigenvector
cent$ID <- V(g1)$name #Ids in this case

############
#In HTML visualizations (like NetworkD3) we need two datasets, one for links, another for nodes attributes.
############
g<-g.c
V(g)$label <- V(g)$name
V(g)$name <- 1:length(V(g)$name)
head(V(g)$name)

#Gets edgelist from graph, also any other attribute at the edge level to be included in the mapping
links<-as.data.frame(cbind(get.edgelist(g), E(g)$weight))

#Needs to be numeric
links$V1<-as.numeric(as.character(links$V1))

links$V2<-as.numeric(as.character(links$V2))
str(links)

links$V3<-round(as.numeric(as.character(links$V3)),3)
head(links)

colnames(links)<-c("source","target", "value")

#Counts begin at zero in computer programming
links[,1:2]<-(links[,1:2]-1)

dim(links)

#Adding attributes at the actor level
#V(g)$firstgen<- actors$firstgen[match(V(g)$label, actors$pseudoid)]
#V(g)$hsgpa<- round(actors$hsgpa[match(V(g)$label, actors$pseudoid)],3)
#V(g)$cume_GPA<- actors$sem2_cume_gpa[match(V(g)$label, actors$pseudoid)]
#V(g)$size<- cent$bet[match(V(g)$label, cent$name)]
#V(g)$No_courses <- cent$course_num[match(V(g)$label, cent$name)]

###############################################################################
# If you have missing data at actor level, this may be needed##
# V(g)$firstgen[1:i] <- ifelse(is.na(V(g)$firstgen[1:i]), "first_Gen_NA", V(g)$firstgen[1:i])
###############################################################################
V(g)$size <- round(cent$bet[match(V(g)$label, cent$ID)],3)
V(g)$eig <- round(cent$eig[match(V(g)$label, cent$ID)],3)
summary(V(g)$size)
#summary(actors$firstgen)
summary(V(g)$eig)

nodes <- data.frame(label= c(paste("ID: ", V(g)$label, 
                                  ", Size: ", V(g)$size, 
                                  ", Country: ", V(g)$country, 
                                  ", eig: ", V(g)$eig, sep="")), 
                    size = abs(V(g)$size), 
                    country=(V(g)$country),
                    eig=abs(V(g)$eig),
                    ID=V(g)$label) 

head(nodes);tail(nodes)


nodes$group<-ifelse(nodes$country=="Chile", "Afiliacion Chile", "No Chile")
nodes$group <- ifelse(is.na(nodes$group), "No Country", nodes$group)
table((nodes$group))
#nodes$group <-cut(nodes$cume_GPA, c(0,2,3,3.5,max(nodes$cume_GPA)), right=TRUE, labels = FALSE)
table(is.na(nodes$group))
table(nodes$group)
head(nodes[is.na(nodes$group),],20)
#nodes$group<-ifelse(is.na(nodes$group), "Course", ifelse(nodes$group==1, "Cume GPA below 2", ifelse(nodes$group==2, "Cume GPA over 2, below 3", ifelse(nodes$group==3, "Cume GPA over 3, below 3.5", "Cume GPA over 3.5"))))
counts<-data.frame(table(nodes$group))

counts$labels <- paste(counts$Var1, ", N= ", counts$Freq, sep="")
nodes$groups <- counts$labels[match(nodes$group, counts$Var1)] 
head(nodes)

install.packages("networkD3")
library(networkD3)
library(magrittr)
library(htmlwidgets)
library(htmltools)
netviz<-forceNetwork(Links = links, Nodes = nodes,
                     Source = 'source', Target = 'target',
                     NodeID = 'label',
                     Group = "groups", # color nodes by group calculated earlier
                     charge = -30, # node repulsion
                     linkDistance = JS("function(d) { return d.linkDistance; }"),#JS("function(d){return d.value}"),
                     linkWidth = JS("function(d) { return Math.sqrt(d.value)*2; }"),
                     opacity = 0.8,
                     Value = "value",
                     Nodesize = 'size', 
                     radiusCalculation = JS("Math.sqrt(d.nodesize*30)+4"),
                     zoom = T, 
                     fontSize=14,
                     bounded= F,
                     legend= TRUE,
                     #linkColour = ifelse(links$value == 1, "#CCFFFF", ifelse(links$value == 2, "#e3eaa7", "#abb2b9")),
                     colourScale = JS("d3.scaleOrdinal(d3.schemeCategory10)"))

### animated graph
HTMLaddons <- 
  "function(el, x) { 
d3.select('body').style('background-color', ' #212f3d ')
d3.selectAll('.legend text').style('fill', 'white') 
 d3.selectAll('.link').append('svg:title')
      .text(function(d) { return 'No. of copublicaciones: ' + d.value ; })
  var options = x.options;
  var svg = d3.select(el).select('svg')
  var node = svg.selectAll('.node');
  var link = svg.selectAll('link');
  var mouseout = d3.selectAll('.node').on('mouseout');
  function nodeSize(d) {
    if (options.nodesize) {
      return eval(options.radiusCalculation);
    } else {
      return 6;
    }
  }

  
d3.selectAll('.node').on('click', onclick)

  function onclick(d) {
    if (d3.select(this).on('mouseout') == mouseout) {
      d3.select(this).on('mouseout', mouseout_clicked);
    } else {
      d3.select(this).on('mouseout', mouseout);
    }
  }

  function mouseout_clicked(d) {
    node.style('opacity', +options.opacity);
    link.style('opacity', +options.opacity);

    d3.select(this).select('circle').transition()
      .duration(750)
      .attr('r', function(d){return nodeSize(d);});
    d3.select(this).select('text').transition()
	
      .duration(1250)
      .attr('x', 0)
      .style('font', options.fontSize + 'px ');
  }

}
"
netviz$x$links$linkDistance <- (1/links$value)*100
#netviz$x$links$campus <- links$value
onRender(netviz, HTMLaddons) 


install.packages("tidyverse")
library(tidyverse)


#### codigo viejo

dta<-cbind(get.edgelist(g.c), E(g.c)$weight)
head(dta)
mat2<-as.matrix(as_adjacency_matrix(g.c, attr="weight"))
mat2
eb <- edge.betweenness.community(g.c)

plot(eb, g.c, main="Coauthor network")
plot

#Centrality
cent<-data.frame(bet=betweenness(g1, normalized=F)/max(betweenness(g1, normalized=F)),eig=evcent(g1)$vector) # evcent returns lots of data associated with the EC, but we only need the leading eigenvector
cent$ID <- V(g1)$name #Ids in this case
cent$Freqi <- diagauthor
cent


write.csv(cent, "G:/My Drive/01 Elite. Proyect2021-2023/02 Data sets (Cuantitativo)/NetworkAuthorship/cent.csv")


