#!/usr/bin/env python

# Generate M-GITM satellite file from MAVEN NGIMS data.
import argparse
import ngims
import ngimsGITM
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Generate M-GITM satellite file from MAVEN NGIMS data.")

    parser.add_argument('-s','--start', required=True, help='Start date (YYYYMMDD)')
    parser.add_argument('-e','--end', required=True, help='End date (YYYYMMDD)')
    parser.add_argument('--version', default=None, help='Optional version string to filter NGIMS files')
    parser.add_argument('--dentype', default='csn', choices=['csn', 'ion'], help='Density type')
    parser.add_argument('--outbound', action='store_true', help='Use outbound leg of orbit (default is inbound)')
    parser.add_argument('--outfile', default='satellite.dat', help='Output satellite filename')
    parser.add_argument('--maxalt', type=float, help='Maximum altitude (km) to include in output')
    parser.add_argument('--location', nargs='+', type=float, help='List of locations (float) for output filtering')
    parser.add_argument('--locationType', choices=['alt', 'lon', 'lat'], help='Type of location (alt, lon, lat)')
    parser.add_argument('--locAveraging', type=float, help='Altitude averaging window in km')
    parser.add_argument('--timeAveraging', type=float, help='Time averaging window in minutes')

    return parser.parse_args()

def main():
    args = parse_args()

    files = ngims.getfiles(
        start=args.start,
        end=args.end,
        dentype=args.dentype,
        version=args.version
    )

    data_raw = ngims.getCSN(files, outbound=args.outbound)
    dataloader = ngims.DataLoader()
    data = dataloader.get(data_raw)

    kwargs = {}
    if args.location:
        kwargs['location'] = args.location
        if not args.locationType:
            raise ValueError("Must specify --locationType if --location is used.")
        kwargs['locationType'] = args.locationType

    if args.locAveraging:
        kwargs['locAveraging'] = args.locAveraging

    if args.timeAveraging:
        kwargs['timeAveraging'] = args.timeAveraging

    if args.maxalt:
        kwargs['maxalt'] = args.maxalt

    ngimsGITM.makeSatelliteFile(data, satfile=args.outfile, **kwargs)

if __name__ == '__main__':
    main()
