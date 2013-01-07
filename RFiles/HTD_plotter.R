
library(ggplot2)
library(plyr)
library(reshape)

rm(list=ls())
outputDir.path <- file.path("~/Py Library/Wx/data")
setwd(outputDir.path)
getwd()


remind<-function(df){
  print (head(df))
  print (names(df))
}

#works
df <- read.csv("cityHTD.csv")
df <- read.csv("out_cityTemperatures.csv")
names(df)<- c("City","Date","Hour","Temperature")
remind(df)

p<-NULL
p<- ggplot(df, aes(City, fill=factor(Temp))) + geom_bar()
p<- p + scale_fill_brewer(type="seq",palette="YlOrRd")
p
#works

redgreenrange<-colorRampPalette(c(rgb(0,0,1), rgb(1,0.7,0) ))
numcolors <- length(unique(df$Temp))
numcolors
p<-NULL
p<- ggplot(df, aes(City, fill=factor(Temperature))) + geom_bar()
p<- p + scale_fill_manual(values=redgreenrange(numcolors))
p






