from ngims import *

def makeSatelliteFile(data,satfile = 'satellite.dat'):
        print "Making satellite file...."

        satdata = ngims.get(data,species='Ar')

        f = open(satfile,'w')
        f.write('#START\n')

        for d in satdata:
            time = d['time']
            f.write('{:4d}\t{:02d}\t{:02d}\t{:02d}\t{:02d}\t{:02d}\t{:4.1f}\t{:4.1f}\t{:4.1f}\n'.format(time.year,time.month,time.day,\
                time.hour,time.minute,time.second,d['lon'],d['lat'],d['alt']))


        return satdata