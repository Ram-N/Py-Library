# Author @ramnarasimhan
# December 2012
# Plotting a simple barchart of each City's data points.
#365 days vs days found and days missing (in Red)

rm(list=ls())
outputDir.path <- file.path("~/RStats/Source Code Web Scraping/")
setwd(outputDir.path)
getwd()

#Using ggplot2 to create the plot
require(ggplot2)
library(reshape)

#read the cumulative scores data
cityscore <-read.csv("city_scores_curves.csv")

names(cityscore)
head(cityscore)

#clean up the data frame by getting rid of a few columns
cs <- cityscore[-c(2,3,5,7,9)]
cs

names(cs)[1] <- "bucket"
names(cs)[2] <- "SCHAUM"
names(cs)[3] <- "RIC"
names(cs)[4] <- "SVALE"
names(cs)[5] <- "MIAMI"

#In order to plot STACKED BARPLOTS, the data frame has to be melted
# melt the dataframe so that each measured variable is its own row
cs.melt <- melt(cs, id="bucket")
names(cs.melt)[2] = "City"
names(cs.melt)[3] = "Score"

#verify 
cs.melt
head(cs.melt)
names(cs.melt)

#first, we take one reading for each city, its 0 bucket score
zeros <- subset(cs.melt, bucket=="0")

#reorder the rows by the scores.
zeros.sort<- zeros[order(zeros$Score),]
# zeros.sort$City becomes the ordering we want

#Using RampPalette to choose a suitable color range
#redgreenrange<-colorRampPalette(c('red', 'green'))
# Using a slightly muted green
redgreenrange<-colorRampPalette(c(rgb(1,0,0), rgb(0,0.7,0)))

#we plot the x as a factor, sorted by the "0" bucket score
po <- ggplot(cs.melt, aes(x=factor(City,levels=zeros.sort$City), y=Score, fill = factor(bucket)) ) 
po<-  po + xlab("City Temperature Scores")
po<-  po + geom_bar(stat="identity")
po <- po + scale_fill_manual(values = redgreenrange(11), name="Temperature")

po

