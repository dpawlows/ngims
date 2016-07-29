#!/usr/bin/python
import ngims
import ngimsGITM


startDate = '20150415'
endDate = '20150515'
files = ngims.getfiles(startDate,endDate,version='v06')

DATA = []
for f in files:
    d = ngims.readCSN(f)
    DATA += d

dataloader = ngims.DataLoader()
data = dataloader.get(DATA,species='Ar')
ngimsGITM.makeSatelliteFile(data)

