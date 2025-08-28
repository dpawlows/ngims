#!/usr/bin/env python

"""Plot NGIMS satellite tracks from one or more CSV files."""

import argparse
import ngims
from matplotlib import pyplot as pp


def main():
    parser = argparse.ArgumentParser(
        description="Plot one or more NGIMS satellite tracks"
    )
    parser.add_argument("files", nargs="+", help="NGIMS CSV files to plot")
    args = parser.parse_args()

    data = []
    for filename in args.files:
        data += ngims.readCSN(filename, outbound=True)

    ngims.plot_track(data)
    pp.show()


if __name__ == "__main__":
    main()
