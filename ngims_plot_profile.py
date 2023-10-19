#!/usr/bin/env python

import ngims
import re
import sys
from matplotlib import pyplot as pp
import numpy as np
from glob import glob

varmap = {16:'O$^+$',32:'O$_2^+$',44:'CO$_2^+$'}
def get_args(argv):

    
    help = 0
    version = 'v06'
    start = ''
    end = ''
    type = 'csn'
    pvar = ''
    minv = 0.0
    maxv = 0.0
    orbits = ''
    maxalt = 250
    inboundonly = False
    orbitave = False

    for arg in argv:

        IsFound = 0
        iError = 0
        if (not IsFound):
            m = re.match(r'-start=(.*)',arg)
            if m:
                start = m.group(1)
                if len(start) != 8:
                    iError = 1
                    message = 'Incorrect format for start date: yyyymmdd'
                IsFound = 1

            m = re.match(r'-end=(.*)',arg)
            if m:
                end = m.group(1)
                if len(end) != 8:
                    iError = 1
                    message = 'Incorrect format for end date: yyyymmdd'

                IsFound = 1        

            m = re.match(r'-h',arg)
            if m:
                help = 1
                IsFound = 1

            m = re.match(r'-ion',arg)
            if m:
                type = 'ion'
                IsFound = 1

            m = re.match(r'-csn',arg)
            if m:
                type = 'csn'
                IsFound = 1

            m = re.match(r'-inboundonly',arg)
            if m:
                inboundonly = True
                IsFound = 1

            m = re.match(r'-ver=(.*)',arg)
            if m:
                version=m.group(1)
                IsFound = 1

            m = re.match(r'-var=(.*)',arg)
            if m:
                pvar=m.group(1)
                IsFound = 1   

            m = re.match(r'-min=(.*)',arg)
            if m:
                minv=float(m.group(1))
                IsFound = 1      

            m = re.match(r'-max=(.*)',arg)
            if m:
                maxv=float(m.group(1))
                IsFound = 1      
            m = re.match(r'-maxalt=(.*)',arg)
            if m:
                maxalt=float(m.group(1))
                IsFound = 1 

            m = re.match(r'-orbit=(.*)',arg)
            if m:
                orbits=[int(o) for o in m.group(1).split(',')]
                IsFound = 1  

            m = re.match(r'-orbitave',arg)
            if m:
                orbitave=True
                IsFound = 1  

            if iError > 0:
                print(message)
                exit(iError)

    args = {'start':start,'end':end, 
            'help':help,
            'version':version,
            'type':type,
            'pvar':pvar,
            'minv':minv,
            'maxv':maxv,
            'orbits':orbits,
            'maxalt':maxalt,
            'inboundonly':inboundonly,
            'orbitave':orbitave}

    return args

args = get_args(sys.argv)    
maxalt = args['maxalt']

if ((len(args['start']) == 0 or len(args['end']) == 0) and len(args['orbits']) == 0) or len(args['pvar']) == 0:
    print('Must specify -start/end or -orbit and a variable')
    args['help'] = 1
    
if (args["help"]):

    print('Usage : ')
    print('ngims_plot_profile.py -orbit=orbits -start=start -end=end -help -ver=version -csn/ion -var=var -min=minv ' )
    print('     -max=maxv')
    print('     Required: -orbit or -start and -end')
    print('                -var')
    print('     -orbit=orbit1,orbit2,orbit3,... : a list of orbit numbers to plot ')
    print('     -start=yyyymmdd : start date of dataset')
    print('     -end=yyyymmdd : end date of dataset')
    print('     -csn or -ion    (default is csn)')
    print('     -help : print this message')
    print('     -ver=str : ngims version string (default: v06)')
    print('     -var=variable : variable to plot. For neutrals, the variable should be the atom or ')
    print('          compound formula (e.g. co2). For ions, it should be the AMU/z. variable can be allions ')
    print('          in which case only a single orbit should be specified')
    print('     -min=minv : plot minimum (optional)')
    print('     -min=maxv : plot maximum (optional)')
    print('     -maxalt=maxalt : maximum altitude to plot (default is 250km)')
    print('     -inboundonly : if set only plot inbound data')
    print('     -orbitave : plot orbit average for the specified time range or orbit numbers')

    exit()

type = args['type']
if args['pvar'] == 'allions':
    allions = True 
    varlist = [32,44,16]
    if len(args['orbits']) != 1:
        print('If plotting multiple variables, you may only select a single orbit using the -orbit flag')
        exit(1)
else:
    varlist = [args['pvar']]
    allions = False

#The data have different column names depending if we are dealing with neutral files or ion files
speciesColumn = 'species'
qualityFlag = 'IV'
if type == 'ion':
    speciesColumn = 'ion_mass'
    qualityFlag = ['SCP','SC0']

#User may specify start and end times, or, a list of orbit numbers. Create the filelist.
versions = [] #handle different versions of ngims data
if len(args['start']) > 0:
    files = ngims.getfiles(args['start'],args['end'],type=type,version=args['version'])
else:
    files = []
    filelist = glob('*'+type+'*csv')

    for file in filelist:
        version = file[-11:-8]
        if not version in versions:
            versions.append(version)
        meta = ngims.getorbit(file)

        if meta['orbit'] in args['orbits']:
            files.append(file)

if args['orbitave'] and len(files) < 2:
    print("When calculating averages over multiple orbits, multiple files must \
        be specified")
    exit(1)


if len(versions) > 1:
    print('Warning: There are multiple versions ngims files being processed: {}'.format(versions))
    sleep(500)

#Given a list of files, grab the data
automin = True if args['minv'] == 0.0 else False
automax = True if args['maxv'] == 0.0 else False
mini = 9999
maxi = -9999

fig = pp.figure()
ax = pp.subplot(111)

for fi in files:
    data = ngims.readNGIMS(fi)
 
    data = data[(data["alt"] < 350)]
    data = data[data["quality"].isin(qualityFlag)]

    for pvar in varlist:
        newdf = data[(data[speciesColumn] == int(pvar))]
        if newdf.shape[0] == 0:
            print("Error in ngims_plot_profile: Empty data frame from {}".format(fi))
            
        if args['inboundonly']:
            minalt = newdf['alt'].idxmin()
            indices = list(newdf.index.values)
            imin = indices.index(minalt)+1
            newdf = newdf.loc[indices[0:imin]] #update the df with only inbound data
        density = np.log10(newdf.loc[newdf["alt"] < maxalt,"abundance"]*1e6)

        starred = ''
        temp = newdf['quality'].isin(['SC0'])
        if temp.values.sum() / newdf.shape[0] > .75:
            starred = '*'
        
        altitude = newdf.loc[newdf["alt"] < maxalt,'alt'].values
        
        # line, = pp.plot(density,altitude,'.',markersize = 5)
        line, = pp.plot(density,altitude)
        if allions:
            line.set_label(varmap[pvar])
        else:
            line.set_label(str(data.orbit.values[0])+starred)

        if automin:
            mini = np.minimum(mini,np.min(density))
        if automax:
            maxi = np.maximum(maxi,np.max(density))



if allions:
    pp.legend(loc='upper right',frameon=False)
else: 
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
    # pp.legend(loc='upper right',frameon=False)
pp.xlim([mini,maxi])
pp.ylim([100,maxalt])
pp.xlabel('Density (#/m$^3$)')
pp.ylabel('Altitude (km)')
pp.savefig('plot.png')


