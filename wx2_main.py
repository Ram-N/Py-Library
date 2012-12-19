#!/usr/bin/env python
from __future__ import division
import logging
import os
import time
import sys
import math
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
        toks = l.split()
        cityList.append(toks[0]+toks[1])      
        fc = open(toks[2],'r')
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

    totlines =len(tlines)
    print len(tlines), "Number of raw lines in file"
  
    for l in tlines:
        dte = l.split()[0] #datestring
        rowsperDay[dte] += 1
    
#now we know how many data points per day
  # print_dict(rowsperDay)

    start = 0
    raw_daily_dict = {}
    tempdict = {}
    for d in range(len(rowsperDay)): #one loop for each date in the file
        l = tlines[start] #first line in file for that date
        dte = l.split()[0] #datestring
        numrows = rowsperDay[dte]
        end = start+numrows
        #print "new date", dte, "has ",numrows," rows"
        for l in tlines[start:end]:
            dte = l.split()[0] #datestring
            hour = l.split()[1].split(",")[0] #timestamp
            hr = int(hour.split(":")[0]) #rounded to the floor hour
            temp = float(l.split()[1].split(",")[1])  #temp as a float
            tempdict[hour] = temp
        ###
        raw_daily_dict[dte] = tempdict
        ###
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
  print "Overall score is", Hcomf , cumulativeScore, "for ", numhrlyDataPoints, "Numhours"

  return  (cityDailyScoreDict, binbounds)









def compare_two_cityScores(cSD1, cSD2):
  '''
  given two scity score dicts, how do the scores compare?
  '''
  for dt,sc in cSD1.items():
    try:
      print dt, city[0], sc, city[1], cSD2[dt]
    except:
      print "missing data for", dt

  print len(cSD1), len(cSD2)

  numZeroes0=0
  numZeroes1=0
  numCent0=0
  numCent1=0
  num70_0=0
  num70_1=0


  for k in cSD1.values():
    if k==0:
      numZeroes0+=1
    if k>=50:
      numCent0+=1
    if k>=70:
      num70_0+=1
    print k,
  print "\n"  

  for k in cSD2.values():
    if k==0:
      numZeroes1+=1
    if k>=50:
      numCent1+=1
    if k>=70:
      num70_1+=1
    print k,
    
  print "\nDays with score  0:", city[0], numZeroes0, city[1],numZeroes1
  print "\nDays with score >70: ", city[0], num70_0, city[1],num70_1

  bincounts = sort_into_bins(cSD2.values(), numbins=10, minv=0, maxv=100)
  for ind, b in enumerate(bincounts):
    print ind*10, b




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

  for ind, b in enumerate(bincounts):
    print low[ind], high[ind], b, (b/totaldpts)*100



# How many data points are missing for each hour
def input_data_profile(cTD):
    cityDataProfile = defaultdict(int)

    for tD in cTD.values():
        for h in tD.keys():
            cityDataProfile[h] += 1

    return cityDataProfile



if __name__ == '__main__':
  os.system('clear')
  rawDirPath = r'ra_score.csv'
  f = open(rawDirPath, 'r')
  scoreRefdict = read_user_scoreDict(f)
  f.close()

  ################
  dfName = 'citydatafiles.csv'
  (cityList, flist) = create_city_file_lists(dfName)
  print "Finished reading City FileNames\n"
  print_list(cityList)

  cityHrTempDictList = []
  for ind, f in enumerate(flist):
    print "\n\n\n", cityList[ind]
    hourlyTempDict = create_Hourly_Temp_Dict_for_city(f)
    cityHrTempDictList.append(hourlyTempDict)
    (cityDSDict, binbounds) = calculate_comfort_score(cityList[ind],cityHrTempDictList[ind],scoreRefdict)
    print_binned_scores(cityList[ind],binbounds)


  fname = "dataprofile.csv"
  fo = open(fname, "w") 

  # Pickling
  cDataProfileL = []  
  for ind,cTD in enumerate(cityHrTempDictList):
      fo = open(fname, "a+") 
      fo.write("City: %s %d\n" % (cityList[ind],len(cTD)))
      fo.close()
      cityDataProfile = input_data_profile(cTD)
      #print_dict(cityDataProfile)
      write_dict_to_file(fname, cityDataProfile)
      cDataProfileL.append(cityDataProfile)

   
  fo.close()

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


