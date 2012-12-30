

#These are needed for the function above
is_Station_Data_Available<- function (stuple, aflag, start_date, end_date){
  
  station <- stuple[1]
  stname <- stuple[2]
  lst_start <- wunder_station_daily(station, aflag, as.Date(start_date))
  lst_end <- wunder_station_daily(station, aflag, as.Date(end_date))
#  lst_start <- NULL
#  lst_end <- NULL
  st_row = nrow(lst_start) #takes on a value of NULL if station has no data
  en_row = nrow(lst_end)
  
  if (is.integer(st_row) && is.integer(en_row))
  {
    return(1)
  }
  else{
        cat(sprintf("No data found for station %s \n", stname))
        return(0) #nothing found.
      }
}



#airpFlag = 1 if airportcode, 0 othw
wunder_station_daily <- function(station, airpFlag, date)
{
  # parse date
  m <- as.integer(format(date, '%m'))
  d <- as.integer(format(date, '%d'))
  y <- format(date, '%Y')


  #wx underground station are of three types
  st_type = c("weatherstation","airport","station")
  #change the final_url, based on the URL
  
  if(airpFlag==1){
    airp_url = 'http://www.wunderground.com/history/'
    coda = '/DailyHistory.html?format=1'    
    #for airport codes
    final_url <- paste(airp_url, st_type[3],'/', station,
                       '/',y,
                       '/',m,
                       '/',d,
                       coda, sep='')
  }
  else {
    base_url <- 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?'
    # compose final url
    final_url <- paste(base_url,
                       'ID=', station,
                       '&month=', m,
                       '&day=', d, 
                       '&year=', y,
                       '&format=1', sep='')
    
  }
  
  
  
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
    
    if(airpFlag==0){ 
      # remove odd numbers starting from 3 --> end
      the_data <- the_data[-seq(3, length(the_data), by=2)]
    }
    
    # extract header and cleanup
    the_header <- the_data[1]
    the_header <- make.names(strsplit(the_header, ',')[[1]])
    
    
    # convert to CSV, without header
    tC <- textConnection(paste(the_data, collapse='\n'))
    the_data <- read.csv(tC, as.is=TRUE, row.names=NULL, header=FALSE, skip=1)
    close(tC)
    
    
    
    if(airpFlag==0){
      
      # remove the last column, created by trailing comma
      the_data <- the_data[, -ncol(the_data)]
      
      # assign column names
      names(the_data) <- the_header
      # convert Time column into properly encoded date time
      the_data$Time <- as.POSIXct(strptime(the_data$Time, format='%Y-%m-%d %H:%M:%S'))
    }
    else{ #is an airport
      #just keep the Temp and time (last columns)
      the_data <- the_data[, c(2, ncol(the_data))]      
      the_data$Time <- as.POSIXct(strptime(the_data[,2], format='%Y-%m-%d %H:%M:%S'))
      
      # remove the second column, since we have saved it as TIME posix
      the_data <- the_data[, -2]
      #swap the column order
      the_data <- the_data[c(2,1)]
      
      the_header <- c("Time",the_header[c(2)])
      
    }
    
    # assign column names
    names(the_data) <- the_header
    
    if(airpFlag==0){
      # remove UTC and software type columns
      the_data$DateUTC.br. <- NULL
      the_data$SoftwareType <- NULL
      
      # sort and fix rownames
      the_data <- the_data[order(the_data$Time), ]
      row.names(the_data) <- 1:nrow(the_data)
    }    
    
    # if there are missing values, delete the line
    #print(which(is.na(the_data), arr.ind=TRUE))
    na <- which(is.na(the_data), arr.ind=TRUE)    
    if (isTRUE(na)){
        na <- as.data.frame(na)
        the_data <- the_data[-na$row,]
    }
    # done
    return(the_data)
  }
}
