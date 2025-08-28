#!/usr/bin/env python 

# Quickly plot a sat file vs. a raw NGIMS csv

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import glob
import ngimsGITM

def plot_sat_vs_raw(satfile,csvfiles):

    """Plots lon, lat, alt vs time"""
    sat_df = ngimsGITM.read_satellite_file(satfile)
    raw_df = ngimsGITM.read_raw_csv_files(csvfiles)  # or use specific pattern like "mvn_ngims*.csv"
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    axs[0].scatter(sat_df['time'], sat_df['lon'], label='Satellite', lw=1.5,marker='^')
    axs[0].scatter(raw_df['time'], raw_df['long'], color='gray', alpha=0.4, s=6, label='Raw')
    axs[0].set_ylabel('Longitude (°)')

    axs[1].scatter(sat_df['time'], sat_df['lat'], lw=1.5,marker='^')
    axs[1].scatter(raw_df['time'], raw_df['lat'], color='gray', alpha=0.4, s=6)
    axs[1].set_ylabel('Latitude (°)')

    axs[2].scatter(sat_df['time'], sat_df['alt'], lw=1.5,marker='^')
    axs[2].scatter(raw_df['time'], raw_df['alt'], color='gray', alpha=0.4, s=6)
    axs[2].set_ylabel('Altitude (km)')
    axs[2].set_xlabel('Time')

    for ax in axs:
        ax.grid(True)

    axs[0].legend()
    plt.tight_layout()
    plt.savefig('satplot.png')

if __name__ == "__main__":
    import sys
    import os

    # Example usage:
    # python plot_sat_vs_raw.py sat.dat raw1.csv raw2.csv raw3.csv
    if len(sys.argv) < 3:
        print("Usage: python plot_sat_vs_raw.py satfile.csv file1.csv [file2.csv ...]")
        sys.exit(1)

    satfile = sys.argv[1]
    csvfiles = sys.argv[2:]

    plot_sat_vs_raw(satfile, csvfiles)