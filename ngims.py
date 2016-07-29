#!/usr/bin/python

from glob import glob
from matplotlib import pyplot as pp
import datetime

"""
Classes and functions for reading and working with MAVEN NGIMS data
"""

class DataLoader():
    """Class for handling filtering NGIMS data"""

    def get(self,data,**kwargs):
        for key in kwargs:
            data = [d for d in data if kwargs[key] == d[key] ]

        return data


def readCSN(file):
    '''Function to read NGIMS data
    Usage: data = readCSN(file)
    file: required input, name of file to be read
    data is a list of dicts; each dict contains a single measurement
    and relevant metadata.
    '''

    data = []
    f=open(file,'r')
    print file
    notStarted = True
    while notStarted:
        line = f.readline()
        if line[0:5] == "t_utc":
            notStarted = False

    t = line.split(',')
    varMap = {}
    for value in range(len(t)):
        varMap[t[value]] = value

    for line in f:

        t = line.split(',')

        try:
            int(t[0][0])
            time = datetime.datetime(int(t[varMap['t_utc']][0:4]),\
                int(t[varMap['t_utc']][5:7]),\
                int(t[varMap['t_utc']][8:10]),int(t[varMap['t_utc']][11:13]),\
                int(t[varMap['t_utc']][14:16]),int(t[varMap['t_utc']][17:19]))

            data.append({'species':t[varMap['species']],
                'alt':float(t[varMap['alt']]),
                'lon':float(t[varMap['long']]),
                'lat':float(t[varMap['lat']]),
                'precision':float(t[varMap['precision']]),
                'sza':float(t[varMap['sza']]),
                'density':float(t[varMap['abundance']]),
                'time':time,
                'orbit':int(t[varMap['orbit']]),
                })
        except:
            pass

    f.close()
    return data

def getfiles(start,end,version=None):
    filelist = glob('*csn*.csv')

    sdate = datetime.date(int(start[0:4]),int(start[4:6]),int(start[6:8]))
    edate = datetime.date(int(end[0:4]),int(end[4:6]),int(end[6:8]))

    if version == None:
        [f for f in filelist if sdate <= \
        datetime.date(int(f[-27:-23]),int(f[-23:-21]),int(f[-21:-19]))\
        and edate >=  datetime.date(int(f[-27:-23]),\
            int(f[-23:-21]),int(f[-21:-19]))]
    else:
        results = \
        [f for f in filelist if sdate <= \
        datetime.date(int(f[-27:-23]),int(f[-23:-21]),int(f[-21:-19]))\
        and edate >=  datetime.date(int(f[-27:-23]),\
            int(f[-23:-21]),int(f[-21:-19])) and (version in f or version == None) ]

    return results