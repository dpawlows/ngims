#!/usr/bin/python
import ngims
import ngimsGITM
# from matplotlib import pyplot as pp





startDate = '20150415'
endDate = '20150515'
files = ngims.getfiles(startDate,endDate,version='v06')

DATA = []
for f in files:
    d = readCSN(f)
    DATA += d

dataloader = ngims.DataLoader()
data = ngims.dataloader.get(DATA,species='Ar')
ngimsGITM.makeSatelliteFile(data)

