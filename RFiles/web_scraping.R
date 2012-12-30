# Accesing and plotting World Bank Data
http://lamages.blogspot.com/2011/09/accessing-and-plotting-world-bank-data.html

#Includes Motion Charts.

WDI package in R.

#Note that R¡¯s XML package, and the good fortune that the Wikipedia editors have a uniform format for Super Bowl box scores, makes this process very easy.

# Function returns quater scores from Wikipedia Super Bown pages
get.scores<-function(numeral) {
    # Base URL for Wikipedia
    wp.url<-getURL(paste("http://en.wikipedia.org/wiki/Super_Bowl_",numeral,sep=""))
    wp.data<-htmlTreeParse(wp.url, useInternalNodes=TRUE)
    score.html<-getNodeSet(wp.data,"//table[@style='background-color:transparent;']")
    score.table<-readHTMLTable(score.html[[1]])
    score.table<-transform(score.table, SB=numeral)
    return(score.table)
}



#Function takes a string as parameter and returns the approximate number of Google search results containing that string
# from https://gist.github.com/791559

require(RCurl)
require(XML)

gtry<-function(s){
    search.url<-paste("http://www.google.com/search?q=",gsub(" ","+",s),sep="")
    search.html<-getURL(search.url)
    return(parse.search<-htmlTreeParse(search.html,useInternalNodes = TRUE))
}
    search.html<-getURL(search.url)
    parse.search<-htmlTreeParse(search.html,useInternalNodes = TRUE)
    search.nodes<-getNodeSet(parse.search,"//div[@id='resultStats']")
    search.value<-strsplit(xmlValue(search.nodes[[1]])," ",fixed=TRUE)[[1]][2]
    return(as.numeric(gsub(",","",search.value,fixed=TRUE)))
}

google.counts<-function(s){

    #gsub substitutes + for each blank char. So a RESTful URL is formed.
    search.url<-paste("http://www.google.com/search?q=",gsub(" ","+",s),sep="")

    #The URL is the whole text feed that comes from getURL
    search.html<-getURL(search.url) #so search.html is a big HTML text string

    parse.search<-htmlTreeParse(search.html,useInternalNodes = TRUE)

    search.nodes<-getNodeSet(parse.search,"//div[@id='resultStats']")
    search.value<-strsplit(xmlValue(search.nodes[[1]])," ",fixed=TRUE)[[1]][2]
    return(as.numeric(gsub(",","",search.value,fixed=TRUE)))
}
