#!/usr/bin/env python

'''Make satelitte files for MGITM'''

import ngimsGITM
import ngims

# DD2
# startDate = '20150417'
# endDate = '20150422'

# DD8
startDate = '20171016'
endDate = '20171023'

startDate = '20170910'
endDate = '20170912'

version = 'v07'

files = ngims.getfiles(startDate,endDate,version=version)
DATA = ngims.getCSN(files,outbound=False)

# version = 'v08'
# files = ngims.getfiles(startDate,endDate,version=version,type='ion')
# DATA = ngims.getCSN(files,outbound=False)

dataloader = ngims.DataLoader()
# species = '32'
# data = dataloader.get(DATA,species=species)
# dataloader.orbits(data,output=True)

# data = dataloader.get(DATA,species=species)
# output = startDate+'_'+endDate+'_'+species+'.dat'
# result = ngimsGITM.outputNGIMS(data,output=output,precision=1)
#
species = 'CO2'
data = dataloader.get(DATA,species=species)
output = startDate+'_'+endDate+'_'+species+'.dat'
result = ngimsGITM.outputNGIMS(data,output=output,precision=1)
dataloader.orbits(data,output=True)

# species = 'Ar'
# data = dataloader.get(DATA,species=species)
# output = startDate+'_'+endDate+'_'+species+'.dat'
# result = ngimsGITM.outputNGIMS(data,output=output,precision=1)

# species = 'O'
# data = dataloader.get(DATA,species=species)
# output = startDate+'_'+endDate+'_'+species+'.dat'
# result = ngimsGITM.outputNGIMS(data,output=output,precision=1)

# ngimsGITM.makeSatelliteFile(data,species=species,location=[140,160],locationType='alt')
# ngimsGITM.makeSatelliteFile(data,species=species,locAveraging=2.5)
