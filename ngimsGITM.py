"""
Functions and variables useful for working with NGIMS data and the M-GITM
model simultaneously...
"""

import ngims
import pdb
from datetime import datetime, timedelta
from numpy import where, array
import traceback

def outputNGIMS(data,output='ngims.dat',*args,**kwargs):
	'''Creates a data file containing ngims data.
	outputOneOrbit(orbit,output='ngims.dat')
	data: ngims data list
	output='ngims.dat': name of output file
	'''

	altres = 5 #km
	f = open(output,'w')
	altold = 1.0e6
	orbitold = 0
	for d in data:

		alt = d['alt']
		time = d['time']
		orbit = d['orbit']
		d['lon'] = d['lon']+360 if d['lon'] < 0 else d['lon']

		if not 'precision' in kwargs or d['precision'] < kwargs['precision']:
			if (altold-alt) > altres or orbitold != orbit:

				f.write('{:4d}  {:02d}  {:02d}  {:02d}  {:02d}  {:02d}  {:02d}\
				{:8.1f}{:8.1f}{:8.1f}   {:4d}    {:8.3g}\n'.format(time.year,time.month,time.day,\
					time.hour,time.minute,time.second,0,d['lon'],d['lat'],alt,\
					orbit,d['density']))

				altold = alt
				orbitold = orbit

	return 1
	f.close()

def makeSatelliteFile(data,species,satfile = 'sat.dat',*args,**kwargs):
	"""Creates a satellite file for use with M-GITM. Can average the data since NGIMS observations are every 
		few seconds.
	makeSatelliteFile(data,satfile = 'satellite.dat,*args,**kwargs) 
	data: ngims data list
	satfile = 'satfile.dat': name of satellite file
	args:
	kwargs:
		timeAveraging=averagingTime: will average data over averagingTime seconds
		locAveraging=averagingLoc: will average data over averagingLoc km
		location=locationlist; output will be 1 satfile per location. Each location 
			will have one lat, lon, alt per orbit
		locationtype=locationtype (alt lon or lat); required if location kw exists


	"""

	print("Making satellite file.... ")

	isAveraging = False
	isTimeAveraging = False
	isLocAveraging = False

	if 'timeAveraging' in kwargs:
		isAveraging = True
		isTimeAveraging = True
		averagingTime = int(kwargs['timeAveraging'])
		print("Time Averaging... ",averagingTime)

	if 'locAveraging' in kwargs:
		isAveraging = True
		isLocAveraging = True
		averagingLoc = int(kwargs['locAveraging'])
		print("Loc Averaging...",averagingLoc)


	if 'location' in kwargs:
		try:
			locationType = kwargs['locationType'].lower()
			if locationType == 'lat' or locationType == 'latitude':
				locationType = 'lat'
			elif locationType == 'lon' or locationType == 'longitude':
				locationType = 'lon'
			elif locationType == 'alt' or locationType == 'altitude':
				locationType = 'alt'
			else:
				print("invalid locationType in makeSatelliteFile")
				print("stopping in ngimsGITM.py")
				exit(1)

		except:
			print("must specify locationtype in makeSatelliteFile")
			print("stopping in ngimsGITM.py")
			exit(1)

		isLocs = True
		locations = kwargs['location']
		nlocations = len(locations)
		print("getting locations: ",locations)
	else:
		isLocs = False
		nlocations = 1


	dataloader = ngims.DataLoader()

	# satdata = dataloader.get(data,species=species)
	satdata = data

	if isAveraging:
		newdata = []
		if isTimeAveraging:
			oldtime = datetime(1900,1,1,0,0,0)
			tempdata = []

			for d in satdata:
				time = d['time']
				lat = d['lat']
				lon = d['lon']
				alt = d['alt']
				dt = time-oldtime
				if dt.total_seconds() > averagingTime*60.0:
					if len(tempdata) > 1:
						lons = array([temp['lon'] for temp in tempdata])

						if min(lons) < -170 and max(lons) > 170:
							#can't average like normal because we are
							#jumping from +180 to -180!
							nlocs = where(lons < 0)
							lons[nlocs] = lons[nlocs]+360.
							alon = sum(lons)/len(lons)
							alon = alon - 360 if alon > 180 else alon
						else:
							alon = (sum(temp['lon'] for temp in tempdata)/len(tempdata))


						newdata.append({
						'time':tempdata[len(tempdata)/2]['time'],
						'lat':(sum(temp['lat'] for temp in tempdata)/len(tempdata)),
						'lon':alon,
						'alt':(sum(temp['alt'] for temp in tempdata)/len(tempdata)),
						})

					tempdata = []
					oldtime = time

				tempdata.append({
				'time':time,
				'alt':alt,
				'lat':lat,
				'lon':lon
				})

			satdata = newdata


		if isLocAveraging:
			#We are averaging over altitude! 
			newdata = []
			alts = []
			oldd = satdata[0]
			tempdata=[]
			for d in satdata:
				time = d['time']
				lat = d['lat']
				lon = d['lon']
				alt = d['alt']
				alts.append(alt)
				# pdb.set_trace()
				if abs(alts[-1]-alts[0]) > averagingLoc or d['orbit'] != d['orbit']:
					if len(tempdata) > 1:
						lons = array([temp['lon'] for temp in tempdata])
						if min(lons) < -170 and max(lons) > 170:
							#can't average like normal because we are
							#jumping from +180 to -180!
							nlocs = where(lons < 0)
							lons[nlocs] = lons[nlocs]+360.
							alon = sum(lons)/len(lons)
							alon = alon - 360 if alon > 180 else alon
						else:
							alon = (sum(temp['lon'] for temp in tempdata)/len(tempdata))

						# pdb.set_trace()
						newdata.append({
						'time':tempdata[int(len(tempdata)/2)]['time'],
						'lat':(sum(temp['lat'] for temp in tempdata)/len(tempdata)),
						'lon':alon,
						'alt':(sum(temp['alt'] for temp in tempdata)/len(tempdata)),
						})

					tempdata = []
					alts = []
					oldd = d

				tempdata.append({
				'time':time,
				'alt':alt,
				'lat':lat,
				'lon':lon
				})

			satdata = newdata


	if isLocs:
		#Getting data at specific locations

		oldd = satdata[0]
		tempdata = [[] for _ in range(nlocations)]
		for d in satdata:
			for iloc in range(nlocations):
				if (d[locationType]-locations[iloc])*(oldd[locationType]-locations[iloc]) < 0 \
				and oldd['orbit'] == d['orbit']:

					if abs(d[locationType] - oldd[locationType]) > 2.0:
						print("Warning!!! Locations are quite different.  This is unexpected\
						in ngitmsGITM.py.  I assume you know what you are doing.  Proceeding optimistically.")
						breakpoint()

					if abs(d[locationType]-locations[iloc]) < abs(oldd[locationType]-locations[iloc]):
						time = d['time']
						lat = d['lat']
						lon = d['lon']
						alt = d['alt']

					else:
						time = oldd['time']
						lat = oldd['lat']
						lon = oldd['lon']
						alt = oldd['alt']

					tempdata[iloc].append({
					'time':time,
					'alt':alt,
					'lat':lat,
					'lon':lon
					})

			oldd = d

		satdata = tempdata


	suffixloc = satfile.find('.dat')
	for iloc in range(nlocations):
		if suffixloc > -1 and nlocations > 1:
			thissatfile = satfile[0:suffixloc]+'_0'+str(iloc)+satfile[suffixloc:]
		else:
			thissatfile = satfile
		f = open(thissatfile,'w')
		f.write('#START\n')
		if nlocations > 1:
			tempdata = satdata[iloc]
		else:
			tempdata = satdata

		for d in tempdata:
			time = d['time']
			d['lon'] = d['lon']+360 if d['lon'] < 0 else d['lon']
			f.write('{:4d}  {:02d}  {:02d}  {:02d}  {:02d}  {:02d}  {:02d}\
			{:8.1f}{:8.1f}{:8.1f}\n'.format(time.year,time.month,time.day,\
				time.hour,time.minute,time.second,0,d['lon'],d['lat'],d['alt']))


	return satdata
