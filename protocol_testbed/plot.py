"""
Reads in .dump files and plots them
"""
from datetime import datetime, timedelta

from matplotlib import pyplot, dates

from helpers import TIME_FORMAT, aggregate, calc_speed, sum_bytes
from protocols import PROC_ARGS

PLOT_TIME_FORMAT = "%M:%S"
MAP_4 = [(0, 0), (0, 1), (1, 0), (1, 1)]

def plot_packets(dumps):
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

    _, axarr = pyplot.subplots(2, 2)
    for i in range(4):
        axarr[MAP_4[i]].plot(axes[i][0], axes[i][1], ".")
        axarr[MAP_4[i]].xaxis.set_major_formatter(dates.DateFormatter(PLOT_TIME_FORMAT))
        axarr[MAP_4[i]].set_title(dumps[i]["protocol"])
        axarr[MAP_4[i]].set_xlabel("Time elapsed")
        axarr[MAP_4[i]].set_ylabel("Length of payload (bytes)")

    pyplot.show()

def plot_aggregate(dumps):
    """
    Displays aggragated statistics as bar graphs
    """
    bar_width = 0.3
    index = range(4)

    _, axarr = pyplot.subplots(3, sharex="col", sharey="row")

    for i, p in enumerate(PROC_ARGS.keys()):
        t_d, t_u, t_t = aggregate([sum_bytes(d) for d in dumps if d["protocol"] == p])
        s_d, s_u, s_t = aggregate([calc_speed(d) for d in dumps if d["protocol"] == p])

        filesize = sum(int(d["file_size"]) for d in dumps)/len(dumps)
        ratio = (1-float(t_t)/float(filesize))*100

        # Transfer
        axarr[0].bar(i , t_t, bar_width)
        # Speed
        axarr[1].bar(i, s_t, bar_width)
        # Overhead
        axarr[2].bar(i, ratio, bar_width)

    axarr[2].set_xticks(index)
    axarr[2].set_xticklabels(("SCP", "HPN-SCP", "FTP", "GridFTP"))
    pyplot.show()



