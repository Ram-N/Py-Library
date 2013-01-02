# Author @ramnarasimhan
# December 2012
# Plotting 24-hour columns vs number of data points per City
#365 days vs days found and days missing (in Red)

rm(list=ls())
outputDir.path <- file.path("~/Py Library/Wx/data")
setwd(outputDir.path)
getwd()

#Using ggplot2 to create the plot
require(ggplot2)
library(reshape)

#first load the data
df = read.csv("out_numDataPoints.csv")

#create a new column for the Gaps in the data
df$Gap <- (365 - df$Dpts)
df
names(df)
head(df)

#shape square is mapped to 15 in geom_point
square=15

df_small = subset(df, Gap<50)
df_big = subset(df, Gap>200)
df_big
#plotting
p <- ggplot() + aes(title= "Missing Data Points, by City, by Hour")  
p<- p + scale_x_continuous(breaks=0:23) #place tick marks on each hour of day
p <- p + geom_point(data=df_big, aes(Hour,City),color="red", shape=square, size=5)
p


p<- p + geom_text(data=df, subset=(df$Gap>200), aes(Hour,City),  label=df$Gap, size=3)
#p <- p + geom_point(data=df_small, aes(Hour,City,color=Gap),shape=square, size=3)

p <- p  + scale_colour_continuous(low="blue", high="orange")

p
