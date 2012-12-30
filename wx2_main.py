#!/usr/bin/env python
from __future__ import division
import logging
import os
import time
import sys
import math
import re
from collections import defaultdict #automatically initializes to zero



logging.basicConfig(level=logging.DEBUG, filename='wx.log')
logging.basicConfig(level=logging.INFO, filename='wx.log')
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def  write_list_to_file(fname, lst):
  fo = open(fname, "a+") #append
  for w in lst:
    fo.write("%s\n" % w)
  fo.close()


def  write_dict_to_file(fname, _dict):
    fo = open(fname, "a+") #append
    for k,v in _dict.items():
        fo.write(" %s , %s\n " % (k , v))
    fo.write("\n")
    fo.close()


def   print_dict(dct):
    for k,v in dct.items():
        print k,v

def   print_list(lst):
    for l in lst:
        print l  


#BINNING UTITLITY. Takes a data (list) and bins it into numbins
def sort_into_bins(data, numbins=10, minv=0, maxv=100):
    bincounts = []
    lowerbound = []
    upperbound = []
    for i in range(numbins+1):
        bincounts.append(0)
        lowerbound.append(i*numbins)
        upperbound.append(((i+1)*numbins) - 1)  
    for d in data:
        b = int((d - minv) / float(maxv - minv) * numbins)
        bincounts[b] += 1
    #print d, "goes to : bin", b
    return (lowerbound, upperbound, bincounts)




#### READ ROUTINES
def read_user_scoreDict(fi):
    scoredict = {}
    score = fi.readlines()[1:] #reads one line at a time, skip the header row  
    for line in score:
        x = line.split(",")
        minmax = (int(x[0]),int(x[1]))
        score = int(x[2])
        scoredict[minmax] = score
    return scoredict

# A meta file that contains the names of all data files
def create_city_file_lists(fName):
    '''
    Read the meta data file, which contains names of all city data files
    Return: CityNamesList, as well as a list of filepointers
    '''
    cityList = []
    flist = []
    df = open(fName, 'r')
    lines = df.readlines()

    for l in lines:
      if l.strip() != "" : #taking care of blank lines
        print "City:", l
        # toks = l.split()
        toks = [x.strip() for x in l.split(',')] #break at the commas, then strip out blanks
        cityList.append(toks[0]+toks[1])      
        fc = open('data/'+toks[2],'r')
        flist.append(fc)

    return (cityList, flist)  


# First a raw temp dict is created for each city
def  create_daily_raw_temp_dicts(fi):
    '''
    returns a dictionary of dictionaries
    Format is:
    {date1: {temp dictionary1}, date2: {temp dictionary2}, ... date_n: {temp dictionary_n}}
    '''
    rowsperDay = defaultdict(int)
    tlines = fi.readlines()[1:] #reads one line at a time, skip the header row  

    pattern = r"NA"

    totlines =len(tlines)
    print len(tlines), "Number of raw lines in file"
  
    for l in tlines:
      if l:
        #drop lines that have an NA for the temperature value
        toks = l.split(',')
        for t in toks:
          if re.match(pattern, t):   #the tok is an NA     
            tlines.remove(l) #drop the line
            print "skipping line:",l
            continue

        #print("parsing %s" % l)
        dte = l.split()[0] #datestring
        if "NA" in dte: 
          print "skipping line", l
          continue
        rowsperDay[dte] += 1
        #print "added date ", dte

    print len(rowsperDay), "Number of unique days in file"    
    # now we know how many data points per day
    #    print_dict(rowsperDay)
    #sys.exit(0)

    start = 0
    raw_daily_dict = {}
    tempdict = {}

    for d in range(len(rowsperDay)): #one loop for each date in the file
      #print d, start, "should go up to",len(rowsperDay) #this sometimes spills over to the next year. need to delete those lines
      l = tlines[start] #first line in file for that date
      

      dte = l.split()[0] #datestring
      #print dte, "starts at", start
      numrows = rowsperDay[dte]
      end = start+numrows
        #print "new date", dte, "has ",numrows," rows"
      for l in tlines[start:end]:
        try:            
          dte = l.split()[0] #datestring
          hour = l.split()[1].split(",")[0] #timestamp
          hr = int(hour.split(":")[0]) #rounded to the floor hour
          temp = float(l.split()[1].split(",")[1])  #temp as a float
          tempdict[hour] = temp
        except:
          print("Unable to Parse %s start %d end %d" %  (l,start,end) )
        ###
      raw_daily_dict[dte] = tempdict
        ###
      #print "Done with ",dte
      start = end    
      tempdict = {} #reset for next date in the file
    
    # print_dict(raw_daily_dict)
    return raw_daily_dict

# All the data for a given hour are averaged and assigned to that hour
def create_rounded_hourly_temp_dict_for_each_day(rawdict):
    dayTempdict = defaultdict(float)
    hourstotal = defaultdict(float)
    samples = defaultdict(int)

    for ts,temp in rawdict.items():
        hr = int(ts.split(":")[0]) #rounded to the floor hour
        samples[hr]+=1
        hourstotal[hr]+=temp
  
    for h in samples.keys():
        # print "hr", h, samples[h], hourstotal[h]
        dayTempdict[h] = (hourstotal[h]/samples[h])

    return dayTempdict


def create_Hourly_Temp_Dict_for_city(f):
    '''
    Given a city temp data file, this function makes it into an Hourly Temp Dictionary
    format or returned dictionary:
    {0: t0, 1: t1, 2: t2, ..., 23: t23}
    '''
    dated_raw_dict = create_daily_raw_temp_dicts(f)
    print "Finished reading Raw Temps file\n"

    hourlyTempDict = {}
    for dt,onedaysdict in dated_raw_dict.items():
        dtdict = create_rounded_hourly_temp_dict_for_each_day(onedaysdict)
        hourlyTempDict[dt] = dtdict
    print "Hourly Temp Dict is now ready for all dates\n"  
    return hourlyTempDict

### End of READ ROUTINES


def calculate_score_give_tempDict(tD,scoredict):
  '''
  function expects two dictionaries as inputs.
  td is of the format {0:temp, 1:temp, ... , 23:temp} where temp is a float
  scoredict is a dictionary with temp range and a comfort score for it
  '''
  aggscore = 0
  numh=0

  for h,t in tD.items():
    score = calculate_score_given_temp(t,scoredict) #get score for single point
    #print h, t, score, "(h,temp,score)"
    aggscore+=score
    numh+=1
  return float(aggscore/numh)

# ATOMIC Score calculation
def calculate_score_given_temp(temp,scoredict):
  score = 0
  for tup in scoredict.keys():
    if temp >= tup[0] and temp < tup[1]:
      # print 'found'
      score = scoredict[tup]      
  return score



#calculate score for ONE CITY, given its hTdictionary
#output is a 3-term tuple, hcomf, dailyscoredict and the bins
def calculate_comfort_score(cityName, hourlyTempDict,scoreRefdict):

  listOfHourlyScores = []
  cumulativeScore = 0
  numhrlyDataPoints = 0
  cityDailyScoreDict = {}
  for dt, tD in hourlyTempDict.items():
    dayscore = 0
    for temp in tD.values():
      score = calculate_score_given_temp(temp,scoreRefdict)
      dayscore +=score
      cumulativeScore += score
      listOfHourlyScores.append(score)
    numhrlyDataPoints += len(tD)
    #print dt, "had ", len(tD), "data points for a score of ", (dayscore/len(tD))
    cityDailyScoreDict[dt] = (dayscore/len(tD))  # {date: day's score}


  binbounds = sort_into_bins(listOfHourlyScores, numbins=10, minv=0, maxv=100)
    
  Hcomf = (cumulativeScore/numhrlyDataPoints)
  print("Overall score is %.2f, %d for %d Numhours" % (Hcomf , cumulativeScore, numhrlyDataPoints))
  return  (Hcomf, cityDailyScoreDict, binbounds)





#NOT USED
def compare_two_cityScores(cSD1, cSD2):
  '''
  given two scity score dicts, how do the scores compare?
  '''
  print "\nDays with score  0:", city[0], numZeroes0, city[1],numZeroes1
  print "\nDays with score >70: ", city[0], num70_0, city[1],num70_1




def  print_binned_scores(cName,binbounds):
  '''
  assumes that the binning has already occurred
  '''
  print "\n\n For City :", cName
  totaldpts = 0
  bincounts = binbounds[2]
  low = binbounds[0]
  high = binbounds[1]


  for ind, b in enumerate(bincounts):
    totaldpts+=b
  print "Total data points", totaldpts
  print("\n")

  print "Low, High, NumHrs, Percent"
  for ind, b in enumerate(bincounts):
    print("%d, %d, %d, %.2f"% (low[ind], high[ind], b, (b/totaldpts)*100))

def  write_to_file_binned_scores(fname, cName, citycomf, binbounds):
  fo = open(fname, "a+") #append

  fo.write( "\n\n ComfortScore For City :%s is %.2f\n" % (cName, citycomf))
  totaldpts = 0
  bincounts = binbounds[2]
  low = binbounds[0]
  high = binbounds[1]

  for ind, b in enumerate(bincounts):
    totaldpts+=b
  fo.write( "Total data points %d \n"% totaldpts)
  fo.write( "Low, High, NumHrs, Percent\n")
  for ind, b in enumerate(bincounts):
    fo.write("%d, %d, %d, %.2f \n"% (low[ind], high[ind], b, (b/totaldpts)*100))

  fo.close()


# How many data points are missing for each hour?
# Returns: A dict with key = hour (0..23) and value to #dpts
def input_data_profile(cTD):
    cityDataProfile = defaultdict(int)

    for tD in cTD.values():
        for h in tD.keys():
            cityDataProfile[h] += 1

    return cityDataProfile



def write_to_file_number_of_hourly_data_points(fname, _city, _dict):

    fo = open(fname, "a+") #append
    for k,v in _dict.items():
        fo.write("%s, %s , %s\n " % (_city, k , v))
    fo.write("\n")
    fo.close()


if __name__ == '__main__':
#  os.system('clear')

  ifName = 'data/input_ra_score.csv'
  f = open(ifName, 'r')
  scoreRefdict = read_user_scoreDict(f)
  f.close()

  ################
  dfName = 'data/input_citydatafiles.csv'
  (cityList, flist) = create_city_file_lists(dfName)
  print "Finished reading City FileNames\n"
  print_list(cityList)


  fname = "data/out_cityScores.csv"
  fo = open(fname, "w") 
  cityHrTempDictList = []
  for ind, f in enumerate(flist):
    print "\n\n\n", cityList[ind]

    # Given a city temperature data file, make it into an Hourly Temp Dictionary
    hourlyTempDict = create_Hourly_Temp_Dict_for_city(f)

    cityHrTempDictList.append(hourlyTempDict)
    (citycomf, cityDSDict, binbounds) = calculate_comfort_score(cityList[ind],cityHrTempDictList[ind],scoreRefdict)
    print_binned_scores(cityList[ind],binbounds)
    write_to_file_binned_scores(fname, cityList[ind], citycomf, binbounds)
  print "Finished writing: ",fname

  fname = "data/out_dataQuality.csv"
  fo = open(fname, "w") 

  # Pickling
  cDataProfileL = []  
  for ind,cTD in enumerate(cityHrTempDictList):
      #fo = open(fname, "a+") 
      cName = cityList[ind]
      #fo.write("City: %s %d\n" % (cName, len(cTD)))
      #fo.close()
      cityDataProfile = input_data_profile(cTD)
      write_to_file_number_of_hourly_data_points(fname, cName, cityDataProfile)
      #print_dict(cityDataProfile)
      #write_dict_to_file(fname, cityDataProfile)
      cDataProfileL.append(cityDataProfile)

   
  fo.close()
  print "Finished writing: ",fname

  ##########
  #

  #ctyScoreDictList = []  
  #for ind, cityDict in enumerate(cityHrTempDictList):
    #print "\n\n City :",city[ind]
    #cityScoreDict = calculate_comfort_score(cityDict, scoreRefdict)
    #ctyScoreDictList.append(cityScoreDict)

  #cSD2 = ctyScoreDictList[1] #dict for the 2nd city
  #cSD1 = ctyScoreDictList[0] #dict for the 1st city

  #compare_two_cityScores(cSD1, cSD2)


