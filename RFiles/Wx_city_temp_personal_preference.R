# Author @ramnarasimhan
# December 2012
#Draw a histogram of a person's TempPreference
#0 is the lowest score, 100 is the most comfortable

rm(list=ls())
outputDir.path <- file.path("~/Py Library/Wx/data")
setwd(outputDir.path)
getwd()

#Using ggplot2 to create the plot
require(ggplot2)
library(reshape)


#read the data file
df <-read.csv("input_personal_preference.csv")
str(pref)
names(df) <- c("Low","High","Score")
df<- rbind(c(75,80,100),df)
df

seq(55,100,5)


#plot a simple histogram
p <- ggplot(df, aes(x=High, y=Score)) 
p <- p + labs(title="Temperature Preference Scale") 
p <- p + xlab("Temperature") + ylab("Personal Comfort Score")
p <- p + geom_bar(stat="identity") + aes(fill=Score)
p <- p + scale_x_continuous(breaks=seq(40,120,5))
p <- p + scale_fill_gradient("score",low="blue", high="orange")
p


