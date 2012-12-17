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

def read_user_scoreDict(fi):
  scoredict = {}
  score = fi.readlines()[1:] #reads one line at a time, skip the header row  
  for line in score:
    x = line.split(",")
    minmax = (int(x[0]),int(x[1]))
    score = int(x[2])
    scoredict[minmax] = score
  return scoredict


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

def calculate_score_given_temp(temp,scoredict):
  score = 0
  for tup in scoredict.keys():
    if temp >= tup[0] and temp < tup[1]:
      # print 'found'
      score = scoredict[tup]      
  return score


def sort_into_bins(data, numbins=10, minv=0, maxv=100):
#binning

  #minv = min(data)
  #maxv = max(data)

  bincounts = []
  for i in range(numbins+1):
    bincounts.append(0)

  for d in data:
    b = int((d - minv) / float(maxv - minv) * numbins)
    bincounts[b] += 1
    #print d, "goes to : bin", b
  return bincounts


def   print_dict(dct):
  for k,v in dct.items():
    print k,v
  

def  create_daily_raw_temp_dicts(fi):
  rowsperDay = defaultdict(int)
  tlines = fi.readlines()[1:] #reads one line at a time, skip the header row  

  totlines =len(tlines)
  print len(tlines), "number of lines"
  
  for l in tlines:
    dte = l.split()[0] #datestring
    rowsperDay[dte] += 1 #now we know how many data points per day

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
    raw_daily_dict[dte] = tempdict
    start = end    
    tempdict = {} #reset for next date in the file
    
              # print_dict(raw_daily_dict)
  return raw_daily_dict

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



def calculate_comfort_score(hourlyTempDict,scoreRefdict):
  cumulativeScore = 0
  numhrlyDataPoints = 0
  cityScoreDict = {}
  for dt, tD in hourlyTempDict.items():
    dayscore = 0
    for temp in tD.values():
      score = calculate_score_given_temp(temp,scoreRefdict)
      dayscore +=score
      cumulativeScore += score
    numhrlyDataPoints += len(tD)
    #print dt, "had ", len(tD), "data points for a score of ", (dayscore/len(tD))
    cityScoreDict[dt] = (dayscore/len(tD))  # {date: day's score}
    
  comf = (cumulativeScore/numhrlyDataPoints)
  print "Overall score is", comf , cumulativeScore, numhrlyDataPoints, "Numhours"
  return  cityScoreDict

def create_Hourly_Temp_Dict_for_city(f):

  dated_raw_dict = create_daily_raw_temp_dicts(f)
  print "Finished reading Raw Temps file\n"

  hourlyTempDict = {}
  for dt,onedaysdict in dated_raw_dict.items():
    dtdict = create_rounded_hourly_temp_dict_for_each_day(onedaysdict)
    hourlyTempDict[dt] = dtdict
  print "Hourly Temp Dict is now ready for all dates\n"  

  return hourlyTempDict




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
  print "\nDays with score >50: ", city[0], numCent0, city[1],numCent1
  print "\nDays with score >70: ", city[0], num70_0, city[1],num70_1

  bincounts = sort_into_bins(cSD2.values(), numbins=10, minv=0, maxv=100)
  for ind, b in enumerate(bincounts):
    print ind*10, b

if __name__ == '__main__':
#  os.system('clear')
  rawDirPath = r'ra_score.csv'
  f = open(rawDirPath, 'r')
  scoreRefdict = read_user_scoreDict(f)
  f.close()
  print "Finished reading User Scoring Scheme\n"

  ################
  rawDirPath1 = r'KILSCHAU1.csv'
  rawDirPath2 = r'KCASUNNY13.csv'

#  rawDirPath1 = r'KFLMIAMI88.csv'
  rawDirPath2 = r'KVARICHM29.csv'

  city=[]
  city.append("Schaumburg, IL")
#  city.append("Sunnyvale, CA")
  city.append("RIC, VA")

  ################
  
  flist = []
  f1 = open(rawDirPath1, 'r')
  flist.append(f1)
  f2 = open(rawDirPath2, 'r')
  flist.append(f2)
  
  cityHrTempDictList = []
  for f in flist:
    hourlyTempDict = create_Hourly_Temp_Dict_for_city(f)
    cityHrTempDictList.append(hourlyTempDict)

  ctyScoreDictList = []  
  for ind, cityDict in enumerate(cityHrTempDictList):
    print "\n\n City :",city[ind]
    cityScoreDict = calculate_comfort_score(cityDict, scoreRefdict)
    ctyScoreDictList.append(cityScoreDict)

  cSD2 = ctyScoreDictList[1] #dict for the 2nd city
  cSD1 = ctyScoreDictList[0] #dict for the 1st city

  compare_two_cityScores(cSD1, cSD2)


  calculate_comfort_score(cityHrTempDictList[0],scoreRefdict)
  calculate_comfort_score(cityHrTempDictList[1],scoreRefdict)

  #data = [1,33, 44,0,-56,100,99]
  #bincounts = sort_into_bins(data, numbins=10, minv=0, maxv=100)


