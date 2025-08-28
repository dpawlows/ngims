#!/usr/bin/env python

"""Plot NGIMS satellite tracks from one or more CSV files.

Points are color-coded by time. For a single file, each point's color
corresponds to its timestamp. When multiple files are supplied, all points
from a file share a color based on that file's start time.
"""

import argparse
import ngims
import pandas as pd
from matplotlib import pyplot as pp
from matplotlib import cm, colors, dates as mdates
import os
import re

def timestamp_from_filename(filename):
    """Extract a timestamp string from a NGIMS filename."""
    base = os.path.basename(filename)
    match = re.search(r'(\d{8}[_T]?\d{6})', base)
    if match:
        return match.group(1).replace('_', 'T')
    return 'unknown'

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot one or more NGIMS satellite tracks",
    )
    parser.add_argument("files", nargs="+", help="NGIMS CSV files to plot")
    args = parser.parse_args()

    # Load each file into a DataFrame sorted by time
    dfs = []
    timestamp = timestamp_from_filename(args.files[0])
    for filename in args.files:
        data = ngims.readCSN(filename, outbound=True)
        df = pd.DataFrame(data).sort_values("time")
        dfs.append(df)

    lon_key = "lon" if "lon" in dfs[0].columns else "long"

    fig, axs = pp.subplots(2, 1, figsize=(8, 8), constrained_layout=True)
    cmap = pp.get_cmap("rainbow_r")
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)

    if len(dfs) == 1:
        df = dfs[0]
        times = mdates.date2num(df["time"])
        sc = axs[0].scatter(
            df[lon_key],
            df["lat"],
            c=times,
            cmap=cmap,
            s=5,
        )
        cbar = fig.colorbar(sc, ax=axs[0], fraction=0.025, pad=0.04)
        cbar.ax.yaxis.set_major_locator(locator)
        cbar.ax.yaxis.set_major_formatter(formatter)
        cbar.set_label("Time (UTC)")
        axs[1].scatter(df["time"], df["alt"], c=times, cmap=cmap, s=5)
    else:
        start_times = [mdates.date2num(df["time"].min()) for df in dfs]
        norm = colors.Normalize(min(start_times), max(start_times))
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)
        for df, tnum in zip(dfs, start_times):
            color = cmap(norm(tnum))
            axs[0].plot(df[lon_key], df["lat"], ".", color=color, ms=2)
            axs[1].plot(df["time"], df["alt"], ".", color=color, ms=2)
        cbar = fig.colorbar(sm, ax=axs[0], fraction=0.025, pad=0.04)
        cbar.ax.yaxis.set_major_locator(locator)
        cbar.ax.yaxis.set_major_formatter(formatter)
        cbar.set_label("File start time (UTC)")

    axs[0].set_xlabel("Longitude (°)")
    axs[0].set_ylabel("Latitude (°)")
    axs[0].set_title("Satellite Location")

    axs[1].set_xlabel("Time")
    axs[1].set_ylabel("Altitude (km)")
    axs[1].set_title("Altitude vs Time")

    plotfile = "track_{}.png".format(timestamp)
    pp.savefig(plotfile)
    print("Saving plot to {}".format(plotfile))
if __name__ == "__main__":
    main()

