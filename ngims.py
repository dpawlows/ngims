#!/usr/bin/env python

from glob import glob
import datetime
import argparse
import os
import re

import numpy as np
import pandas as pd
from matplotlib import pyplot as pp

"""
Classes and functions for reading and working with MAVEN NGIMS data.
Added a quicker method to simply load a pandas data frame.
"""

class DataLoader():

    """Class for handling filtering NGIMS data"""

    def get(self,data,**kwargs):
        for key in kwargs:
            data = [d for d in data if kwargs[key] == d[key] ]

        return data

    def orbits(self,data,output=False):
        sorbit = data[0]['orbit']
        iorbits = [0]
        i = 0
        for d in data:
            if d['orbit'] != sorbit:
                iorbits.append(i)
                sorbit = d['orbit']
            i += 1

        orbits = []
        time = []
        for i in range(len(iorbits[0:-1])):
            orbits.append(data[iorbits[i]]['orbit'])
            iavg = int((iorbits[i]+iorbits[i+1])/2)
            time.append(data[iavg]['time'])

        if output:
            f = open('orbits.dat','w')
            for i in range(len(orbits)):
                f.write('{:02d} {:02d} {:02d} {:02d} {:02d} {:02d} {:04d}\n'.format(
                time[i].year,time[i].month,time[i].day,time[i].hour,
                time[i].minute,time[i].second,orbits[i]
                ))
        return {'time':time,"orbits":orbits}



def getCSN(files,outbound=True):
    if len(files) > 0:
        data = []
        for f in files:
            d = readCSN(f,outbound)
            data += d

        return data
    else:
        print("No files found")
        print("In function ngims.getCSN")
        print("Are the files L2? Is the version correct?")
        exit(1)

def readNGIMS(file): 
    '''Given a file, load and return a pandas data frame'''
    data = pd.read_csv(file)
    return(data)

def getorbit(file):
    f = open(file,'r')
    temp = f.readline().split(',')
    orbitindex = temp.index('orbit')
    timeindex = temp.index('t_utc')
    tidindex = temp.index('tid')

    temp = f.readline().split(',')
    tid = int(temp[tidindex])
    orbit = int(temp[orbitindex])
    time = datetime.datetime(int(temp[timeindex][0:4]),\
            int(temp[timeindex][5:7]),\
            int(temp[timeindex][8:10]),int(temp[timeindex][11:13]),\
            int(temp[timeindex][14:16]),int(temp[timeindex][17:19]))
    f.close()
    return {'orbit':orbit,'time':time,'tid':tid}

def writeCSVOrbits(filelist):
    '''Quickly write the orbit numbers for a list of files to orbits.txt
    Usage: writeCSVOrbits(filelist)
        Required: filelist : a list of csv filenames to be read

    '''
    pos = filelist[0].rfind('csv')
    filelist.sort(key = lambda x: x[pos-30:pos-25])
    g = open('orbits.txt','w')
    g.write('Year Mon Day Hr Min Sec OrbitNum tid\n')
    for file in filelist:
        
        data = getorbit(file)
        orbit = data['orbit']
        time = data['time']
        g.write('{:02d} {:02d} {:02d} {:02d} {:02d} {:02d} {:04d} {:05d}\n'.format(
                time.year,time.month,time.day,time.hour,
                time.minute,time.second,orbit,data['tid']
                ))
    g.close()

def readCSN(file,outbound=False):
    '''Function to read NGIMS data
    Usage: data = readCSN(file)
    file: required input, name of file to be read
    data is a list of dicts; each dict contains a single measurement
    and relevant metadata.
    outbound: true to include outbound data
    '''

    data = []
    f=open(file,'r')
    if file.find('ion') > -1:
        specieskey = 'ion_mass'
    else:
        specieskey = "species"

    print(file)
    notStarted = True
    while notStarted:
        line = f.readline()
        if line[0:5] == "t_utc":
            notStarted = False

    t = line.split(',')
    varMap = {}
    for value in range(len(t)):
        varMap[t[value]] = value
    oldalt = 1.0e7
    oldspecies = ''
    for line in f:

        t = line.split(',')
        try:
            int(t[0][0])
            time = datetime.datetime(int(t[varMap['t_utc']][0:4]),\
                int(t[varMap['t_utc']][5:7]),\
                int(t[varMap['t_utc']][8:10]),int(t[varMap['t_utc']][11:13]),\
                int(t[varMap['t_utc']][14:16]),int(t[varMap['t_utc']][17:19]))

            alt = float(t[varMap['alt']])
            species = t[varMap[specieskey]]
            if (outbound and alt < 300) or (alt < oldalt or (species != oldspecies
            and alt < 300)):
                data.append({'species':species,
                    'alt':alt,
                    'lon':float(t[varMap['long']]),
                    'lat':float(t[varMap['lat']]),
                    'precision':float(t[varMap['precision']]),
                    'sza':float(t[varMap['sza']]),
                    'density':float(t[varMap['abundance']]),
                    'time':time,
                    'orbit':int(t[varMap['orbit']]),
                    })
                oldalt = alt
                oldspecies = species
        except:
            pass

    f.close()
    return data

def getfiles(start,end,dentype='csn',version=None,dir=''):
    if dentype != 'csn' and dentype != 'ion':
        print('type: {} is not recognized'.format(dentype))
        exit(1)

    filelist = glob(dir+'mvn_ngi*'+dentype+'*.csv')

    sdate = datetime.date(int(start[0:4]),int(start[4:6]),int(start[6:8]))
    edate = datetime.date(int(end[0:4]),int(end[4:6]),int(end[6:8]))
    if version == None:
        results = [f for f in filelist if sdate <= \
        datetime.date(int(f[-27:-23]),int(f[-23:-21]),int(f[-21:-19]))\
        and edate >=  datetime.date(int(f[-27:-23]),\
            int(f[-23:-21]),int(f[-21:-19]))]
    else:
        results = \
        [f for f in filelist if sdate <= \
        datetime.date(int(f[-27:-23]),int(f[-23:-21]),int(f[-21:-19]))\
        and edate >=  datetime.date(int(f[-27:-23]),\
            int(f[-23:-21]),int(f[-21:-19])) and (version in f or version == None) ]
    pos = filelist[0].rfind('csv')
    results.sort(key = lambda x: x[pos-30:pos-25]) #sort by tid

    return results




