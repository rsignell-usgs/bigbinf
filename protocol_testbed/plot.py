"""
Reads in .dump files and plots them
"""
from datetime import datetime, timedelta
import argparse
import json
import sys

from matplotlib import pyplot, dates

from protocols import PROC_ARGS
from helpers import get_dump_fnames, TIME_FORMAT

PLOT_TIME_FORMAT = "%M:%S"
MAP_4 = [(0, 0), (0, 1), (1, 0), (1, 1)]

def plot_packets(dumps, splots):
    """
    Plots time on the x axis vs length on the y axis
    """
    # Convert all the times to an offset from 0
    axes = []

    for dump in dumps:
        print "Processing %s dump" % dump["protocol"]
        x = [datetime.strptime(l["time"], TIME_FORMAT) for l in dump["packets"]]
        t0 = min(x)
        dt = timedelta(hours=t0.hour, minutes=t0.minute, seconds=t0.second,
                       microseconds=t0.microsecond)
        x = [t-dt for t in x]
        y = [l["length"] for l in dump["packets"]]
        axes.append((x, y))

    if splots == 4:
        _, axarr = pyplot.subplots(2, 2)
        for i in range(4):
            axarr[MAP_4[i]].plot(axes[i][0], axes[i][1], ".")
            axarr[MAP_4[i]].xaxis.set_major_formatter(dates.DateFormatter(PLOT_TIME_FORMAT))
            axarr[MAP_4[i]].set_title(dumps[i]["protocol"])
            axarr[MAP_4[i]].set_xlabel("Time elapsed")
            axarr[MAP_4[i]].set_ylabel("Length of payload (bytes)")

    pyplot.show()

def plot_aggregate(dumps):
    pass
