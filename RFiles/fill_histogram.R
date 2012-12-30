# Author @ramnarasimhan
# December 2012
# Plotting a simple barchart of each City's data points.

rm(list=ls())
outputDir.path <- file.path("~/Py Library/Wx")
setwd(outputDir.path)
getwd()

#Using ggplot2 to create the plot
require(ggplot2)
library(reshape)

#read the cumulative scores data
cityscore <-read.csv("data/city_scores_curves.csv")

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


#Rename each cell in df with bucket =100 to be hi.
#reason for doing this is that the string "100" gets sorted between "10" and "20", which we don't want
cs.melt[cs.melt$bucket=='100',]$bucket = "hi"
cs.melt[cs.melt$bucket=='hi',]



#first, we take one reading for each city, its 0 bucket score
zeros <- subset(cs.melt, bucket=="0")

#reorder the rows by the scores.
zeros.sort<- zeros[order(zeros$Score),]
# zeros.sort$City becomes the ordering we want

#Using RampPalette to choose a suitable color range
#redgreenrange<-colorRampPalette(c('red', 'green'))
# Using a slightly muted green
redgreenrange<-colorRampPalette(c(rgb(1,0,0), rgb(0,0.7,0) )) 

#we plot the x as a factor, sorted by the "0" bucket score

po <- ggplot(cs.melt, aes(x=factor(City,levels=zeros.sort$City), y=Score, fill = factor(bucket)) ) 

po<-  po + xlab("City Temperature Scores")
po<-  po + geom_bar(stat="identity")
po <- po + scale_fill_manual(values = redgreenrange(11), name="Temperature")

po


#### Now let's try to center the graph around a score of 50
#0-40 goes to one side, 50-100 goes above center line
lowbuckets = c("0",'10','20','30','40')

#subset the lower half of the dataframe, rows with small scores
lowcs = subset(cs.melt,bucket %in% lowbuckets)

#Group that smaller df, by one row per City, score is sum of the scores. 100-x becomes the offset
#create a subset of df, one for each city, with score = 100-low_scores, and call that bucket "-"
newc <- ddply(lowcs, .(City), summarize, Score = 100-sum(Score), bucket="-"  ) 
newcs <- rbind(newc,cs.melt)
newcs

#order the cities, based on the Score of the lower half
newc[order(newc$Score),]$City

#we plot the x as a factor, sorted by the "0" bucket score
po <- ggplot(newcs, aes(x=factor(City,levels=newc[order(newc$Score),]$City), y=Score, fill = factor(bucket)) ) 
po <- ggplot(newcs, aes(x=factor(City,levels=zeros.sort$City), y=Score, fill = factor(bucket)) ) 
po<-  po + xlab("City Temperature Scores (sorted by Increasing 0-score bucket size)")
po<-  po + geom_bar(stat="identity") 
po <- po + scale_fill_manual(values = c(rgb(1,1,1),redgreenrange(11)), name="Temperature")

po


