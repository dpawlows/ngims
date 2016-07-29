"""
Functions and variables useful for working with NGIMS data and the M-GITM 
model simultaneously...
"""

import ngims

def makeSatelliteFile(data,satfile = 'satellite.dat'):
	"""Creates a satellite file for use with M-GITM.
	makeSatelliteFile(data,satfile = 'satellite.dat')
	data is ngims data list."""

        print "Making satellite file...."
        dataloader = ngims.DataLoader()
        satdata = dataloader.get(data,species='Ar')

        f = open(satfile,'w')
        f.write('#START\n')

        for d in satdata:
            time = d['time']
            f.write('{:4d}\t{:02d}\t{:02d}\t{:02d}\t{:02d}\t{:02d}\t{:4.1f}\t{:4.1f}\t{:4.1f}\n'.format(time.year,time.month,time.day,\
                time.hour,time.minute,time.second,d['lon'],d['lat'],d['alt']))


        return satdata