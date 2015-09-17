"""
Reads in .dump files and plots them
"""
from datetime import datetime, timedelta

from matplotlib import pyplot, dates

from helpers import TIME_FORMAT, aggregate, calc_speed, sum_bytes
from protocols import PROC_ARGS

PLOT_TIME_FORMAT = "%M:%S"

def plot_packets(dumps):
    """
    Plots time on the x axis vs length on the y axis
    """
    map_4 = [(0, 0), (0, 1), (1, 0), (1, 1)]
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
        axarr[map_4[i]].plot(axes[i][0], axes[i][1], ".")
        axarr[map_4[i]].xaxis.set_major_formatter(dates.DateFormatter(PLOT_TIME_FORMAT))
        axarr[map_4[i]].set_title(dumps[i]["protocol"])
        axarr[map_4[i]].set_xlabel("Time elapsed")
        axarr[map_4[i]].set_ylabel("Length of payload (bytes)")

    pyplot.suptitle("Individual Packets", size=16)
    pyplot.show()

def plot_aggregate(dumps):
    """
    Displays aggragated statistics as bar graphs
    """
    bar_width = 0.3
    index = range(4)

    _, axarr = pyplot.subplots(2, sharex="col", sharey="row")

    total_transferred = []
    filesize = sum(int(d["file_size"]) for d in dumps)/len(dumps)
    axarr[0].plot([filesize]*5, "r--", label="filesize")

    for i, p in enumerate(PROC_ARGS.keys()):
        _, _, t_t = aggregate([sum_bytes(d) for d in dumps if d["protocol"] == p])
        _, _, s_t = aggregate([calc_speed(d) for d in dumps if d["protocol"] == p])
        total_transferred.append(t_t)


        # Transfer
        axarr[0].bar(i, t_t, bar_width)
        # Speed
        axarr[1].bar(i, s_t, bar_width)

    diff = max(abs(x-filesize) for x in total_transferred)
    axarr[0].set_ylim([filesize-2*diff, filesize+2*diff])
    axarr[0].set_ylabel("Total transferred (bytes)")
    axarr[0].legend()
    axarr[1].set_ylabel("Total speed (bytes/s)")
    axarr[1].set_xticks([i+bar_width/2 for i in index])
    axarr[1].set_xticklabels(("SCP", "HPN-SCP", "FTP", "GridFTP"))
    pyplot.suptitle("Aggregated Transfer Dumps", size=16)
    pyplot.show()

