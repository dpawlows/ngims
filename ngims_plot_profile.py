#!/usr/bin/env python

import ngims
import re
import sys
from matplotlib import pyplot as pp
import numpy as np
from glob import glob
import datetime
import pandas as pd 
from collections import defaultdict 

varmap = {16:'O$^+$',32:'O$_2^+$',44:'CO$_2^+$'}
def get_args(argv):

    
    help = 0
    version = None
    start = ''
    end = ''
    datatype = 'csn'
    pvar = ''
    minv = 0.0
    maxv = 0.0
    orbits = ''
    maxalt = 250
    inboundonly = False
    orbitave = False
    plotall = False
    orbit = None

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
                datatype = 'ion'
                IsFound = 1

            m = re.match(r'-csn',arg)
            if m:
                datatype = 'csn'
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

            m = re.match(r'-orbits=(.*)',arg)
            if m:
                orbits=[int(o) for o in m.group(1).split(',')]
                IsFound = 1  

            m = re.match(r'-orbitave',arg)
            if m:
                orbitave=True
                IsFound = 1  

            m = re.match(r'-plotall',arg)
            if m:
                plotall=True
                IsFound = 1  
                
            m = re.match(r'-orbit=(.*)',arg)
            if m:
                orbit=int(m.group(1))
                IsFound = 1  

            if iError > 0:
                print(message)
                exit(iError)

    args = {'start':start,'end':end, 
            'help':help,
            'version':version,
            'datatype':datatype,
            'pvar':pvar,
            'minv':minv,
            'maxv':maxv,
            'orbits':orbits,
            'maxalt':maxalt,
            'inboundonly':inboundonly,
            'orbitave':orbitave,
            'orbit':orbit,
            'plotall':plotall}

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
    print('     Required: -orbits or -start and -end')
    print('                -var')
    print('     -orbits=orbit1,orbit2,orbit3,... : a list of orbit numbers to plot ')
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
    print('     -orbit=X :  also plot that orbit as a thin colored line (assumes -orbitave)')
    print('     -plotall: if orbitave, still plot all orbits')
    exit()

datatype = args['datatype']

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
qualityFlag = ['IV','IU']
if datatype == 'ion':
    speciesColumn = 'ion_mass'
    qualityFlag = ['SCP','SC0']

#User may specify start and end times, or, a list of orbit numbers. Create the filelist.
versions = [] #handle different versions of ngims data
if len(args['start']) > 0:
    files = ngims.getfiles(args['start'],args['end'],dentype=datatype,version=args['version'])
else:
    files = []
    filelist = glob('*'+datatype+'*csv')

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

fig = pp.figure()
ax = pp.subplot(111)

if args['orbitave']:
    profiles = defaultdict(list)  
    alt_grid = np.arange(100, maxalt + 1, 2.5)
    
    overlay_orbit = args['orbit'] if args['orbitave'] and args['orbit'] else None

for fi in files:
    data = ngims.readNGIMS(fi)
    data1 = data[data["alt"] < 350]
    data2 = data1[data1["quality"].isin(qualityFlag)]
    meta = ngims.getorbit(fi)
    orbit_num = meta['orbit']
    is_overlay = (overlay_orbit is not None and orbit_num == overlay_orbit)

    for pvar in varlist:
        newdf = data2[data2[speciesColumn] == data2[speciesColumn].dtype.type(pvar)]

        if newdf.empty:
            print(f"Skipping {pvar} in {fi}: no data")
            continue

        if args['inboundonly']:
            min_idx = newdf['alt'].idxmin()
            newdf = newdf.loc[:min_idx]

        mask_alt = newdf["alt"] < maxalt
        vals = newdf.loc[mask_alt, "abundance"].values * 1e6
        vals = vals[vals > 0]

        if len(vals) == 0:
            continue

        density = np.log10(vals)
        altitude = newdf.loc[mask_alt, "alt"].values

        starred = ''
        frac = (newdf['quality'] == 'SC0').mean()
        if frac > 0.75:
            starred = '*'

        if args['orbitave'] and not is_overlay:    
            interp = np.interp(
                alt_grid,
                altitude[::-1],     # ensure monotonic
                density[::-1],
                left=np.nan,
                right=np.nan
                )

            profiles[pvar].append(interp)

        if not args['orbitave'] or args['plotall']:
            line, = pp.plot(density, altitude)
            if not args['plotall']:
                label = pd.to_datetime(newdf.t_utc.iloc[0]).strftime("%m-%d %H:%M") + starred
                line.set_label(label)
            else:
                line.set_linewidth(.5)
                line.set_color('cornflowerblue')

        if is_overlay:
            meta = ngims.getorbit(fi)
            if meta['orbit'] == overlay_orbit:
                pp.plot(density, altitude, lw=1.5, color='C1',
                        label=f"Orbit {overlay_orbit}")


if args['orbitave']:   
   for pvar, profs in profiles.items():
    arr = np.vstack(profiles[pvar])   # shape: (n_orbits, n_alt)

    mean = np.nanmean(arr, axis=0)
    std  = np.nanstd(arr, axis=0)


    pp.plot(mean, alt_grid, color='k', lw=2,
            label=f"{varmap.get(pvar, pvar)} mean")

    pp.fill_betweenx(
        alt_grid,
        mean - std,
        mean + std,
        color='k',
        alpha=0.25,
        label=r'$\pm 1\sigma$'
    )



if allions:
    pp.legend(loc='upper right',frameon=False)
else: 
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
    # pp.legend(loc='upper right',frameon=False)


if automin:
    mini = np.min(density)
else:
    mini = args['minv']

if automax:
    maxi = np.max(density)
else:
    maxi = args['maxv']

minalt = max([100,min(altitude)])
pp.xlim([mini,maxi])
pp.ylim([minalt,maxalt])
pp.xlabel('Density (#/m$^3$)')
pp.ylabel('Altitude (km)')
pp.savefig('plot.png')

