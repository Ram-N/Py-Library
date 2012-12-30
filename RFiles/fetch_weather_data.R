# Author: Ram Narasimhan

#weather data (mainly Temperature) retrieval from the WEB
# We are interested in getting historical Temperature data, by City
# SOURCE: wunderground.com (weather underground)

# To get a single day's worth of (hourly) data
#USAGE: w <- wunder_station_daily('KCAANGEL4', as.Date('2011-05-05'))
  #     writeToFile_Wx_data_for_date_range(st=c("KPIT","Pittsburgh"), airportFlag=1, start_date, end_date)


#Note that URL's should be of the form:
#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=KCASUNNY13&month=1&day=1&year=2011&format=1

#This format is slightly different for AIRPORT DATA:
# http://www.wunderground.com/history/airport/KPHX/2010/11/18/DailyHistory.html?format=1
#http://www.wunderground.com/history/airport/(K or P)<3-letter airport code>/2010/11/18/DailyHistory.html?format=1

#sometimes there a P instead of a K in front of the 3-letter code


# more on usage 
#station2 ='KCASUNNY13'
#start_date = '2011-01-01'
#end_date = '2011-12-31'
#airport  = 1 if an airport or 0 if not an airport


#PYTHON example of a similar functionality is at
# example from: http://casoilresource.lawr.ucdavis.edu/drupal/node/991
# for PYTHON http://craigsimpson.net/2012/09/getting-rain-fall-inches-in-python/



rm(list=ls())
#PC
outputDir.path <- file.path("~/Py Library/Wx/RFiles")
#mac
#outputDir.path <- file.path("~/Python/Wx/RFiles")
setwd(outputDir.path)
getwd()

# Load libraries
library('ggplot2')
library('plyr')

# A couple of other functions have to compiled first for this to work

source("sub_data_fetch_routines.R")

# output: gzipped file with stationname.csv
#Dependencies: is_Station_Data_Available, wunder_station_daily

writeToFile_Wx_data_for_date_range <- function(stuple, airpFlag, start_date, end_date) {

  station <- stuple[1] #wunderground code of the station
  stname <- stuple[2] #common name of the station
  
  validity = is_Station_Data_Available(station, airpFlag, start_date, end_date)
  if (validity==0){
    print("Station data not available.")
    return(0) #returning a NULL to signal no data
  }
  
  date.range <- seq.Date(from=as.Date(start_date), to=as.Date(end_date), by='1 day')
  print(station)
  # pre-allocate list
  l <- vector(mode='list', length=length(date.range))

  # loop over dates, and fetch data
  for(i in seq_along(date.range))
  {
    #print (station)
    print( date.range[i])

  # print(station, date.range[i])
    l[[i]] <- wunder_station_daily(station, airpFlag, date.range[i])
    #print(l[[i]])
  }

  
  # stack elements of list into DF, filling missing columns with NA
  d <- ldply(l, .inform=TRUE)
  
  #print(d)
  #keep only the first two columns (time and temp)
  d <- d[,1:2]
  
  #remove space, tabs and newlines from stname. "Las Vegas" becomes LasVegas.
  stname <- gsub("\\s",'', stname , fixed=TRUE)
  
  outFileName = paste(stname, "csv","gz", sep='.')
  # save to CSV
  write.csv(d, file=gzfile(outFileName), row.names=FALSE)
  print(outFileName)  
}


###################


#write out a bunch of data files
writeToFile_Wx_data_for_date_range(station1, airpFlag, start_date, end_date)


#data availability testing
start_date = '2011-01-01'
end_date = '2011-12-31'
airpFlag = 1

start_date; end_date

lst = c("KSEA","KHOU","KPHX","KDEN","KBOS","KNYC","KLAS")
common_name = c("Seattle", "Houston", "Phoenix", "Denver", "Boston", "NYC", "Las Vegas")

lst2 = c("WSAP", "VIDP", "VOMM","VABB", "WMKK","YBBN")
common_name2 = c("Singapore", "New Delhi", "Chennai", "Mumbai","Kuala Lumpur", "Brisbane")

lst2 = c("42754")
common_name2 = c("Indore")


#a two column data frame of code and common_name
cdf <- data.frame(lst2,common_name2)
cdf
cdf[1,]

#send the (city code, and the common name) to the function being called
apply(cdf,1, is_Station_Data_Available, airpFlag, start_date, end_date)

#send the (city code, and the common name) to the function being called
apply(cdf,1, writeToFile_Wx_data_for_date_range, airpFlag, start_date, end_date)


source("sub_data_fetch_routines.R")
###### debugging below. Ignore #########

lst_start <- wunder_station_daily(station1, airpFlag, as.Date(start_date))
lst_end <- wunder_station_daily(station1, airpFlag, as.Date(end_date))


lapply(lst, fprint)
fprint<- function(st){ 
  cat (sprintf(" %s %s \n", st[1], st[2]))
}

lapply(lst, is_Station_Data_Available, airpFlag, start_date, end_date)  

lst_start <- wunder_station_daily(station1, airpFlag, as.Date(start_date))

