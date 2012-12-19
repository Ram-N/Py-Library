# Author: Ram Narasimhan

#weather data retrieval from the WEB
#
# example from: http://casoilresource.lawr.ucdavis.edu/drupal/node/991
# for Excel http://craigsimpson.net/2012/09/getting-rain-fall-inches-in-python/
# To get a single day's worth of (hourly) data
#USAGE: w <- wunder_station_daily('KCAANGEL4', as.Date('2011-05-05'))


#Note that URL's should be of the form:
#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=KCASUNNY13&month=1&day=1&year=2011&format=1

#This format also works for AIRPORT DATA:
# http://www.wunderground.com/history/airport/KPHX/2010/11/18/DailyHistory.html?format=1
#http://www.wunderground.com/history/airport/K<3-letter airport code>/2010/11/18/DailyHistory.html?format=1


# Updated Usage
#station2 ='KCASUNNY13'
#start_date = '2011-01-01'
#end_date = '2011-12-31'

#get_Wx_data_for_date_range(station1,start_date, end_date)



rm(list=ls())
outputDir.path <- file.path("~/RStats/Source Code Web Scraping")
setwd(outputDir.path)
getwd()

# Load libraries
library('ggplot2')
library('plyr')



get_Wx_data_for_date_range <- function(station, start_date, end_date) {

  validity = is_Station_Data_Available(station, start_date, end_date)
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
    print (station)
    print (i); 
    print( date.range[i])

#    print(station, date.range[i])
    l[[i]] <- wunder_station_daily(station, date.range[i])
  }

  #print(l)  
  # stack elements of list into DF, filling missing columns with NA
  d <- ldply(l)

  #print(d)
  #keep only the first two rows (time and temp)
  d <- d[,1:2]
  
  outFileName = paste(station, "csv","gz", sep='.')
  # save to CSV
  write.csv(d, file=gzfile(outFileName), row.names=FALSE)
  outFileName
  getwd()
  
}

stations: 
KILSCHAU1 Schaumburg, IL
KCASUNNY13 Sunnyvale, CA

station1 = 'KILSCHAU1'
station2 ='KCASUNNY13'

station1 ='KFLMIAMI43' #Pinecrest Miami
station1 = 'KVARICHM29' #richmond, va
station1 = 'aKVARICHM29d' #richmond, va

start_date = '2011-01-01'
#end_date = '2011-12-31'
end_date = '2011-01-11'



get_Wx_data_for_date_range(station1,start_date, end_date)

get_Wx_data_for_date_range(station2,start_date, end_date)




#These are needed for the function above
is_Station_Data_Available<- function (station, start_date, end_date){
  
  lst_start <- wunder_station_daily(station, as.Date(start_date))
  lst_end <- wunder_station_daily(station, as.Date(end_date))
  print(nrow(lst_start))
  st_row = nrow(lst_start) #takes on a value of NULL if station has no data
  en_row = nrow(lst_end)
  
  if (is.integer(st_row) && is.integer(en_row))
  {
    return(1)
  }
  else
    return(0) #nothing found.
}

#testing
start_date; end_date
lst = list("KCASUNNY13", "KFLMIAMI43", "BUOYPXOC1")
lapply(lst, is_Station_Data_Available, start_date, end_date)
  

str(w1)
#testing


wunder_station_daily <- function(station, date)
{
  # parse date
  m <- as.integer(format(date, '%m'))
  d <- as.integer(format(date, '%d'))
  y <- format(date, '%Y')
  
  
  base_url = 'http://www.wunderground.com/history/airport/K'
  coda = '/DailyHistory.html?format=1'
  
  base_url <- 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?'
  
  
  # compose final url
  final_url <- paste(base_url,
                     'ID=', station,
                     '&month=', m,
                     '&day=', d, 
                     '&year=', y,
                     '&format=1', sep='')

  #for airport codes
  final_url <- paste(airp_url, station,
                         '/',y,
                         '/',m,
                         '/',d,
                         coda, sep='')
  
  
  # reading in as raw lines from the web server
  # contains <br> tags on every other line
  print(final_url)
  u <- url(final_url)
  the_data <- readLines(u)
  close(u)
  
  # only keep records with more than 5 rows of data
  if(length(the_data) > 5 )
  {
    # remove the first and last lines
    the_data <- the_data[-c(1, length(the_data))]
    
    # remove odd numbers starting from 3 --> end
    the_data <- the_data[-seq(3, length(the_data), by=2)]
    
    # extract header and cleanup
    the_header <- the_data[1]
    the_header <- make.names(strsplit(the_header, ',')[[1]])
    
    # convert to CSV, without header
    tC <- textConnection(paste(the_data, collapse='\n'))
    the_data <- read.csv(tC, as.is=TRUE, row.names=NULL, header=FALSE, skip=1)
    close(tC)
    
    # remove the last column, created by trailing comma
    the_data <- the_data[, -ncol(the_data)]
    
    # assign column names
    names(the_data) <- the_header
    
    # convert Time column into properly encoded date time
    the_data$Time <- as.POSIXct(strptime(the_data$Time, format='%Y-%m-%d %H:%M:%S'))
    
    # remove UTC and software type columns
    the_data$DateUTC.br. <- NULL
    the_data$SoftwareType <- NULL
    
    # sort and fix rownames
    the_data <- the_data[order(the_data$Time), ]
    row.names(the_data) <- 1:nrow(the_data)
    
    # done
    return(the_data)
  }
}


###End of These are needed for the function above



str(w)
###############

#TRIALS

# be sure to load the function above first
# get a single day's worth of (hourly) data
#w <- wunder_station_daily('KCASUNNY13', as.Date('2012-10-04'))
w <- wunder_station_daily('KILSCHAU1', as.Date('2012-10-04'))
w <- wunder_station_daily('KVARICHM29', as.Date('2012-10-04'))

w1 <- wunder_station_daily('KFLMIAMI43', as.Date('2011-02-01'))
w1


station1 ='KMIA'
station1 = 'KVARICHM29' #richmond, va

start_date = '2011-01-01'
end_date = '2011-12-31'

names(w)
head(w[,1:2])
w[,1:2]
write.csv(w[,1:2], file= 'KCASUNNY13.csv', row.names=FALSE)
getwd()
# get data for a range of dates


date.range <- seq.Date(from=as.Date('2009-1-01'), to=as.Date('2011-05-06'), by='1 day')

# pre-allocate list
l <- vector(mode='list', length=length(date.range))

# loop over dates, and fetch data
for(i in seq_along(date.range))
{
  print(date.range[i])
  l[[i]] <- wunder_station_daily('KCASUNNY13', date.range[i])
}

# stack elements of list into DF, filling missing columns with NA
d <- ldply(l)

# save to CSV
write.csv(d, file=gzfile('KCASUNNY13.csv.gz'), row.names=FALSE)


