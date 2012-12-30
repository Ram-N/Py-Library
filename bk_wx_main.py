#!/usr/bin/env python

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


def score_give_tempDict(tD,scoredict):
  aggscore = 0
  numh=0

  for h,t in tD.items():
    score = score_given_temp(t,scoredict)
    print h, t, score, "(h,temp,score)"
    aggscore+=score
    numh+=1
  return float(aggscore/numh)

def score_given_temp(temp,scoredict):
  score = 0
  for tup in scoredict.keys():
    if temp >= tup[0] and temp < tup[1]:
        print 'found'
        score = scoredict[tup]      
  return score

def   read_daily_temp(fi):
  dayTempdict = defaultdict(float)
  hourstotal = defaultdict(float)
  samples = defaultdict(int)
  tlines = fi.readlines()[1:] #reads one line at a time, skip the header row  
  for l in tlines:
    dte = l.split()[0]
    hour = l.split()[1].split(",")[0]
    hr = int(hour.split(":")[0])
    temp = float(l.split()[1].split(",")[1])
    print dte, hr, temp
    samples[hr]+=1
    hourstotal[hr]+=temp

  for h in samples.keys():
    print "hr", h, samples[h], hourstotal[h]
    dayTempdict[h] = (hourstotal[h]/samples[h])

  return dayTempdict


if __name__ == '__main__':

  # Step 1 Read in the relevant file
  #read the input directory path

  #dirList=os.listdir(rawDirPath) #list of filenames
  # ##########################

  rawDirPath = r'ra_score.csv'
  f = open(rawDirPath, 'r')
  scoredict = read_user_scoreDict(f)
  f.close()

  rawDirPath = r'KILSCHAU1.csv'
  f = open(rawDirPath, 'r')
  dayTempdict = read_daily_temp(f)
  f.close()

  for h,t in dayTempdict.items():
    print h, t

  #for (k,v) in scoredict.items():
  #  print k,v


  score =  score_give_tempDict(dayTempdict,scoredict)
  print score, "agg score"
