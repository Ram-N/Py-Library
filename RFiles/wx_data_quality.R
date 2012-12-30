# Author @ramnarasimhan
# December 2012
# Plotting a simple barchart of each City's data points.
#365 days vs days found and days missing (in Red)

rm(list=ls())
outputDir.path <- file.path("~/RStats")
setwd(outputDir.path)
getwd()

#Using ggplot2 to create the plot
require(ggplot2)
library(reshape)

#first load the data
df = read.csv("city_data_points.csv")
#create a new column for the Gaps in the data
df$Gap <- (365 - df$Numdpts)
df

#In order to plot STACKED BARPLOTS, the data frame has to be melted
# melt the dataframe so that each measured variable is its own row
df.melt <- melt(df, id="City", varnames="dtype", value.name="numvals")

names(df.melt)[2] <- "dtype"
names(df.melt)[3] <- "numvals"
df.melt

#plot the stacked bar plot
plotObj <- ggplot(df.melt, aes(City, y=numvals, fill=dtype)) +
     geom_bar(stat="identity") +
    scale_fill_manual(values = c("Gap" = "red","Numdpts"="darkgreen")) 
                      
plotObj


