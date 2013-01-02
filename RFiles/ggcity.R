# Author @ramnarasimhan
# December 2012
#plotting on GGMAP


rm(list=ls())
#PC
outputDir.path <- file.path("~/Py Library/Wx/data")

#mac
#outputDir.path <- file.path("~/Python/Wx")
setwd(outputDir.path)
getwd()

# Load libraries
library('ggplot2')
library('plyr')
library(ggmap)
library(mapproj)
library('maps')

#read the cumulative scores data
cityscore <-read.csv("out_city_final.csv")

#verify load
cityscore

cities <- as.character(cityscore$City)
cities
score <- cityscore$Score
round(score)

ll = geocode(cities)
ll <- cbind(ll,score)
ll

mtype = "watercolor"
mtype = "roadmap"
mtype = "terrain"
mtype= "toner"

skin = map("state")

mp = get_map(location = 'USA', zoom = 4, maptype = mtype)
mp = get_map(location = 'India', zoom = 5, maptype = mtype)

#prefer bw maps so that our data can be easily seen
mp = get_map(location = 'USA', zoom = 4, maptype = mtype, color="bw")
mp <- ggmap(mp)
mp<- mp+ geom_point( data=ll, aes(x=lon, y=lat, color=score), size=score/12)
mp<- mp  + scale_colour_continuous(low="blue", high="red")
mp<- mp+geom_text(data=ll,aes(y=lat-1,label=cities), size=4)
mp<- mp+geom_text(data=ll,aes(y=lat+1.5,label=round(score),color=score), size=5)
mp


?ggmap